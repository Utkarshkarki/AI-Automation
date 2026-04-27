"""
services/email/imap_worker.py — IMAP reply detection and LLM classification.
"""
import email
import imaplib
import logging
from email.header import decode_header

from core.celery_app import celery_app
from core.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from services.email.database import SessionLocal
from services.email.models import Contact, Email as EmailModel, Event
from services.llm.service import LLMService

logger = logging.getLogger(__name__)

# IMAP Settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

llm_svc = LLMService()

def decode_mime_words(s):
    if not s:
        return ""
    decoded_words = decode_header(s)
    result = ""
    for word, charset in decoded_words:
        if isinstance(word, bytes):
            result += word.decode(charset or 'utf-8', errors='ignore')
        else:
            result += word
    return result

def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(errors='ignore')
    else:
        return msg.get_payload(decode=True).decode(errors='ignore')
    return ""

@celery_app.task
def check_replies_task():
    """
    Celery task to connect to IMAP, fetch UNSEEN emails, and classify intent via LLM.
    Runs periodically via Celery Beat.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logger.warning("[imap] Gmail credentials missing, skipping IMAP check.")
        return

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            mail.logout()
            return

        email_ids = messages[0].split()
        logger.info(f"[imap] Found {len(email_ids)} unread emails.")

        with SessionLocal() as db:
            for e_id in email_ids:
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        raw_from = msg.get("From")
                        sender_email = ""
                        if "<" in raw_from and ">" in raw_from:
                            sender_email = raw_from.split("<")[1].split(">")[0].strip().lower()
                        else:
                            sender_email = raw_from.strip().lower()

                        # 1. Check if sender is a known contact
                        contact = db.query(Contact).filter(Contact.email == sender_email).first()
                        if not contact:
                            continue # Ignore emails from unknown senders

                        logger.info(f"[imap] Found reply from known contact: {sender_email}")
                        
                        # 2. Extract body and classify via LLM
                        body = extract_body(msg)
                        intent = llm_svc.classify_reply(body)
                        logger.info(f"[imap] Classified as: {intent}")
                        
                        # 3. Auto-stop active sequences for this contact
                        queued_emails = db.query(EmailModel).filter(
                            EmailModel.contact_id == contact.id,
                            EmailModel.status == "queued"
                        ).all()
                        for qe in queued_emails:
                            qe.status = "cancelled"
                            
                        # 4. Update contact status
                        if intent == "unsubscribe":
                            contact.status = "unsubscribed"
                        elif intent == "interested":
                            contact.status = "converted"
                        else:
                            contact.status = "replied"
                            
                        # Try to link reply to the last sent email
                        last_sent = db.query(EmailModel).filter(
                            EmailModel.contact_id == contact.id,
                            EmailModel.status == "sent"
                        ).order_by(EmailModel.sent_at.desc()).first()
                        
                        if last_sent:
                            import json
                            reply_event = Event(
                                email_id=last_sent.id,
                                event_type="reply",
                                metadata_json=json.dumps({"intent": intent, "snippet": body[:100]})
                            )
                            db.add(reply_event)

                        db.commit()

        mail.logout()

    except Exception as e:
        logger.error(f"[imap] Error checking replies: {e}")
