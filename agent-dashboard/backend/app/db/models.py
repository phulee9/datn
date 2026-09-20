"""ORM cho staging, silver, gold và metadata vận hành pipeline."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base bắt buộc cho SQLAlchemy ORM."""


class StagingProduct(Base):
    """Catalog Dunnhumby gốc tại landing layer."""

    __tablename__ = "product"
    __table_args__ = {"schema": "staging"}

    product_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    department: Mapped[str | None] = mapped_column(String(255))
    commodity_desc: Mapped[str | None] = mapped_column(String(255))
    sub_commodity_desc: Mapped[str | None] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(255))
    curr_size_of_product: Mapped[str | None] = mapped_column(String(255))
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class StagingTransaction(Base):
    """Dòng transaction Dunnhumby gốc tại landing layer."""

    __tablename__ = "transaction"
    __table_args__ = (
        Index("idx_staging_transaction_basket_store", "basket_id", "store_id"),
        Index("idx_staging_transaction_product", "product_id"),
        Index("idx_staging_transaction_day", "day"),
        {"schema": "staging"},
    )

    transaction_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    household_key: Mapped[int | None] = mapped_column(BigInteger)
    basket_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    sales_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False)
    retail_disc: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    trans_time: Mapped[int | None] = mapped_column(Integer)
    week_no: Mapped[int | None] = mapped_column(Integer)
    coupon_disc: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    coupon_match_disc: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class Store(Base):
    """Dimension cửa hàng canonical tại silver."""

    __tablename__ = "dim_store"
    __table_args__ = {"schema": "silver"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_code: Mapped[str | None] = mapped_column(String(100), unique=True)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class Product(Base):
    """Dimension sản phẩm canonical tại silver."""

    __tablename__ = "dim_product"
    __table_args__ = {"schema": "silver"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255))
    brand: Mapped[str | None] = mapped_column(String(255))
    product_size: Mapped[str | None] = mapped_column(String(100))
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    aliases: Mapped[list[ProductAlias]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductAlias(Base):
    """Alias đã xác nhận để map tên Gemini sang product canonical."""

    __tablename__ = "dim_product_alias"
    __table_args__ = {"schema": "silver"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("silver.dim_product.id", ondelete="CASCADE"), nullable=False)
    raw_alias: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product: Mapped[Product] = relationship(back_populates="aliases")


class Receipt(Base):
    """Landing hóa đơn upload/Gemini, quản lý lifecycle tại staging."""

    __tablename__ = "receipt"
    __table_args__ = (
        UniqueConstraint("source_type", "source_receipt_id", name="uq_staging_receipt_source"),
        CheckConstraint("status IN ('pending', 'processing', 'confirmed', 'needs_review', 'error')", name="ck_staging_receipt_status"),
        Index("idx_staging_receipt_status", "status"),
        {"schema": "staging"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    image_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    image_uri: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_receipt_id: Mapped[str] = mapped_column(String(100), nullable=False)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("silver.dim_store.id"))
    store_name_guess: Mapped[str | None] = mapped_column(String(255))
    receipt_date: Mapped[Any | None] = mapped_column(Date)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(100))
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    items: Mapped[list[ReceiptItem]] = relationship(back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItem(Base):
    """Landing item Gemini; product_id null khi chưa map được SKU."""

    __tablename__ = "receipt_item"
    __table_args__ = (Index("idx_staging_receipt_item_receipt", "receipt_id"), {"schema": "staging"})

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("staging.receipt.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("silver.dim_product.id"))
    raw_item_name: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    line_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    match_method: Mapped[str | None] = mapped_column(String(30))
    match_score: Mapped[int | None] = mapped_column(SmallInteger)
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    receipt: Mapped[Receipt] = relationship(back_populates="items")
    product: Mapped[Product | None] = relationship()


class ConversationMessage(Base):
    """Placeholder lịch sử chat của module sẽ triển khai sau."""

    __tablename__ = "conversation_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class AgentLog(Base):
    """Placeholder log agent của module sẽ triển khai sau."""

    __tablename__ = "agent_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[UUID | None] = mapped_column()
    user_question: Mapped[str] = mapped_column(Text, nullable=False)
    tools_called: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    final_answer: Mapped[str | None] = mapped_column(Text)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    was_helpful: Mapped[bool | None] = mapped_column()


class ForecastTrainingRun(Base):
    """Metadata vận hành dùng để Airflow quyết định retrain Forecast."""

    __tablename__ = "forecast_training_runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    business_date_to: Mapped[Any | None] = mapped_column(Date)
    receipt_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    dih_fetch_day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dih_fetch_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
