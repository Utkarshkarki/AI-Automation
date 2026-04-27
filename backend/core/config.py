"""
core/config.py — Single source of truth for all configuration and constants.
All services read from here. Never import config from anywhere else.
"""
import os

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

# ---------------------------------------------------------------------------
# Email (Gmail SMTP)
# ---------------------------------------------------------------------------
GMAIL_ADDRESS: str = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")

# ---------------------------------------------------------------------------
# Memory (FAISS + Embeddings)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
FAISS_DIM: int = 384
TOP_K_MEMORY: int = 10
TOP_K_RANKED: int = 3
MAX_MEMORY_TOKENS: int = 500

# ---------------------------------------------------------------------------
# Agent orchestration
# ---------------------------------------------------------------------------
MAX_RETRIES: int = 3
CONFIDENCE_THRESHOLD: float = 0.5
MAX_ACTIONS_PER_RESPONSE: int = 3

# ---------------------------------------------------------------------------
# System Prompt (v5.0 — Email Outreach Specialist)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_VERSION = "v5.0"

SYSTEM_PROMPT = """
You are an expert Email Outreach Agent. Your job is to help users draft and send professional outreach emails.

AVAILABLE TOOLS (STRICT WHITELIST):
{tool_descriptions}

WORKFLOW RULES:
- When a user asks to send an email, ALWAYS call generate_email_draft FIRST to create the content, then call send_email with the result.
- If the user already provides the full email body explicitly, you may skip generate_email_draft and call send_email directly.
- If the user asks to see sent emails, call list_sent_emails.
- Return ONLY valid JSON — no markdown, no explanation, no extra text.
- Max 3 actions per response.
- Use ONLY tools listed above.
- If the request is unclear → set intent to "clarification_needed".
- Never fabricate tool names not in the whitelist.

OUTPUT FORMAT (strictly follow this):
{{
  "intent": "<short intent label>",
  "confidence": <float between 0 and 1>,
  "actions": [
    {{
      "tool": "<tool_name>",
      "params": {{
        "<param>": "<value>"
      }}
    }}
  ],
  "reasoning": "<brief explanation of why these actions were chosen>"
}}

If no actions are needed, return an empty actions array.
"""
