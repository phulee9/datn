"""Create staging, silver, gold schemas and pipeline tables.

Revision ID: 0002_medallion_pipeline
Revises: 0001_initial
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_medallion_pipeline"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

FETCH_COLUMNS = [
    sa.Column("dih_fetch_day", sa.SmallInteger(), nullable=False),
    sa.Column("dih_fetch_month", sa.SmallInteger(), nullable=False),
    sa.Column("dih_fetch_year", sa.SmallInteger(), nullable=False),
]


def upgrade() -> None:
    """Tạo các schema medallion, landing tables và gold marts vật lý."""
    op.execute("CREATE SCHEMA IF NOT EXISTS staging")
    op.execute("CREATE SCHEMA IF NOT EXISTS silver")
    op.execute("CREATE SCHEMA IF NOT EXISTS gold")
    op.create_table(
        "product",
        sa.Column("product_id", sa.BigInteger(), primary_key=True),
        sa.Column("department", sa.String(255)), sa.Column("commodity_desc", sa.String(255)),
        sa.Column("sub_commodity_desc", sa.String(255)), sa.Column("manufacturer", sa.String(255)),
        sa.Column("brand", sa.String(255)), sa.Column("curr_size_of_product", sa.String(255)),
        *FETCH_COLUMNS, schema="staging",
    )
    op.create_table(
        "transaction",
        sa.Column("transaction_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("household_key", sa.BigInteger()), sa.Column("basket_id", sa.BigInteger(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False), sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False), sa.Column("sales_value", sa.Numeric(14, 2), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False), sa.Column("retail_disc", sa.Numeric(14, 2)),
        sa.Column("trans_time", sa.Integer()), sa.Column("week_no", sa.Integer()),
        sa.Column("coupon_disc", sa.Numeric(14, 2)), sa.Column("coupon_match_disc", sa.Numeric(14, 2)),
        *FETCH_COLUMNS, schema="staging",
    )
    op.create_index("idx_staging_transaction_basket_store", "transaction", ["basket_id", "store_id"], schema="staging")
    op.create_index("idx_staging_transaction_product", "transaction", ["product_id"], schema="staging")
    op.create_index("idx_staging_transaction_day", "transaction", ["day"], schema="staging")
    op.create_table(
        "dim_store",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("source_code", sa.String(100), unique=True),
        sa.Column("store_name", sa.String(255), nullable=False), *FETCH_COLUMNS, schema="silver",
    )
    op.create_table(
        "dim_product",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("sku", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(500), nullable=False), sa.Column("category", sa.String(255)),
        sa.Column("brand", sa.String(255)), sa.Column("product_size", sa.String(100)), *FETCH_COLUMNS, schema="silver",
    )
    op.create_table(
        "dim_product_alias",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("product_id", sa.BigInteger(), sa.ForeignKey("silver.dim_product.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_alias", sa.String(500), nullable=False), sa.Column("normalized_alias", sa.String(500), nullable=False, unique=True),
        *FETCH_COLUMNS, schema="silver",
    )
    op.create_table(
        "receipt",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("image_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("image_uri", sa.Text(), nullable=False), sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_receipt_id", sa.String(100), nullable=False),
        sa.Column("store_id", sa.BigInteger(), sa.ForeignKey("silver.dim_store.id")),
        sa.Column("store_name_guess", sa.String(255)), sa.Column("receipt_date", sa.Date()),
        sa.Column("total_amount", sa.Numeric(14, 2)), sa.Column("confidence_score", sa.Numeric(4, 3)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"), sa.Column("raw_json", postgresql.JSONB()),
        sa.Column("error_message", sa.Text()), sa.Column("assigned_to", sa.String(100)), *FETCH_COLUMNS,
        sa.UniqueConstraint("source_type", "source_receipt_id", name="uq_staging_receipt_source"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'confirmed', 'needs_review', 'error')", name="ck_staging_receipt_status"),
        schema="staging",
    )
    op.create_index("idx_staging_receipt_status", "receipt", ["status"], schema="staging")
    op.create_table(
        "receipt_item",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("receipt_id", sa.BigInteger(), sa.ForeignKey("staging.receipt.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger(), sa.ForeignKey("silver.dim_product.id")),
        sa.Column("raw_item_name", sa.String(500), nullable=False), sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2)), sa.Column("line_total", sa.Numeric(14, 2)),
        sa.Column("match_method", sa.String(30)), sa.Column("match_score", sa.SmallInteger()), *FETCH_COLUMNS, schema="staging",
    )
    op.create_index("idx_staging_receipt_item_receipt", "receipt_item", ["receipt_id"], schema="staging")
    op.create_table(
        "fact_receipt",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("staging_receipt_id", sa.BigInteger(), unique=True),
        sa.Column("store_id", sa.BigInteger(), sa.ForeignKey("silver.dim_store.id")), sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_receipt_id", sa.String(100), nullable=False), sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2)), sa.Column("confidence_score", sa.Numeric(4, 3)),
        sa.Column("raw_json", postgresql.JSONB()), *FETCH_COLUMNS,
        sa.UniqueConstraint("source_type", "source_receipt_id", name="uq_silver_fact_receipt_source"), schema="silver",
    )
    op.create_table(
        "fact_receipt_item",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("receipt_id", sa.BigInteger(), sa.ForeignKey("silver.fact_receipt.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger(), sa.ForeignKey("silver.dim_product.id")), sa.Column("raw_item_name", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False), sa.Column("unit_price", sa.Numeric(14, 2)),
        sa.Column("line_total", sa.Numeric(14, 2)), *FETCH_COLUMNS, schema="silver",
    )
    op.create_table(
        "mart_daily_sales",
        sa.Column("business_date", sa.Date(), nullable=False), sa.Column("store_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False), sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("category", sa.String(255)), sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False), *FETCH_COLUMNS,
        sa.PrimaryKeyConstraint("business_date", "store_id", "product_id"), schema="gold",
    )
    op.create_index("idx_gold_daily_sales_lookup", "mart_daily_sales", ["sku", "store_id", "business_date"], schema="gold")
    op.create_table(
        "mart_forecast_features",
        sa.Column("business_date", sa.Date(), nullable=False), sa.Column("store_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False), sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("category", sa.String(255)), sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("lag_1", sa.Numeric(14, 3)), sa.Column("lag_7", sa.Numeric(14, 3)), sa.Column("lag_14", sa.Numeric(14, 3)),
        sa.Column("rolling_mean_7", sa.Numeric(14, 4)), sa.Column("rolling_std_7", sa.Numeric(14, 4)),
        sa.Column("weekday", sa.SmallInteger(), nullable=False), sa.Column("is_weekend", sa.SmallInteger(), nullable=False),
        *FETCH_COLUMNS, sa.PrimaryKeyConstraint("business_date", "store_id", "product_id"), schema="gold",
    )
    op.create_index("idx_gold_forecast_features_lookup", "mart_forecast_features", ["sku", "store_id", "business_date"], schema="gold")
    op.execute("""
        CREATE VIEW gold.v_forecast_input AS
        SELECT business_date, store_id, product_id, sku, category, quantity, lag_1, lag_7, lag_14,
               rolling_mean_7, rolling_std_7, weekday, is_weekend
        FROM gold.mart_forecast_features
        WHERE lag_1 IS NOT NULL AND lag_7 IS NOT NULL AND lag_14 IS NOT NULL
          AND rolling_mean_7 IS NOT NULL AND rolling_std_7 IS NOT NULL
    """)
    op.create_table(
        "forecast_training_runs", sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("business_date_to", sa.Date()), sa.Column("receipt_count", sa.BigInteger(), nullable=False),
        sa.Column("metrics", postgresql.JSONB()), *FETCH_COLUMNS,
    )


def downgrade() -> None:
    """Xóa các schema dữ liệu medallion theo thứ tự phụ thuộc."""
    op.drop_table("forecast_training_runs")
    op.execute("DROP SCHEMA IF EXISTS gold CASCADE")
    op.execute("DROP SCHEMA IF EXISTS silver CASCADE")
    op.execute("DROP SCHEMA IF EXISTS staging CASCADE")
