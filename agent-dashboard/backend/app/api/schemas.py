"""Pydantic request/response schema cho API ingestion và Forecast."""

from datetime import date

from pydantic import BaseModel

from app.ingestion.schemas import ReceiptExtract


class ReceiptUploadResponse(BaseModel):
    """Phản hồi sau khi API nhận một ảnh upload."""

    receipt_id: int
    status: str


class ReceiptItemOut(BaseModel):
    """Một item staging hiển thị cho màn review."""

    raw_item_name: str
    quantity: float
    unit_price: float | None
    line_total: float | None
    product_sku: str | None
    match_method: str | None
    match_score: int | None


class ReceiptOut(BaseModel):
    """Receipt staging và trạng thái xử lý trả về API."""

    id: int
    store_id: int | None
    image_uri: str
    receipt_date: date | None
    total_amount: float | None
    confidence_score: float | None
    status: str
    error_message: str | None
    items: list[ReceiptItemOut]
    dih_fetch_day: int
    dih_fetch_month: int
    dih_fetch_year: int


class ReceiptPatchRequest(ReceiptExtract):
    """Dữ liệu nhân viên sửa để xác nhận receipt."""


class ForecastTrainResponse(BaseModel):
    """Metadata sau khi train CatBoost."""

    method: str
    metrics: dict
    artifact_path: str
    date_from: str
    date_to: str


class DailyForecastOut(BaseModel):
    """Một điểm dự báo ngày."""

    date: str
    predicted_quantity: float


class ForecastResponse(BaseModel):
    """Kết quả CatBoost forecast trả Dashboard."""

    sku: str
    store_id: int | None
    horizon_days: int
    method: str
    predicted_quantity: float
    daily: list[DailyForecastOut]
    metrics: dict
    trained_date_range: dict[str, str]


class SeedResponse(BaseModel):
    """Tóm tắt raw Dunnhumby seed."""

    store_count: int
    product_count: int
    receipt_count: int
    item_count: int
    skipped_existing_receipts: int
    date_from: date | None
    date_to: date | None
