from dataclasses import dataclass, field
from typing import List, Optional

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import settings


@dataclass
class EmbeddingResult:
    vector: List[float]
    is_fallback: bool
    model: str
    error: Optional[str] = field(default=None)


class EmbeddingService:
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.base_url = settings.embedding_openai_base_url
        self.api_key = settings.embedding_openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def embed(self, text: str, model: str = settings.EMBEDDING_MODEL) -> EmbeddingResult:
        try:
            text = text.replace("\n", " ")
            response = await self.client.embeddings.create(
                input=[text],
                model=model,
                dimensions=self.dimensions,
            )
            embedding = response.data[0].embedding
            if len(embedding) != self.dimensions:
                raise ValueError(f"Embedding dimensions mismatch: expected {self.dimensions}, got {len(embedding)}")
            return EmbeddingResult(vector=embedding, is_fallback=False, model=model)
        except Exception as e:
            if settings.ALLOW_EMBEDDING_FALLBACK:
                logger.warning(
                    f"Embedding provider unavailable for model={model}; using zero-vector fallback ({self.dimensions} dims)"
                )
                return EmbeddingResult(
                    vector=[0.0] * self.dimensions,
                    is_fallback=True,
                    model=model,
                    error=str(e),
                )
            logger.error(f"Embedding failed using model={model} base_url={self.base_url}: {e}")
            raise


embedding_service = EmbeddingService()
