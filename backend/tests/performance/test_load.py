import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_latency(client: AsyncClient):
    # Seed data
    for i in range(10):
        await client.post("/api/v1/memory/save", json={
            "content": f"Performance test memory {i}",
            "type": "knowledge",
            "tags": ["perf"],
            "metadata": {}
        })

    start_time = time.perf_counter()
    iterations = 50

    for _ in range(iterations):
        response = await client.post("/api/v1/memory/search", json={
            "query": "Performance",
            "limit": 10,
            "enable_rlm": False
        })
        assert response.status_code == 200

    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_latency = total_time / iterations

    # Assert reasonable latency (e.g. < 50ms per request for SQLite in-memory)
    # Relaxed to 100ms to be safe in CI environment
    assert avg_latency < 0.1, f"Average latency {avg_latency:.4f}s exceeded 100ms"
