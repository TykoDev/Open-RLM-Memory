# Running Tests

## Backend

```bash
cd backend
python -m pytest
```

Targeted unit runs:

```bash
python -m pytest tests/unit/test_memory_service.py
python -m pytest tests/unit/test_mcp_metadata.py
```

Lint:

```bash
cd backend
ruff check .
```

## Frontend

```bash
cd frontend
npm run test
npm run typecheck
npm run lint
npm run build
```

## Notes

- Prefer focused test files first, then full suites.
- Mock external model calls in unit tests where possible.
- Namespace behavior should be explicitly tested with different `X-Memory-Namespace` values.
