from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, desc, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryEmbedding

# Try import pgvector functions
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


def _is_postgres(session: AsyncSession) -> bool:
    bind = session.get_bind()
    return bool(bind and bind.dialect.name == "postgresql")


async def get_by_id(session: AsyncSession, memory_id: str, user_id: str) -> Optional[Memory]:
    stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def search_by_embedding(
    session: AsyncSession,
    query_embedding: List[float],
    user_id: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Tuple[Memory, float]]:
    # Apply filters
    if filters and filters.get("type"):
        base_filters = [Memory.user_id == user_id, Memory.type == filters["type"]]
    else:
        base_filters = [Memory.user_id == user_id]

    # Additional tag filtering would go here

    if _is_postgres(session) and Vector:
        # PostgreSQL with pgvector: Select Memory and (1 - cosine_distance)
        distance_expr = MemoryEmbedding.embedding.cosine_distance(query_embedding)
        score_expr = 1 - distance_expr

        stmt = (
            select(Memory, score_expr).join(MemoryEmbedding).where(*base_filters).order_by(distance_expr).limit(limit)
        )
    else:
        # SQLite/Fallback: Return Memory and 0.0 score, ordered by recency
        stmt = (
            select(Memory, literal(0.0))
            .join(MemoryEmbedding)
            .where(*base_filters)
            .order_by(desc(Memory.created_at))
            .limit(limit)
        )

    result = await session.execute(stmt)
    rows = result.all()
    return [(row[0], float(row[1])) for row in rows]


async def get_memories(
    session: AsyncSession,
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    tags: Optional[List[str]] = None,
    memory_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    created_before: Optional[datetime] = None,
    created_after: Optional[datetime] = None,
) -> List[Memory]:
    stmt = select(Memory).where(Memory.user_id == user_id)

    if memory_type:
        stmt = stmt.where(Memory.type == memory_type)

    if tags:
        if _is_postgres(session):
            stmt = stmt.where(Memory.tags.overlap(tags))
        else:
            stmt = stmt.where(Memory.tags.contains(tags))

    if metadata and _is_postgres(session):
        stmt = stmt.where(Memory.metadata_.contains(metadata))

    if created_after:
        stmt = stmt.where(Memory.created_at >= created_after)
    if created_before:
        stmt = stmt.where(Memory.created_at <= created_before)

    stmt = stmt.order_by(desc(Memory.created_at)).offset(offset).limit(limit)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_distinct_types(session: AsyncSession, user_id: str) -> List[str]:
    stmt = select(Memory.type).where(Memory.user_id == user_id).distinct()
    result = await session.execute(stmt)
    return [row[0] for row in result.all()]


async def get_memories_by_ids(
    session: AsyncSession,
    memory_ids: List[str],
    user_id: str,
) -> List[Memory]:
    if not memory_ids:
        return []

    stmt = select(Memory).where(Memory.user_id == user_id, Memory.id.in_(memory_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_memory(session: AsyncSession, memory: Memory) -> Memory:
    session.add(memory)
    await session.flush()
    return memory


async def create_embedding(session: AsyncSession, embedding: MemoryEmbedding) -> MemoryEmbedding:
    session.add(embedding)
    return embedding


async def delete_memory(session: AsyncSession, memory_id: str, user_id: str) -> None:
    stmt = delete(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    await session.execute(stmt)
