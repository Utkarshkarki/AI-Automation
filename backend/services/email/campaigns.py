"""
services/email/campaigns.py — Celery tasks for sending campaign emails.
"""
import logging
import random
import time
from smtplib import SMTPException

from celery.exceptions import MaxRetriesExceededError

from core.celery_app import celery_app
from core.config import GMAIL_ADDRESS
from .database import SessionLocal
from .models import Email, Template
from .smtp import smtp_send

logger = logging.getLogger(__name__)

DAILY_SEND_LIMIT = 50
# Note: In a true distributed system, this daily counter should be moved to Redis cache
# so all workers share the same limit. For simplicity, we use local vars or rely on DB checks.

@celery_app.task(bind=True, max_retries=5)
def send_email_task(self, email_id: int):
    """
    Background task to send a single scheduled email with exponential backoff on failure.
    """
    with SessionLocal() as db:
        email_record = db.query(Email).get(email_id)
        
        if not email_record:
            logger.error(f"[celery] Email {email_id} not found.")
            return

        # Double check status in case it was cancelled by IMAP worker
        if email_record.status != "queued":
            logger.info(f"[celery] Skipping email {email_id} because status is '{email_record.status}'.")
            return

        try:
            if not email_record.template_id:
                raise ValueError("No template provided")
                
            template = db.query(Template).filter(Template.id == email_record.template_id).first()
            if not template:
                raise ValueError("Template not found")

            contact = email_record.contact
            
            # Simple variable substitution
            subject = template.subject
            body = template.body
            
            replacements = {
                "{{name}}": contact.name or "there",
                "{{company}}": contact.company or "your company",
                "{{industry}}": contact.industry or "your industry",
            }
            
            for k, v in replacements.items():
                subject = subject.replace(k, v)
                body = body.replace(k, v)

            # Random delay to mimic human behavior before sending
            delay = random.randint(15, 45)
            logger.info(f"[celery] Sleeping {delay}s to protect deliverability before sending to {contact.email}")
            time.sleep(delay)

            # Send via SMTP
            logger.info(f"[celery] Sending drip email to {contact.email}")
            smtp_send(to=contact.email, subject=subject, body=body)

            # Update record
            email_record.status = "sent"
            email_record.sender_email = GMAIL_ADDRESS
            email_record.subject = subject
            email_record.body = body
            db.commit()

        except SMTPException as exc:
            logger.warning(f"[celery] SMTP Error sending to {email_record.recipient_email}: {exc}")
            # Retry with exponential backoff: 60s, 120s, 240s...
            retry_countdown = 60 * (2 ** self.request.retries)
            logger.info(f"[celery] Retrying in {retry_countdown} seconds...")
            raise self.retry(exc=exc, countdown=retry_countdown)
            
        except MaxRetriesExceededError:
            logger.error(f"[celery] Max retries exceeded for email {email_id}")
            email_record.status = "failed"
            db.commit()
            
        except Exception as e:
            logger.error(f"[celery] Failed to send email {email_record.id}: {e}")
            email_record.status = "failed"
            db.commit()
