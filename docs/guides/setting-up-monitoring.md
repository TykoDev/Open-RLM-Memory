# Setting Up Monitoring

## Core Endpoints

- `GET /health` — overall service health
- `GET /health/db` — database and cache connectivity
- `GET /health/postgres` — PostgreSQL version and connection status
- `GET /health/cache` — `pg_cache` health and entry count
- `GET /health/config` — configured LLM and embedding model info
- `GET /metrics` — metrics summary payload

## What to Watch

- API latency for `/api/v1/memory/search`
- Error rate for `/mcp` and REST endpoints
- PostgreSQL connectivity and query latency
- Cache hit/miss trends from application metrics
- Embedding fallback rate (indicates provider availability issues)
- LLM classification success rate

## Suggested Alerts

- Health endpoint not `200` for 3+ checks
- Search p95 latency above threshold
- Repeated DB connection failures
- Sustained cache miss spike
- Sustained embedding fallbacks (degraded search quality)

## Logging

- Use `LOG_LEVEL=INFO` by default.
- Raise to `DEBUG` only for short troubleshooting windows.
- Do not log secrets or credential values.
