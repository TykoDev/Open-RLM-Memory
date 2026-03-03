# Quick Start — Local Deploy with Docker + LM Studio

Get Open RLM Memory running locally in under 15 minutes using Docker Desktop and LM Studio.

---

## Prerequisites

| Tool | Purpose |
| --- | --- |
| **Docker Desktop** | Runs the app + PostgreSQL containers |
| **LM Studio** | Hosts the LLM and embedding models locally |
| **Git** | Clone the repository |

---

## Step 1 — Install Docker Desktop

1. Download Docker Desktop from <https://www.docker.com/products/docker-desktop/>.
2. Run the installer and follow the prompts.
   - On Windows, enable **WSL 2 backend** when asked (recommended).
   - On macOS, choose the correct chip (Apple Silicon / Intel).
3. Launch Docker Desktop and wait until the engine status shows **Running** (green icon in the system tray / menu bar).
4. Verify in a terminal:

```bash
docker --version
docker compose version
```

Both commands should print version numbers without errors.

---

## Step 2 — Install & Configure LM Studio

### 2a — Install LM Studio

1. Download LM Studio from <https://lmstudio.ai/>.
2. Run the installer for your OS.
3. Launch LM Studio.

### 2b — Download the Required Models

You need **two** models — one for chat/reasoning and one for embeddings.

Open the **Discover** tab (magnifying glass icon) in LM Studio and search for, then download:

| Model | Search Term | Purpose |
| --- | --- | --- |
| **Ministral 8B Instruct** | `ministral-8b-instruct` | Chat, classification & re-ranking |
| **Qwen3 Embedding** | `text-embedding-qwen3` | Vector embeddings for semantic search |

> **Tip:** Pick a quantization that fits your GPU VRAM. **Q4_K_M** is a good balance of quality and size for most setups.

### 2c — Load the Models

1. Go to the **My Models** tab (sidebar), find **Ministral 8B Instruct**, and click **Load**.
2. After it finishes loading, also load **Qwen3 Embedding** — LM Studio supports multiple models simultaneously.

### 2d — Start the Local Server

1. Go to the **Developer** tab (code brackets icon `<>` in the left sidebar).
2. Make sure both loaded models appear in the model list.
3. Toggle the server **ON**. By default it starts on port **1234**.
4. Note the **Status** area — it should show the server listening at `http://localhost:1234`.

### 2e — Enable Network Access (if Docker runs in WSL / VM)

By default LM Studio only listens on `localhost`. Docker containers need to reach it via the host network.

1. In the **Developer** tab, click the **Settings** gear icon.
2. Enable **"Serve on Local Network"** (or set the bind address to `0.0.0.0`).
3. Restart the server if prompted.

> **Finding your LAN IP:**
> - **Windows:** run `ipconfig` and look for your Wi-Fi or Ethernet adapter's **IPv4 Address** (e.g. `192.168.1.42`).
> - **macOS/Linux:** run `ifconfig` or `ip addr`.
>
> On Windows with Docker Desktop (WSL 2 backend) you can also use the special hostname `host.docker.internal` instead of your LAN IP.

---

## Step 3 — Clone the Repository

```bash
git clone https://github.com/TykoDev/open-rlm-memory.git
cd open-rlm-memory
```

---

## Step 4 — Create the `.env` File

Copy the example and edit it:

```bash
cp .env.example .env
```

Open `.env` in any text editor and set the **`OPENAI_BASE_URL`** to point at your LM Studio server. Replace `<your-lm-studio-host>` with the correct address:

```dotenv
# === The only line you MUST change ===
OPENAI_BASE_URL=http://host.docker.internal:1234/v1
```

> **Which host value to use?**
>
> | Scenario | Value |
> | --- | --- |
> | Docker Desktop on Windows (WSL 2) | `host.docker.internal` |
> | Docker Desktop on macOS | `host.docker.internal` |
> | Docker on native Linux | Your machine's LAN IP (e.g. `192.168.1.42`) |
> | LM Studio on a different machine | That machine's LAN IP |

Update the model names to match exactly what you downloaded in LM Studio. Open the **Developer** tab in LM Studio and look at the loaded model identifiers, then set:

```dotenv
OPENAI_MODEL=<chat-model-id-from-lm-studio>
EMBEDDING_MODEL=<embedding-model-id-from-lm-studio>
```

