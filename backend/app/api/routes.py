from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    AssetOut,
    CandleOut,
    DataHealthOut,
    ExchangeOut,
    HealthResponse,
    MarketOut,
)
from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.exchanges.factory import get_exchange_adapter
from app.models import Asset, Candle, Exchange, Market
from app.services.data_quality import data_health

api = APIRouter(prefix="/api/v1")
health = APIRouter(prefix="/health")


@health.get("/live", response_model=HealthResponse)
async def live() -> dict[str, object]:
    return {"status": "healthy", "details": {"app": "CryptoPilot"}}


@health.get("/ready", response_model=HealthResponse)
async def ready(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    await session.execute(text("select 1"))
    return {"status": "healthy", "details": {"database": "healthy"}}


@health.get("/data", response_model=HealthResponse)
async def health_data(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    h = await data_health(session)
    return {
        "status": "degraded" if h["status"] in {"stale", "unavailable"} else "healthy",
        "details": h,
    }


@health.get("/exchanges", response_model=HealthResponse)
async def exchanges_health() -> dict[str, object]:
    details: dict[str, Any] = {}
    for key in ("kraken", "binance"):
        adapter = get_exchange_adapter(key)
        try:
            details[key] = (await adapter.check_health()).model_dump()
        finally:
            await adapter.close()
    return {"status": "healthy", "details": details}


@api.get("/exchanges", response_model=list[ExchangeOut])
async def list_exchanges(session: AsyncSession = Depends(get_session)) -> list[Exchange]:
    return list((await session.execute(select(Exchange).order_by(Exchange.key))).scalars().all())


@api.get("/market/universe", response_model=list[MarketOut])
async def universe(
    session: AsyncSession = Depends(get_session), settings: Settings = Depends(get_settings)
) -> list[dict[str, object]]:
    stmt = (
        select(Market, Exchange)
        .join(Exchange)
        .where(Market.active)
        .order_by(Market.base_currency)
        .limit(settings.market_universe_max)
    )
    return [
        {
            "exchange": e.key,
            "symbol": m.exchange_symbol,
            "base_currency": m.base_currency,
            "quote_currency": m.quote_currency,
            "active": m.active,
        }
        for m, e in (await session.execute(stmt)).all()
    ]


@api.get("/market/data-health", response_model=DataHealthOut)
async def all_health(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    return await data_health(session)


@api.get("/market/data-health/{symbol}", response_model=DataHealthOut)
async def symbol_health(
    symbol: str, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    return await data_health(session, symbol)


@api.get("/assets/{symbol}", response_model=AssetOut)
async def get_asset(symbol: str, session: AsyncSession = Depends(get_session)) -> Asset:
    asset = await session.scalar(select(Asset).where(Asset.symbol == symbol.upper()))
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


@api.get("/assets/{symbol}/candles", response_model=list[CandleOut])
async def candles(
    symbol: str,
    exchange: str,
    timeframe: str = "1h",
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(500, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> list[Candle]:
    stmt = (
        select(Candle)
        .join(Market)
        .join(Exchange)
        .where(
            Market.base_currency == symbol.upper(),
            Exchange.key == exchange,
            Candle.timeframe == timeframe,
        )
    )
    if start:
        stmt = stmt.where(Candle.opened_at >= start)
    if end:
        stmt = stmt.where(Candle.opened_at <= end)
    rows = (
        (await session.execute(stmt.order_by(desc(Candle.opened_at)).limit(limit))).scalars().all()
    )
    return list(reversed(rows))
