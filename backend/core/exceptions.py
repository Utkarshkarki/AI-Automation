"""
core/exceptions.py — All custom exception types for the application.
Centralised here so every service and the orchestrator uses the same types.
"""


class AgentError(Exception):
    """Base class for all agent errors."""
    pass


class HallucinationError(AgentError):
    """Raised when the LLM produces a tool name not in the registry."""
    def __init__(self, tool_name: str):
        super().__init__(
            f"Tool '{tool_name}' is not in the tool registry (possible hallucination)."
        )
        self.tool_name = tool_name


class MissingParameterError(AgentError):
    """Raised when a required tool parameter is absent from an action."""
    def __init__(self, param: str, tool: str):
        super().__init__(
            f"Missing required parameter '{param}' for tool '{tool}'."
        )
        self.param = param
        self.tool = tool


class LLMConnectionError(AgentError):
    """Raised when the backend cannot reach the Ollama server."""
    pass


class EmailDeliveryError(AgentError):
    """Raised when an email fails to send via SMTP."""
    pass


class CredentialsNotConfiguredError(AgentError):
    """Raised when required credentials (e.g. Gmail) are missing."""
    pass
