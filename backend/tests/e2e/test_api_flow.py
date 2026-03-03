import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_memory_lifecycle(client: AsyncClient):
    # 1. Save Memory

    # Note: The endpoint expects the body directly matching SaveMemoryRequest
    # If the user prompt implied an MCP envelope "tool", the current implementation
    # in backend/app/api/routers/memory.py takes the flat body.
    # I will stick to the implementation I read in `memory.py` earlier.

    api_payload = {
        "content": "E2E Test Memory",
        "type": "knowledge",
        "tags": ["e2e"],
        "metadata": {"test": True}
    }

    response = await client.post("/api/v1/memory/save", json=api_payload)
    assert response.status_code == 200
    data = response.json()
    memory_id = data["id"]
    assert data["status"] == "saved"

    # 2. Search Memory
    search_payload = {
        "query": "E2E",
        "limit": 5,
        "enable_rlm": False
    }
    response = await client.post("/api/v1/memory/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    assert data["results"][0]["id"] == memory_id

    # 3. Delete Memory
    response = await client.delete(f"/api/v1/memory/{memory_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # 4. Verify Deleted
    response = await client.post("/api/v1/memory/search", json=search_payload)
    data = response.json()
    # It might still return other results if parallel tests ran, but let's check this specific ID is gone
    found_ids = [r["id"] for r in data["results"]]
    assert memory_id not in found_ids

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
