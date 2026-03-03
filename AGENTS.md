# AGENTS.md - Working Rules for This Repository
# Scope: entire repo. Keep this file around 150 lines and update when tools/rules change.

## 1) Mission and Operating Mode
- Act as a senior engineer: concise, security-first, and production-focused.
- Make minimal, targeted diffs; avoid unrelated cleanup or renames.
- Preserve existing architecture and conventions unless a task explicitly changes them.
- Prefer deterministic behavior, clear errors, and test-backed changes.

## 2) Rule Sources (Cursor/Copilot)
- Checked for `.cursor/rules/`, `.cursorrules`, and `.github/copilot-instructions.md`.
- No Cursor or Copilot rule files are present in this repository at this time.
- If such files are added later, treat them as additional mandatory instructions and merge guidance here.

## 3) Repository Map
- Backend: `backend/app` (FastAPI, SQLAlchemy, PostgreSQL/pgvector, Loguru).
- Backend routers: `backend/app/api/routers`.
- MCP HTTP router: `backend/app/api/routers/mcp.py` (streamable HTTP at `/mcp`).
- Backend services: `backend/app/services`; models: `backend/app/models`.
- Frontend: `frontend/src` (React 18, TypeScript, Vite, Tailwind).
- Frontend state stores: `frontend/src/store` (`memoryStore`).
- Frontend API wrapper: `frontend/src/services/api.ts`.
- Backend tests: `backend/tests`; frontend unit tests: `frontend/src/**/__tests__` and `*.test.tsx`.
- Frontend E2E tests: `frontend/tests/e2e`.
- Root infra: `docker-compose.yml`, `.env.example`.

## 4) Build, Lint, and Test Commands
### Backend (run in `backend/`, Python 3.11)
- Install: `pip install -r requirements.txt`
- Run dev server: `uvicorn app.main:app --host ${SERVER_HOST:-0.0.0.0} --port ${SERVER_PORT:-8000} --reload`
- Lint: `ruff check .`
- Run all tests: `pytest`
- Single test file: `pytest tests/unit/test_memory_service.py`
- Single test function: `pytest tests/unit/test_memory_service.py::test_search_memory_with_rlm`
- Pattern match single test: `pytest tests -k "search_memory_with_rlm"`

