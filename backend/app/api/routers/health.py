"""Health check endpoints for database and cache."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import engine, get_db
from app.services.pg_cache_service import pg_cache_service

router = APIRouter()


@router.get("")
async def health_check():
    return {"status": "ok"}


@router.get("/")
async def health_check_slash():
    return {"status": "ok"}


@router.get("/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    result = {
        "status": "ok",
        "postgres": {"status": "unknown"},
        "pg_cache": {"status": "unknown"},
    }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        result["postgres"] = {"status": "connected", "latency_ms": 0}
    except Exception as exc:
        result["postgres"] = {"status": "error", "error": str(exc)}
        result["status"] = "degraded"

    try:
        stats = await pg_cache_service.stats(db)
        result["pg_cache"] = {"status": "connected", **stats}
    except Exception as exc:
        result["pg_cache"] = {"status": "error", "error": str(exc)}
        result["status"] = "degraded"

    return result


@router.get("/postgres")
async def postgres_health():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
        return {"status": "connected", "version": version}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.get("/cache")
async def cache_health(db: AsyncSession = Depends(get_db)):
    try:
        stats = await pg_cache_service.stats(db)
        return {"status": "connected", **stats}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.get("/config")
async def get_config():
    return {
        "llm": {
            "model": settings.OPENAI_MODEL,
            "base_url": settings.OPENAI_BASE_URL,
        },
        "embedding": {
            "model": settings.EMBEDDING_MODEL,
            "base_url": settings.embedding_openai_base_url,
            "dimensions": settings.EMBEDDING_DIMENSIONS,
        },
    }
