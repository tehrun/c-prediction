from app.workers.celery_app import celery_app


@celery_app.task
def refresh_exchange_markets() -> str:
    return "scheduled market refresh queued"


@celery_app.task
def update_market_universe() -> str:
    return "scheduled universe update queued"


@celery_app.task
def fetch_recent_hourly_candles() -> str:
    return "scheduled recent candle fetch queued"


@celery_app.task
def detect_missing_candles() -> str:
    return "scheduled missing candle detection queued"


@celery_app.task
def backfill_missing_candles() -> str:
    return "scheduled missing candle backfill queued"


@celery_app.task
def backfill_ohlcv(exchange: str, symbol: str, timeframe: str = "1h", days: int = 90) -> str:
    return f"backfill requested for {exchange} {symbol} {timeframe} {days}d"
