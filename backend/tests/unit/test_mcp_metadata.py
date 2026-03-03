import pytest


@pytest.mark.asyncio
async def test_well_known_resource_metadata(client):
    response = await client.get("/.well-known/oauth-protected-resource")
    assert response.status_code == 200
    data = response.json()
    assert data["resource"] == "http://test/mcp"
    assert data["issuer"] == "http://test"


@pytest.mark.asyncio
async def test_well_known_mcp_metadata(client):
    response = await client.get("/.well-known/oauth-protected-resource/mcp")
    assert response.status_code == 200
    data = response.json()
    assert data["resource"] == "http://test/mcp"
    assert data["issuer"] == "http://test"


@pytest.mark.asyncio
async def test_mcp_initialize_dev_without_auth(client):
    payload = {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}
    response = await client.post("/mcp", json=payload)
    assert response.status_code == 200
    assert response.headers.get("mcp-session-id")


@pytest.mark.asyncio
async def test_mcp_initialize_prod_without_auth(client):
    payload = {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}
    response = await client.post("/mcp", json=payload)
    assert response.status_code == 200
    assert response.headers.get("mcp-session-id")
