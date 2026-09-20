"""Train và dự báo demand bằng CatBoost native categorical từ gold marts."""

from __future__ import annotations

from time import perf_counter
from typing import Any

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from app.config import settings
from app.core.errors import ForecastError

RANDOM_SEED = 20260920
NUMERIC_FEATURES = ["lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_std_7", "weekday", "is_weekend"]
CATEGORICAL_FEATURES = ["store_id", "sku", "category"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def validate_feature_frame(feature_frame: pd.DataFrame) -> pd.DataFrame:
    """Kiểm tra input CatBoost lấy từ gold.v_forecast_input.

    Output:
        DataFrame đã chuẩn hóa cột ngày, numeric và categorical.
    """
    required_columns = {"business_date", "quantity", *ALL_FEATURES}
    missing_columns = required_columns - set(feature_frame.columns)
    if missing_columns:
        raise ForecastError(f"Thiếu cột gold forecast feature: {sorted(missing_columns)}")
    result = feature_frame.copy()
    result["business_date"] = pd.to_datetime(result["business_date"])
    result["quantity"] = result["quantity"].astype(float)
    for column in NUMERIC_FEATURES:
        result[column] = result[column].astype(float)
    if result[NUMERIC_FEATURES + ["quantity"]].isna().any().any() or (result["quantity"] < 0).any():
        raise ForecastError("Gold forecast feature có quantity/lag/rolling không hợp lệ.")
    for column in CATEGORICAL_FEATURES:
        result[column] = result[column].astype(str)
    return result.sort_values(["store_id", "sku", "business_date"]).reset_index(drop=True)


def create_catboost_model() -> CatBoostRegressor:
    """Tạo CatBoost regressor dùng category native, không cần encode thủ công."""
    return CatBoostRegressor(
        iterations=settings.catboost_iterations,
        learning_rate=0.05,
        depth=6,
        loss_function="MAE",
        random_seed=RANDOM_SEED,
        verbose=False,
        allow_writing_files=False,
    )


def fit_catboost(feature_frame: pd.DataFrame) -> CatBoostRegressor:
    """Fit global CatBoost trên feature mart đã có lag/rolling.

    Output:
        Model đã fit.
    """
    validated = validate_feature_frame(feature_frame)
    model = create_catboost_model()
    model.fit(validated[ALL_FEATURES], validated["quantity"], cat_features=CATEGORICAL_FEATURES)
    return model


def calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Tính MAE để lưu metadata train CatBoost."""
    return float(np.mean(np.abs(actual - predicted)))


def calculate_wape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Tính WAPE, trả 0 khi tổng actual bằng 0."""
    denominator = float(np.abs(actual).sum())
    return 0.0 if denominator == 0 else float(np.abs(actual - predicted).sum() / denominator)


def train_global_forecast_model(feature_frame: pd.DataFrame) -> dict[str, Any]:
    """Train CatBoost duy nhất từ gold feature mart và lưu artifact.

    Output:
        Metadata train, đường dẫn artifact và date range.
    """
    validated = validate_feature_frame(feature_frame)
    if validated.empty:
        raise ForecastError("Gold forecast input chưa có row đủ lag_14 để train.")
    started_at = perf_counter()
    model = fit_catboost(validated)
    predictions = model.predict(validated[ALL_FEATURES])
    metrics = {
        "method": "catboost",
        "mae_train": round(calculate_mae(validated["quantity"].to_numpy(), predictions), 4),
        "wape_train": round(calculate_wape(validated["quantity"].to_numpy(), predictions), 4),
        "train_seconds": round(perf_counter() - started_at, 3),
        "row_count": len(validated),
    }
    artifact = {
        "method": "catboost", "model": model, "feature_columns": ALL_FEATURES,
        "metrics": metrics,
        "trained_date_from": validated["business_date"].min().date().isoformat(),
        "trained_date_to": validated["business_date"].max().date().isoformat(),
    }
    settings.forecast_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, settings.forecast_artifact_path)
    return {
        "method": "catboost", "metrics": metrics, "artifact_path": str(settings.forecast_artifact_path),
        "date_from": artifact["trained_date_from"], "date_to": artifact["trained_date_to"],
    }


