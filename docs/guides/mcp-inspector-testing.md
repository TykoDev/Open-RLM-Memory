# Testing with MCP Inspector

## Start Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Use transport type `Streamable HTTP` and URL `http://localhost:8000/mcp`.

## Available Tools

- `search_memory` — semantic similarity search
- `list_memory` — list/filter memories
- `save_memory` — save with auto-classification (just provide `content`)
- `delete_memory` — delete by ID

## Namespace Requirement

Scope requests with one of:

1. `namespace` in MCP tool `arguments`
2. `X-Memory-Namespace` header

## Save Memory Examples

**Minimal (auto-classification)** — the server classifies type and generates tags:

```json
{
  "content": "The project uses PostgreSQL with pgvector for semantic search."
}
```

Response will include `classified_by_llm: true` with auto-detected `type` and `tags`.

**With explicit overrides** — LLM classification is skipped:

```json
{
  "content": "Finish onboarding flow",
  "memory_type": "event",
  "tags": ["onboarding", "todo"]
}
```

Response will include `classified_by_llm: false`.

## Response Fields

- `embedding_generated` — `true` if real embedding was created, `false` if zero-vector fallback was used (embedding provider unavailable)
- `classified_by_llm` — `true` if the server auto-classified type and tags

## Quick Checks

- `initialize` returns `200` and `mcp-session-id`
- `tools/list` returns 4 tools
- `save_memory` with only `content` returns auto-classified `type` and `tags`
- `save_memory` then `search_memory` returns saved content in same namespace
- Different namespaces do not see each other's memories
