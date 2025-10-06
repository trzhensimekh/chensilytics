"""SQLAlchemy ORM models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Item(Base):
    """Item (type) in EVE."""

    __tablename__ = "items"

    item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    group_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    volume_m3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Market(Base):
    """Market hub definition."""

    __tablename__ = "markets"

    hub_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    system_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OrderSnapshot(Base):
    """Market order snapshot."""

    __tablename__ = "orders_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    hub_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # 'buy' or 'sell'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    ts_snapshot: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_orders_item_hub_ts", "item_id", "hub_id", "ts_snapshot"),
        Index("idx_orders_hub_ts", "hub_id", "ts_snapshot"),
    )


class PriceHistory(Base):
    """Daily price history."""

    __tablename__ = "prices_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    hub_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    avg_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        Index("idx_price_hist_item_hub_date", "item_id", "hub_id", "date", unique=True),
    )


class AnalyticsArbitrageRun(Base):
    """Analytics run metadata."""

    __tablename__ = "analytics_arbitrage_run"

    run_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    num_candidates: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")


class AnalyticsArbitrageItem(Base):
    """Arbitrage candidate result."""

    __tablename__ = "analytics_arbitrage_item"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    from_hub_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    to_hub_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    sell_price: Mapped[float] = mapped_column(Float, nullable=False)
    spread_pct: Mapped[float] = mapped_column(Float, nullable=False)
    fees_total: Mapped[float] = mapped_column(Float, nullable=False)
    liquidity_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ev_isk: Mapped[float] = mapped_column(Float, nullable=False)
    net_margin_pct: Mapped[float] = mapped_column(Float, nullable=False)
    decay_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    capital_required: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("idx_arb_item_run", "run_id", "item_id"),)
