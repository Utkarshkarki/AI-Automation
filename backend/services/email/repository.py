"""
services/email/repository.py — Data access layer for the email domain.
Encapsulates all database queries and interactions.
"""
from typing import List

from sqlalchemy.orm import Session

from .models import Contact, Email, Template, Campaign


def create_or_update_contact(db: Session, email: str, user_id: str = None, **kwargs) -> Contact:
    """Find a contact by email or create a new one, updating any provided fields."""
    query = db.query(Contact).filter(Contact.email == email)
    if user_id:
        query = query.filter(Contact.user_id == user_id)
    contact = query.first()
    
    if not contact:
        contact = Contact(email=email, user_id=user_id)
        db.add(contact)
    
    # Update provided fields
    for key, value in kwargs.items():
        if hasattr(contact, key) and value is not None:
            setattr(contact, key, value)
            
    db.commit()
    db.refresh(contact)
    return contact


def get_contact_by_email(db: Session, email: str, user_id: str = None) -> dict:
    """Retrieve a contact's rich context by email."""
    query = db.query(Contact).filter(Contact.email == email)
    if user_id:
        query = query.filter(Contact.user_id == user_id)
    contact = query.first()
    if not contact:
        return None
    return {
        "id": contact.id,
        "email": contact.email,
        "name": contact.name,
        "company": contact.company,
        "website": contact.website,
        "linkedin": contact.linkedin,
        "industry": contact.industry,
        "pain_points": contact.pain_points,
        "recent_news": contact.recent_news,
        "status": contact.status,
    }


def list_all_contacts(db: Session, user_id: str = None) -> list[dict]:
    """Return all contacts in the database."""
    query = db.query(Contact)
    if user_id:
        query = query.filter(Contact.user_id == user_id)
    contacts = query.all()
    return [
        {
            "email": c.email,
            "name": c.name,
            "company": c.company,
            "status": c.status
        }
        for c in contacts
    ]


# --- Templates ---

def create_template(db: Session, name: str, subject: str, body: str, user_id: str = None) -> Template:
    """Create a new email template."""
    t = Template(name=name, subject=subject, body=body, user_id=user_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def get_template(db: Session, template_id: int, user_id: str = None) -> Template:
    query = db.query(Template).filter(Template.id == template_id)
    if user_id:
        query = query.filter(Template.user_id == user_id)
    return query.first()


def list_templates(db: Session, user_id: str = None) -> list[dict]:
    query = db.query(Template)
    if user_id:
        query = query.filter(Template.user_id == user_id)
    templates = query.all()
    return [{"id": t.id, "name": t.name, "subject": t.subject, "body": t.body} for t in templates]


# --- Campaigns ---

def create_campaign(db: Session, name: str, description: str = None, user_id: str = None) -> Campaign:
    """Create a new campaign."""
    c = Campaign(name=name, description=description, user_id=user_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def get_campaign(db: Session, campaign_id: int, user_id: str = None) -> Campaign:
    query = db.query(Campaign).filter(Campaign.id == campaign_id)
    if user_id:
        query = query.filter(Campaign.user_id == user_id)
    return query.first()


def list_campaigns(db: Session, user_id: str = None) -> list[dict]:
    """Return all campaigns."""
    query = db.query(Campaign)
    if user_id:
        query = query.filter(Campaign.user_id == user_id)
    campaigns = query.all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in campaigns
    ]


def link_contact_to_campaign(db: Session, contact_email: str, campaign_id: int, template_id: int, delay_days: list[int] = None, user_id: str = None):
    """
    Queue a contact for a campaign. If delay_days is provided (e.g. [0, 3, 7]), 
    it creates a sequence of scheduled emails.
    """
    if delay_days is None:
        delay_days = [0]
        
    contact = get_contact_by_email(db, contact_email, user_id)
    if not contact:
        raise ValueError(f"Contact {contact_email} not found")
        
    # Check if already queued for this campaign to prevent duplicates
    existing = db.query(Email).filter(
        Email.contact_id == contact["id"],
        Email.campaign_id == campaign_id
    ).first()
    
    if not existing:
        from datetime import datetime, timedelta
        from services.email.campaigns import send_email_task
        contact_record = db.query(Contact).filter(Contact.email == contact_email).first()
        
        for delay in delay_days:
            schedule_time = datetime.utcnow() + timedelta(days=delay)
            
            email_record = Email(
                user_id=user_id,
                contact_id=contact_record.id,
                campaign_id=campaign_id,
                template_id=template_id,
                sender_email="queued",
                recipient_email=contact_email,
                subject="queued",
                body="queued",
                status="queued",
                scheduled_for=schedule_time
            )
            db.add(email_record)
            db.commit()
            
            # Immediately queue the task in Celery, delayed via `eta`
            send_email_task.apply_async(args=[email_record.id], eta=schedule_time)


# --- Emails ---

def create_sent_email(db: Session, sender: str, to: str, subject: str, body: str, cc: str = None, user_id: str = None) -> Email:
    """Record a newly sent email in the database."""
    contact = create_or_update_contact(db, email=to, user_id=user_id)

    email_record = Email(
        user_id=user_id,
        contact_id=contact.id,
        sender_email=sender,
        recipient_email=to,
        cc_email=cc,
        subject=subject,
        body=body,
        status="sent",
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)
    return email_record


def get_recent_emails(db: Session, limit: int = 10, user_id: str = None) -> List[dict]:
    """Retrieve the most recent sent emails, formatted as dicts for the agent."""
    query = db.query(Email)
    if user_id:
        query = query.filter(Email.user_id == user_id)
    emails = query.order_by(Email.sent_at.desc()).limit(limit).all()
    
    result = []
    for e in emails:
        result.append({
            "timestamp": e.sent_at.isoformat(),
            "from": e.sender_email,
            "to": e.recipient_email,
            "cc": e.cc_email,
            "subject": e.subject,
            "body_preview": e.body[:200],
            "status": e.status,
        })
    return result
