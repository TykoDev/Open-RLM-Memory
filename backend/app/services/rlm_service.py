from typing import Any, Dict, List, Optional

from loguru import logger

from app.rlm_engine.dispatcher import SubLMDispatcher
from app.rlm_engine.repl import REPLEnvironment
from app.services.llm_service import llm_service


class RLMService:
    """RLM-powered search and reasoning engine."""

    def __init__(self):
        self.llm = llm_service
        self.repl = REPLEnvironment()
        self.dispatcher = SubLMDispatcher(self.llm)

    async def create_context(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create RLM context for user session."""
        # Reuse existing session if provided and valid
        if session_id and session_id in self.repl.sessions:
            logger.debug(f"Reusing existing RLM session: {session_id}")
            current_session_id = session_id
        else:
            current_session_id = self.repl.create_session()

        context = {
            "user_id": user_id,
            "session_id": current_session_id,
            "from_cache": False,
            "variables": {},
        }
        return context

    async def decompose_query(self, query: str) -> List[str]:
        """Break complex query into sub-queries using RLM."""
        prompt = f"""
Decompose this query into 2-3 specific sub-queries that would help answer it:
Query: {query}

Provide sub-queries as a JSON list of strings.
"""
        try:
            response = await self.llm.complete(prompt)
            return self.llm.parse_json(response)
        except Exception as e:
            logger.warning(f"Failed to decompose query: {query}, error: {e}")
            return [query]

    async def re_rank_results(
        self,
        original_query: str,
        results: List[Any],
        context: Dict[str, Any],
    ) -> List[Any]:
        """Re-rank results using RLM evaluation."""
        if not results:
            return []

        # Prepare data for REPL (remove non-serializable objects)
        repl_results = []
        for r in results:
            # Optimize: copy and pop is significantly faster than dict comprehension
            d = dict(r)
            d.pop("memory_obj", None)
            repl_results.append(d)

        session_id = context["session_id"]

        # Load data into REPL
        import json
        setup_code = f"""
results = {json.dumps(repl_results)}
query = {json.dumps(original_query)}
"""
        await self.repl.execute(setup_code, session_id)

        eval_code = """
def calculate_relevance(item, query):
    score = item.get('score', 0)
    content = item.get('content', '').lower()
    q_words = query.lower().split()
    match_count = sum(1 for w in q_words if w in content)
    boost = match_count * 0.1
    return score + boost

ranked_results = sorted(results, key=lambda x: calculate_relevance(x, query), reverse=True)
ranked_ids = [r['id'] for r in ranked_results]
"""
        await self.repl.execute(eval_code, session_id)

        ranked_ids = await self.repl.evaluate("ranked_ids", session_id)

        # Re-order original results
        result_map = {r['id']: r for r in results}
        ordered_results = []
        for rid in ranked_ids:
            if rid in result_map:
                ordered_results.append(result_map[rid])

        return ordered_results

rlm_service = RLMService()
