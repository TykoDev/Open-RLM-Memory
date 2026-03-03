from unittest.mock import patch

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


def _build_service(
    *,
    openai_base_url: str,
    openai_api_key: str,
    embed_base_url: str | None,
    embed_api_key: str | None,
):
    with (
        patch.object(settings, "OPENAI_BASE_URL", openai_base_url),
        patch.object(settings, "OPENAI_API_KEY", openai_api_key),
        patch.object(settings, "EMBED_OPENAI_BASE_URL", embed_base_url),
        patch.object(settings, "EMBED_OPENAI_API_KEY", embed_api_key),
        patch("app.services.embedding_service.AsyncOpenAI") as mock_client,
    ):
        service = EmbeddingService()

    return service, mock_client


def test_embedding_service_uses_openai_defaults_when_embed_vars_unset():
    service, mock_client = _build_service(
        openai_base_url="http://llm-host:1234/v1",
        openai_api_key="llm-key",
        embed_base_url=None,
        embed_api_key=None,
    )

    assert service.base_url == "http://llm-host:1234/v1"
    assert service.api_key == "llm-key"
    mock_client.assert_called_once_with(api_key="llm-key", base_url="http://llm-host:1234/v1")


def test_embedding_service_uses_embed_specific_provider_when_set():
    service, mock_client = _build_service(
        openai_base_url="http://llm-host:1234/v1",
        openai_api_key="llm-key",
        embed_base_url="http://embed-host:1235/v1",
        embed_api_key="embed-key",
    )

    assert service.base_url == "http://embed-host:1235/v1"
    assert service.api_key == "embed-key"
    mock_client.assert_called_once_with(api_key="embed-key", base_url="http://embed-host:1235/v1")


def test_embedding_service_falls_back_when_embed_vars_are_empty():
    service, mock_client = _build_service(
        openai_base_url="http://llm-host:1234/v1",
        openai_api_key="llm-key",
        embed_base_url="   ",
        embed_api_key="",
    )

    assert service.base_url == "http://llm-host:1234/v1"
    assert service.api_key == "llm-key"
    mock_client.assert_called_once_with(api_key="llm-key", base_url="http://llm-host:1234/v1")
