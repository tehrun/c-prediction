#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILES=(-f docker-compose.yml -f docker-compose.prod.yml)
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-cryptopilot}"
INITIAL_BACKFILL="${INITIAL_BACKFILL:-0}"

log() { printf '\n[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || fail "docker is not installed"
docker compose version >/dev/null 2>&1 || fail "docker compose plugin is not installed"
[ -f .env ] || fail "missing .env. Copy .env.example to .env and set production values first"

log "Validating compose configuration"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" config >/dev/null

log "Pulling base images"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" pull --ignore-buildable

log "Building application images"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" build

log "Starting database and Redis"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" up -d db redis

log "Starting application services"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" up -d backend worker beat frontend

log "Running database migrations"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" exec -T backend alembic upgrade head

log "Seeding bootstrap records"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" exec -T backend python -m app.ingestion.bootstrap

if [ "$INITIAL_BACKFILL" = "1" ]; then
  log "Running optional small BTC/ETH backfills"
  docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" exec -T backend python -m app.ingestion.backfill --exchange kraken --symbol BTC/USD --timeframe 1h --days "${INITIAL_BACKFILL_DAYS:-7}"
  docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" exec -T backend python -m app.ingestion.backfill --exchange kraken --symbol ETH/USD --timeframe 1h --days "${INITIAL_BACKFILL_DAYS:-7}"
fi

log "Service status"
docker compose "${COMPOSE_FILES[@]}" -p "$PROJECT_NAME" ps

log "Deployment complete"
printf '\nFrontend: http://%s\n' "${PUBLIC_HOSTNAME:-your-server-ip}"
printf 'Backend health: http://%s/health/live if proxied, or http://127.0.0.1:8000/health/live on the VPS\n' "${PUBLIC_HOSTNAME:-your-server-ip}"
