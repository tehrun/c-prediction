from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Exchange(TimestampMixin, Base):
    __tablename__ = "exchanges"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Market(TimestampMixin, Base):
    __tablename__ = "markets"
    __table_args__ = (UniqueConstraint("exchange_id", "exchange_symbol"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    exchange_symbol: Mapped[str] = mapped_column(String(64), index=True)
    base_currency: Mapped[str] = mapped_column(String(32), index=True)
    quote_currency: Mapped[str] = mapped_column(String(32), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_amount: Mapped[Decimal | None] = mapped_column(Numeric(38, 18))
    minimum_cost: Mapped[Decimal | None] = mapped_column(Numeric(38, 18))
    amount_precision: Mapped[int | None] = mapped_column(Integer)
    price_precision: Mapped[int | None] = mapped_column(Integer)
    exchange: Mapped[Exchange] = relationship()
    asset: Mapped[Asset] = relationship()


class Candle(Base):
    __tablename__ = "candles"
    __table_args__ = (UniqueConstraint("exchange_id", "market_id", "timeframe", "opened_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    high: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    low: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    close: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    volume: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    trade_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class DataQualityEvent(Base):
    __tablename__ = "data_quality_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_id: Mapped[int | None] = mapped_column(ForeignKey("exchanges.id"), index=True)
    market_id: Mapped[int | None] = mapped_column(ForeignKey("markets.id"), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_key: Mapped[str] = mapped_column(String(32), index=True)
    job_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
