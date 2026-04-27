"""
services/email/campaigns.py — Background scheduler for drip campaigns.
"""
import logging
import time
import random
from datetime import datetime, timedelta

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

DAILY_SEND_LIMIT = 50
daily_send_count = 0
last_reset_date = datetime.utcnow().date()

def process_queued_emails():
    """
    Fetch up to 5 queued emails that are scheduled for <= NOW and send them.
    Respects daily limits and adds random delays.
    """
    global daily_send_count, last_reset_date
    
    # Reset daily limit
    today = datetime.utcnow().date()
    if today != last_reset_date:
        daily_send_count = 0
        last_reset_date = today

    if daily_send_count >= DAILY_SEND_LIMIT:
        logger.info(f"[campaigns] Daily limit ({DAILY_SEND_LIMIT}) reached. Pausing until tomorrow.")
        return

    with SessionLocal() as db:
        # Find queued emails ready to send
        queued = db.query(Email).filter(
            Email.status == "queued",
            Email.scheduled_for <= datetime.utcnow()
        ).limit(5).all()
        
        if not queued:
            return

        logger.info(f"[campaigns] Processing {len(queued)} queued emails")
        for email_record in queued:
            if daily_send_count >= DAILY_SEND_LIMIT:
                break
                
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
                
                daily_send_count += 1
                
                # Random delay to mimic human behavior and protect deliverability
                delay = random.randint(15, 45)
                logger.info(f"[campaigns] Sleeping {delay}s for deliverability protection")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"[campaigns] Failed to send email {email_record.id}: {e}")
                email_record.status = "failed"
                db.commit()

# Register the drip campaign job to run every 1 minute
scheduler.add_job(
    process_queued_emails,
    trigger=IntervalTrigger(minutes=1),
    id="drip_campaign_job",
    name="Process queued campaign emails",
    replace_existing=True,
)

# Register the IMAP reply detection job to run every 5 minutes
from .imap_worker import check_replies
scheduler.add_job(
    check_replies,
    trigger=IntervalTrigger(minutes=5),
    id="imap_reply_check_job",
    name="Check IMAP for replies",
    replace_existing=True,
)
