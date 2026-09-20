"""Initial schema for stores, products, receipts, seed metadata and logs.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-19

Role app_readonly phải được tạo bởi tài khoản admin, không nằm trong migration ứng dụng:

    CREATE ROLE app_readonly LOGIN PASSWORD 'password';
    GRANT CONNECT ON DATABASE agent_dashboard TO app_readonly;
    GRANT USAGE ON SCHEMA public TO app_readonly;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Tạo toàn bộ bảng schema đồ án cho ingestion, seed và forecast."""
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("address", sa.String(255)),
        sa.Column("source_code", sa.String(80), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(80), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(120)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "product_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_alias", sa.String(255), nullable=False),
        sa.UniqueConstraint("product_id", "raw_alias", name="uq_product_aliases_product_alias"),
    )
    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("store_id", sa.Integer(), sa.ForeignKey("stores.id")),
        sa.Column("image_path", sa.String(255), nullable=False),
        sa.Column("receipt_date", sa.Date()),
        sa.Column("total_amount", sa.Numeric(14, 2)),
        sa.Column("raw_json", postgresql.JSONB()),
        sa.Column("confidence_score", sa.Numeric(4, 3)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text()),
        sa.Column("source_type", sa.String(50)),
        sa.Column("source_receipt_id", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("source_type", "source_receipt_id", name="uq_receipts_source"),
    )
    op.create_index("idx_receipts_store_date", "receipts", ["store_id", "receipt_date"])
    op.create_table(
        "receipt_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("raw_item_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2)),
        sa.Column("line_total", sa.Numeric(14, 2)),
    )
    op.create_index("idx_receipt_items_receipt", "receipt_items", ["receipt_id"])
    op.create_index("idx_receipt_items_product", "receipt_items", ["product_id"])
    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "agent_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("user_question", sa.Text(), nullable=False),
        sa.Column("tools_called", postgresql.JSONB()),
        sa.Column("final_answer", sa.Text()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("was_helpful", sa.Boolean()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Xóa schema theo thứ tự phụ thuộc."""
    op.drop_table("agent_logs")
    op.drop_table("conversation_messages")
    op.drop_table("receipt_items")
    op.drop_table("receipts")
    op.drop_table("product_aliases")
    op.drop_table("products")
    op.drop_table("stores")
