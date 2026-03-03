# Open RLM Memory Docs

Open RLM Memory is a local-first memory server for AI agents.

- Backend and frontend are served by one FastAPI app on port `8000`.
- Memory data is stored in PostgreSQL with `pgvector`.
- Search caching uses an app-owned PostgreSQL table: `pg_cache`.
- Identity and data isolation use `X-Memory-Namespace` (no OAuth/JWT/Auth0).
- LLM and embedding calls use an OpenAI-compatible endpoint (LM Studio by default).

## Sections

- [Getting Started](getting-started/)
  - [Installation](getting-started/01-installation.md)
  - [Configuration](getting-started/02-configuration.md)
  - [Local Development](getting-started/03-local-development.md)
- [Guides](guides/)
  - [MCP Inspector Testing](guides/mcp-inspector-testing.md)
  - [Run Tests](guides/run-tests.md)
  - [Setting Up Monitoring](guides/setting-up-monitoring.md)
  - [Deploying to Production](guides/deploying-to-production.md)
- [Concepts](concepts/)
  - [Architectural Overview](concepts/architectural-overview.md)
  - [Security Model](concepts/security-model.md)
- [Reference](reference/)
  - [API Endpoints](reference/api-endpoints.md)
  - [Data Model](reference/data-model.md)
  - [Environment Variables](reference/environment-variables.md)
  - [Commands & Scripts](reference/commands-scripts.md)
  - [Dependencies](reference/dependencies.md)
  - [Docker Reference](reference/docker-reference.md)
