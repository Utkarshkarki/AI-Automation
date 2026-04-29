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

from .database import SessionLocal
from .repository import (
    create_sent_email,
    get_recent_emails,
    create_or_update_contact,
    get_contact_by_email,
    list_all_contacts,
    create_template,
    get_template,
    list_templates,
    create_campaign,
    get_campaign,
    link_contact_to_campaign,
)
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
        user_id: str = None,
    ) -> dict:
        """
        Ask the local LLM to write an outreach email.
        Pulls rich contact context from the database if available.
        Returns {"subject": str, "body": str, "recipient": str}.
        """
        # Fetch rich context
        with SessionLocal() as db:
            contact = get_contact_by_email(db, recipient, user_id=user_id)
            
        context_block = ""
        if contact:
            context_block = "Use this context to hyper-personalize the email:\n"
            if contact.get("name"): context_block += f"- Recipient Name: {contact['name']}\n"
            if contact.get("company"): context_block += f"- Company: {contact['company']}\n"
            if contact.get("industry"): context_block += f"- Industry: {contact['industry']}\n"
            if contact.get("pain_points"): context_block += f"- Pain Points: {contact['pain_points']}\n"
            if contact.get("recent_news"): context_block += f"- Recent News: {contact['recent_news']}\n"
        
        prompt = (
            f"Write a {tone} outreach email.\n"
            f"From: {sender_name}\n"
            f"To: {recipient}\n"
            f"Purpose: {purpose}\n\n"
            f"{context_block}\n"
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

    def send(self, to: str, subject: str, body: str, cc: str = None, user_id: str = None) -> dict:
        """
        Send a real email via Gmail SMTP and persist to the SQLite DB.
        Returns a confirmation dict.
        """
        smtp_send(to=to, subject=subject, body=body, cc=cc)

        with SessionLocal() as db:
            create_sent_email(db, sender=GMAIL_ADDRESS, to=to, subject=subject, body=body, cc=cc, user_id=user_id)

        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "from": GMAIL_ADDRESS,
        }

    def list_sent(self, limit: int = 5, user_id: str = None) -> dict:
        """Return the most recently sent emails from the database."""
        with SessionLocal() as db:
            emails = get_recent_emails(db, limit=int(limit), user_id=user_id)
        return {"count": len(emails), "emails": emails}

    def add_contact(self, email: str, user_id: str = None, **kwargs) -> dict:
        """Add or update a contact with rich personalization fields."""
        with SessionLocal() as db:
            contact = create_or_update_contact(db, email, user_id=user_id, **kwargs)
            return {
                "status": "success",
                "message": f"Contact {email} saved.",
                "id": contact.id
            }
            
    def get_contact(self, email: str, user_id: str = None) -> dict:
        """Retrieve full details for a specific contact."""
        with SessionLocal() as db:
            contact = get_contact_by_email(db, email, user_id=user_id)
            if not contact:
                return {"error": f"Contact {email} not found."}
            return contact
            
    def list_contacts(self, user_id: str = None) -> dict:
        """List all contacts in the database."""
        with SessionLocal() as db:
            contacts = list_all_contacts(db, user_id=user_id)
            return {"count": len(contacts), "contacts": contacts}

    def create_template(self, name: str, subject: str, body: str, user_id: str = None) -> dict:
        """Create a reusable email template with {{variables}}."""
        with SessionLocal() as db:
            t = create_template(db, name, subject, body, user_id=user_id)
            return {"status": "success", "template_id": t.id}
            
    def list_templates(self, user_id: str = None) -> dict:
        """List all available templates."""
        with SessionLocal() as db:
            templates = list_templates(db, user_id=user_id)
            return {"count": len(templates), "templates": templates}
            
    def create_campaign(self, name: str, description: str = None, user_id: str = None) -> dict:
        """Create a new campaign."""
        with SessionLocal() as db:
            c = create_campaign(db, name, description, user_id=user_id)
            return {"status": "success", "campaign_id": c.id}
            
    def schedule_campaign(self, campaign_id: int, template_id: int, contact_emails: list[str], delay_days: list[int] = None, user_id: str = None) -> dict:
        """Queue a list of contacts into a sequence campaign for background sending."""
        if delay_days is None:
            delay_days = [0]
        queued = 0
        with SessionLocal() as db:
            for email in contact_emails:
                try:
                    link_contact_to_campaign(db, email, campaign_id, template_id, delay_days, user_id=user_id)
                    queued += len(delay_days)
                except Exception as e:
                    logger.error(f"Failed to queue {email}: {e}")
                    
        return {"status": "success", "total_emails_queued": queued}

    def track_replies(self, user_id: str = None) -> dict:
        """Get stats on received replies from the database."""
        from .models import Event, Email as EmailModel
        with SessionLocal() as db:
            query = db.query(Event).join(EmailModel)
            if user_id:
                query = query.filter(EmailModel.user_id == user_id)
            replies = query.filter(Event.event_type == "reply").all()
            
            intents = {}
            for r in replies:
                try:
                    meta = json.loads(r.metadata_json)
                    intent = meta.get("intent", "unknown")
                    intents[intent] = intents.get(intent, 0) + 1
                except:
                    pass
                    
            return {
                "total_replies": len(replies),
                "breakdown": intents
            }

    def pause_campaign(self, campaign_id: int, user_id: str = None) -> dict:
        """Pause all queued emails for a campaign."""
        from .models import Email as EmailModel
        with SessionLocal() as db:
            query = db.query(EmailModel).filter(
                EmailModel.campaign_id == campaign_id,
                EmailModel.status == "queued"
            )
            if user_id:
                query = query.filter(EmailModel.user_id == user_id)
            updated = query.update({"status": "paused"})
            db.commit()
            return {"status": "success", "paused_emails_count": updated}

    def get_analytics(self, user_id: str = None) -> dict:
        """Get overall email deliverability analytics."""
        from .models import Email as EmailModel
        with SessionLocal() as db:
            def q(status):
                query = db.query(EmailModel).filter(EmailModel.status == status)
                if user_id:
                    query = query.filter(EmailModel.user_id == user_id)
                return query.count()
                
            sent = q("sent")
            queued = q("queued")
            failed = q("failed")
            cancelled = q("cancelled")
            
            return {
                "sent": sent,
                "queued": queued,
                "failed": failed,
                "cancelled_due_to_replies": cancelled
            }

