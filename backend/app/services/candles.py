from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.exchanges.types import Candle as DomainCandle
from app.models import Candle


async def upsert_candles(
    session: AsyncSession,
    exchange_id: int,
    market_id: int,
    timeframe: str,
    candles: list[DomainCandle],
) -> int:
    if not candles:
        return 0
    rows = [
        dict(
            exchange_id=exchange_id,
            market_id=market_id,
            timeframe=timeframe,
            opened_at=c.opened_at,
            open=c.open,
            high=c.high,
            low=c.low,
            close=c.close,
            volume=c.volume,
            trade_count=c.trade_count,
        )
        for c in candles
    ]
    if session.bind and session.bind.dialect.name == "postgresql":
        stmt = (
            pg_insert(Candle)
            .values(rows)
            .on_conflict_do_update(
                index_elements=[
                    Candle.exchange_id,
                    Candle.market_id,
                    Candle.timeframe,
                    Candle.opened_at,
                ],
                set_={
                    "open": pg_insert(Candle).excluded.open,
                    "high": pg_insert(Candle).excluded.high,
                    "low": pg_insert(Candle).excluded.low,
                    "close": pg_insert(Candle).excluded.close,
                    "volume": pg_insert(Candle).excluded.volume,
                },
            )
        )
        await session.execute(stmt)
    else:
        for row in rows:
            existing = await session.scalar(
                select(Candle).filter_by(
                    exchange_id=exchange_id,
                    market_id=market_id,
                    timeframe=timeframe,
                    opened_at=row["opened_at"],
                )
            )
            if existing:
                for k, v in row.items():
                    setattr(existing, k, v)
            else:
                session.add(Candle(**row))
    await session.commit()
    return len(rows)


def expected_missing(
    existing: list[datetime], start: datetime, end: datetime, step: timedelta
) -> list[datetime]:
    have = set(existing)
    cur = start
    missing = []
    while cur <= end:
        if cur not in have:
            missing.append(cur)
        cur += step
    return missing