For example, if you downloaded the recommended models:

```dotenv
OPENAI_MODEL=ministral-8b-instruct-2410
EMBEDDING_MODEL=text-embedding-qwen3-embedding-4b@q4_k_m
```

> **Tip:** The exact model ID string is shown in LM Studio's Developer tab server logs or in the model selector dropdown. Copy it verbatim.

Leave all other values at their defaults — they work out of the box.

<details>
<summary>Full <code>.env</code> reference (click to expand)</summary>

```dotenv
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=rlm_memory
POSTGRES_SERVER=postgres
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/rlm_memory

# Cache & Namespace
SEARCH_CACHE_TTL_SECONDS=300
DEFAULT_MEMORY_NAMESPACE=local
MAX_NAMESPACE_LENGTH=64

# LM Studio
OPENAI_BASE_URL=http://host.docker.internal:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=ministral-8b-instruct-2410
EMBEDDING_MODEL=text-embedding-qwen3-embedding-4b@q4_k_m
EMBEDDING_DIMENSIONS=1536

# Logging
LOG_LEVEL=INFO
```

</details>

---

## Step 5 — Start the Stack

Make sure Docker Desktop is running, then from the project root:

```bash
docker compose up -d
```

The first run builds the image (takes a few minutes). Watch the logs:

```bash
docker compose logs -f app
```

Wait until you see a line like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 6 — Verify Everything Works

### 6a — Web UI

Open your browser and go to:

```
http://localhost:8000
```

You should see the Open RLM Memory dashboard.

### 6b — Health Check

```bash
curl http://localhost:8000/health
```

Expected response: `{"status":"ok"}`

### 6c — Config Check

```bash
curl http://localhost:8000/health/config
```

This shows the active LLM and embedding model configuration. Confirm the model names match what you loaded in LM Studio.

### 6d — Save Your First Memory

```bash
curl -X POST http://localhost:8000/api/v1/memory/save \
  -H "Content-Type: application/json" \
  -H "X-Memory-Namespace: local" \
  -d '{"content": "Open RLM Memory is up and running!"}'
```

A successful response returns the saved memory with `classified_by_llm: true` and `embedding_generated: true`.

### 6e — Search It Back

```bash
curl -X POST http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -H "X-Memory-Namespace: local" \
  -d '{"query": "What is running?", "top_k": 5}'
```

You should get back your saved memory as a search result.

---

## Stopping & Restarting

```bash
# Stop everything (data is preserved in the Docker volume)
docker compose down

# Start again
docker compose up -d

# Full reset — removes database volume (deletes all memories)
docker compose down -v
```

---

## Troubleshooting

| Problem | Solution |
| --- | --- |
| **App can't connect to LM Studio** | Make sure LM Studio's server is ON, "Serve on Local Network" is enabled, and `OPENAI_BASE_URL` in `.env` uses the correct host. Test with `curl http://<host>:1234/v1/models` from inside the container. |
| **`docker compose up` fails to build** | Ensure Docker Desktop is running and has enough resources (at least 4 GB RAM allocated). |
| **Embedding returns zero-vector fallback** | The embedding model isn't loaded in LM Studio. Load it and verify it appears in the Developer tab. |
| **Models not found (404)** | The model ID in `.env` doesn't match LM Studio's model ID. Copy the exact string from LM Studio's Developer tab. |
| **Port 8000 already in use** | Stop the conflicting process or change `SERVER_PORT` in `.env` and the port mapping in `docker-compose.yml`. |
| **WSL 2: `host.docker.internal` not resolving** | Update Docker Desktop to the latest version. As a workaround, use your LAN IP instead. |

---

## Step 7 — Connect AI Agents via MCP

Open RLM Memory exposes a **Model Context Protocol (MCP)** endpoint using Streamable HTTP transport. This lets AI agents (Claude, Cursor, Windsurf, custom agents, etc.) use your memory server as a tool provider — no auth required.

**Endpoint:** `http://localhost:8000/mcp`
**Transport:** Streamable HTTP
**Auth:** None

### Available MCP Tools

| Tool | Description |
| --- | --- |
| `search_memory` | Semantic similarity search with optional RLM re-ranking |
| `save_memory` | Save a memory (auto-classifies type & tags via LLM) |
| `list_memory` | List/filter memories with pagination |
| `delete_memory` | Delete a memory by ID |

