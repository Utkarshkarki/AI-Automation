"""
agent/loop.py — Orchestration layer.
Receives all services via constructor injection. Does NOT import service internals.
"""
import logging

from core.config import CONFIDENCE_THRESHOLD, MAX_ACTIONS_PER_RESPONSE

from services.llm.service import LLMService
from services.memory.service import MemoryService
from services.metrics.service import MetricsService

from .rate_limiter import increment_rate, is_rate_limited
from .tools import get_tool_descriptions, validate_tool_call, tool_execute

logger = logging.getLogger(__name__)


class AgentLoop:
    """
    Main agent orchestration loop.
    All service dependencies are injected — making this trivially testable
    and easy to rewire when services become standalone microservices.
    """

    def __init__(
        self,
        llm: LLMService,
        memory: MemoryService,
        metrics: MetricsService,
    ):
        self.llm = llm
        self.memory = memory
        self.metrics = metrics

    def run(self, user_input: str) -> dict:
        """
        Execute the full agent loop for a single user input.

        Steps:
          1. Retrieve + rank relevant memories from FAISS
          2. Build prompt with memory context and call LLM (with retry)
          3. If confidence < threshold → return review status
          4. For each action: validate → rate-check → execute → record
          5. Store interaction in memory
          6. Return structured results
        """
        logger.info(f"[agent.loop] Processing: {user_input[:80]}...")

        # --- Memory ---
        raw_memories = self.memory.retrieve(user_input)
        ranked = self.memory.rank(user_input, raw_memories)
        memory_text = self.memory.format(ranked)

        # --- LLM ---
        tool_descriptions = get_tool_descriptions()
        output = self.llm.call_with_retry(user_input, tool_descriptions, memory_text)
        self.metrics.record_intent(output.get("intent", "unknown"))

        # --- Low confidence → human review ---
        if output.get("confidence", 0) < CONFIDENCE_THRESHOLD:
            logger.warning(
                f"[agent.loop] Low confidence={output['confidence']} → requesting review"
            )
            self.memory.store(user_input, output, [])
            return {
                "status": "review",
                "output": output,
                "results": [],
                "memory_context": ranked,
            }

        # --- Action execution ---
        results = []
        for action in output.get("actions", [])[:MAX_ACTIONS_PER_RESPONSE]:
            tool = action.get("tool", "unknown")
            try:
                validate_tool_call(action)

                if is_rate_limited(tool):
                    raise Exception(f"Tool '{tool}' is currently rate limited.")

                result = tool_execute(action)
                increment_rate(tool)
                self.metrics.record_tool_result(tool, "success")
                results.append({"tool": tool, "status": "success", "result": result})
                logger.info(f"[agent.loop] Tool={tool} executed successfully")

            except Exception as e:
                logger.error(f"[agent.loop] Tool={tool} failed: {e}")
                self.metrics.record_tool_result(tool, "fail")
                results.append({"tool": tool, "status": "fail", "error": str(e)})

        # --- Persist memory ---
        self.memory.store(user_input, output, results)

        return {
            "status": "ok",
            "output": output,
            "results": results,
            "memory_context": [
                {k: v for k, v in m.items() if k != "embedding"}
                for m in ranked
            ],
        }
