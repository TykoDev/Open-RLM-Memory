# Commands, Scripts & Tests Reference

Complete reference of all available commands, scripts, and tests implemented in the project.

## Backend Commands

| Command | Description | Usage Example |
| --- | --- | --- |
| Start server | Starts the development server with hot reload | `uvicorn app.main:app --reload` |
| Run all tests | Executes the complete test suite | `pytest` |
| Run specific test file | Executes tests in a single file | `pytest tests/unit/test_memory_service.py` |
| Run specific test | Executes a single test by name | `pytest tests/unit/test_memory_service.py::test_name` |
| Run with coverage | Generates code coverage report | `pytest --cov=app tests/` |
| Verbose output | Shows detailed test output | `pytest -v` |
| Run linting | Checks code style using Ruff | `ruff check .` |
| Fix linting | Auto-fixes linting issues | `ruff check --fix .` |
| Run migrations | Applies pending database migrations | `alembic upgrade head` |
| Generate migration | Creates new migration file | `alembic revision --autogenerate -m "message"` |
| Rollback migration | Reverts last migration | `alembic downgrade -1` |

## Frontend Commands

| Command | Description | Usage Example |
| --- | --- | --- |
| Start dev server | Starts Vite development server with HMR | `npm run dev` |
| Build production | Creates optimized production build | `npm run build` |
| Preview build | Locally previews production build | `npm run preview` |
| Run all tests | Executes complete test suite | `npm run test` |
| Run in watch mode | Runs tests in watch mode | `npm run test -- --watch` |
| Run in UI mode | Opens Vitest UI | `npm run test -- --ui` |
| Run linting | Checks code style using ESLint | `npm run lint` |
| Type check | Runs TypeScript compiler | `npm run typecheck` |

## Docker Commands

| Command | Description | Usage Example |
| --- | --- | --- |
| Start all services | Starts all containers in detached mode | `docker-compose up -d` |
| Build and start | Builds images and starts services | `docker-compose up -d --build` |
| View all logs | Shows logs from all services | `docker-compose logs -f` |
| View specific logs | Shows logs for a single service | `docker-compose logs -f backend` |
| Stop services | Stops all running containers | `docker-compose down` |
| Remove volumes | Deletes all named volumes | `docker-compose down -v` |
| Restart services | Restarts all containers | `docker-compose restart` |
| Execute command in container | Runs command inside a container | `docker-compose exec backend pytest` |

## Utility Scripts

No utility shell scripts are included. Use the backend and frontend commands above directly.

## Testing Reference

### Backend Testing

#### Unit Tests

Run isolated unit tests that mock external dependencies:

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html
```

#### Integration Tests

Run tests that use real database connections:

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_memory_integration.py
```

#### End-to-End Tests

Run complete API workflow tests:

```bash
# Run all E2E tests
pytest tests/e2e/

# Run specific E2E test
pytest tests/e2e/test_api_flow.py
```

### Frontend Testing

#### Component Tests

Run tests for individual React components:

```bash
# Run all component tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run in UI mode
npm run test -- --ui
```

#### Coverage Reports

Generate coverage reports for frontend:

```bash
npm run test -- --coverage

# View coverage report
open coverage/index.html
```

## Pre-Commit Hooks

Run before committing changes:

```bash
# Backend
cd backend
ruff check .
pytest

# Frontend
cd frontend
npm run lint
npm run typecheck
npm run test
```

## CI/CD Commands

GitHub Actions automatically run:

```bash
# On push/PR
npm run lint
npm run typecheck
npm run test
ruff check .
pytest
```

## Next Steps

- [Environment Variables Reference](./environment-variables.md) - Complete .env reference
- [Dependencies Reference](./dependencies.md) - Package dependencies
- [API Endpoints](./api-endpoints.md) - Complete API documentation
