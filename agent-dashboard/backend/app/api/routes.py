"""FastAPI routes cho staging ingestion và Forecast."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.forecast_agent import forecast_product, train_global_forecast_model
from app.api.schemas import ForecastResponse, ForecastTrainResponse, ReceiptOut, ReceiptPatchRequest, ReceiptUploadResponse, SeedResponse
from app.config import settings
from app.core.errors import ForecastError, SeedError
from app.db.database import WriteSessionLocal, get_readonly_session, get_write_session
from app.db.models import Receipt
from app.db.repository import (
    create_pending_receipt,
    get_daily_sales_history,
    get_forecast_training_input,
    get_gold_max_business_date,
    get_receipt_by_image_hash,
    get_receipt_with_items,
    list_receipts,
)
from app.ingestion.schemas import ReceiptExtract
from app.ingestion.seed_dunnhumby import seed_dunnhumby
from app.ingestion.service import confirm_manual_receipt, process_uploaded_receipt
from app.pipeline.airflow_trigger import trigger_receipt_transform_dag

router = APIRouter()
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def receipt_to_response(receipt: Receipt) -> ReceiptOut:
    """Chuyển staging ORM Receipt thành schema trả API."""
    return ReceiptOut(
        id=receipt.id, store_id=receipt.store_id, image_uri=receipt.image_uri,
        receipt_date=receipt.receipt_date,
        total_amount=float(receipt.total_amount) if receipt.total_amount is not None else None,
        confidence_score=float(receipt.confidence_score) if receipt.confidence_score is not None else None,
        status=receipt.status, error_message=receipt.error_message,
        items=[
            {
                "raw_item_name": item.raw_item_name, "quantity": float(item.quantity),
                "unit_price": float(item.unit_price) if item.unit_price is not None else None,
                "line_total": float(item.line_total) if item.line_total is not None else None,
                "product_sku": item.product.sku if item.product is not None else None,
                "match_method": item.match_method, "match_score": item.match_score,
            }
            for item in receipt.items
        ],
        dih_fetch_day=receipt.dih_fetch_day, dih_fetch_month=receipt.dih_fetch_month, dih_fetch_year=receipt.dih_fetch_year,
    )


async def run_receipt_background_job(receipt_id: int, image_uri: str) -> None:
    """Mở write session riêng cho BackgroundTask xử lý Gemini."""
    async with WriteSessionLocal() as session:
        await process_uploaded_receipt(session, receipt_id, image_uri)


@router.post("/receipts/upload", response_model=list[ReceiptUploadResponse], status_code=status.HTTP_202_ACCEPTED)
async def upload_receipts(
    background_tasks: BackgroundTasks, files: list[UploadFile] = File(...), session: AsyncSession = Depends(get_write_session)
) -> list[ReceiptUploadResponse]:
    """Lưu ảnh vào MinIO và tạo staging receipt pending; chống trùng theo hash."""
    if not files:
        raise HTTPException(status_code=422, detail="Cần upload ít nhất một ảnh hóa đơn.")
    responses = []
    for file in files:
        extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
        if extension is None:
            raise HTTPException(status_code=415, detail=f"File {file.filename} không phải ảnh JPEG/PNG/WebP.")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=422, detail=f"File {file.filename} rỗng.")
        image_hash = sha256(content).hexdigest()
        existing = await get_receipt_by_image_hash(session, image_hash)
        if existing is not None:
            raise HTTPException(status_code=409, detail=f"Ảnh đã tồn tại với receipt_id={existing.id}.")
        fetch_date = date.today()
        from app.storage.minio_storage import upload_receipt_image
        try:
            image_uri = upload_receipt_image(content, extension, fetch_date)
        except Exception as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        receipt = await create_pending_receipt(session, image_uri, image_hash, uuid4().hex, fetch_date)
        background_tasks.add_task(run_receipt_background_job, receipt.id, image_uri)
        responses.append(ReceiptUploadResponse(receipt_id=receipt.id, status=receipt.status))
    return responses


@router.get("/receipts", response_model=list[ReceiptOut])
async def get_receipts(
    status_filter: str | None = Query(default=None, alias="status"), store_id: int | None = None, session: AsyncSession = Depends(get_write_session)
) -> list[ReceiptOut]:
    """Lấy queue staging receipt theo trạng thái hoặc store."""
    return [receipt_to_response(receipt) for receipt in await list_receipts(session, status_filter, store_id)]


@router.get("/receipts/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: int, session: AsyncSession = Depends(get_write_session)) -> ReceiptOut:
    """Lấy chi tiết staging receipt để hiển thị review."""
    receipt = await get_receipt_with_items(session, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn.")
    return receipt_to_response(receipt)


@router.patch("/receipts/{receipt_id}", response_model=ReceiptOut)
async def patch_receipt(receipt_id: int, payload: ReceiptPatchRequest, session: AsyncSession = Depends(get_write_session)) -> ReceiptOut:
    """Nhận dữ liệu sửa tay và chuyển receipt sang confirmed staging rồi trigger Airflow."""
    receipt = await get_receipt_with_items(session, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn.")
    await confirm_manual_receipt(session, receipt_id, payload)
    updated_receipt = await get_receipt_with_items(session, receipt_id)
    if updated_receipt is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn sau khi cập nhật.")
    return receipt_to_response(updated_receipt)


@router.post("/forecast/train", response_model=ForecastTrainResponse)
async def train_forecast(session: AsyncSession = Depends(get_readonly_session)) -> ForecastTrainResponse:
    """Train CatBoost duy nhất từ gold feature mart."""
    gold_max_date = await get_gold_max_business_date(session)
    feature_frame = await get_forecast_training_input(session)
    try:
        result = train_global_forecast_model(feature_frame)
    except ForecastError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if gold_max_date is not None:
        from sqlalchemy import text
        import json
        await session.execute(
            text(
                "INSERT INTO forecast_training_runs(business_date_to, receipt_count, metrics, dih_fetch_day, dih_fetch_month, dih_fetch_year) VALUES (:business_date_to, :receipt_count, CAST(:metrics AS jsonb), :dih_fetch_day, :dih_fetch_month, :dih_fetch_year)"
            ),
            {
                "business_date_to": gold_max_date, "receipt_count": len(feature_frame),
                "metrics": json.dumps(result["metrics"]),
                "dih_fetch_day": date.today().day, "dih_fetch_month": date.today().month, "dih_fetch_year": date.today().year,
            },
        )
        await session.commit()
    return ForecastTrainResponse(**result)


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    sku: str, store_id: int | None = None, horizon_days: int = Query(default=7, ge=1, le=30), session: AsyncSession = Depends(get_readonly_session)
) -> ForecastResponse:
    """Dự báo demand SKU/store từ gold mart và CatBoost artifact."""
    history = await get_daily_sales_history(session, sku, store_id)
    try:
        result = forecast_product(history, horizon_days)
    except ForecastError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ForecastResponse(**result)


@router.post("/internal/seed/dunnhumby", response_model=SeedResponse)
async def seed_history(session: AsyncSession = Depends(get_write_session)) -> SeedResponse:
    """Nạp raw Dunnhumby vào staging khi API seed được bật rõ ràng."""
    if not settings.allow_seed_api:
        raise HTTPException(status_code=403, detail="Seed API đang tắt. Chạy script seed hoặc bật ALLOW_SEED_API.")
    try:
        result = await seed_dunnhumby(session)
    except SeedError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if result["receipt_count"]:
        latest_fetch = date.today()
        trigger_receipt_transform_dag(result["receipt_count"], latest_fetch, "dunnhumby")
    return SeedResponse(**result)
