import pytest
from app.services.rlm_service import RLMService
from unittest.mock import AsyncMock
@pytest.mark.asyncio
async def test_re_rank_results_ordering():
    service = RLMService()

    # Mock REPL and LLM to avoid external calls
    service.repl = AsyncMock()
    service.llm = AsyncMock()

    results = [
        {"id": 1, "content": "first"},
        {"id": 2, "content": "second"},
        {"id": 3, "content": "third"},
    ]
    ranked_ids = [2, 3, 1]

    service.repl.evaluate.return_value = ranked_ids

    context = {"session_id": "test-session"}
    ordered = await service.re_rank_results("query", results, context)

    assert [r["id"] for r in ordered] == ranked_ids
    assert ordered[0]["content"] == "second"
    assert ordered[1]["content"] == "third"
    assert ordered[2]["content"] == "first"
@pytest.mark.asyncio
async def test_re_rank_results_missing_ids():
    service = RLMService()
    service.repl = AsyncMock()

    results = [
        {"id": 1, "content": "first"},
        {"id": 2, "content": "second"},
    ]
    # REPL returns an ID that's not in results (should be ignored)
    ranked_ids = [2, 3, 1]

    service.repl.evaluate.return_value = ranked_ids

    context = {"session_id": "test-session"}
    ordered = await service.re_rank_results("query", results, context)

    assert [r["id"] for r in ordered] == [2, 1]
