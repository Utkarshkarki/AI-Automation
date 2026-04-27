import logging
import os
from typing import Any

import requests

from .email_service import get_sent_emails, send_real_email

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


class AgentError(Exception):
    """Base class for all agent errors."""
    pass


class HallucinationError(AgentError):
    """Raised when the LLM produces a tool name not in the registry."""
    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' is not in the tool registry (possible hallucination).")
        self.tool_name = tool_name


class MissingParameterError(AgentError):
    """Raised when a required tool parameter is missing from the action."""
    def __init__(self, param: str, tool: str):
        super().__init__(f"Missing required parameter '{param}' for tool '{tool}'.")
        self.param = param
        self.tool = tool


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, dict[str, list[str]]] = {
    "generate_email_draft": {
        "description": (
            "Generate a professional outreach email body using AI. "
            "Call this BEFORE send_email when the user has not provided the full email text."
        ),
        "required": ["recipient", "purpose"],
        "optional": ["tone", "sender_name"],
    },
    "send_email": {
        "description": "Send an email via Gmail SMTP. Requires subject and body — use generate_email_draft first if needed.",
        "required": ["to", "subject", "body"],
        "optional": ["cc"],
    },
    "list_sent_emails": {
        "description": "List the most recently sent emails from the outreach log.",
        "required": [],
        "optional": ["limit"],
    },
}

TOOL_EXECUTORS: dict[str, Any] = {}


def register_tool(name: str, func) -> None:
    """Register an executor function for a named tool."""
    TOOL_EXECUTORS[name] = func
    logger.info(f"[tools] Registered executor for tool: {name}")


def get_tool_descriptions() -> str:
    """Return a formatted string of all available tools and their schemas."""
    lines = []
    for name, schema in TOOL_REGISTRY.items():
        req = ", ".join(schema["required"]) if schema["required"] else "none"
        opt = ", ".join(schema["optional"]) if schema["optional"] else "none"
        lines.append(
            f"- {name}: {schema['description']} | required: [{req}] | optional: [{opt}]"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_tool_call(action: dict) -> None:
    """
    Validate a single action dict against the tool registry.
    Raises HallucinationError or MissingParameterError on failure.
    """
    tool = action.get("tool", "")
    params = action.get("params", {})

    if tool not in TOOL_REGISTRY:
        raise HallucinationError(tool)

    schema = TOOL_REGISTRY[tool]
    for required_param in schema["required"]:
        if required_param not in params:
            raise MissingParameterError(required_param, tool)

    logger.debug(f"[tools] Validation passed for tool: {tool}")


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def tool_execute(action: dict) -> dict:
    """Execute a validated tool action."""
    tool = action["tool"]
    params = action.get("params", {})

    if tool not in TOOL_EXECUTORS:
        raise AgentError(f"No executor registered for tool '{tool}'.")

    logger.info(f"[tools] Executing tool={tool} params={params}")
    return TOOL_EXECUTORS[tool](**params)


# ---------------------------------------------------------------------------
# Tool Executors
# ---------------------------------------------------------------------------

def generate_email_draft_executor(
    recipient: str,
    purpose: str,
    tone: str = "professional",
    sender_name: str = "the sender",
) -> dict:
    """
    Uses the local Ollama LLM to generate an email body.
    Returns the draft subject and body as a dict.
    """
    prompt = (
        f"Write a {tone} outreach email.\n"
        f"From: {sender_name}\n"
        f"To: {recipient}\n"
        f"Purpose: {purpose}\n\n"
        "Return ONLY a JSON object with two keys: 'subject' (string) and 'body' (string). "
        "No markdown, no explanation."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.7},
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "{}")

        import json, re
        try:
            draft = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            draft = json.loads(match.group(0)) if match else {}

        subject = draft.get("subject", f"Outreach: {purpose[:50]}")
        body = draft.get("body", raw)

        logger.info(f"[generate_email_draft] Generated draft for recipient={recipient}")
        return {"subject": subject, "body": body, "recipient": recipient}

    except Exception as e:
        raise AgentError(f"Failed to generate email draft: {e}")


def send_email_executor(to: str, subject: str, body: str, cc: str = None) -> dict:
    """Send a real email via Gmail SMTP."""
    return send_real_email(to=to, subject=subject, body=body, cc=cc)


def list_sent_emails_executor(limit: int = 5) -> dict:
    """Return a list of recently sent emails from the log."""
    emails = get_sent_emails(limit=int(limit))
    return {
        "count": len(emails),
        "emails": emails,
    }


# Register all executors at module load time
register_tool("generate_email_draft", generate_email_draft_executor)
register_tool("send_email", send_email_executor)
register_tool("list_sent_emails", list_sent_emails_executor)
