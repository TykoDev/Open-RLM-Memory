from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Open RLM Memory"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Database
    DB_TYPE: str = "postgres"
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = "localhost"
    POSTGRES_DB: Optional[str] = "rlm_memory"

    # Search cache
    SEARCH_CACHE_TTL_SECONDS: int = 300
    DEFAULT_MEMORY_NAMESPACE: str = "local"
    MAX_NAMESPACE_LENGTH: int = 64

    # LLM
    OPENAI_BASE_URL: str = "http://127.0.0.1:1234/v1"
    OPENAI_API_KEY: str = "lm-studio"
    OPENAI_MODEL: str = "mistralai/ministral-3-14b-reasoning"
    EMBED_OPENAI_BASE_URL: Optional[str] = None
    EMBED_OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-qwen3-embedding-4b@q4_k_m"
    EMBEDDING_DIMENSIONS: int = 1536
    ALLOW_EMBEDDING_FALLBACK: bool = True
    LLM_PROVIDER: str = "openai-compatible"

    # Logging
    LOG_LEVEL: str = "INFO"

    @staticmethod
    def _resolve_optional(value: Optional[str], fallback: str) -> str:
        if value is None:
            return fallback
        normalized = value.strip()
        return normalized if normalized else fallback

    @property
    def embedding_openai_base_url(self) -> str:
        return self._resolve_optional(self.EMBED_OPENAI_BASE_URL, self.OPENAI_BASE_URL)

    @property
    def embedding_openai_api_key(self) -> str:
        return self._resolve_optional(self.EMBED_OPENAI_API_KEY, self.OPENAI_API_KEY)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
