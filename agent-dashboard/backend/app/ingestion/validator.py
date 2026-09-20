"""Tính data-quality score cho kết quả Gemini Vision."""

from app.config import settings
from app.ingestion.schemas import ReceiptExtract


def compute_confidence(extract: ReceiptExtract) -> float:
    """Tính điểm tin cậy nội bộ dựa trên tính đầy đủ và tổng tiền.

    Input:
        extract: dữ liệu Gemini đã parse theo ReceiptExtract.
    Output:
        Điểm từ 0.000 đến 1.000; đây không phải confidence gốc của Gemini.
    """
    score = 1.0
    if extract.receipt_date is None:
        score -= 0.20
    if extract.total_amount is None:
        score -= 0.20
    if not extract.items:
        score -= 0.50
    for item in extract.items:
        if item.unit_price is None or item.line_total is None:
            score -= 0.05
    if extract.total_amount is not None and extract.items:
        calculated_total = sum(item.line_total or 0 for item in extract.items)
        if abs(calculated_total - extract.total_amount) > extract.total_amount * 0.05:
            score -= 0.15
    return max(0.0, round(score, 3))


def needs_manual_review(confidence_score: float) -> bool:
    """Quyết định kết quả OCR có cần nhân viên kiểm tra thủ công không."""
    return confidence_score < settings.confidence_threshold
