from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
class HealthResponse(BaseModel): status: str; details: dict = Field(default_factory=dict)
class ExchangeOut(BaseModel): key: str; name: str; enabled: bool
class MarketOut(BaseModel): exchange: str; symbol: str; base_currency: str; quote_currency: str; active: bool
class AssetOut(BaseModel): symbol: str; name: str; active: bool
class CandleOut(BaseModel): opened_at: datetime; open: Decimal; high: Decimal; low: Decimal; close: Decimal; volume: Decimal; trade_count: int | None
class DataHealthOut(BaseModel): status: str; latest_candle: datetime | None = None; stale_markets: int = 0; message: str | None = None
