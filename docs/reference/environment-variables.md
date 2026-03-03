# Environment Variables

Source of truth: `.env.example` and `backend/app/core/config.py`.

## Server

| Variable | Default | Description |
| --- | --- | --- |
| `SERVER_HOST` | `0.0.0.0` | API bind host |
| `SERVER_PORT` | `8000` | API bind port |
| `LOG_LEVEL` | `INFO` | Application log level |

## Database

| Variable | Default | Description |
| --- | --- | --- |
| `DB_TYPE` | `postgres` | Database backend |
| `DATABASE_URL` | `postgresql+asyncpg://...` | SQLAlchemy async connection URL |
| `POSTGRES_USER` | `postgres` | DB username |
| `POSTGRES_PASSWORD` | `password` | DB password |
| `POSTGRES_SERVER` | `postgres` | DB host |
| `POSTGRES_DB` | `rlm_memory` | DB name |

## Namespace and Cache

| Variable | Default | Description |
| --- | --- | --- |
| `DEFAULT_MEMORY_NAMESPACE` | `local` | Namespace used when header is missing |
| `MAX_NAMESPACE_LENGTH` | `64` | Max namespace size |
| `SEARCH_CACHE_TTL_SECONDS` | `300` | TTL for `pg_cache` entries |

## Model Provider

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_BASE_URL` | `http://127.0.0.1:1234/v1` | OpenAI-compatible API base URL (used for LLM and embeddings unless overridden) |
| `OPENAI_API_KEY` | `lm-studio` | API key value used by client |
| `OPENAI_MODEL` | `mistralai/ministral-3-14b-reasoning` | Chat/classification model |
| `EMBED_OPENAI_BASE_URL` | unset | Optional separate embedding endpoint; falls back to `OPENAI_BASE_URL` |
| `EMBED_OPENAI_API_KEY` | unset | Optional separate embedding API key; falls back to `OPENAI_API_KEY` |
| `EMBEDDING_MODEL` | `text-embedding-qwen3-embedding-4b@q4_k_m` | Embedding model name |
| `EMBEDDING_DIMENSIONS` | `1536` | Embedding vector dimensions |
| `ALLOW_EMBEDDING_FALLBACK` | `true` | When `true`, stores zero-vector if embedding provider is unavailable (response shows `embedding_generated: false`). When `false`, save fails on embedding error. |
| `LLM_PROVIDER` | `openai-compatible` | Provider identifier (informational) |

## Frontend

| Variable | Default | Description |
| --- | --- | --- |
| `VITE_API_URL` | unset | Optional API override; default uses same-origin |

## Not Used in Current Architecture

The active local stack does not use Auth0, OAuth, or JWT authentication variables.
