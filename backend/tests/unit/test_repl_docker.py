import json
import pytest
from unittest.mock import MagicMock, patch
from app.rlm_engine.repl import DockerExecutionBackend

@pytest.fixture
def mock_docker():
    with patch("app.rlm_engine.repl.docker") as mock:
        yield mock

@pytest.fixture
def backend(mock_docker):
    # Mock from_env return value
    mock_client = MagicMock()
    mock_docker.from_env.return_value = mock_client
    return DockerExecutionBackend()

@pytest.mark.asyncio
async def test_docker_execute_success(backend, mock_docker):
    mock_client = backend.client
    mock_container = MagicMock()
    mock_client.containers.run.return_value = json.dumps({
        "status": "success",
        "variables": {"x": 10}
    }).encode("utf-8")

    code = "x = 10"
    variables = {}

    result = await backend.execute(code, variables)

    assert result == {"x": 10}

    # Verify container run call
    mock_client.containers.run.assert_called_once()
    call_args = mock_client.containers.run.call_args
    assert call_args[0][0] == "python:3.11-slim"
    assert "command" in call_args[1]
    assert "network_disabled" in call_args[1]
    assert call_args[1]["network_disabled"] is True

@pytest.mark.asyncio
async def test_docker_evaluate_success(backend):
    mock_client = backend.client
    mock_client.containers.run.return_value = json.dumps({
        "status": "success",
        "result": 42
    }).encode("utf-8")

    expression = "6 * 7"
    variables = {}

    result = await backend.evaluate(expression, variables)

    assert result == 42

@pytest.mark.asyncio
async def test_docker_execute_error(backend):
    mock_client = backend.client
    mock_client.containers.run.return_value = json.dumps({
        "status": "error",
        "error": "SyntaxError"
    }).encode("utf-8")

    with pytest.raises(RuntimeError, match="Execution error: SyntaxError"):
        await backend.execute("invalid syntax", {})

@pytest.mark.asyncio
async def test_docker_evaluate_error(backend):
    mock_client = backend.client
    mock_client.containers.run.return_value = json.dumps({
        "status": "error",
        "error": "ZeroDivisionError"
    }).encode("utf-8")

    with pytest.raises(RuntimeError, match="Evaluation error: ZeroDivisionError"):
        await backend.evaluate("1 / 0", {})

@pytest.mark.asyncio
async def test_docker_client_init_failure(mock_docker):
    mock_docker.from_env.side_effect = Exception("Docker not found")

    backend = DockerExecutionBackend()
    assert backend.client is None

    # Should attempt to init again on execute and fail
    with pytest.raises(RuntimeError, match="Docker client not available"):
        await backend.execute("print('hi')", {})
