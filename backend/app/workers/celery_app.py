from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("cryptopilot", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "refresh-markets-hourly": {
        "task": "app.workers.tasks.refresh_exchange_markets",
        "schedule": crontab(minute=5),
    },
    "recent-candles-hourly": {
        "task": "app.workers.tasks.fetch_recent_hourly_candles",
        "schedule": crontab(minute=10),
    },
    "detect-missing-hourly": {
        "task": "app.workers.tasks.detect_missing_candles",
        "schedule": crontab(minute=20),
    },
}
