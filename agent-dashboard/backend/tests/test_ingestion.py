"""Unit test cho validator và hình thức ReceiptExtract."""

from datetime import date

from app.ingestion.schemas import ReceiptExtract, ReceiptItemExtract
from app.ingestion.validator import compute_confidence, needs_manual_review


def test_clean_receipt_has_maximum_confidence() -> None:
    """Hóa đơn đủ trường và tổng tiền khớp thì điểm cao và không cần review."""
    extract = ReceiptExtract(
        receipt_date=date(2025, 1, 10),
        total_amount=10.0,
        items=[ReceiptItemExtract(raw_item_name="COCA 330", quantity=2, unit_price=5.0, line_total=10.0)],
    )
    confidence_score = compute_confidence(extract)
    assert abs(confidence_score - 1.0) < 1e-9
    assert needs_manual_review(confidence_score) is False


def test_missing_date_and_mismatched_total_reduces_confidence() -> None:
    """Thiếu ngày và tổng tiền lệch quá 5% thì bị trừ điểm và cần review."""
    extract = ReceiptExtract(
        receipt_date=None,
        total_amount=10.0,
        items=[ReceiptItemExtract(raw_item_name="COCA 330", quantity=2, unit_price=5.0, line_total=7.0)],
    )
    confidence_score = compute_confidence(extract)
    assert confidence_score < 0.85
    assert needs_manual_review(confidence_score) is True


def test_empty_items_gives_low_confidence() -> None:
    """Không đọc được item nào thì điểm rất thấp."""
    extract = ReceiptExtract(receipt_date=None, total_amount=None, items=[])
    assert compute_confidence(extract) <= 0.5


def test_missing_prices_only_small_deduction() -> None:
    """Thiếu unit_price/line_total từng dòng chỉ trừ 0.05 mỗi dòng."""
    extract = ReceiptExtract(
        receipt_date=date(2025, 1, 10),
        total_amount=None,
        items=[ReceiptItemExtract(raw_item_name="MIST 250", quantity=1)],
    )
    assert compute_confidence(extract) == 0.75
