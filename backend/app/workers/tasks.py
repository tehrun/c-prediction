from collections.abc import Callable
from typing import TypeVar, cast

from app.workers.celery_app import celery_app

TaskFunc = TypeVar("TaskFunc", bound=Callable[..., object])
task = cast(Callable[[TaskFunc], TaskFunc], celery_app.task)


@task
def refresh_exchange_markets() -> str:
    return "scheduled market refresh queued"


@task
def update_market_universe() -> str:
    return "scheduled universe update queued"


@task
def fetch_recent_hourly_candles() -> str:
    return "scheduled recent candle fetch queued"


@task
def detect_missing_candles() -> str:
    return "scheduled missing candle detection queued"


@task
def backfill_missing_candles() -> str:
    return "scheduled missing candle backfill queued"


@task
def backfill_ohlcv(exchange: str, symbol: str, timeframe: str = "1h", days: int = 90) -> str:
    return f"backfill requested for {exchange} {symbol} {timeframe} {days}d"
