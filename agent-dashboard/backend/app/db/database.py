"""Kết nối và cấp AsyncSession cho PostgreSQL."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

write_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
readonly_engine = create_async_engine(settings.readonly_database_url, pool_pre_ping=True)
WriteSessionLocal = async_sessionmaker(write_engine, expire_on_commit=False)
ReadOnlySessionLocal = async_sessionmaker(readonly_engine, expire_on_commit=False)


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """Cấp session có quyền ghi cho API ingestion.

    Output:
        AsyncSession được FastAPI tự đóng sau request.
    """
    async with WriteSessionLocal() as session:
        yield session


async def get_readonly_session() -> AsyncGenerator[AsyncSession, None]:
    """Cấp session chỉ đọc cho các truy vấn Forecast.

    Output:
        AsyncSession dùng role app_readonly.
    """
    async with ReadOnlySessionLocal() as session:
        yield session


async def close_database_engines() -> None:
    """Đóng pool kết nối khi FastAPI tắt."""
    await write_engine.dispose()
    await readonly_engine.dispose()
