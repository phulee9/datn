"""Entry point seed Dunnhumby. Không dùng argparse; đọc cấu hình từ app.config."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import WriteSessionLocal
from app.ingestion.seed_dunnhumby import seed_dunnhumby


async def run_seed() -> None:
    """Mở write session, seed dữ liệu lịch sử và in SeedSummary."""
    async with WriteSessionLocal() as session:
        summary = await seed_dunnhumby(session)
    print(
        "Seed xong: "
        f"{summary['store_count']} stores, {summary['product_count']} products, "
        f"{summary['receipt_count']} receipts mới, {summary['item_count']} items, "
        f"{summary['skipped_existing_receipts']} receipts đã tồn tại, "
        f"{summary['date_from']} -> {summary['date_to']}"
    )


if __name__ == "__main__":
    asyncio.run(run_seed())
