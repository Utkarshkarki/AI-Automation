"""
services/email/service.py — PUBLIC API for the Email domain.

This is the ONLY file other modules are allowed to import from this package.
Internal implementation (smtp.py, log.py) is private.

To extract this into a standalone microservice later:
  1. Deploy services/email/ as its own FastAPI app.
  2. Replace this class body with HTTP calls to that new service.
  3. Nothing else in the codebase needs to change.
"""
import json
import logging
import re
from datetime import datetime

import requests

from core.config import GMAIL_ADDRESS, OLLAMA_BASE_URL, OLLAMA_MODEL
from core.exceptions import AgentError

from .log import append_to_log, get_recent
from .smtp import smtp_send

logger = logging.getLogger(__name__)


class EmailService:
    """
    Public facade for all email-related operations.
    Instantiated once in main.py and injected wherever needed.
    """

    def generate_draft(
        self,
        recipient: str,
        purpose: str,
        tone: str = "professional",
        sender_name: str = "the sender",
    ) -> dict:
        """
        Ask the local LLM to write an outreach email.
        Returns {"subject": str, "body": str, "recipient": str}.
        """
        prompt = (
            f"Write a {tone} outreach email.\n"
            f"From: {sender_name}\n"
            f"To: {recipient}\n"
            f"Purpose: {purpose}\n\n"
            "Return ONLY a JSON object with exactly two keys: "
            "'subject' (string) and 'body' (string). "
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

            try:
                draft = json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                draft = json.loads(match.group(0)) if match else {}

            subject = draft.get("subject", f"Outreach: {purpose[:50]}")
            body = draft.get("body", raw)

            logger.info(f"[email.service] Draft generated for recipient={recipient}")
            return {"subject": subject, "body": body, "recipient": recipient}

        except Exception as e:
            raise AgentError(f"Failed to generate email draft: {e}")

    def send(self, to: str, subject: str, body: str, cc: str = None) -> dict:
        """
        Send a real email via Gmail SMTP and persist to the sent log.
        Returns a confirmation dict.
        """
        smtp_send(to=to, subject=subject, body=body, cc=cc)

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": GMAIL_ADDRESS,
            "to": to,
            "cc": cc,
            "subject": subject,
            "body_preview": body[:200],
            "status": "sent",
        }
        append_to_log(entry)

        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "from": GMAIL_ADDRESS,
        }

    def list_sent(self, limit: int = 5) -> dict:
        """Return the most recently sent emails from the local log."""
        emails = get_recent(limit=int(limit))
        return {"count": len(emails), "emails": emails}
