import json
import logging
import os
import re

import requests

from .config import MAX_RETRIES, OLLAMA_BASE_URL, SYSTEM_PROMPT
from .tools import get_tool_descriptions

logger = logging.getLogger(__name__)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def _build_prompt(user_input: str, memory_context: str = "") -> str:
    """Construct the full prompt string for the LLM."""
    tool_descriptions = get_tool_descriptions()
    system = SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)
    context_block = f"\nMEMORY CONTEXT (most relevant past interactions):\n{memory_context}" if memory_context else ""
    return f"{system}{context_block}\n\nUSER INPUT: {user_input}"


def _call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the raw text response."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Make sure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out after 120s.")


def _extract_json(text: str) -> dict:
    """Attempt to extract a JSON object from raw LLM output."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to pull JSON block from markdown fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("No valid JSON found in response", text, 0)


def call_llm_with_retry(user_input: str, memory_context: str = "") -> dict:
    """
    Call Ollama with retry logic. On JSON parse failure, append correction
    instruction and retry up to MAX_RETRIES times.
    """
    prompt = _build_prompt(user_input, memory_context)
    fallback = {
        "intent": "clarification_needed",
        "confidence": 0.0,
        "actions": [],
        "reasoning": "Failed to parse LLM response after retries.",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        logger.info(f"[llm] Attempt {attempt}/{MAX_RETRIES} model={OLLAMA_MODEL}")
        try:
            raw = _call_ollama(prompt)
            logger.debug(f"[llm] Raw response: {raw[:300]}")
            result = _extract_json(raw)

            # Ensure required fields exist
            result.setdefault("intent", "unknown")
            result.setdefault("confidence", 0.0)
            result.setdefault("actions", [])
            result.setdefault("reasoning", "")

            logger.info(f"[llm] Parsed intent={result['intent']} confidence={result['confidence']}")
            return result

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"[llm] Parse failed on attempt {attempt}: {e}")
            prompt += (
                "\n\nYour previous response was not valid JSON. "
                "Return ONLY a raw JSON object with no markdown, no explanation. "
                "Fix and try again."
            )
        except RuntimeError as e:
            logger.error(f"[llm] Runtime error: {e}")
            raise

    logger.error("[llm] All retries exhausted. Returning fallback.")
    return fallback


def check_ollama_health() -> dict:
    """Check if Ollama is running and the configured model is available."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
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
