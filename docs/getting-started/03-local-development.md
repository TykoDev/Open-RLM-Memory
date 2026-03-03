# Local Development

## Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

When running separately, set `VITE_API_URL=http://localhost:8000` in frontend env.

## Useful Checks

```bash
# backend
cd backend
ruff check .
pytest

# frontend
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Namespace Testing

Use different `X-Memory-Namespace` values to verify isolation between users/apps.
