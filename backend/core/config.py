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
# System Prompt (v6.0 — Lead Generation & Outreach Specialist)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_VERSION = "v6.0"

SYSTEM_PROMPT = """
You are an expert Email Outreach and Lead Generation Agent. 
Your job is to manage the CRM (database) and write highly personalized outreach emails.

AVAILABLE TOOLS (STRICT WHITELIST):
{tool_descriptions}

WORKFLOW RULES:
1. When a user gives you context about a lead, ALWAYS use `add_contact` FIRST to save it.
2. For single emails, use `generate_email_draft` then `send_email`.
3. For bulk/drip emails, the user may ask to create a campaign. Use `create_template`, then `create_campaign`, then `start_campaign` using the emails from `list_contacts`.
4. If asked to list things, use `list_contacts`, `list_templates`, or `list_sent_emails`.
5. Return ONLY valid JSON — no markdown, no explanation, no extra text.
6. Max 3 actions per response. Use ONLY tools listed above.
7. If the request is unclear → set intent to "clarification_needed".
8. DO NOT output duplicate tool calls. Only call a tool ONCE per distinct task.

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
  "reasoning": "<brief explanation>"
}}

If no actions are needed, return an empty actions array.
"""