### 7a — Claude Desktop

Add to your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "open-rlm-memory": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Restart Claude Desktop. The memory tools will appear in the tool list (hammer icon).

### 7b — Claude Code (CLI)

Add the server using the CLI:

```bash
claude mcp add open-rlm-memory --transport http http://localhost:8000/mcp
```

Or add it manually to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "open-rlm-memory": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 7c — Cursor

Open Cursor Settings (`Ctrl+Shift+J` / `Cmd+Shift+J`) → **MCP** → **+ Add new MCP server**, then:

- **Name:** `open-rlm-memory`
- **Type:** `StreamableHTTP`
- **URL:** `http://localhost:8000/mcp`

Or add it directly to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "open-rlm-memory": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 7d — Windsurf

Add to your Windsurf MCP config at `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "open-rlm-memory": {
      "type": "streamableHttp",
      "serverUrl": "http://localhost:8000/mcp"
    }
  }
}
```

### 7e — Any MCP-Compatible Client

Use these connection details for any client that supports MCP Streamable HTTP:

| Setting | Value |
| --- | --- |
| **URL** | `http://localhost:8000/mcp` |
| **Transport** | Streamable HTTP |
| **Auth** | None |

The server responds to standard MCP JSON-RPC methods: `initialize`, `tools/list`, and `tools/call`.

### 7f — Namespaces in MCP

Namespaces isolate memories so different projects don't mix. You can scope every MCP tool call by including `"namespace": "my-project"` in the tool arguments. If omitted, the server uses the default namespace (`local`).

### 7g — Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Set transport to **Streamable HTTP** and URL to `http://localhost:8000/mcp`. Click **Initialize**, then **List Tools** to see all 4 tools. Try saving and searching a memory to confirm the full round-trip.

### 7h — Verify MCP Endpoint

```bash
curl http://localhost:8000/mcp/info
```

Expected response:

```json
{
  "endpoint": "/mcp",
  "transport": "streamable-http",
  "tools": ["search_memory", "list_memory", "save_memory", "delete_memory"],
  "protocol_version": "2024-11-05",
  "server_name": "Open RLM Memory",
  "auth_required": false
}
```

---

## Stopping & Restarting

```bash
# Stop everything (data is preserved in the Docker volume)
docker compose down

# Start again
docker compose up -d

# Full reset — removes database volume (deletes all memories)
docker compose down -v
```

---

## Troubleshooting

| Problem | Solution |
| --- | --- |
| **App can't connect to LM Studio** | Make sure LM Studio's server is ON, "Serve on Local Network" is enabled, and `OPENAI_BASE_URL` in `.env` uses the correct host. Test with `curl http://<host>:1234/v1/models` from inside the container. |
| **`docker compose up` fails to build** | Ensure Docker Desktop is running and has enough resources (at least 4 GB RAM allocated). |
| **Embedding returns zero-vector fallback** | The embedding model isn't loaded in LM Studio. Load it and verify it appears in the Developer tab. |
| **Models not found (404)** | The model ID in `.env` doesn't match LM Studio's model ID. Copy the exact string from LM Studio's Developer tab. |
| **Port 8000 already in use** | Stop the conflicting process or change `SERVER_PORT` in `.env` and the port mapping in `docker-compose.yml`. |
| **WSL 2: `host.docker.internal` not resolving** | Update Docker Desktop to the latest version. As a workaround, use your LAN IP instead. |
| **MCP tools not showing in Claude/Cursor** | Restart the client after editing the config. Check `http://localhost:8000/mcp/info` returns a valid response. |
| **MCP "namespace not found" errors** | Include `"namespace": "local"` in your tool arguments, or set the `X-Memory-Namespace` header. |

---

## What's Next

- **API Docs** — interactive OpenAPI explorer at `http://localhost:8000/docs`
- **MCP Inspector Guide** — see [docs/guides/mcp-inspector-testing.md](docs/guides/mcp-inspector-testing.md)
- **Configuration Reference** — see [docs/getting-started/02-configuration.md](docs/getting-started/02-configuration.md)
- **Architecture** — see [docs/concepts/architectural-overview.md](docs/concepts/architectural-overview.md)
