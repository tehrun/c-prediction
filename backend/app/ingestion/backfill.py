import argparse, asyncio
from datetime import UTC, datetime, timedelta
from app.db.session import SessionLocal
from app.exchanges.factory import get_exchange_adapter
from app.ingestion.validation import validate_candles

async def run(exchange: str, symbol: str, timeframe: str, days: int) -> None:
    adapter = get_exchange_adapter(exchange)
    since = datetime.now(UTC) - timedelta(days=days)
    try:
        candles = await adapter.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        validate_candles(candles)
        async with SessionLocal():
            print(f"Fetched {len(candles)} validated candles for {exchange} {symbol}")
    finally:
        await adapter.close()

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--exchange", required=True); p.add_argument("--symbol", required=True); p.add_argument("--timeframe", default="1h"); p.add_argument("--days", type=int, default=90)
    a = p.parse_args(); asyncio.run(run(a.exchange, a.symbol, a.timeframe, a.days))
if __name__ == "__main__": main()
