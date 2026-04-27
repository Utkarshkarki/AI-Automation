"""
services/email/campaigns.py — Background scheduler for drip campaigns.
"""
import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.config import GMAIL_ADDRESS
from .database import SessionLocal
from .models import Email, Template
from .smtp import smtp_send

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("[campaigns] Background scheduler started")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[campaigns] Background scheduler stopped")

def process_queued_emails():
    """
    Fetch up to 5 queued emails and send them.
    This function runs periodically.
    """
    with SessionLocal() as db:
        # Find queued emails
        queued = db.query(Email).filter(Email.status == "queued").limit(5).all()
        
        if not queued:
            return

        logger.info(f"[campaigns] Processing {len(queued)} queued emails")
        for email_record in queued:
            try:
                # Need to resolve template
                if not email_record.template_id:
                    email_record.status = "failed"
                    email_record.body = "No template provided"
                    continue
                    
                template = db.query(Template).filter(Template.id == email_record.template_id).first()
                if not template:
                    email_record.status = "failed"
                    email_record.body = "Template not found"
                    continue

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

                # Send via SMTP
                logger.info(f"[campaigns] Sending drip email to {contact.email}")
                smtp_send(to=contact.email, subject=subject, body=body)

                # Update record
                email_record.status = "sent"
                email_record.sender_email = GMAIL_ADDRESS
                email_record.subject = subject
                email_record.body = body
                db.commit()
                
                # Small sleep to prevent rate limiting issues with SMTP
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"[campaigns] Failed to send email {email_record.id}: {e}")
                email_record.status = "failed"
                db.commit()

# Register the job to run every 1 minute (adjust interval for 20/day pacing in real life)
scheduler.add_job(
    process_queued_emails,
    trigger=IntervalTrigger(minutes=1),
    id="drip_campaign_job",
    name="Process queued campaign emails",
    replace_existing=True,
)
