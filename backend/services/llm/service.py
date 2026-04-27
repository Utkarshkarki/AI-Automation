"""
services/llm/service.py — PUBLIC API for the LLM domain.

This is the ONLY file other modules are allowed to import from this package.

To extract into a standalone microservice later:
  1. Deploy services/llm/ as its own FastAPI app.
  2. Replace this class body with HTTP calls to that new service.
  3. Nothing else in the codebase needs to change.
"""
import json
import logging
import re

from core.config import MAX_RETRIES, OLLAMA_MODEL, SYSTEM_PROMPT
from core.exceptions import LLMConnectionError

from .ollama_client import call_generate, fetch_tags

logger = logging.getLogger(__name__)


class LLMService:
    """
    Public facade for all LLM interactions.
    Instantiated once in main.py and injected wherever needed.
    """

    def _build_prompt(self, user_input: str, tool_descriptions: str, memory_context: str = "") -> str:
        system = SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)
        context_block = (
            f"\nMEMORY CONTEXT (most relevant past interactions):\n{memory_context}"
            if memory_context else ""
        )
        return f"{system}{context_block}\n\nUSER INPUT: {user_input}"

    def _extract_json(self, text: str) -> dict:
        """Try multiple strategies to extract a JSON object from raw LLM output."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("No valid JSON found in LLM response", text, 0)

    def call_with_retry(
        self,
        user_input: str,
        tool_descriptions: str,
        memory_context: str = "",
    ) -> dict:
        """
        Call Ollama with retry logic. On JSON parse failure, appends a correction
        instruction and retries up to MAX_RETRIES times.
        Returns a parsed dict with keys: intent, confidence, actions, reasoning.
        """
        prompt = self._build_prompt(user_input, tool_descriptions, memory_context)
        fallback = {
            "intent": "clarification_needed",
            "confidence": 0.0,
            "actions": [],
            "reasoning": "Failed to parse LLM response after retries.",
        }

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"[llm.service] Attempt {attempt}/{MAX_RETRIES} model={OLLAMA_MODEL}")
            try:
                raw = call_generate(prompt)
                logger.debug(f"[llm.service] Raw response: {raw[:300]}")
                result = self._extract_json(raw)

                result.setdefault("intent", "unknown")
                result.setdefault("confidence", 0.0)
                result.setdefault("actions", [])
                result.setdefault("reasoning", "")

                logger.info(
                    f"[llm.service] Parsed intent={result['intent']} "
                    f"confidence={result['confidence']}"
                )
                return result

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"[llm.service] Parse failed on attempt {attempt}: {e}")
                prompt += (
                    "\n\nYour previous response was not valid JSON. "
                    "Return ONLY a raw JSON object with no markdown, no explanation. "
                    "Fix and try again."
                )
            except LLMConnectionError:
                raise

        logger.error("[llm.service] All retries exhausted. Returning fallback.")
        return fallback

    def check_health(self) -> dict:
        """Check if Ollama is running and the configured model is available."""
        try:
            data = fetch_tags()
            models = [m["name"] for m in data.get("models", [])]
            available = OLLAMA_MODEL in models or any(OLLAMA_MODEL in m for m in models)
            return {
                "ollama_running": True,
                "model": OLLAMA_MODEL,
                "model_available": available,
                "available_models": models,
            }
        except Exception as e:
            return {
                "ollama_running": False,
                "model": OLLAMA_MODEL,
                "model_available": False,
                "error": str(e),
            }
