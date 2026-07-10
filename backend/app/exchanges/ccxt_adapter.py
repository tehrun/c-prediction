from datetime import UTC, datetime
from decimal import Decimal

import ccxt.async_support as ccxt

from app.exchanges.base import ExchangeAdapter
from app.exchanges.types import Candle, ExchangeMarket, ExchangeStatus, Ticker


def dec(v: object) -> Decimal | None:
    return None if v is None else Decimal(str(v))


class CcxtExchangeAdapter(ExchangeAdapter):
    ccxt_id: str

    def __init__(self) -> None:
        klass = getattr(ccxt, self.ccxt_id)
        self.client = klass({"enableRateLimit": True})

    async def load_markets(self) -> list[ExchangeMarket]:
        raw = await self.client.load_markets()
        out = []
        for m in raw.values():
            limits = m.get("limits", {})
            precision = m.get("precision", {})
            out.append(
                ExchangeMarket(
                    symbol=m["symbol"],
                    base=m.get("base") or "",
                    quote=m.get("quote") or "",
                    active=bool(m.get("active", True)),
                    spot=bool(m.get("spot", False)),
                    amount_precision=precision.get("amount"),
                    price_precision=precision.get("price"),
                    minimum_amount=dec(limits.get("amount", {}).get("min")),
                    minimum_cost=dec(limits.get("cost", {}).get("min")),
                )
            )
        return out

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str, since: datetime | None = None, limit: int | None = None
    ) -> list[Candle]:
        since_ms = int(since.timestamp() * 1000) if since else None
        rows = await self.client.fetch_ohlcv(
            symbol, timeframe=timeframe, since=since_ms, limit=limit
        )
        return [
            Candle(
                opened_at=datetime.fromtimestamp(r[0] / 1000, UTC),
                open=Decimal(str(r[1])),
                high=Decimal(str(r[2])),
                low=Decimal(str(r[3])),
                close=Decimal(str(r[4])),
                volume=Decimal(str(r[5])),
            )
            for r in rows
        ]

    async def fetch_ticker(self, symbol: str) -> Ticker:
        t = await self.client.fetch_ticker(symbol)
        ts = datetime.fromtimestamp(t["timestamp"] / 1000, UTC) if t.get("timestamp") else None
        return Ticker(
            symbol=symbol,
            last=dec(t.get("last")),
            quote_volume=dec(t.get("quoteVolume")),
            timestamp=ts,
        )

    async def check_health(self) -> ExchangeStatus:
        try:
            await self.client.fetch_status()
            return ExchangeStatus(key=self.key, status="healthy")
        except Exception as exc:
            return ExchangeStatus(key=self.key, status="degraded", message=str(exc))

    async def close(self) -> None:
        await self.client.close()


class KrakenExchangeAdapter(CcxtExchangeAdapter):
    key = "kraken"
    ccxt_id = "kraken"


class BinanceExchangeAdapter(CcxtExchangeAdapter):
    key = "binance"
    ccxt_id = "binance"
