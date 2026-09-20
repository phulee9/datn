"""Chuẩn hóa tên hàng thô từ hóa đơn thành product_id nội bộ."""

from typing import TypedDict

from rapidfuzz import fuzz, process
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Product
from app.db.repository import list_products


ProductMatch = TypedDict(
    "ProductMatch",
    {"product_id": int | None, "sku": str | None, "match_method": str | None, "score": int | None},
)


def create_product_match(
    product_id: int | None,
    sku: str | None,
    match_method: str | None,
    score: int | None,
) -> ProductMatch:
    """Tạo dict ProductMatch."""
    return {"product_id": product_id, "sku": sku, "match_method": match_method, "score": score}


def normalize_product_name(raw_name: str) -> str:
    """Chuẩn hóa chữ hoa/thường và khoảng trắng để so tên hàng."""
    return " ".join(raw_name.casefold().split())


async def map_product_name(session: AsyncSession, raw_name: str) -> ProductMatch:
    """Map tên thô theo exact display name/alias, sau đó fuzzy match.

    Input:
        raw_name: tên Gemini hoặc nhân viên nhập.
    Output:
        ProductMatch, product_id=None khi không đạt ngưỡng tin cậy.
    """
    normalized_raw_name = normalize_product_name(raw_name)
    products = await list_products(session)
    for product in products:
        if normalize_product_name(product.display_name) == normalized_raw_name:
            return create_product_match(product.id, product.sku, "exact_display_name", 100)
        for alias in product.aliases:
            if normalize_product_name(alias.raw_alias) == normalized_raw_name:
                return create_product_match(product.id, product.sku, "exact_alias", 100)
    names_to_product = {normalize_product_name(product.display_name): product for product in products}
    fuzzy_result = process.extractOne(normalized_raw_name, names_to_product.keys(), scorer=fuzz.token_sort_ratio)
    if fuzzy_result is None:
        return create_product_match(None, None, None, None)
    candidate_name, score, _ = fuzzy_result
    if score < settings.sku_fuzzy_threshold:
        return create_product_match(None, None, None, int(score))
    product: Product = names_to_product[candidate_name]
    return create_product_match(product.id, product.sku, "fuzzy_display_name", int(score))
