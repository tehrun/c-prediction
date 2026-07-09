from datetime import UTC, datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Candle, Market

async def data_health(session: AsyncSession, symbol: str | None = None) -> dict:
    stmt = select(func.max(Candle.opened_at))
    if symbol:
        stmt = stmt.join(Market, Market.id == Candle.market_id).where(Market.base_currency == symbol.upper())
    latest = await session.scalar(stmt)
    if latest is None: return {"status":"unavailable","latest_candle":None,"stale_markets":0,"message":"No candle data loaded"}
    stale = latest < datetime.now(UTC) - timedelta(hours=3)
    return {"status":"stale" if stale else "healthy","latest_candle":latest,"stale_markets":1 if stale else 0,"message":None}
