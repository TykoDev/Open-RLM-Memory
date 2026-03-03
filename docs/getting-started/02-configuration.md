# Configuration

Configuration is defined by `.env.example` and `backend/app/core/config.py`.

## Required Variables

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/rlm_memory
OPENAI_BASE_URL=http://<your-lm-studio-host>:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=mistralai/ministral-3-14b-reasoning
EMBEDDING_MODEL=text-embedding-qwen3-embedding-4b@q4_k_m
EMBEDDING_DIMENSIONS=1536
```

Optional dedicated embedding provider:

```env
EMBED_OPENAI_BASE_URL=http://<your-embed-host>:1234/v1
EMBED_OPENAI_API_KEY=lm-studio-embed
```

If `EMBED_OPENAI_BASE_URL` or `EMBED_OPENAI_API_KEY` is unset/empty, embedding requests fall back to `OPENAI_BASE_URL` and `OPENAI_API_KEY`.

## Namespace and Cache

```env
DEFAULT_MEMORY_NAMESPACE=local
MAX_NAMESPACE_LENGTH=64
SEARCH_CACHE_TTL_SECONDS=300
ALLOW_EMBEDDING_FALLBACK=true
```

### About Namespaces

A namespace scopes all memory operations so that different projects, agents, or users have independent memory stores. Memories saved in namespace `project-a` are invisible to namespace `project-b`.

- Set the namespace per request via the `X-Memory-Namespace` header (REST) or the `namespace` MCP tool argument.
- If omitted, the server uses `DEFAULT_MEMORY_NAMESPACE` (default: `local`).
- Namespaces are created automatically on first use.
- Namespaces are case-insensitive and normalized to lowercase.
- Max length is controlled by `MAX_NAMESPACE_LENGTH` (default: 64 characters).

Search results are cached per namespace in the PostgreSQL `pg_cache` table with TTL controlled by `SEARCH_CACHE_TTL_SECONDS`.

## Network Defaults

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Important

- This build does not use OAuth, JWT, or Auth0.