def load_forecast_artifact() -> dict[str, Any]:
    """Tải CatBoost artifact đã train rõ ràng trước đó."""
    if not settings.forecast_artifact_path.exists():
        raise ForecastError("Chưa có model Forecast. Gọi POST /api/forecast/train trước.")
    try:
        artifact = joblib.load(settings.forecast_artifact_path)
    except (OSError, ValueError, EOFError) as error:
        raise ForecastError(f"Không thể tải Forecast artifact: {error}") from error
    if artifact.get("method") != "catboost":
        raise ForecastError("Forecast artifact không phải CatBoost hợp lệ.")
    return artifact


def validate_history(history: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa gold.mart_daily_sales history cho một SKU/store.

    Output:
        DataFrame dense history đã sort.
    """
    required_columns = {"date", "store_id", "sku", "category", "qty"}
    missing_columns = required_columns - set(history.columns)
    if missing_columns:
        raise ForecastError(f"Thiếu cột daily sales: {sorted(missing_columns)}")
    result = history.copy()
    result["date"] = pd.to_datetime(result["date"])
    result["qty"] = result["qty"].astype(float)
    if result.empty or result["qty"].isna().any() or (result["qty"] < 0).any():
        raise ForecastError("Lịch sử bán hàng không hợp lệ hoặc trống.")
    return result.sort_values("date").reset_index(drop=True)


def build_future_feature_row(history: pd.DataFrame, target_date: pd.Timestamp) -> pd.DataFrame:
    """Tạo một feature row cho ngày tương lai từ 14 giá trị trước đó."""
    quantities = history["qty"].to_numpy(dtype=float)
    if len(quantities) < settings.forecast_minimum_history_days:
        raise ForecastError(f"Chưa đủ lịch sử bán hàng, cần ít nhất {settings.forecast_minimum_history_days} ngày.")
    return pd.DataFrame([{
        "lag_1": quantities[-1], "lag_7": quantities[-7], "lag_14": quantities[-14],
        "rolling_mean_7": float(np.mean(quantities[-7:])), "rolling_std_7": float(np.std(quantities[-7:], ddof=1)),
        "weekday": target_date.dayofweek, "is_weekend": int(target_date.dayofweek >= 5),
        "store_id": str(history["store_id"].iloc[0]), "sku": str(history["sku"].iloc[0]), "category": str(history["category"].iloc[0]),
    }])


def recursive_forecast(model: CatBoostRegressor, history: pd.DataFrame, horizon_days: int) -> list[dict[str, str | float]]:
    """Dự báo nhiều ngày, đưa prediction trước vào lịch sử cho bước sau."""
    work_history = validate_history(history)
    predictions = []
    for _ in range(horizon_days):
        target_date = work_history["date"].max() + pd.Timedelta(days=1)
        feature_row = build_future_feature_row(work_history, target_date)
        prediction = max(0.0, float(model.predict(feature_row[ALL_FEATURES])[0]))
        predictions.append({"date": target_date.date().isoformat(), "predicted_quantity": round(prediction, 2)})
        work_history = pd.concat([work_history, pd.DataFrame([{
            "date": target_date, "store_id": work_history["store_id"].iloc[0], "sku": work_history["sku"].iloc[0],
            "category": work_history["category"].iloc[0], "qty": prediction,
        }])], ignore_index=True)
    return predictions


def forecast_product(history: pd.DataFrame, horizon_days: int) -> dict[str, Any]:
    """Dự báo một SKU/store từ CatBoost artifact.

    Output:
        Payload API gồm daily prediction và metadata train.
    """
    if not 1 <= horizon_days <= 30:
        raise ForecastError("horizon_days phải nằm trong khoảng 1 đến 30.")
    validated_history = validate_history(history)
    series_count = validated_history[["store_id", "sku"]].drop_duplicates().shape[0]
    if series_count != 1:
        raise ForecastError("Cần chỉ định store_id khi SKU có nhiều cửa hàng.")
    artifact = load_forecast_artifact()
    daily = recursive_forecast(artifact["model"], validated_history, horizon_days)
    return {
        "sku": str(validated_history["sku"].iloc[0]), "store_id": int(validated_history["store_id"].iloc[0]),
        "horizon_days": horizon_days, "method": "catboost",
        "predicted_quantity": round(sum(float(row["predicted_quantity"]) for row in daily), 2), "daily": daily,
        "metrics": artifact["metrics"],
        "trained_date_range": {"from": artifact["trained_date_from"], "to": artifact["trained_date_to"]},
    }
