"""Các lỗi nghiệp vụ được API chuyển thành phản hồi phù hợp."""


class IngestionError(Exception):
    """Lỗi ở luồng xử lý ảnh hóa đơn hoặc Gemini Vision."""


class ForecastError(Exception):
    """Lỗi khi train, tải artifact hoặc dự báo nhu cầu."""


class SeedError(Exception):
    """Lỗi khi đọc hoặc chuyển đổi dữ liệu Dunnhumby."""
