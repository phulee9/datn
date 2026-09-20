"""Schema dữ liệu có cấu trúc Gemini phải trả về khi đọc hóa đơn."""

from datetime import date

from pydantic import BaseModel, Field


class ReceiptItemExtract(BaseModel):
    """Một dòng hàng hóa Gemini trích xuất từ ảnh hóa đơn."""

    raw_item_name: str = Field(min_length=1, description="Tên hàng đúng như đọc được")
    quantity: float = Field(gt=0, description="Số lượng hàng")
    unit_price: float | None = Field(default=None, ge=0, description="Đơn giá nếu đọc được")
    line_total: float | None = Field(default=None, ge=0, description="Thành tiền dòng hàng nếu đọc được")


class ReceiptExtract(BaseModel):
    """Kết quả Gemini Vision cho toàn bộ hóa đơn."""

    store_name_guess: str | None = Field(default=None)
    receipt_date: date | None = Field(default=None)
    items: list[ReceiptItemExtract] = Field(default_factory=list)
    total_amount: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None)
