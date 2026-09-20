"""Điểm khởi tạo FastAPI cho Agent Dashboard backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.db.database import close_database_engines


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Đảm bảo MinIO buckets tồn tại lúc start và đóng engine khi shutdown."""
    settings.forecast_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from app.storage.minio_storage import ensure_bucket

        ensure_bucket(settings.receipts_raw_bucket)
        ensure_bucket(settings.dunnhumby_raw_bucket)
    except Exception:
        pass
    yield
    await close_database_engines()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Trả trạng thái đơn giản để Docker hoặc người dùng kiểm tra API đang chạy."""
    return {"status": "ok"}
