from typing import Any, Dict

from app.services.llm_service import LLMService


class SubLMDispatcher:
    """Routes queries to sub-LMs for specialized processing."""

    def __init__(self, llm: LLMService):
        self.llm = llm
        self.sub_llm_cache = {}

    async def dispatch_query(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> Any:
        """Dispatch query to appropriate sub-LM."""
        # Determine query type
        query_type = await self._classify_query(query)

        # Get or create sub-LM
        sub_llm = await self._get_sub_llm(query_type)

        # In a real implementation, this would delegate to a specialized handler
        # For MVP, we just return the query type for now
        return {"query_type": query_type, "processed": True}

    async def _classify_query(self, query: str) -> str:
        """Classify query type for routing."""
        prompt = f"""
Classify this query into one category:
- factual: factual information lookup
- reasoning: complex reasoning
- code: code generation/analysis
- summary: summarization
- other: other

Query: {query}

Response (single word):
"""
        try:
            response = await self.llm.complete(prompt)
            return response.strip().lower()
        except Exception:
            # Fallback
            return "other"

    async def _get_sub_llm(self, query_type: str):
        """Get or create sub-LM for query type."""
        if query_type not in self.sub_llm_cache:
            # Create specialized sub-LM
            self.sub_llm_cache[query_type] = self.llm.create_specialized(
                query_type
            )
        return self.sub_llm_cache[query_type]
