# API Endpoints Reference

## Docs

| URL | Description |
| --- | --- |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/api/v1/openapi.json` | OpenAPI spec |

## Memory REST API

Base path: `/api/v1`

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/memory/search` | Semantic memory search (vector similarity + optional RLM re-ranking) |
| `POST` | `/api/v1/memory/save` | Save memory with auto-classification and embedding |
| `GET` | `/api/v1/memory/list` | List memories with pagination and filters |
| `DELETE` | `/api/v1/memory/{memory_id}` | Delete memory by ID |
| `GET` | `/api/v1/memory/stats` | Namespace memory statistics (total, storage, entries today, cache hits) |
| `GET` | `/api/v1/memory/namespaces` | List all existing namespaces |
| `GET` | `/api/v1/memory/types` | List distinct memory types in the namespace |

Use `X-Memory-Namespace` header to scope all operations.

### Save Memory Details

When saving a memory, the server auto-classifies `type` and `tags` via LLM when the caller uses defaults (`type=knowledge`, `tags=[]`). The response includes:

- `classified_by_llm` — `true` if the server auto-classified, `false` if the caller provided explicit values or LLM failed
- `embedding_generated` — `true` if a real embedding was generated, `false` if the embedding provider was unavailable and a zero-vector fallback was used

Valid memory types: `knowledge`, `context`, `summary`, `event`, `code_snippet`, `preference`.

## MCP Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/mcp` | MCP JSON-RPC methods (`initialize`, `tools/list`, `tools/call`) |
| `GET` | `/mcp` | Streamable HTTP event stream |
| `DELETE` | `/mcp` | Close MCP session |
| `GET` | `/mcp/info` | MCP server metadata |

### MCP Tools

| Tool | Description |
| --- | --- |
| `search_memory` | Semantic similarity search with optional RLM re-ranking |
| `list_memory` | List memories with filters (tags, type, date range) |
| `save_memory` | Save memory — server auto-classifies type and tags via LLM. Only provide `content` (and optionally `namespace`). Set `memory_type` or `tags` only to override auto-classification. |
| `delete_memory` | Delete a memory by ID |

Compatibility discovery endpoints:

| Method | Path |
| --- | --- |
| `GET` | `/.well-known/oauth-protected-resource` |
| `GET` | `/.well-known/oauth-protected-resource/mcp` |

## Health and Metrics

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Overall service health |
| `GET` | `/health/` | Alias of `/health` |
| `GET` | `/health/db` | Database and cache connectivity |
| `GET` | `/health/postgres` | PostgreSQL version and status |
| `GET` | `/health/cache` | `pg_cache` status and entry count |
| `GET` | `/health/config` | Configured LLM and embedding model info |
| `GET` | `/metrics` | App metrics summary |
