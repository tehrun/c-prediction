# Implementation Roadmap

## 1. Foundation
- [x] Repository structure, Docker Compose, FastAPI, Vite, CI, docs.
- [x] Settings, logging, CORS, health routes, Alembic schema.

## 2. Market-data ingestion
- [x] Exchange adapter boundary for Kraken and Binance public data.
- [x] Market-universe filtering rules.
- [x] OHLCV validation, idempotent upsert service, CLI entry, Celery task skeletons.
- [x] Data-health endpoints.

## 3. Feature engineering and top-five rankings
- [ ] Compute returns, volatility, volume/liquidity features.
- [ ] Rank top five markets by configurable scoring.

## 4. Machine-learning models
- [ ] Train/evaluate baseline models.
- [ ] Persist model metadata and predictions.

## 5. Backtesting
- [ ] Historical strategy replay.
- [ ] Metrics, drawdown, and fee/slippage modeling.

## 6. Paper trading
- [ ] Simulated portfolio and order lifecycle.
- [ ] Risk-limited strategy execution without exchange credentials.

## 7. Guarded live trading
- [ ] Manual activation, encrypted keys, audit logs, risk controls.
- [ ] Trading-only exchange keys; withdrawals disabled.
