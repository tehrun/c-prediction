# CryptoPilot

CryptoPilot is a cryptocurrency market-analysis and future paper-trading application. Phase 1 implements the foundation: real public market-data collection, candle storage, health/data APIs, Docker services, and a basic React frontend. It does not guarantee profit, and live trading is not implemented in this phase.

## Requirements
Docker, Docker Compose, Python 3.12 for local backend work, and Node 22 for frontend work.

## Docker setup
Copy `.env.example` to `.env` if desired, then run:

```bash
docker compose up --build
```

Frontend: <http://localhost:5173>. Backend docs: <http://localhost:8000/docs>.

## Environment
See `.env.example` for safe development defaults. Do not commit real secrets.

## Database migrations
```bash
docker compose exec backend alembic upgrade head
```
The initial migration enables TimescaleDB, creates exchanges/assets/markets/candles/data-quality/ingestion tables, converts candles to a hypertable, and seeds Kraken/Binance exchange records.

## Market bootstrap and ingestion
Load metadata through the exchange adapter services or scheduled worker tasks. Example OHLCV command:

```bash
docker compose exec backend python -m app.ingestion.backfill --exchange kraken --symbol BTC/USD --timeframe 1h --days 90
```

## API endpoints
- `GET /health/live`, `/health/ready`, `/health/data`, `/health/exchanges`
- `GET /api/v1/exchanges`
- `GET /api/v1/market/universe`
- `GET /api/v1/market/data-health` and `/{symbol}`
- `GET /api/v1/assets/{symbol}`
- `GET /api/v1/assets/{symbol}/candles?exchange=kraken&timeframe=1h&limit=500`

## Tests
Backend: `ruff check .`, `ruff format --check .`, `mypy app`, `pytest` from `backend/`. Frontend: `npm ci`, `npm run lint`, `npm run typecheck`, `npm test -- --run`, `npm run build` from `frontend/`.

## Troubleshooting
If the UI is empty, run migrations and ingestion. If exchange calls fail, check network access and public exchange availability. If TimescaleDB extension creation fails, confirm the `timescale/timescaledb` image is used.

## Current limitations
Market metadata persistence/bootstrap is intentionally minimal, Redis locks are represented in the worker design but need production hardening, and prediction, backtesting, paper trading, and live trading remain roadmap items.
