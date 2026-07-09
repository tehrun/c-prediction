# Bootstrap
1. `docker compose up --build -d`
2. `docker compose exec backend alembic upgrade head`
3. `docker compose exec backend python -m app.ingestion.backfill --exchange kraken --symbol BTC/USD --timeframe 1h --days 7`
