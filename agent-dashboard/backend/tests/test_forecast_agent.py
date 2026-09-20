"""Unit test cho logic feature và backtest Forecast."""

import pandas as pd

from app.agents.forecast_agent import build_training_features, rolling_origin_backtest
from app.core.errors import ForecastError


def build_small_history() -> pd.DataFrame:
    """Tạo chuỗi thời gian ngắn gọn test leakage/boundary."""
    dates = pd.date_range("2024-01-01", periods=22, freq="D")
    return pd.DataFrame(
        {
            "date": dates.tolist() * 2,
            "store_id": [1] * 22 + [1] * 22,
            "sku": ["SKU_A"] * 22 + ["SKU_B"] * 22,
            "category": ["CAT_A"] * 22 + ["CAT_B"] * 22,
            "qty": [1, 2, 3, 4, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4] * 2,
        }
    )


def test_training_features_use_only_past_values() -> None:
    """Các row train không được thiếu lag và không được rò rỉ qty hiện tại."""
    history = build_small_history().query("sku == 'SKU_A'").copy()
    features = build_training_features(history)
    oldest_row = features.iloc[0]
    # Ngày đầu tiên còn lại phải là ngày 15, vì cần tới lag_14 và rolling 7 qua shift(1).
    assert oldest_row["date"].date().isoformat() == "2024-01-15"
    assert oldest_row["lag_1"] == history[history["date"] == pd.Timestamp("2024-01-14")]["qty"].iloc[0]
    assert oldest_row["lag_7"] == history[history["date"] == pd.Timestamp("2024-01-08")]["qty"].iloc[0]


def test_rolling_origin_requires_minimum_history() -> None:
    """Backtest phải báo lỗi rõ ràng khi dữ liệu quá ngắn."""
    short_history = build_small_history().head(10)
    try:
        rolling_origin_backtest(short_history, "seasonal_naive", 7, 3)
        assert False, "phải raise ForecastError khi lịch sử quá ngắn"
    except ForecastError:
        pass
