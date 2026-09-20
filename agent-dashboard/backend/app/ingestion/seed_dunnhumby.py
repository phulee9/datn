"""Nạp toàn bộ CSV Dunnhumby vào staging layer để dbt transform."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TypedDict

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import SeedError
from app.db.models import StagingProduct, StagingTransaction

SeedSummary = TypedDict(
    "SeedSummary",
    {"store_count": int, "product_count": int, "receipt_count": int, "item_count": int, "skipped_existing_receipts": int, "date_from": date | None, "date_to": date | None},
)


def create_seed_summary(product_count: int, transaction_count: int, skipped: int) -> SeedSummary:
    """Tạo payload tương thích API seed từ kết quả raw load."""
    return {
        "store_count": 0,
        "product_count": product_count,
        "receipt_count": transaction_count,
        "item_count": transaction_count,
        "skipped_existing_receipts": skipped,
        "date_from": None,
        "date_to": None,
    }


def resolve_source_files(raw_dir: Path) -> tuple[Path, Path]:
    """Kiểm tra product.csv và transaction_data.csv tồn tại.

    Output:
        Tuple đường dẫn product và transaction.
    """
    product_path = raw_dir / "product.csv"
    transaction_path = raw_dir / "transaction_data.csv"
    missing = [path.name for path in (product_path, transaction_path) if not path.exists()]
    if missing:
        raise SeedError(f"Thiếu file Dunnhumby: {missing}. Đặt file vào {raw_dir}.")
    return product_path, transaction_path


def normalize_text(value: object) -> str | None:
    """Đổi giá trị Pandas nullable thành text hoặc None cho PostgreSQL."""
    return None if pd.isna(value) else str(value)


def build_product_rows(product_frame: pd.DataFrame, fetch_date: date) -> list[dict]:
    """Đổi các cột product.csv thành record staging.product.

    Output:
        Danh sách record bulk insert/upsert.
    """
    required_columns = {"PRODUCT_ID", "DEPARTMENT", "COMMODITY_DESC", "SUB_COMMODITY_DESC", "MANUFACTURER", "BRAND", "CURR_SIZE_OF_PRODUCT"}
    missing = required_columns - set(product_frame.columns)
    if missing:
        raise SeedError(f"product.csv thiếu cột: {sorted(missing)}")
    return [
        {
            "product_id": int(row.PRODUCT_ID), "department": normalize_text(row.DEPARTMENT),
            "commodity_desc": normalize_text(row.COMMODITY_DESC), "sub_commodity_desc": normalize_text(row.SUB_COMMODITY_DESC),
            "manufacturer": normalize_text(row.MANUFACTURER), "brand": normalize_text(row.BRAND),
            "curr_size_of_product": normalize_text(row.CURR_SIZE_OF_PRODUCT),
            "dih_fetch_day": fetch_date.day, "dih_fetch_month": fetch_date.month, "dih_fetch_year": fetch_date.year,
        }
        for row in product_frame.itertuples(index=False)
    ]


def build_transaction_rows(transaction_frame: pd.DataFrame, fetch_date: date) -> list[dict]:
    """Đổi transaction CSV chunk thành record staging.transaction.

    Output:
        Record chuẩn hóa để bulk insert.
    """
    required_columns = {"household_key", "BASKET_ID", "DAY", "PRODUCT_ID", "QUANTITY", "SALES_VALUE", "STORE_ID", "RETAIL_DISC", "TRANS_TIME", "WEEK_NO", "COUPON_DISC", "COUPON_MATCH_DISC"}
    missing = required_columns - set(transaction_frame.columns)
    if missing:
        raise SeedError(f"transaction_data.csv thiếu cột: {sorted(missing)}")
    return [
        {
            "household_key": None if pd.isna(row.household_key) else int(row.household_key),
            "basket_id": int(row.BASKET_ID), "day": int(row.DAY), "product_id": int(row.PRODUCT_ID),
            "quantity": float(row.QUANTITY), "sales_value": float(row.SALES_VALUE), "store_id": int(row.STORE_ID),
            "retail_disc": None if pd.isna(row.RETAIL_DISC) else float(row.RETAIL_DISC),
            "trans_time": None if pd.isna(row.TRANS_TIME) else int(row.TRANS_TIME),
            "week_no": None if pd.isna(row.WEEK_NO) else int(row.WEEK_NO),
            "coupon_disc": None if pd.isna(row.COUPON_DISC) else float(row.COUPON_DISC),
            "coupon_match_disc": None if pd.isna(row.COUPON_MATCH_DISC) else float(row.COUPON_MATCH_DISC),
            "dih_fetch_day": fetch_date.day, "dih_fetch_month": fetch_date.month, "dih_fetch_year": fetch_date.year,
        }
        for row in transaction_frame.itertuples(index=False)
    ]


async def insert_rows_in_batches(session: AsyncSession, model, rows: list[dict], batch_size: int) -> None:
    """Ghi danh sách record bằng SQL bulk insert theo batch."""
    for start_index in range(0, len(rows), batch_size):
        await session.execute(insert(model), rows[start_index : start_index + batch_size])


async def seed_dunnhumby(session: AsyncSession) -> SeedSummary:
    """Nạp toàn bộ raw CSV vào staging, chỉ chạy một lần cho cùng database.

    Output:
        SeedSummary ghi số product/transaction staging đã nạp.
    """
    existing_transaction_count = await session.scalar(select(func.count()).select_from(StagingTransaction))
    if existing_transaction_count:
        print(f"Staging đã có {existing_transaction_count:,} transaction, bỏ qua load raw trùng.", flush=True)
        existing_product_count = await session.scalar(select(func.count()).select_from(StagingProduct))
        return create_seed_summary(int(existing_product_count or 0), 0, int(existing_transaction_count))

    fetch_date = date.today()
    product_path, transaction_path = resolve_source_files(settings.dunnhumby_raw_dir)
    print(f"Đang đọc dữ liệu raw từ {settings.dunnhumby_raw_dir} ...", flush=True)
    product_frame = pd.read_csv(product_path)
    product_rows = build_product_rows(product_frame, fetch_date)
    product_insert = insert(StagingProduct).values(product_rows)
    product_update_columns = {
        column: getattr(product_insert.excluded, column)
        for column in ["department", "commodity_desc", "sub_commodity_desc", "manufacturer", "brand", "curr_size_of_product", "dih_fetch_day", "dih_fetch_month", "dih_fetch_year"]
    }
    await session.execute(product_insert.on_conflict_do_update(index_elements=["product_id"], set_=product_update_columns))
    print(f"Đã nạp {len(product_rows):,} product raw.", flush=True)

    transaction_count = 0
    for transaction_chunk in pd.read_csv(transaction_path, chunksize=settings.seed_batch_size):
        transaction_rows = build_transaction_rows(transaction_chunk, fetch_date)
        await session.execute(insert(StagingTransaction), transaction_rows)
        transaction_count += len(transaction_rows)
        if transaction_count % (settings.seed_batch_size * 10) == 0:
            print(f"  Đã nạp {transaction_count:,} transaction ...", flush=True)
    await session.commit()
    print(f"Đã nạp {transaction_count:,} transaction vào staging.", flush=True)
    return create_seed_summary(len(product_rows), transaction_count, 0)
