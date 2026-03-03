from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.memory import Memory
from app.services.embedding_service import EmbeddingResult
from app.services.llm_service import ClassificationResult
from app.services.memory_service import MemoryService, SaveResult


@pytest.mark.asyncio
async def test_search_memory_calls_db_no_rlm():
    # Mock DB session
    mock_db = AsyncMock()
    mock_rlm = AsyncMock()

    # Mock MemoryService to use mocked dependencies
    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                mock_embedding.embed = AsyncMock(
                    return_value=EmbeddingResult(vector=[0.1, 0.2, 0.3], is_fallback=False, model="test-model")
                )
                mock_cache.build_search_key.return_value = "cache-key"
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache.set = AsyncMock()

                # Setup mock return for search_by_embedding
                mock_mem = MagicMock(spec=Memory)
                mock_mem.id = "123"
                mock_queries.search_by_embedding = AsyncMock(return_value=[(mock_mem, 0.95)])

                service = MemoryService(mock_db, mock_rlm)

                results, metrics, time = await service.search_memory(
                    query="test",
                    user_id="user1",
                    enable_rlm=False,
                )

                assert len(results) == 1
                assert results[0][1] == 0.95
                assert metrics["steps"] == 1
                assert metrics["sub_queries"] == 0

                mock_queries.search_by_embedding.assert_called_once()


@pytest.mark.asyncio
async def test_search_memory_with_rlm():
    mock_db = AsyncMock()
    mock_rlm = AsyncMock()

    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                mock_embedding.embed = AsyncMock(
                    return_value=EmbeddingResult(vector=[0.1], is_fallback=False, model="test-model")
                )
                mock_cache.build_search_key.return_value = "cache-key"
                mock_cache.get = AsyncMock(return_value=None)
                mock_cache.set = AsyncMock()

                # Mock RLM behavior
                mock_rlm.create_context.return_value = {"session_id": "sess1"}
                mock_rlm.decompose_query.return_value = ["sub1", "sub2"]

                mock_mem1 = MagicMock(spec=Memory)
                mock_mem1.id = "1"
                mock_mem1.content = "content1"
                mock_mem1.type = "knowledge"
                mock_mem1.tags = []

                mock_mem2 = MagicMock(spec=Memory)
                mock_mem2.id = "2"
                mock_mem2.content = "content2"
                mock_mem2.type = "knowledge"
                mock_mem2.tags = []

                # Return different results for sub-queries
                mock_queries.search_by_embedding = AsyncMock(
                    side_effect=[
                        [(mock_mem1, 0.8)],  # sub1 result
                        [(mock_mem2, 0.7)],  # sub2 result
                    ]
                )

                # Mock re-ranking
                mock_rlm.re_rank_results.return_value = [
                    {"memory_obj": mock_mem1, "score": 0.9},
                    {"memory_obj": mock_mem2, "score": 0.6},
                ]

                service = MemoryService(mock_db, mock_rlm)

                results, metrics, time = await service.search_memory(
                    query="complex query",
                    enable_rlm=True,
                    user_id="user1",
                )

                assert len(results) == 2
                assert results[0][0] == mock_mem1
                assert results[0][1] == 0.9

                assert metrics["steps"] == 3  # 2 sub-queries + 1 step
                assert metrics["sub_queries"] == 2

                assert mock_rlm.decompose_query.called
                assert mock_queries.search_by_embedding.call_count == 2
                assert mock_rlm.re_rank_results.called


@pytest.mark.asyncio
async def test_save_memory_auto_classification():
    """When type is default 'knowledge' and tags are empty, LLM classification should be called."""
    mock_db = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                with patch("app.services.memory_service.llm_service") as mock_llm:
                    mock_embedding.embed = AsyncMock(
                        return_value=EmbeddingResult(vector=[0.1, 0.2], is_fallback=False, model="test-model")
                    )
                    mock_queries.create_memory = AsyncMock()
                    mock_queries.create_embedding = AsyncMock()
                    mock_cache.invalidate_namespace = AsyncMock()

                    mock_llm.classify_memory = AsyncMock(
                        return_value=ClassificationResult(
                            memory_type="code_snippet",
                            tags=["python", "testing"],
                            classified_by_llm=True,
                        )
                    )

                    service = MemoryService(mock_db)
                    result = await service.save_memory(
                        content="def hello(): pass",
                        memory_type="knowledge",
                        tags=[],
                        metadata={},
                        user_id="user1",
                    )

                    assert isinstance(result, SaveResult)
                    assert result.classified_by_llm is True
                    assert result.embedding_is_fallback is False
                    assert result.memory.type == "code_snippet"
                    assert result.memory.tags == ["python", "testing"]
                    mock_llm.classify_memory.assert_called_once()


