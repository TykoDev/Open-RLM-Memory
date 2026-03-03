from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy import text

# Import models to ensure they are registered with Base.metadata
import app.models  # noqa
from app.api.routers import health, memory, metrics
from app.api.routers import mcp as mcp_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.database.connection import engine
from app.models.base import Base

# Setup logging
setup_logging()


async def _initialize_database() -> None:
    logger.info("Starting up Open RLM Memory Server...")
    try:
        async with engine.begin() as conn:
            if engine.url.get_backend_name().startswith("postgresql"):
                logger.info(f"Initializing Postgres connection to {settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}")
                # Create pgvector extension (required for vector similarity search)
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_prewarm"))
                except Exception as exc:
                    logger.warning(f"pg_prewarm extension unavailable: {exc}")
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_buffercache"))
                except Exception as exc:
                    logger.warning(f"pg_buffercache extension unavailable: {exc}")

            logger.info("Creating database tables...")
            # Create all tables for both SQLite and Postgres
            await conn.run_sync(Base.metadata.create_all)

            if engine.url.get_backend_name().startswith("postgresql"):
                await conn.execute(text("ALTER TABLE pg_cache ADD COLUMN IF NOT EXISTS hit_count INTEGER DEFAULT 0"))
                await conn.execute(
                    text("ALTER TABLE pg_cache ADD COLUMN IF NOT EXISTS last_hit_at TIMESTAMP WITHOUT TIME ZONE")
                )
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_pg_cache_last_hit_at ON pg_cache (last_hit_at)"))

            # Verify table creation
            def check_tables(connection):
                from sqlalchemy import inspect

                inspector = inspect(connection)
                return inspector.get_table_names()

            tables = await conn.run_sync(check_tables)
            logger.info(f"Existing tables in DB: {tables}")

            if "memory" not in tables:
                logger.error("CRITICAL: 'memory' table was NOT created! Check database permissions and models.")
            else:
                logger.info("Table 'memory' verified successfully.")

    except Exception as exc:
        logger.error(f"Database initialization failed: {exc}")
        # Build failures should catch this, but in dev we might want to see the error
        raise


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await _initialize_database()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Open RLM Memory - Long-term memory for AI agents",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - allow MCP Inspector and other clients
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:6274",  # MCP Inspector UI
    "http://localhost:6277",  # MCP Inspector proxy
    "*",  # Intentional wildcard: local-only server with no auth; restrict if exposing publicly
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(mcp_router.well_known_router)
app.include_router(mcp_router.router)  # MCP endpoints at /mcp

FRONTEND_DIST = Path(__file__).resolve().parent / "static"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"


@app.get("/", tags=["Root"])
async def root():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    return {
        "message": "Open RLM Memory Server Running",
        "version": settings.VERSION,
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    if not FRONTEND_INDEX.exists():
        raise HTTPException(status_code=404, detail="Not found")

    blocked_prefixes = (
        "api/",
        "health",
        "metrics",
        "mcp",
        "docs",
        "redoc",
        ".well-known",
    )
    if any(full_path.startswith(prefix) for prefix in blocked_prefixes):
        raise HTTPException(status_code=404, detail="Not found")

    requested_path = FRONTEND_DIST / full_path
    if requested_path.is_file():
        return FileResponse(requested_path)

    return FileResponse(FRONTEND_INDEX)
