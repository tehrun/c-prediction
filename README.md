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

## Ubuntu VPS deployment

The repository includes a development compose file (`docker-compose.yml`), a production override (`docker-compose.prod.yml`), and an executable deployment helper (`scripts/deploy.sh`).

### 1. Prepare the VPS

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git ufw
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and back in so your user can run Docker without `sudo`.

### 2. Clone and configure

```bash
git clone <your-repo-url> /opt/cryptopilot
cd /opt/cryptopilot
cp .env.example .env
nano .env
```

Set at minimum:

```env
POSTGRES_PASSWORD=<long-random-password>
DATABASE_URL=postgresql+asyncpg://cryptopilot:<same-password>@db:5432/cryptopilot
BACKEND_CORS_ORIGINS=https://your-domain.example
VITE_API_BASE_URL=https://your-domain.example
PUBLIC_HOSTNAME=your-domain.example
```

### 3. Deploy

```bash
./scripts/deploy.sh
```

Optional first small Kraken BTC/ETH backfill:

```bash
INITIAL_BACKFILL=1 INITIAL_BACKFILL_DAYS=7 ./scripts/deploy.sh
```

### 4. Firewall and TLS

For a simple HTTP-only deployment:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw enable
```

For HTTPS, install host-level Nginx and Certbot, adapt `infrastructure/nginx/cryptopilot.conf`, and issue a certificate:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
sudo cp infrastructure/nginx/cryptopilot.conf /etc/nginx/sites-available/cryptopilot
sudo ln -s /etc/nginx/sites-available/cryptopilot /etc/nginx/sites-enabled/cryptopilot
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.example
```

### 5. Operations

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend python -m app.ingestion.backfill --exchange kraken --symbol BTC/USD --timeframe 1h --days 90
```

PostgreSQL and Redis data are stored in named Docker volumes. Back them up before destructive upgrades.
