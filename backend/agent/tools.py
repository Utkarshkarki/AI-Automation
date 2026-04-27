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
    "generate_email": {
        "description": (
            "Generate a professional outreach email body using AI. "
            "Call this BEFORE send_email when the user has not provided the full email text."
        ),
        "required": ["recipient", "purpose"],
        "optional": ["tone", "sender_name"],
    },
    "send_email": {
        "description": (
            "Send a single email via Gmail SMTP immediately. "
            "Requires subject and body — use generate_email first if needed."
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
    "create_template": {
        "description": "Create a reusable email template. Use {{name}}, {{company}}, {{industry}} as variables.",
        "required": ["name", "subject", "body"],
        "optional": [],
    },
    "list_templates": {
        "description": "List all available email templates.",
        "required": [],
        "optional": [],
    },
    "create_campaign": {
        "description": "Create a new outreach campaign.",
        "required": ["name"],
        "optional": ["description"],
    },
    "schedule_campaign": {
        "description": "Start sending a campaign to a list of contacts. Can schedule multi-day follow-up sequences (e.g. Day 0, Day 3, Day 7).",
        "required": ["campaign_id", "template_id", "contact_emails"],
        "optional": ["delay_days"],
    },
    "track_replies": {
        "description": "Check the database for detected email replies and their AI-classified intents (interested, unsubscribe, etc).",
        "required": [],
        "optional": [],
    },
    "pause_campaign": {
        "description": "Pause all currently queued emails for a specific campaign.",
        "required": ["campaign_id"],
        "optional": [],
    },
    "get_analytics": {
        "description": "Get overall deliverability analytics: sent, queued, failed, and cancelled emails.",
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
        "generate_email",
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
    
    register_tool(
        "create_template",
        lambda name, subject, body: email_svc.create_template(name=name, subject=subject, body=body),
    )

    register_tool(
        "list_templates",
        lambda: email_svc.list_templates(),
    )

    register_tool(
        "create_campaign",
        lambda name, description=None: email_svc.create_campaign(name=name, description=description),
    )

    register_tool(
        "schedule_campaign",
        lambda campaign_id, template_id, contact_emails, delay_days=None: email_svc.schedule_campaign(campaign_id=campaign_id, template_id=template_id, contact_emails=contact_emails, delay_days=delay_days),
    )

    register_tool(
        "track_replies",
        lambda: email_svc.track_replies(),
    )

    register_tool(
        "pause_campaign",
        lambda campaign_id: email_svc.pause_campaign(campaign_id=campaign_id),
    )

    register_tool(
        "get_analytics",
        lambda: email_svc.get_analytics(),
    )
