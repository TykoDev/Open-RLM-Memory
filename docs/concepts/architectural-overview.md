# Architectural Overview

## System Shape

```text
Browser / MCP Client
        |
        v
 FastAPI app (port 8000)
   - REST API (/api/v1/*)
   - MCP streamable HTTP (/mcp)
   - SPA static hosting
        |
        v
 PostgreSQL
   - memory, memory_embedding, users
   - pgvector extension for similarity search
   - pg_cache table for search caching
        |
        v
 OpenAI-compatible provider (LM Studio)
   - /chat/completions (LLM: classification, RLM query decomposition, re-ranking)
   - /embeddings (vector generation)
```

## Core Flows

### Memory Save

1. Request enters REST (`POST /api/v1/memory/save`) or MCP (`save_memory` tool).
2. Namespace is normalized from `X-Memory-Namespace` header or tool arguments.
3. Namespace resolves to an internal user row (created on first use).
4. If caller uses default type (`knowledge`) and empty tags, server calls LLM to auto-classify the memory type and generate tags.
5. Embedding is generated via the configured embedding model. If the provider is unavailable and `ALLOW_EMBEDDING_FALLBACK=true`, a zero-vector fallback is used and flagged in the response.
6. Memory and embedding are persisted. Namespace cache is invalidated.
7. Response includes `classified_by_llm` and `embedding_generated` flags.

### Memory Search

1. Request enters REST or MCP endpoint.
2. Cache is checked first (`pg_cache` with TTL).
3. If RLM is enabled: query is decomposed into sub-queries, each sub-query is embedded and searched, results are re-ranked by LLM.
4. If RLM is disabled: single embedding lookup with cosine similarity.
5. Results are cached and returned with RLM metrics.

### Memory List

1. Direct database query filtered by namespace user.
2. No embeddings involved — pagination via `limit`/`offset`.

## Backend Services

| Service | File | Purpose |
| --- | --- | --- |
| `MemoryService` | `services/memory_service.py` | Orchestrates save, search, list, delete operations |
| `EmbeddingService` | `services/embedding_service.py` | Generates embeddings via OpenAI-compatible API, returns `EmbeddingResult` with fallback info |
| `LLMService` | `services/llm_service.py` | LLM completions, JSON parsing, `classify_memory()` for auto-classification |
| `RLMService` | `services/rlm_service.py` | Query decomposition and re-ranking for search |
| `PgCacheService` | `services/pg_cache_service.py` | PostgreSQL-based search result caching |
| `UserService` | `services/user_service.py` | Namespace normalization and user resolution |

## Frontend Pages

| Page | File | Purpose |
| --- | --- | --- |
| Dashboard | `pages/Dashboard.tsx` | Overview stats, model config cards, recent memories |
| Memory | `pages/Memory.tsx` | Search, paginated list, add/delete memories |

## Frontend Components

| Component | File | Purpose |
| --- | --- | --- |
| `TopNav` | `components/Layout/TopNav.tsx` | Navigation bar with namespace dropdown switcher, theme toggle |
| `AppLayout` | `components/Layout/AppLayout.tsx` | Page layout wrapper |
| `StatCard` | `components/common/StatCard.tsx` | Reusable statistics display card |
| `MemoryCard` | `components/common/MemoryCard.tsx` | Individual memory display card |
| `AddMemorySidebar` | `components/Dashboard/AddMemorySidebar.tsx` | Sidebar form for adding new memories |

## Design Choices

- Single deployable app for local hosting simplicity.
- PostgreSQL-first stack.
- Server-side namespace enforcement for tenant isolation.
- LLM auto-classification reduces client complexity — agents only need to provide `content`.
- Embedding fallback transparency — callers know when search may be degraded.
