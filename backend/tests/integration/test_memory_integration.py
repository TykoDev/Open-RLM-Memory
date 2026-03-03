import pytest

from app.services.memory_service import MemoryService


@pytest.mark.asyncio
async def test_save_and_retrieve_memory(db_session, user_id):
    service = MemoryService(db_session)

    # Save
    result = await service.save_memory(
        content="Integration test content",
        memory_type="knowledge",
        tags=["integration", "test"],
        metadata={"source": "test"},
        user_id=user_id
    )
    memory = result.memory

    assert memory.id is not None
    assert memory.content == "Integration test content"

    # Retrieve via search (mocking embedding to match logic if needed,
    # but for integration with real DB, we rely on what's there.
    # Since we use SQLite in tests, vector search is mocked/simplified in queries/memory.py)

    results, metrics, time_ms = await service.search_memory(
        query="test",
        user_id=user_id,
        enable_rlm=False
    )

    assert len(results) >= 1
    found_memory = results[0][0] # (Memory, score)
    assert found_memory.id == memory.id

@pytest.mark.asyncio
async def test_delete_memory(db_session, user_id):
    service = MemoryService(db_session)

    result = await service.save_memory(
        content="To be deleted",
        memory_type="event",
        tags=[],
        metadata={},
        user_id=user_id
    )
    memory = result.memory

    await service.delete_memory(str(memory.id), user_id)

    # Verify deletion
    results, _, _ = await service.search_memory("deleted", user_id=user_id, enable_rlm=False)
    # Should not find the specific deleted id
    found_ids = [str(r[0].id) for r in results]
    assert str(memory.id) not in found_ids
