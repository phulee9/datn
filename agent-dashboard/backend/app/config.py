"""Cấu hình tập trung cho Agent Dashboard."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Đọc cấu hình runtime từ file .env và biến môi trường."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Agent Dashboard API"
    api_prefix: str = "/api"
    database_url: str = "postgresql+asyncpg://app:password@localhost:5432/agent_dashboard"
    readonly_database_url: str = "postgresql+asyncpg://app_readonly:password@localhost:5432/agent_dashboard"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_max_retries: int = 2
    confidence_threshold: float = 0.85
    sku_fuzzy_threshold: int = 86
    minio_endpoint_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_region: str = "us-east-1"
    receipts_raw_bucket: str = "receipts-raw"
    dunnhumby_raw_bucket: str = "dunnhumby-raw"
    use_minio_dunnhumby_source: bool = False
    dunnhumby_raw_dir: Path = Path("data/raw/dunnhumby")
    seed_base_date: str = "2024-10-11"
    seed_top_skus: int = 150
    seed_top_stores: int = 15
    seed_batch_size: int = 10000
    allow_seed_api: bool = False
    airflow_api_url: str = "http://localhost:8080/api/v1"
    airflow_username: str = "airflow"
    airflow_password: str = "airflow"
    airflow_transform_dag_id: str = "receipt_transform_dag"
    forecast_retrain_receipt_threshold: int = 30
    forecast_artifact_path: Path = Path("artifacts/forecast/global_model.joblib")
    forecast_horizon_days: int = 7
    forecast_minimum_history_days: int = 14
    catboost_iterations: int = 250
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
