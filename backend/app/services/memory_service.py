import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.queries import memory as memory_queries
from app.models.memory import Memory, MemoryEmbedding
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.pg_cache_service import pg_cache_service
from app.services.rlm_service import RLMService


class MemoryNotFoundError(Exception):
    pass


@dataclass
class SaveResult:
    memory: Memory
    classified_by_llm: bool
    embedding_is_fallback: bool
    embedding_error: Optional[str] = field(default=None)


class MemoryService:
    def __init__(
        self,
        db: AsyncSession,
        rlm: Optional[RLMService] = None,
    ):
        self.db = db
        self.rlm = rlm

    @staticmethod
    def _utcnow_naive() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    async def search_memory(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        enable_rlm: bool = True,
        session_id: Optional[str] = None,
    ) -> Tuple[List[Tuple[Memory, float]], Dict[str, Any], float]:
        if not user_id:
            raise ValueError("user_id is required for memory search")

        start_time = datetime.now()
        cache_key = pg_cache_service.build_search_key(
            namespace=user_id,
            query=query,
            limit=limit,
            filters=filters,
            enable_rlm=enable_rlm,
            session_id=session_id,
        )

        try:
            cached_payload = await pg_cache_service.get(self.db, cache_key)
            if cached_payload:
                cached_results = cached_payload.get("results", [])
                cached_ids = [str(item.get("memory_id")) for item in cached_results]
                memories = await memory_queries.get_memories_by_ids(self.db, cached_ids, user_id)
                memory_by_id = {str(memory.id): memory for memory in memories}

                results = [
                    (memory, float(item.get("score", 0.0)))
                    for item in cached_results
                    if (memory := memory_by_id.get(str(item.get("memory_id")))) is not None
                ]

                rlm_metrics = cached_payload.get("rlm_metrics", {"steps": 1, "sub_queries": 0})
                rlm_metrics["used_cache"] = True
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                return results, rlm_metrics, processing_time

            rlm_metrics = {"steps": 0, "sub_queries": 0, "used_cache": False}
            results = []

            if enable_rlm and self.rlm:
                # 1. Create RLM context
                context = await self.rlm.create_context(user_id, session_id=session_id)

                # 2. Decompose
                sub_queries = await self.rlm.decompose_query(query)

                # 3. Search for each sub-query
                candidates = []
                seen_ids = set()

                # Embed all sub-queries
                for sub_q in sub_queries:
                    embed_result = await embedding_service.embed(sub_q)
                    sub_results = await memory_queries.search_by_embedding(
                        self.db, embed_result.vector, user_id, limit, filters
                    )

                    for mem, score in sub_results:
                        if mem.id not in seen_ids:
                            safe_score = float(score)
                            if not math.isfinite(safe_score):
                                safe_score = 0.0
                            # Structure compatible with REPL
                            candidates.append(
                                {
                                    "id": str(mem.id),
                                    "content": mem.content,
                                    "type": mem.type,
                                    "tags": mem.tags,
                                    "score": safe_score,
                                    "memory_obj": mem,
                                }
                            )
                            seen_ids.add(mem.id)

                # 4. Re-rank using RLM
                if candidates:
                    ranked_candidates = await self.rlm.re_rank_results(query, candidates, context)
                    # Take top limits
                    for cand in ranked_candidates[:limit]:
                        results.append((cand["memory_obj"], cand["score"]))

                rlm_metrics = {"steps": len(sub_queries) + 1, "sub_queries": len(sub_queries), "used_cache": False}

            else:
                # Direct semantic search
                embed_result = await embedding_service.embed(query)
                results = await memory_queries.search_by_embedding(
                    self.db, embed_result.vector, user_id, limit, filters
                )
                rlm_metrics = {"steps": 1, "sub_queries": 0, "used_cache": False}

            normalized_results: List[Tuple[Memory, float]] = []
            for memory, score in results:
                safe_score = float(score)
                if not math.isfinite(safe_score):
                    safe_score = 0.0
                normalized_results.append((memory, safe_score))

            results = normalized_results

            cache_payload = {
                "results": [{"memory_id": str(memory.id), "score": score} for memory, score in results],
                "rlm_metrics": {
                    "steps": int(rlm_metrics.get("steps", 0)),
                    "sub_queries": int(rlm_metrics.get("sub_queries", 0)),
                },
            }
            await pg_cache_service.set(self.db, cache_key=cache_key, namespace=user_id, payload=cache_payload)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return results, rlm_metrics, processing_time

        except Exception as e:
            logger.error(f"search_memory_failed query={query} error={e}")
            raise

    async def save_memory(
        self,
        content: str,
        memory_type: str,
        tags: List[str],
        metadata: Dict[str, Any],
        user_id: str,
    ) -> SaveResult:
        # Auto-classify via LLM when caller uses defaults
        classified_by_llm = False
        if memory_type == "knowledge" and not tags:
            classification = await llm_service.classify_memory(content)
            memory_type = classification.memory_type
            tags = classification.tags
            classified_by_llm = classification.classified_by_llm

        # Generate embedding
        embed_result = await embedding_service.embed(content)

        # Create Memory
        memory = Memory(
            content=content,
            type=memory_type,
            tags=tags,
            metadata_=metadata,
            user_id=user_id,
            created_at=self._utcnow_naive(),
        )

        await memory_queries.create_memory(self.db, memory)

        # Create Embedding
        embedding = MemoryEmbedding(memory_id=memory.id, embedding=embed_result.vector, model=embed_result.model)
        await memory_queries.create_embedding(self.db, embedding)

        await pg_cache_service.invalidate_namespace(self.db, str(user_id))
        await self.db.commit()
        await self.db.refresh(memory)

        return SaveResult(
            memory=memory,
            classified_by_llm=classified_by_llm,
            embedding_is_fallback=embed_result.is_fallback,
            embedding_error=embed_result.error,
        )

    async def list_memories(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        tags: Optional[List[str]] = None,
        memory_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
    ) -> List[Memory]:
        return await memory_queries.get_memories(
            self.db,
            user_id=user_id,
            limit=limit,
            offset=offset,
            tags=tags,
            memory_type=memory_type,
            metadata=metadata,
            created_before=created_before,
            created_after=created_after,
        )

    async def delete_memory(self, memory_id: str, user_id: str) -> datetime:
        memory = await memory_queries.get_by_id(self.db, memory_id, user_id)
        if not memory:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")

        await memory_queries.delete_memory(self.db, memory_id, user_id)
        await pg_cache_service.invalidate_namespace(self.db, str(user_id))
        await self.db.commit()

        return self._utcnow_naive()
