import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cache import PgCache


class PgCacheService:
    @staticmethod
    def _utcnow_naive() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def build_search_key(
        self,
        namespace: str,
        query: str,
        limit: int,
        filters: dict[str, Any] | None,
        enable_rlm: bool,
        session_id: str | None,
    ) -> str:
        payload = {
            "namespace": namespace,
            "query": query,
            "limit": limit,
            "filters": filters or {},
            "enable_rlm": enable_rlm,
            "session_id": session_id or "",
            "embedding_model": settings.EMBEDDING_MODEL,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def get(self, db: AsyncSession, cache_key: str) -> dict[str, Any] | None:
        row = await db.get(PgCache, cache_key)
        if not row:
            return None

        if row.expires_at <= self._utcnow_naive():
            await db.delete(row)
            await db.flush()
            return None

        row.hit_count = int(row.hit_count or 0) + 1
        row.last_hit_at = self._utcnow_naive()
        await db.flush()

        return dict(row.payload)

    async def set(self, db: AsyncSession, cache_key: str, namespace: str, payload: dict[str, Any]) -> None:
        expires_at = self._utcnow_naive() + timedelta(seconds=settings.SEARCH_CACHE_TTL_SECONDS)
        row = PgCache(
            cache_key=cache_key,
            namespace=namespace,
            payload=payload,
            expires_at=expires_at,
            hit_count=0,
            last_hit_at=None,
        )
        await db.merge(row)
        await db.flush()

    async def invalidate_namespace(self, db: AsyncSession, namespace: str) -> int:
        existing = await db.execute(select(func.count(PgCache.cache_key)).where(PgCache.namespace == namespace))
        count = int(existing.scalar() or 0)
        await db.execute(delete(PgCache).where(PgCache.namespace == namespace))
        await db.flush()
        return count

    async def stats(self, db: AsyncSession) -> dict[str, int]:
        await db.execute(delete(PgCache).where(PgCache.expires_at <= self._utcnow_naive()))
        await db.flush()

        rows = await db.execute(select(func.count(PgCache.cache_key)))
        active_entries = int(rows.scalar() or 0)
        last_24h = self._utcnow_naive() - timedelta(hours=24)
        hit_rows = await db.execute(
            select(func.coalesce(func.sum(PgCache.hit_count), 0)).where(
                PgCache.last_hit_at.is_not(None), PgCache.last_hit_at >= last_24h
            )
        )
        hits_last_24h = int(hit_rows.scalar() or 0)

        return {"active_entries": active_entries, "hits_last_24h": hits_last_24h}


pg_cache_service = PgCacheService()
