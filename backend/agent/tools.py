"""
agent/tools.py — Tool registry and executors.
Uses EmailService (injected) rather than importing email internals directly.
"""
import logging
from typing import Any

from core.exceptions import AgentError, HallucinationError, MissingParameterError
from services.email.service import EmailService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "generate_email_draft": {
        "description": (
            "Generate a professional outreach email body using AI. "
            "Call this BEFORE send_email when the user has not provided the full email text."
        ),
        "required": ["recipient", "purpose"],
        "optional": ["tone", "sender_name"],
    },
    "send_email": {
        "description": (
            "Send an email via Gmail SMTP. "
            "Requires subject and body — use generate_email_draft first if needed."
        ),
        "required": ["to", "subject", "body"],
        "optional": ["cc"],
    },
    "list_sent_emails": {
        "description": "List the most recently sent emails from the outreach log.",
        "required": [],
        "optional": ["limit"],
    },
    "add_contact": {
        "description": "Add or update a lead/contact. Use this to save rich context BEFORE drafting an email for maximum personalization.",
        "required": ["email"],
        "optional": ["name", "company", "website", "linkedin", "industry", "pain_points", "recent_news", "status"],
    },
    "get_contact": {
        "description": "Retrieve full context and details for a specific contact.",
        "required": ["email"],
        "optional": [],
    },
    "list_contacts": {
        "description": "List all contacts in the database.",
        "required": [],
        "optional": [],
    },
}

TOOL_EXECUTORS: dict[str, Any] = {}


def register_tool(name: str, func) -> None:
    TOOL_EXECUTORS[name] = func
    logger.info(f"[agent.tools] Registered: {name}")


def get_tool_descriptions() -> str:
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
    tool = action.get("tool", "")
    params = action.get("params", {})

    if tool not in TOOL_REGISTRY:
        raise HallucinationError(tool)

    for required_param in TOOL_REGISTRY[tool]["required"]:
        if required_param not in params:
            raise MissingParameterError(required_param, tool)

    logger.debug(f"[agent.tools] Validation passed for tool: {tool}")


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def tool_execute(action: dict) -> dict:
    tool = action["tool"]
    params = action.get("params", {})

    if tool not in TOOL_EXECUTORS:
        raise AgentError(f"No executor registered for tool '{tool}'.")

    logger.info(f"[agent.tools] Executing tool={tool} params={params}")
    return TOOL_EXECUTORS[tool](**params)


# ---------------------------------------------------------------------------
# Executor factory — receives EmailService via injection
# ---------------------------------------------------------------------------

def build_executors(email_svc: EmailService) -> None:
    """
    Register all tool executors using the injected EmailService.
    Called once at startup from main.py.
    This pattern allows swapping EmailService for an HTTP client
    without touching any executor logic.
    """
    register_tool(
        "generate_email_draft",
        lambda recipient, purpose, tone="professional", sender_name="the sender": (
            email_svc.generate_draft(
                recipient=recipient,
                purpose=purpose,
                tone=tone,
                sender_name=sender_name,
            )
        ),
    )

    register_tool(
        "send_email",
        lambda to, subject, body, cc=None: email_svc.send(
            to=to, subject=subject, body=body, cc=cc
        ),
    )

    register_tool(
        "list_sent_emails",
        lambda limit=5: email_svc.list_sent(limit=limit),
    )

    register_tool(
        "add_contact",
        lambda email, **kwargs: email_svc.add_contact(email=email, **kwargs),
    )

    register_tool(
        "get_contact",
        lambda email: email_svc.get_contact(email=email),
    )

    register_tool(
        "list_contacts",
        lambda: email_svc.list_contacts(),
    )
