"""Metrics endpoints for system monitoring."""

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.memory import Memory
from app.services.pg_cache_service import pg_cache_service

router = APIRouter()


@router.get(
    "",
    summary="System Metrics",
    description="Get memory service metrics.",
)
async def metrics(db: AsyncSession = Depends(get_db)):
    """Get system metrics."""
    # Total memories
    total_result = await db.execute(select(func.count(Memory.id)))
    total_memories = total_result.scalar()

    # Distribution by type
    type_result = await db.execute(select(Memory.type, func.count(Memory.id)).group_by(Memory.type))
    type_dist = {r[0]: r[1] for r in type_result.all()}

    return {"total_memories": total_memories, "type_distribution": type_dist, "system_status": "operational"}


@router.get(
    "/prometheus",
    summary="Prometheus Metrics",
    description="Prometheus-compatible metrics endpoint.",
)
async def prometheus_metrics(db: AsyncSession = Depends(get_db)):
    """Get Prometheus-formatted metrics."""
    total_result = await db.execute(select(func.count(Memory.id)))
    total_memories = total_result.scalar() or 0

    # Prometheus text format
    metrics_text = f"""# HELP rlm_memories_total Total number of memories stored
# TYPE rlm_memories_total gauge
rlm_memories_total {total_memories}

# HELP rlm_server_up Server status
# TYPE rlm_server_up gauge
rlm_server_up 1
"""
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(content=metrics_text, media_type="text/plain")


@router.get(
    "/sysinfo",
    summary="System Information",
    description="Get system resource usage by service (Backend, Postgres, pg_cache).",
)
async def sysinfo(db: AsyncSession = Depends(get_db)):
    """Get system information: storage, CPU, memory by service."""

    # Get host system info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net_io = psutil.net_io_counters()

    services = {
        "backend": {
            "cpu_percent": cpu_percent,
            "memory_used_mb": round(memory.used / (1024 * 1024), 2),
            "memory_total_mb": round(memory.total / (1024 * 1024), 2),
            "memory_percent": memory.percent,
        },
        "postgres": {
            "status": "unknown",
            "storage_used_mb": 0,
        },
        "pg_cache": {
            "status": "unknown",
            "active_entries": 0,
        },
    }

    # Check Postgres
    try:
        result = await db.execute(text("SELECT pg_database_size(current_database())"))
        db_size = result.scalar()
        if db_size:
            services["postgres"]["storage_used_mb"] = round(db_size / (1024 * 1024), 2)
            services["postgres"]["status"] = "connected"
    except Exception as e:
        services["postgres"]["status"] = f"error: {str(e)}"

    # Check application cache in PostgreSQL
    try:
        info = await pg_cache_service.stats(db)
        services["pg_cache"]["active_entries"] = info.get("active_entries", 0)
        services["pg_cache"]["status"] = "connected"
    except Exception as e:
        services["pg_cache"]["status"] = f"error: {str(e)}"

    # Network I/O (last 24h approximation - uses cumulative counters)
    network = {
        "bytes_sent_total_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
        "bytes_recv_total_mb": round(net_io.bytes_recv / (1024 * 1024), 2),
        "note": "Cumulative since system boot",
    }

    return {
        "services": services,
        "disk": {
            "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
            "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
            "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
            "percent": disk.percent,
        },
        "network": network,
    }
