"""Các hàm CRUD và truy vấn analytics dùng chung cho staging, silver, gold."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy import Select, delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ForecastTrainingRun, Product, ProductAlias, Receipt, ReceiptItem, Store


def build_fetch_partition(target_date: date) -> dict[str, int]:
    """Chuyển receipt/business fetch date thành ba cột dih_fetch_*."""
    return {"dih_fetch_day": target_date.day, "dih_fetch_month": target_date.month, "dih_fetch_year": target_date.year}


async def get_or_create_store_by_source_code(
    session: AsyncSession, source_code: str, store_name: str, fetch_date: date
) -> Store:
    """Tìm dim_store theo mã nguồn; nếu chưa có thì tạo mới."""
    fetch_values = build_fetch_partition(fetch_date)
    result = await session.execute(select(Store).where(Store.source_code == source_code))
    store = result.scalar_one_or_none()
    if store is not None:
        store.store_name = store_name
        store.dih_fetch_day = fetch_values["dih_fetch_day"]
        store.dih_fetch_month = fetch_values["dih_fetch_month"]
        store.dih_fetch_year = fetch_values["dih_fetch_year"]
        return store
    store = Store(source_code=source_code, store_name=store_name, **fetch_values)
    session.add(store)
    await session.flush()
    return store


async def upsert_product(
    session: AsyncSession, sku: str, display_name: str, category: str | None, fetch_date: date
) -> Product:
    """Thêm dim_product theo SKU; nếu đã có thì cập nhật hiển thị."""
    fetch_values = build_fetch_partition(fetch_date)
    result = await session.execute(select(Product).where(Product.sku == sku))
    product = result.scalar_one_or_none()
    if product is None:
        product = Product(sku=sku, display_name=display_name, category=category, **fetch_values)
        session.add(product)
        await session.flush()
        return product
    product.display_name = display_name
    product.category = category
    product.dih_fetch_day = fetch_values["dih_fetch_day"]
    product.dih_fetch_month = fetch_values["dih_fetch_month"]
    product.dih_fetch_year = fetch_values["dih_fetch_year"]
    return product


async def get_receipt_by_source(session: AsyncSession, source_type: str, source_receipt_id: str) -> Receipt | None:
    """Tìm staging receipt theo khóa nguồn."""
    result = await session.execute(
        select(Receipt).where(Receipt.source_type == source_type, Receipt.source_receipt_id == source_receipt_id)
    )
    return result.scalar_one_or_none()


async def get_receipt_by_image_hash(session: AsyncSession, image_hash: str) -> Receipt | None:
    """Tìm staging receipt theo SHA-256 hash ảnh để chống upload trùng."""
    result = await session.execute(select(Receipt).where(Receipt.image_hash == image_hash))
    return result.scalar_one_or_none()


async def create_pending_receipt(
    session: AsyncSession, image_uri: str, image_hash: str, source_receipt_id: str, fetch_date: date
) -> Receipt:
    """Tạo staging receipt pending ngay khi upload."""
    receipt = Receipt(
        image_hash=image_hash, image_uri=image_uri, source_type="gemini_upload",
        source_receipt_id=source_receipt_id, status="pending",
        dih_fetch_day=fetch_date.day, dih_fetch_month=fetch_date.month, dih_fetch_year=fetch_date.year,
    )
    session.add(receipt)
    await session.commit()
    await session.refresh(receipt)
    return receipt


async def update_receipt_status(
    session: AsyncSession, receipt_id: int, status: str, error_message: str | None = None
) -> Receipt | None:
    """Cập nhật trạng thái vòng đời receipt staging."""
    receipt = await session.get(Receipt, receipt_id)
    if receipt is None:
        return None
    receipt.status = status
    receipt.error_message = error_message
    await session.commit()
    await session.refresh(receipt)
    return receipt


async def save_extracted_receipt(
    session: AsyncSession,
    receipt_id: int,
    store_id: int | None,
    receipt_date: date | None,
    total_amount: Decimal | None,
    raw_json: dict[str, Any],
    confidence_score: Decimal,
    status: str,
    items: list[dict[str, Any]],
) -> Receipt | None:
    """Ghi kết quả Gemini/review vào staging receipt và thay toàn bộ item."""
    receipt = await session.get(Receipt, receipt_id)
    if receipt is None:
        return None
    receipt.store_id = store_id
    receipt.receipt_date = receipt_date
    receipt.total_amount = total_amount
    receipt.raw_json = raw_json
    receipt.confidence_score = confidence_score
    receipt.status = status
    receipt.error_message = None
    await session.execute(delete(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id))
    for item in items:
        session.add(
            ReceiptItem(
                receipt_id=receipt_id, product_id=item.get("product_id"), raw_item_name=item["raw_item_name"],
                quantity=item["quantity"], unit_price=item.get("unit_price"), line_total=item.get("line_total"),
                match_method=item.get("match_method"), match_score=item.get("match_score"),
                dih_fetch_day=receipt.dih_fetch_day, dih_fetch_month=receipt.dih_fetch_month, dih_fetch_year=receipt.dih_fetch_year,
            )
        )
    await session.commit()
    return await get_receipt_with_items(session, receipt_id)


async def get_receipt_with_items(session: AsyncSession, receipt_id: int) -> Receipt | None:
    """Lấy staging receipt kèm item."""
    result = await session.execute(
        select(Receipt).options(selectinload(Receipt.items).selectinload(ReceiptItem.product)).where(Receipt.id == receipt_id)
    )
    return result.scalar_one_or_none()


async def list_receipts(session: AsyncSession, status: str | None = None, store_id: int | None = None) -> list[Receipt]:
    """Liệt kê receipt staging theo trạng thái hoặc store."""
    statement: Select[tuple[Receipt]] = select(Receipt).options(
        selectinload(Receipt.items).selectinload(ReceiptItem.product)
    ).order_by(Receipt.id.desc())
    if status:
        statement = statement.where(Receipt.status == status)
    if store_id is not None:
        statement = statement.where(Receipt.store_id == store_id)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def list_products(session: AsyncSession) -> list[Product]:
    """Lấy toàn bộ dim_product kèm alias để map tên thô."""
    result = await session.execute(select(Product).options(selectinload(Product.aliases)))
    return list(result.scalars().all())


async def add_product_alias(session: AsyncSession, product_id: int, raw_alias: str, fetch_date: date) -> None:
    """Ghi dim_product_alias nếu chưa tồn tại."""
    normalized_alias = " ".join(raw_alias.casefold().split())
    fetch_values = build_fetch_partition(fetch_date)
    result = await session.execute(select(ProductAlias).where(ProductAlias.normalized_alias == normalized_alias))
    if result.scalar_one_or_none() is not None:
        return
    session.add(ProductAlias(product_id=product_id, raw_alias=raw_alias, normalized_alias=normalized_alias, **fetch_values))


async def get_daily_sales_history(session: AsyncSession, sku: str, store_id: int | None) -> pd.DataFrame:
    """Gom doanh số ngày cho một SKU; ngày thiếu sau đó được làm dense tại mart forecast."""
    statement = (
        select(
            text("mart_daily_sales.business_date AS date"), text("mart_daily_sales.store_id"),
            text("mart_daily_sales.sku"), text("mart_daily_sales.category"), text("mart_daily_sales.quantity AS qty"),
        )
        .select_from(text("gold.mart_daily_sales"))
        .where(text("mart_daily_sales.sku = :sku"))
        .order_by(text("mart_daily_sales.business_date"))
    )
    params: dict[str, Any] = {"sku": sku}
    if store_id is not None:
        statement = statement.where(text("mart_daily_sales.store_id = :store_id"))
        params["store_id"] = store_id
    result = await session.execute(statement, params)
    rows = result.mappings().all()
    if not rows:
        return pd.DataFrame(columns=["date", "store_id", "sku", "category", "qty"])
    frame = pd.DataFrame([dict(row) for row in rows])
    frame["date"] = pd.to_datetime(frame["date"])
    frame["qty"] = frame["qty"].astype(float)
    return frame


async def get_forecast_training_input(session: AsyncSession) -> pd.DataFrame:
    """Lấy toàn bộ feature row đã chuẩn bị từ gold.v_forecast_input.

    Output:
        DataFrame CatBoost train input, không rebuild lag trong API.
    """
    result = await session.execute(text("SELECT * FROM gold.v_forecast_input ORDER BY business_date"))
    return pd.DataFrame([dict(row) for row in result.mappings().all()])


async def get_gold_max_business_date(session: AsyncSession) -> date | None:
    """Lấy business_date lớn nhất hiện có trong gold mart."""
    result = await session.execute(select(func.max(text("business_date"))).select_from(text("gold.mart_daily_sales")))
    value = result.scalar_one_or_none()
    if value is None:
        return None
    return date.fromisoformat(str(value)) if isinstance(value, str) else value


async def count_confirmed_receipts_since_last_train(session: AsyncSession) -> tuple[int, date | None]:
    """Đếm số receipt confirmed trong silver kể từ lần train gần nhất."""
    last_train = await session.execute(select(func.max(ForecastTrainingRun.business_date_to)))
    last_business_date = last_train.scalar_one_or_none()
    if last_business_date is None:
        result = await session.execute(select(func.count()).select_from(text("silver.fact_receipt")))
        return int(result.scalar_one()), None
    result = await session.execute(
        select(func.count()).select_from(text("silver.fact_receipt")).where(text("receipt_date > :date")), {"date": str(last_business_date)}
    )
    return int(result.scalar_one()), last_business_date
