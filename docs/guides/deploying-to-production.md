# Deploying to Production

This project is designed for local/self-hosted deployments with PostgreSQL and a local-network model endpoint.

## Baseline Deployment

1. Provision PostgreSQL with `pgvector` enabled.
2. Build and run the unified app container.
3. Provide environment values from `.env.example`.
4. Expose only port `8000` from the app service.

## Minimum Environment

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DATABASE_URL=postgresql+asyncpg://...
OPENAI_BASE_URL=http://<lm-studio-host>:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=mistralai/ministral-3-14b-reasoning
EMBEDDING_MODEL=text-embedding-qwen3-embedding-4b@q4_k_m
EMBEDDING_DIMENSIONS=1536
# Optional dedicated embedding endpoint/key (falls back to OPENAI_* when empty)
EMBED_OPENAI_BASE_URL=
EMBED_OPENAI_API_KEY=
DEFAULT_MEMORY_NAMESPACE=local
SEARCH_CACHE_TTL_SECONDS=300
```

## Hardening Checklist

- Keep PostgreSQL non-public when possible.
- Restrict inbound access to app port `8000`.
- Use strong DB credentials and rotate periodically.
- Enable backup/restore for PostgreSQL data volume.
- Keep namespace conventions stable across clients.

## Validation

- `GET /health`
- `GET /health/cache`
- `GET /mcp/info`
- `POST /api/v1/memory/search` with `X-Memory-Namespace`
