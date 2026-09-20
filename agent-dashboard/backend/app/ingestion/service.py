"""Điều phối Gemini Vision, validator, staging receipt và trigger Airflow."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from google import genai
from google.genai import errors, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import IngestionError
from app.db.repository import save_extracted_receipt, update_receipt_status
from app.ingestion.schemas import ReceiptExtract
from app.ingestion.sku_mapper import map_product_name
from app.ingestion.validator import compute_confidence, needs_manual_review
from app.pipeline.airflow_trigger import trigger_receipt_transform_dag
from app.storage.minio_storage import get_object_bytes, parse_storage_uri

EXTRACTION_PROMPT = """
Bạn là hệ thống đọc hóa đơn bán lẻ. Đọc ảnh và trả về đúng JSON schema đã cung cấp.
Giữ nguyên tên hàng đúng như in/nhìn thấy. Nếu ngày, đơn giá, thành tiền hoặc tổng tiền
không đọc được rõ thì để null, không tự đoán. Quantity phải là số dương.
""".strip()


def build_gemini_client() -> genai.Client:
    """Khởi tạo Gemini client từ GEMINI_API_KEY."""
    if not settings.gemini_api_key:
        raise IngestionError("GEMINI_API_KEY chưa được cấu hình.")
    return genai.Client(api_key=settings.gemini_api_key)


def get_image_mime_type(storage_uri: str) -> str:
    """Suy ra MIME type Gemini cần từ extension object URI."""
    _, object_key = parse_storage_uri(storage_uri)
    extension = object_key.rsplit(".", maxsplit=1)[-1].casefold() if "." in object_key else "jpg"
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(extension, "image/jpeg")


def extract_receipt(storage_uri: str) -> ReceiptExtract:
    """Gọi Gemini Vision từ ảnh MinIO với structured JSON output.

    Output:
        ReceiptExtract đã được Pydantic validate.
    """
    client = build_gemini_client()
    image_bytes = get_object_bytes(storage_uri)
    image_mime_type = get_image_mime_type(storage_uri)
    last_error: Exception | None = None
    for _ in range(settings.gemini_max_retries):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=[types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type), EXTRACTION_PROMPT],
                config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=ReceiptExtract, temperature=0),
            )
            return ReceiptExtract.model_validate_json(response.text)
        except (errors.APIError, TimeoutError, ConnectionError) as error:
            last_error = error
    raise IngestionError(f"Gemini không đọc được hóa đơn sau {settings.gemini_max_retries} lần: {last_error}")


async def build_mapped_items(session: AsyncSession, extract: ReceiptExtract) -> list[dict]:
    """Map từng item Gemini sang product_id và audit method/score."""
    items = []
    for item in extract.items:
        product_match = await map_product_name(session, item.raw_item_name)
        items.append(
            {
                "product_id": product_match["product_id"], "raw_item_name": item.raw_item_name,
                "quantity": Decimal(str(item.quantity)),
                "unit_price": Decimal(str(item.unit_price)) if item.unit_price is not None else None,
                "line_total": Decimal(str(item.line_total)) if item.line_total is not None else None,
                "match_method": product_match["match_method"] or "unmatched", "match_score": product_match["score"],
            }
        )
    return items


def trigger_confirmed_receipt_pipeline(receipt_id: int, fetch_date: date, source_type: str) -> None:
    """Trigger Airflow sau commit confirmed; lỗi trigger không rollback receipt."""
    triggered, message = trigger_receipt_transform_dag(receipt_id, fetch_date, source_type)
    print(message, flush=True)
    if not triggered:
        print(f"Receipt {receipt_id} vẫn confirmed; chạy DAG thủ công để cập nhật silver/gold.", flush=True)


async def process_uploaded_receipt(session: AsyncSession, receipt_id: int, image_uri: str) -> None:
    """Chạy worker Gemini và kết thúc staging receipt ở confirmed/review/error."""
    receipt = await update_receipt_status(session, receipt_id, "processing")
    if receipt is None:
        return
    try:
        extract = extract_receipt(image_uri)
        confidence_score = compute_confidence(extract)
        mapped_items = await build_mapped_items(session, extract)
        unmatched_items = any(item["product_id"] is None for item in mapped_items)
        status = "needs_review" if needs_manual_review(confidence_score) or unmatched_items else "confirmed"
        saved = await save_extracted_receipt(
            session, receipt_id, None, extract.receipt_date,
            Decimal(str(extract.total_amount)) if extract.total_amount is not None else None,
            extract.model_dump(mode="json"), Decimal(str(confidence_score)), status, mapped_items,
        )
        if saved is not None and saved.status == "confirmed":
            fetch_date = date(saved.dih_fetch_year, saved.dih_fetch_month, saved.dih_fetch_day)
            trigger_confirmed_receipt_pipeline(saved.id, fetch_date, saved.source_type)
    except IngestionError as error:
        await update_receipt_status(session, receipt_id, "error", str(error))
    except Exception:
        await update_receipt_status(session, receipt_id, "error", "Không thể xử lý hóa đơn. Hãy thử lại ảnh khác.")


async def confirm_manual_receipt(session: AsyncSession, receipt_id: int, extract: ReceiptExtract) -> None:
    """Lưu bản người dùng sửa tại staging rồi trigger dbt/Airflow."""
    mapped_items = await build_mapped_items(session, extract)
    saved = await save_extracted_receipt(
        session, receipt_id, None, extract.receipt_date,
        Decimal(str(extract.total_amount)) if extract.total_amount is not None else None,
        extract.model_dump(mode="json"), Decimal(str(compute_confidence(extract))), "confirmed", mapped_items,
    )
    if saved is not None:
        fetch_date = date(saved.dih_fetch_year, saved.dih_fetch_month, saved.dih_fetch_day)
        trigger_confirmed_receipt_pipeline(saved.id, fetch_date, saved.source_type)
