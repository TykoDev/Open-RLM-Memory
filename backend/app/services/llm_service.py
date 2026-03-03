import json
from dataclasses import dataclass
from typing import Any

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import settings

VALID_MEMORY_TYPES = frozenset(
    {"knowledge", "context", "summary", "event", "code_snippet", "preference"}
)


@dataclass
class ClassificationResult:
    memory_type: str
    tags: list[str]
    classified_by_llm: bool


class LLMService:
    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

    async def complete(
        self,
        prompt: str,
        model: str = settings.OPENAI_MODEL,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM completion failed using model={model} base_url={settings.OPENAI_BASE_URL}: {e}")
            raise

    def parse_json(self, text: str) -> Any:
        """Helper to parse JSON from LLM output (handling potential markdown blocks)."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM: {e}")
            # Return empty list as fallback for array expectations
            if text.strip().startswith("["):
                return []
            raise ValueError("Invalid JSON from LLM")

    async def classify_memory(self, content: str) -> ClassificationResult:
        """Classify memory content into a type and generate tags using LLM."""
        try:
            truncated = content[:500]
            prompt = (
                "Classify the following text and return a JSON object with two fields:\n"
                '- "type": one of [knowledge, context, summary, event, code_snippet, preference]\n'
                '- "tags": a list of 1-5 lowercase single-word tags describing the content\n\n'
                "Rules:\n"
                "- knowledge: facts, definitions, how-to information\n"
                "- context: project context, environment details, current state\n"
                "- summary: summaries of conversations or documents\n"
                "- event: things that happened, log entries, incidents\n"
                "- code_snippet: code blocks, configurations, scripts\n"
                "- preference: user preferences, settings, style choices\n\n"
                "Return ONLY valid JSON, no other text.\n\n"
                f"Text: {truncated}"
            )
            raw = await self.complete(prompt, max_tokens=150, temperature=0.1)
            parsed = self.parse_json(raw)

            # Validate type
            memory_type = parsed.get("type", "knowledge")
            if memory_type not in VALID_MEMORY_TYPES:
                memory_type = "knowledge"

            # Sanitize tags
            raw_tags = parsed.get("tags", [])
            if not isinstance(raw_tags, list):
                raw_tags = []
            seen = set()
            tags = []
            for tag in raw_tags:
                if not isinstance(tag, str):
                    continue
                cleaned = tag.lower().strip()
                if cleaned and cleaned not in seen:
                    seen.add(cleaned)
                    tags.append(cleaned)
                if len(tags) >= 5:
                    break

            return ClassificationResult(
                memory_type=memory_type,
                tags=tags,
                classified_by_llm=True,
            )
        except Exception as e:
            logger.warning(f"LLM classification failed, using defaults: {e}")
            return ClassificationResult(
                memory_type="knowledge",
                tags=[],
                classified_by_llm=False,
            )

    def create_specialized(self, role: str) -> "LLMService":
        # In a real impl, this might return a configured instance with system prompts
        # For MVP, we return self
        return self


llm_service = LLMService()
