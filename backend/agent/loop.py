import logging

from .llm import call_llm_with_retry
from .memory import (
    format_memories,
    rank_memories,
    retrieve_memory,
    store_memory,
)
from .metrics import record_intent, record_tool_result
from .rate_limiter import increment_rate, is_rate_limited
from .tools import validate_tool_call, tool_execute

logger = logging.getLogger(__name__)


def agent_loop(user_input: str) -> dict:
    """
    Main agent execution loop.

    Steps:
      1. Retrieve relevant memories from FAISS
      2. Rank memories by semantic similarity + recency
      3. Build prompt with memory context and call LLM (with retry)
      4. If confidence < 0.5 → return review status
      5. For each action: validate → rate-check → execute → record
      6. Store this interaction in memory
      7. Return structured results

    Returns:
        dict with keys: status, output, results, memory_context
    """
    logger.info(f"[loop] Processing input: {user_input[:80]}...")

    # --- Memory ---
    raw_memories = retrieve_memory(user_input)
    ranked = rank_memories(user_input, raw_memories)
    memory_text = format_memories(ranked)

    # --- LLM Call ---
    output = call_llm_with_retry(user_input, memory_context=memory_text)
    record_intent(output.get("intent", "unknown"))

    # --- Low confidence → human review ---
    if output.get("confidence", 0) < 0.5:
        logger.warning(f"[loop] Low confidence={output['confidence']} → requesting review")
        store_memory(user_input, output, [])
        return {
            "status": "review",
            "output": output,
            "results": [],
            "memory_context": ranked,
        }

    # --- Action execution ---
    results = []
    actions = output.get("actions", [])

    # Guard: max 3 actions
    for action in actions[:3]:
        tool = action.get("tool", "unknown")
        try:
            validate_tool_call(action)

            if is_rate_limited(tool):
                raise Exception(f"Tool '{tool}' is currently rate limited.")

            result = tool_execute(action)
            increment_rate(tool)
            record_tool_result(tool, "success")

            results.append({
                "tool": tool,
                "status": "success",
                "result": result,
            })
            logger.info(f"[loop] Tool={tool} executed successfully")

        except Exception as e:
            logger.error(f"[loop] Tool={tool} failed: {e}")
            record_tool_result(tool, "fail")
            results.append({
                "tool": tool,
                "status": "fail",
                "error": str(e),
            })

    # --- Persist memory ---
    store_memory(user_input, output, results)

    return {
        "status": "ok",
        "output": output,
        "results": results,
        "memory_context": [
            {k: v for k, v in m.items() if k != "embedding"}
            for m in ranked
        ],
    }
