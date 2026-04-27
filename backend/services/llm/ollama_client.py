"""
services/llm/ollama_client.py — Private: raw HTTP client for Ollama.
Only used internally by LLMService.
"""
import logging

import requests

from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from core.exceptions import LLMConnectionError

logger = logging.getLogger(__name__)


def call_generate(prompt: str) -> str:
    """POST /api/generate to Ollama and return the raw text response."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0},
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
        raise LLMConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Make sure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise LLMConnectionError("Ollama request timed out after 120s.")


def fetch_tags() -> dict:
    """GET /api/tags — returns available models from Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise LLMConnectionError(f"Cannot reach Ollama: {e}")
