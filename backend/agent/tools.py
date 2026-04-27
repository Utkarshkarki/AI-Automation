import logging
from typing import Any

logger = logging.getLogger(__name__)


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
    "send_email": {
        "description": "Send an email to a recipient.",
        "required": ["to", "message"],
        "optional": ["cc", "subject"],
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
        req = ", ".join(schema["required"])
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
# Stub Executors
# ---------------------------------------------------------------------------

def send_email_executor(to: str, message: str, cc: str = None, subject: str = None) -> dict:
    logger.info(f"[send_email] to={to} subject={subject}")
    return {
        "status": "sent",
        "to": to,
        "subject": subject or "(no subject)",
        "preview": message[:100],
    }





# Register all stubs at module load time
register_tool("send_email", send_email_executor)

