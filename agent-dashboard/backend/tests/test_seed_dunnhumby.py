"""Unit test cho hàm chuyển đổi Dunnhumby, không chạm DB."""

import pandas as pd
from datetime import datetime

from app.ingestion.seed_dunnhumby import build_receipt_tables, filter_top_skus, filter_top_stores, map_relative_day


def test_map_relative_day_uses_one_based_offset() -> None:
    """DAY=1 map chính xác base_date, DAY=2 là hôm sau."""
    base_date = datetime(2024, 1, 1)
    assert map_relative_day(1, base_date).isoformat() == "2024-01-01"
    assert map_relative_day(2, base_date).isoformat() == "2024-01-02"


def test_filter_functions_reduce_dataset() -> None:
    """Bộ lọc top store/SKU giữ đúng số lượng mong đợi."""
    transactions = pd.DataFrame(
        [
            {"STORE_ID": 1, "BASKET_ID": 10, "PRODUCT_ID": 1, "QUANTITY": 2},
            {"STORE_ID": 1, "BASKET_ID": 11, "PRODUCT_ID": 2, "QUANTITY": 10},
            {"STORE_ID": 2, "BASKET_ID": 12, "PRODUCT_ID": 2, "QUANTITY": 10},
        ]
    )
    assert filter_top_stores(transactions, 1) == {1}
    assert filter_top_skus(transactions, 1) == {"2"}


def test_build_receipt_tables_groups_basket_correctly() -> None:
    """Mỗi basket thành một receipt; từng dòng thành item với unit_price và line_total."""
    base_date = datetime(2024, 1, 1)
    transactions = pd.DataFrame(
        [
            {"BASKET_ID": 1, "STORE_ID": 292, "DAY": 1, "PRODUCT_ID": "100", "QUANTITY": 2, "SALES_VALUE": 4.0, "COMMODITY_DESC": "SOFT DRINKS"},
            {"BASKET_ID": 1, "STORE_ID": 292, "DAY": 1, "PRODUCT_ID": "101", "QUANTITY": 1, "SALES_VALUE": 5.0, "COMMODITY_DESC": "BEER"},
            {"BASKET_ID": 2, "STORE_ID": 292, "DAY": 2, "PRODUCT_ID": "100", "QUANTITY": 1, "SALES_VALUE": 2.0, "COMMODITY_DESC": "SOFT DRINKS"},
        ]
    )
    receipts, items = build_receipt_tables(transactions, base_date)
    assert len(receipts) == 2
    assert len(items) == 3
    first_receipt = receipts[receipts["BASKET_ID"] == 1].iloc[0]
    assert first_receipt["receipt_date"].isoformat() == "2024-01-01"
    assert first_receipt["total_amount"] == 9.0
    first_item = items[(items["basket_id"] == 1) & (items["sku"] == "100")].iloc[0]
    assert first_item["unit_price"] == 2.0
    assert first_item["line_total"] == 4.0
