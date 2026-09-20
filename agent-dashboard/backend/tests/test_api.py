"""Test route upload/patch/forecast validation bằng override dependency."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.models import Receipt
from app.main import app
from app.db.database import get_write_session


class FakeSession:
    """Session giả cho test API, không kết nối PostgreSQL."""

    async def close(self) -> None:
        return None


async def fake_write_session():
    """Cung cấp FakeSession cho FastAPI Depends."""
    yield FakeSession()


async def fake_create_pending_receipt(_session, image_path: str) -> Receipt:
    """Trả hóa đơn pending giả lập sau upload."""
    return Receipt(id=1, image_path=image_path, status="pending", created_at=datetime.now(timezone.utc), items=[])


app.dependency_overrides[get_write_session] = fake_write_session
client = TestClient(app)


def test_health() -> None:
    """Health check không phụ thuộc DB."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_forecast_rejects_invalid_horizon() -> None:
    """horizon_days ngoài 1-30 bị FastAPI 422 trước khi chạy model."""
    response = client.get("/api/forecast", params={"sku": "SKU_A", "horizon_days": 0})
    assert response.status_code == 422
