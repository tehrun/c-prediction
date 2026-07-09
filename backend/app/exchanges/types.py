from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ExchangeMarket(BaseModel):
    symbol: str
    base: str
    quote: str
    active: bool = True
    spot: bool = True
    amount_precision: int | None = None
    price_precision: int | None = None
    minimum_amount: Decimal | None = None
    minimum_cost: Decimal | None = None
    quote_volume: Decimal | None = None


class Ticker(BaseModel):
    symbol: str
    last: Decimal | None = None
    quote_volume: Decimal | None = None
    timestamp: datetime | None = None


class Candle(BaseModel):
    opened_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    trade_count: int | None = None


class ExchangeStatus(BaseModel):
    key: str
    status: str
    message: str | None = None
