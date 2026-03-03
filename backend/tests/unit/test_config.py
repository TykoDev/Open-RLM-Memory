from app.core.config import Settings
def test_resolve_optional():
    # Test None
    assert Settings._resolve_optional(None, "fallback") == "fallback"
    # Test empty string
    assert Settings._resolve_optional("", "fallback") == "fallback"
    # Test whitespace string
    assert Settings._resolve_optional("   ", "fallback") == "fallback"
    # Test normal value
    assert Settings._resolve_optional("value", "fallback") == "value"
    # Test value with whitespace
    assert Settings._resolve_optional("  value  ", "fallback") == "value"

def test_embedding_openai_base_url_property():
    # Test with custom base URL
    s = Settings(
        EMBED_OPENAI_BASE_URL="http://custom:1234/v1",
        OPENAI_BASE_URL="http://default:1234/v1"
    )
    assert s.embedding_openai_base_url == "http://custom:1234/v1"

    # Test fallback to OPENAI_BASE_URL when EMBED_OPENAI_BASE_URL is None
    s = Settings(
        EMBED_OPENAI_BASE_URL=None,
        OPENAI_BASE_URL="http://default:1234/v1"
    )
    assert s.embedding_openai_base_url == "http://default:1234/v1"

    # Test fallback to OPENAI_BASE_URL when EMBED_OPENAI_BASE_URL is empty/whitespace
    s = Settings(
        EMBED_OPENAI_BASE_URL="  ",
        OPENAI_BASE_URL="http://default:1234/v1"
    )
    assert s.embedding_openai_base_url == "http://default:1234/v1"

def test_embedding_openai_api_key_property():
    # Test with custom API key
    s = Settings(
        EMBED_OPENAI_API_KEY="custom-key",
        OPENAI_API_KEY="default-key"
    )
    assert s.embedding_openai_api_key == "custom-key"

    # Test fallback to OPENAI_API_KEY when EMBED_OPENAI_API_KEY is None
    s = Settings(
        EMBED_OPENAI_API_KEY=None,
        OPENAI_API_KEY="default-key"
    )
    assert s.embedding_openai_api_key == "default-key"

    # Test fallback to OPENAI_API_KEY when EMBED_OPENAI_API_KEY is empty
    s = Settings(
        EMBED_OPENAI_API_KEY="",
        OPENAI_API_KEY="default-key"
    )
    assert s.embedding_openai_api_key == "default-key"
