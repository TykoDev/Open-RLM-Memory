from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.identity import get_memory_namespace
from app.database.connection import get_db
from app.database.queries.memory import get_distinct_types
from app.models.memory import Memory
from app.models.user import User
from app.services.memory_service import MemoryNotFoundError, MemoryService
from app.services.pg_cache_service import pg_cache_service
from app.services.rlm_service import rlm_service
from app.services.user_service import get_or_create_user_by_namespace

router = APIRouter(prefix="/memory", tags=["memory"])


async def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(db, rlm=rlm_service)


async def get_user_context(
    namespace: str = Depends(get_memory_namespace),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    user = await get_or_create_user_by_namespace(db, namespace)
    return {"namespace": namespace, "user_id": str(user.id)}


class MemoryFilter(BaseModel):
    created_after: str | None = None
    tags: list[str] | None = None
    type: str | None = Field(None, alias="memory_type")


class SearchMemoryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=1000)
    filters: MemoryFilter | None = None
    enable_rlm: bool = True
    session_id: str | None = None


class RLMMetrics(BaseModel):
    steps: int
    sub_queries: int
    used_cache: bool


class MemoryResult(BaseModel):
    id: str
    content: str
    score: float = 0.0
    type: str
    tags: list[str]
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class SearchMemoryResponse(BaseModel):
    namespace: str
    results: list[MemoryResult]
    total_results: int
    processing_time_ms: float
    rlm_decomposition: RLMMetrics


class ListMemoryResponse(BaseModel):
    namespace: str
    results: list[MemoryResult]
    total_results: int


class SaveMemoryRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000)
    type: str = Field("knowledge", pattern="^(knowledge|context|summary|event|code_snippet|preference)$")
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None


class SaveMemoryResponse(BaseModel):
    namespace: str
    id: str
    status: str
    created_at: str
    content_preview: str
    embedding_generated: bool
    classified_by_llm: bool
    indexed: bool


class DeleteMemoryResponse(BaseModel):
    namespace: str
    id: str
    status: str
    deleted_at: str


@router.post("/search", response_model=SearchMemoryResponse)
async def search_memory(
    request: SearchMemoryRequest,
    service: MemoryService = Depends(get_memory_service),
    user_context: dict[str, str] = Depends(get_user_context),
):
    try:
        filters_dict = request.filters.model_dump() if request.filters else None

        results, rlm_metrics, processing_time = await service.search_memory(
            query=request.query,
            limit=request.limit,
            filters=filters_dict,
            user_id=user_context["user_id"],
            enable_rlm=request.enable_rlm,
            session_id=request.session_id,
        )

        mapped_results: list[MemoryResult] = []
        for memory, score in results:
            mapped_results.append(
                MemoryResult(
                    id=str(memory.id),
                    content=memory.content,
                    score=score,
                    type=memory.type,
                    tags=memory.tags,
                    created_at=memory.created_at.isoformat(),
                    metadata=memory.metadata_,
                )
            )

        return SearchMemoryResponse(
            namespace=user_context["namespace"],
            results=mapped_results,
            total_results=len(mapped_results),
            processing_time_ms=processing_time,
            rlm_decomposition=RLMMetrics(**rlm_metrics),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/save", response_model=SaveMemoryResponse)
async def save_memory(
    request: SaveMemoryRequest,
    service: MemoryService = Depends(get_memory_service),
    user_context: dict[str, str] = Depends(get_user_context),
):
    try:
        result = await service.save_memory(
            content=request.content,
            memory_type=request.type,
            tags=request.tags,
            metadata=request.metadata or {},
            user_id=user_context["user_id"],
        )

        return SaveMemoryResponse(
            namespace=user_context["namespace"],
            id=str(result.memory.id),
            status="saved",
            created_at=result.memory.created_at.isoformat(),
            content_preview=result.memory.content[:100],
            embedding_generated=not result.embedding_is_fallback,
            classified_by_llm=result.classified_by_llm,
            indexed=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{memory_id}", response_model=DeleteMemoryResponse)
async def delete_memory(
    memory_id: str,
    service: MemoryService = Depends(get_memory_service),
    user_context: dict[str, str] = Depends(get_user_context),
):
    try:
        deleted_at = await service.delete_memory(memory_id, user_context["user_id"])
        return DeleteMemoryResponse(
            namespace=user_context["namespace"],
            id=memory_id,
            status="deleted",
            deleted_at=deleted_at.isoformat(),
        )
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Memory not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/types")
async def get_memory_types(
    user_context: dict[str, str] = Depends(get_user_context),
    db: AsyncSession = Depends(get_db),
):
    types = await get_distinct_types(db, user_context["user_id"])
    return {"types": sorted(types)}


@router.get("/stats")
async def get_memory_stats(
    user_context: dict[str, str] = Depends(get_user_context),
    db: AsyncSession = Depends(get_db),
):
    user_id = user_context["user_id"]

    result = await db.execute(select(func.count(Memory.id)).where(Memory.user_id == user_id))
    total_memories = result.scalar() or 0

    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)

    result_today = await db.execute(
        select(func.count(Memory.id)).where(Memory.user_id == user_id).where(Memory.created_at >= start_of_day)
    )
    entries_today = result_today.scalar() or 0

    result_size = await db.execute(select(func.sum(func.length(Memory.content))).where(Memory.user_id == user_id))
    size_bytes = result_size.scalar() or 0
    size_mb = round(size_bytes / (1024 * 1024), 2)
    cache_stats = await pg_cache_service.stats(db)

    return {
        "namespace": user_context["namespace"],
        "total_memories": total_memories,
        "storage_size": size_mb,
        "entries_today": entries_today,
        "cache_hits_24h": cache_stats.get("hits_last_24h", 0),
    }


@router.get("/namespaces")
async def list_namespaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User.namespace).order_by(User.namespace))
    namespaces = [row[0] for row in result.all()]
    return {"namespaces": namespaces}


@router.get("/list", response_model=ListMemoryResponse)
async def list_memory(
    limit: int = 1000,
    offset: int = 0,
    memory_type: str | None = None,
    service: MemoryService = Depends(get_memory_service),
    user_context: dict[str, str] = Depends(get_user_context),
):
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 1000")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    memories = await service.list_memories(
        user_id=user_context["user_id"], limit=limit, offset=offset, memory_type=memory_type
    )

    mapped_results: list[MemoryResult] = [
        MemoryResult(
            id=str(memory.id),
            content=memory.content,
            score=0.0,
            type=memory.type,
            tags=memory.tags,
            created_at=memory.created_at.isoformat(),
            metadata=memory.metadata_,
        )
        for memory in memories
    ]

    return ListMemoryResponse(
        namespace=user_context["namespace"],
        results=mapped_results,
        total_results=len(mapped_results),
    )