### Frontend (run in `frontend/`, Node >= 24, npm >= 11)
- Install: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`
- Typecheck: `npm run typecheck`
- Unit test suite: `npm run test`

### E2E (run in `frontend/`)
- E2E suite: `npx playwright test`
- Single spec: `npx playwright test tests/e2e/ui-verification.spec.ts`
- Single test title: `npx playwright test -g "Root Dashboard loads correctly"`

### Docker
- Start full stack: `docker-compose up -d`
- Rebuild one service: `docker-compose up -d --build app`

## 5) Environment and Config Rules
- Source of truth for env vars: `.env.example` and `backend/app/core/config.py`.
- Backend host/port defaults: `SERVER_HOST=0.0.0.0`, `SERVER_PORT=8000`.
- Namespace identity is provided by `X-Memory-Namespace` and defaults to `DEFAULT_MEMORY_NAMESPACE`.
- Frontend API base is `VITE_API_URL` (optional; same-origin by default in unified container).
- When adding an env var, update both `.env.example` and backend `Settings`.

## 6) General Coding Standards
- Keep edits narrow and task-scoped; do not refactor broadly unless requested.
- Prefer explicit types in both Python and TypeScript.
- Avoid `any` in TS and untyped function params in Python.
- Keep comments minimal; only explain non-obvious logic.
- Do not add new formatting tools; use existing project tooling only.

## 7) Backend Python Standards
- Formatter/lint rules come from `backend/pyproject.toml` (`ruff`, line length 120, rules E/F/I).
- Import order: stdlib, third-party, then `app.*`; remove duplicates and unused imports.
- Use async I/O for DB/network paths; avoid blocking code in request handlers.
- Use dependencies (`Depends(get_db)`, `AsyncSessionLocal`) rather than ad-hoc sessions.
- Avoid mutable default args; copy incoming lists/dicts before mutation.
- API errors should use `HTTPException(status_code=..., detail=...)` with sanitized details.
- Do not expose raw exceptions or stack traces in responses.
- Log with `loguru`; never log secrets, tokens, or sensitive payloads.
- Respect UUID handling differences between SQLite and Postgres.

## 8) Frontend TypeScript/React Standards
- TypeScript is strict; keep code compatible with `tsconfig.json` strict settings.
- Prefer typed props, typed API responses, and narrow unions over casts.
- Import style: React/libs first, then local modules; prefer `@/` alias when practical.
- Use functional components and keep state minimal and local unless shared.
- Shared state should go through Zustand stores in `frontend/src/store`.
- API calls should use `frontend/src/services/api.ts` (axios instance + interceptors).
- Handle 401/403 flows gracefully in UI; avoid noisy console logging.
- Tailwind-first styling; avoid unnecessary inline styles.

## 9) Naming and Layout Conventions
- Python names: `snake_case`; TypeScript variables/functions: `camelCase`.
- React components/types: `PascalCase`; constants: `UPPER_SNAKE_CASE` when global.
- Keep backend logic in `services/*`, transport in `api/routers/*`, data models in `models/*`.
- Keep frontend pages in `src/pages`, shared UI in `src/components`, services in `src/services`.

## 10) Testing Guidance
- Prefer deterministic tests with minimal fixtures and explicit setup.
- Backend: use `pytest` + `pytest-asyncio`; mock external APIs/services.
- Frontend: use Testing Library queries by role/text; avoid brittle selectors.
- E2E: keep tests idempotent and use `-g` for focused iteration.
- For every behavior change, add/update at least one focused unit test where feasible.

## 11) Security and Identity Requirements
- This local build does not use OAuth/JWT/Auth0; do not reintroduce hosted auth flows unless explicitly requested.
- Namespace isolation must remain strict: all memory operations must be scoped server-side by normalized namespace.
- Never store or print credentials/tokens in client logs or API responses.
- Validate user-scoped operations server-side; do not trust client-supplied identity beyond namespace normalization.

## 12) Performance and Reliability
- Avoid N+1 query patterns; prefer batched/focused queries.
- Reuse DB sessions through dependencies and commit only when needed.
- Prefer pagination/incremental fetch for large memory lists.
- Watch frontend bundle size and avoid unnecessary re-renders.

## 13) Documentation Expectations
- Keep docs concise, actionable, and command-oriented.
- Update docs when changing commands, env vars, auth flows, or endpoints.
- If LAN behavior changes, document host/firewall implications for port `8000`.

## 14) Working Agreements for Agents
- Do not create commits unless explicitly requested.
- Prefer `npm` over yarn/pnpm.
- Use existing lint/type/test commands; do not introduce new tooling.
- Do not run destructive git commands unless explicitly requested.

## 15) Handy One-Liners
- Backend single test: `pytest tests/unit/test_memory_service.py::test_search_memory_with_rlm` (workdir `backend`)
- Backend grep-run: `pytest tests -k "memory and not integration"` (workdir `backend`)
- E2E single test: `npx playwright test -g "Root Dashboard loads correctly"` (workdir `frontend`)
- Ruff auto-fix (only when requested): `ruff check . --fix` (workdir `backend`)

## 16) Key Endpoints
- API base: `/api/v1`
- MCP endpoints: `/mcp`, `/mcp/info`, `/.well-known/oauth-protected-resource`, `/.well-known/oauth-protected-resource/mcp`
- Health: `/health`
- Metrics: `/metrics`
- API docs: `/docs`

## 17) Delivery Checklist
- Run the smallest relevant lint/type/test command set for changed files.
- Prefer single-test commands first, then broader suites only when needed.
- Ensure user-scoped operations are validated server-side before returning data.
- Confirm no secrets or tokens are introduced in logs, errors, or fixtures.
- Update docs/config samples when behavior, env vars, or commands change.
- Keep diffs reviewable: avoid broad refactors unless explicitly requested.

Keep changes incremental, secure, and easy to review.