@pytest.mark.asyncio
async def test_save_memory_explicit_override_skips_llm():
    """When caller provides explicit type or tags, LLM classification should be skipped."""
    mock_db = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                with patch("app.services.memory_service.llm_service") as mock_llm:
                    mock_embedding.embed = AsyncMock(
                        return_value=EmbeddingResult(vector=[0.1, 0.2], is_fallback=False, model="test-model")
                    )
                    mock_queries.create_memory = AsyncMock()
                    mock_queries.create_embedding = AsyncMock()
                    mock_cache.invalidate_namespace = AsyncMock()

                    service = MemoryService(mock_db)
                    result = await service.save_memory(
                        content="some content",
                        memory_type="preference",
                        tags=["dark-mode"],
                        metadata={},
                        user_id="user1",
                    )

                    assert isinstance(result, SaveResult)
                    assert result.classified_by_llm is False
                    assert result.memory.type == "preference"
                    assert result.memory.tags == ["dark-mode"]
                    mock_llm.classify_memory.assert_not_called()


@pytest.mark.asyncio
async def test_save_memory_llm_failure_uses_defaults():
    """When LLM classification fails, defaults should be used gracefully."""
    mock_db = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                with patch("app.services.memory_service.llm_service") as mock_llm:
                    mock_embedding.embed = AsyncMock(
                        return_value=EmbeddingResult(vector=[0.1, 0.2], is_fallback=False, model="test-model")
                    )
                    mock_queries.create_memory = AsyncMock()
                    mock_queries.create_embedding = AsyncMock()
                    mock_cache.invalidate_namespace = AsyncMock()

                    # LLM fails gracefully -> returns defaults with classified_by_llm=False
                    mock_llm.classify_memory = AsyncMock(
                        return_value=ClassificationResult(
                            memory_type="knowledge",
                            tags=[],
                            classified_by_llm=False,
                        )
                    )

                    service = MemoryService(mock_db)
                    result = await service.save_memory(
                        content="some content",
                        memory_type="knowledge",
                        tags=[],
                        metadata={},
                        user_id="user1",
                    )

                    assert isinstance(result, SaveResult)
                    assert result.classified_by_llm is False
                    assert result.memory.type == "knowledge"
                    assert result.memory.tags == []


@pytest.mark.asyncio
async def test_save_memory_embedding_fallback():
    """When embedding falls back to zero vector, result should indicate fallback."""
    mock_db = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch("app.services.memory_service.embedding_service") as mock_embedding:
        with patch("app.services.memory_service.memory_queries") as mock_queries:
            with patch("app.services.memory_service.pg_cache_service") as mock_cache:
                with patch("app.services.memory_service.llm_service") as mock_llm:
                    mock_embedding.embed = AsyncMock(
                        return_value=EmbeddingResult(
                            vector=[0.0, 0.0],
                            is_fallback=True,
                            model="test-model",
                            error="Connection refused",
                        )
                    )
                    mock_queries.create_memory = AsyncMock()
                    mock_queries.create_embedding = AsyncMock()
                    mock_cache.invalidate_namespace = AsyncMock()

                    mock_llm.classify_memory = AsyncMock(
                        return_value=ClassificationResult(
                            memory_type="event",
                            tags=["test"],
                            classified_by_llm=True,
                        )
                    )

                    service = MemoryService(mock_db)
                    result = await service.save_memory(
                        content="something happened",
                        memory_type="knowledge",
                        tags=[],
                        metadata={},
                        user_id="user1",
                    )

                    assert isinstance(result, SaveResult)
                    assert result.embedding_is_fallback is True
                    assert result.embedding_error == "Connection refused"
                    assert result.classified_by_llm is True
