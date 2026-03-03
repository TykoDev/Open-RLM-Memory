# Installation

## Prerequisites

- Docker Desktop / Docker Engine + Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 24+ and npm 11+ (for local frontend development)
- PostgreSQL access (Compose provides this by default)
- LM Studio or another OpenAI-compatible endpoint

## Clone and Configure

```bash
git clone https://github.com/TykoDev/open-rlm-memory.git
cd open-rlm-memory
cp .env.example .env
```

Set `OPENAI_BASE_URL` in `.env` to your model server (for example `http://<your-lm-studio-host>:1234/v1`).

## Start with Docker Compose

```bash
docker-compose up -d
```

Services started:

- `postgres` on `5432`
- `app` (FastAPI + React static assets) on `8000`

## Verify

- App: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- MCP info: `http://localhost:8000/mcp/info`
