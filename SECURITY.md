# Security

Phase 1 uses only public exchange endpoints; no exchange credentials are required. Secrets must come only from environment variables or a future secret manager, must never be logged, and must not be committed. Future exchange API keys must have trading permission only and no withdrawal permission.

Live trading is not implemented. Before it exists, CryptoPilot requires encryption at rest for credentials, audit logs for every operator and automated action, manual activation gates, position/risk limits, kill switches, and reviewable strategy configuration.

CORS is configured through `BACKEND_CORS_ORIGINS`; development defaults allow the Vite origin only. Rate limiting is planned at the API gateway/reverse proxy and per-user/API-token levels. Dependency scanning should run in CI through Dependabot or equivalent. Container scanning should run before deployment with tools such as Trivy or registry-native scanners.

Database backup and restore plan: take scheduled PostgreSQL/TimescaleDB logical or physical backups, test restores in a non-production environment, retain point-in-time recovery logs where available, and document RPO/RTO before production use.
