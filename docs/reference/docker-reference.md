# Docker Reference

## Compose Services

| Service | Image/Build | Ports | Purpose |
| --- | --- | --- | --- |
| `postgres` | `pgvector/pgvector:pg15` | `5432` | Primary database + pgvector |
| `app` | Local `Dockerfile` | `8000` | Unified FastAPI + React app |

## Common Commands

```bash
docker-compose up -d
docker-compose down
docker-compose up -d --build app
docker-compose logs -f app
docker-compose logs -f postgres
```

## Runtime Variables (app service)

- `DATABASE_URL`
- `POSTGRES_*`
- `DEFAULT_MEMORY_NAMESPACE`
- `SEARCH_CACHE_TTL_SECONDS`
- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `EMBED_OPENAI_BASE_URL` (optional)
- `EMBED_OPENAI_API_KEY` (optional)
- `EMBEDDING_MODEL`
- `EMBEDDING_DIMENSIONS`

## Notes

- `pg_cache` is an application table in PostgreSQL.
