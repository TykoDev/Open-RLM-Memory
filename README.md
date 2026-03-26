# Open RLM (Open Recursive Language Model) Memory

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/TykoDev/open-rlm-memory/actions/workflows/ci.yml)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/TykoDev/open-rlm-memory/blob/main/LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3.11.0/)
[![Node.js 24](https://img.shields.io/badge/node-24-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

> Intelligent semantic memory search with Reasoning-Language Models (RLM) for AI agents.

Open RLM Memory (Open Recursive Language Model Memory) is a Model Context Protocol server that provides context-aware semantic search over stored memories. It combines vector embeddings with LLM-powered query decomposition, re-ranking, and automatic memory classification.

## Key Features

- **Semantic Search** — Vector similarity search using pgvector embeddings
- **RLM Intelligence** — Query decomposition and intelligent re-ranking using LLMs
- **Auto-Classification** — Server-side LLM classifies memory type and tags on save
- **Embedding Transparency** — Response indicates whether a real embedding or zero-vector fallback was used
- **Fast Performance** — PostgreSQL-backed `pg_cache` and async operations
- **Local Namespaces** — Memory isolation by `X-Memory-Namespace` with dropdown switcher in the UI
- **PostgreSQL First** — Local hosting with PostgreSQL + pgvector + pg cache table
- **Unified App** — Frontend and backend served from one container
- **MCP Compliant** — Full Model Context Protocol implementation

## Getting Started

### Prerequisites

- Docker & Docker Compose
- LM Studio or another OpenAI-compatible endpoint running on the local network
- Python 3.11+ (for local backend development without Docker)
- Node.js 24+ (for local frontend development without Docker)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/TykoDev/open-rlm-memory.git
cd open-rlm-memory

# 2. Configure environment
cp .env.example .env
# Edit .env — set OPENAI_BASE_URL to your LM Studio host (e.g. http://<your-host>:1234/v1)
# Optional: set EMBED_OPENAI_BASE_URL / EMBED_OPENAI_API_KEY for a separate embedding provider

# 3. Start with Docker
docker-compose up -d

# 4. Access application
# App + API:    http://localhost:8000
# API docs:     http://localhost:8000/docs
# Health:       http://localhost:8000/health
# MCP info:     http://localhost:8000/mcp/info
# Model config: http://localhost:8000/health/config
```

### Manual Start (without Docker)

```bash
# Backend
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# Set VITE_API_URL=http://localhost:8000 when running frontend separately
```

### MCP Inspector (dev mode)

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

- Transport: `Streamable HTTP` at `http://localhost:8000/mcp`
- Namespace: set `X-Memory-Namespace` header or pass `namespace` in tool arguments
- Save a memory with only `content` — the server auto-classifies type and tags via LLM

## Namespaces

Namespaces isolate memories so that different projects, agents, or users do not see each other's stored memories. Each namespace maps to an independent memory store on the server.

**How to set a namespace:**

- **REST API**: Set the `X-Memory-Namespace` HTTP header on every request.
- **MCP tools**: Pass `namespace` in the tool arguments.
- **UI**: Use the namespace switcher in the top navigation bar.

If no namespace is provided, the server falls back to the `DEFAULT_MEMORY_NAMESPACE` value (default: `local`).

**Rules:**
- Namespaces are case-insensitive and normalized to lowercase.
- Maximum length: 64 characters.
- On first use, a namespace is automatically created.

See [docs/getting-started/02-configuration.md](docs/getting-started/02-configuration.md) for configuration details.

## Screenshots

### Dashboard
![Dashboard](docs/assets/dashboard.PNG)

### Memory Management
![Memory Management](docs/assets/memory.PNG)

## Architecture

```
┌─────────────────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ Unified FastAPI + React SPA │────▶│  PostgreSQL   │────▶│ LM Studio (LAN host)│
│         (Port 8000)         │     │ + pgvector   │     │ OpenAI-compatible    │
└─────────────────────────────┘     │ + pg_cache   │     │ /chat + /embeddings  │
                                    └──────────────┘     └─────────────────────┘
```

### Backend Services

| Service | Purpose |
| --- | --- |
| `MemoryService` | Orchestrates save (with auto-classification), search (with RLM), list, delete |
| `EmbeddingService` | Generates embeddings, returns `EmbeddingResult` with fallback transparency |
| `LLMService` | Chat completions, `classify_memory()` for auto type/tag classification |
| `RLMService` | Query decomposition and re-ranking for intelligent search |
| `PgCacheService` | PostgreSQL-based search result caching with TTL |
| `UserService` | Namespace normalization and user resolution |

### API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/memory/search` | Semantic search with optional RLM |
| `POST` | `/api/v1/memory/save` | Save with auto-classification |
| `GET` | `/api/v1/memory/list` | List memories (paginated) |
| `DELETE` | `/api/v1/memory/{id}` | Delete memory |
| `GET` | `/api/v1/memory/stats` | Namespace statistics |
| `GET` | `/api/v1/memory/namespaces` | List all namespaces |
| `POST` | `/mcp` | MCP JSON-RPC endpoint |
| `GET` | `/health/config` | LLM and embedding model configuration |
| `GET` | `/docs` | Swagger UI (interactive API documentation) |

### Frontend Pages

| Page | Description |
| --- | --- |
| **Dashboard** | Stats overview (memories, storage, cache hits, entries today), LLM model info card, embedding model info card, namespace status with recent memories |
| **Memory** | Search bar, paginated memory list (5/10/50 per page), add memory sidebar, delete with confirmation |

### MCP Tools

| Tool | Description |
| --- | --- |
| `save_memory` | Save a memory. Server auto-classifies type and tags — just provide `content`. |
| `search_memory` | Semantic search with optional RLM re-ranking |
| `list_memory` | List/filter memories |
| `delete_memory` | Delete by ID |

## Configuration

Key environment variables (see [docs/reference/environment-variables.md](docs/reference/environment-variables.md) for full list):

```env
# Required
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/rlm_memory
OPENAI_BASE_URL=http://<your-lm-studio-host>:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=mistralai/ministral-3-14b-reasoning
EMBEDDING_MODEL=text-embedding-qwen3-embedding-4b@q4_k_m
EMBEDDING_DIMENSIONS=1536

# Optional — separate embedding provider (falls back to OPENAI_* if unset)
EMBED_OPENAI_BASE_URL=
EMBED_OPENAI_API_KEY=

# Behavior
ALLOW_EMBEDDING_FALLBACK=true    # Zero-vector fallback when embedding provider is down
DEFAULT_MEMORY_NAMESPACE=local   # Default namespace when header is missing
SEARCH_CACHE_TTL_SECONDS=300     # Search result cache TTL
```

## Development

### Run Tests

```bash
# Backend
cd backend
python -m pytest tests/unit/ -v

# Frontend
cd frontend
npm run typecheck
npm run lint
```

### Code Quality

```bash
# Backend
cd backend
ruff check .

# Frontend
cd frontend
npm run lint
```

For complete development guidelines, see [AGENTS.md](AGENTS.md).

## Documentation

Full documentation is available in the [docs](docs/) directory:

- [Getting Started](docs/getting-started/) — Installation, configuration, local development
- [Guides](docs/guides/) — MCP Inspector testing, running tests, monitoring, deployment
- [Concepts](docs/concepts/) — Architecture overview, security model
- [Reference](docs/reference/) — API endpoints, data model, environment variables, Docker, dependencies

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Security

For security vulnerability reporting, please see [SECURITY.md](SECURITY.md).

**Do not** report security vulnerabilities via public GitHub issues.

## License

This project is dual-licensed:

- **Open Source**: [GNU AGPLv3](LICENSE) — free for open-source use
- **Commercial**: See [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) for proprietary/commercial use

Contact: contact@tykotech.eu

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [React](https://react.dev/) — UI framework
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector) — Vector database
- [LM Studio](https://lmstudio.ai/) — OpenAI-compatible local model serving
- [MCP](https://modelcontextprotocol.io/) — Model Context Protocol

---

Created by TykoTech
