# Data Model

## Core Tables

### `users`

- `id` (UUID, PK)
- `namespace` (string, normalized, unique, indexed)
- `display_name` (string)
- `created_at`, `updated_at`

### `memory`

- `id` (UUID, PK)
- `user_id` (FK -> `users.id`)
- `content` (text)
- `type` (string — one of: `knowledge`, `context`, `summary`, `event`, `code_snippet`, `preference`)
- `tags` (JSON/array, dialect-aware)
- `metadata_` (JSON)
- `created_at`, `updated_at`, `deleted_at`

### `memory_embedding`

- `id` (UUID, PK)
- `memory_id` (FK -> `memory.id`)
- `embedding` (vector, `EMBEDDING_DIMENSIONS` — default 1536)
- `model` (string — the model name used to generate the embedding)

### `pg_cache`

- `cache_key` (string/hash, PK)
- `namespace` (string)
- `payload` (JSON)
- `expires_at` (UTC datetime)
- `hit_count` (integer)
- `last_hit_at` (datetime)
- `created_at`, `updated_at`

## Service Data Objects

### `EmbeddingResult`

Returned by `EmbeddingService.embed()`:

- `vector` — the embedding float array
- `is_fallback` — `true` if embedding provider was unavailable and zero-vector was used
- `model` — the model name used
- `error` — error message if fallback was triggered, `null` otherwise

### `ClassificationResult`

Returned by `LLMService.classify_memory()`:

- `memory_type` — one of the 6 valid types
- `tags` — list of 1-5 lowercase tags
- `classified_by_llm` — `true` if LLM successfully classified, `false` if defaults were used

### `SaveResult`

Returned by `MemoryService.save_memory()`:

- `memory` — the persisted `Memory` object
- `classified_by_llm` — whether LLM auto-classification was used
- `embedding_is_fallback` — whether embedding fell back to zero-vector
- `embedding_error` — error message if embedding failed, `null` otherwise

## Isolation Rule

All memory operations are scoped by resolved namespace user on the server side. A namespace is resolved to a user row on first use.
