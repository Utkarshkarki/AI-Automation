"""
services/email/repository.py — Data access layer for the email domain.
Encapsulates all database queries and interactions.
"""
from typing import List

from sqlalchemy.orm import Session

from .models import Contact, Email


def create_or_update_contact(db: Session, email: str, **kwargs) -> Contact:
    """Find a contact by email or create a new one, updating any provided fields."""
    contact = db.query(Contact).filter(Contact.email == email).first()
    
    if not contact:
        contact = Contact(email=email)
        db.add(contact)
    
    # Update provided fields
    for key, value in kwargs.items():
        if hasattr(contact, key) and value is not None:
            setattr(contact, key, value)
            
    db.commit()
    db.refresh(contact)
    return contact


def get_contact_by_email(db: Session, email: str) -> dict:
    """Retrieve a contact's rich context by email."""
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        return None
    return {
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


def list_all_contacts(db: Session) -> list[dict]:
    """Return all contacts in the database."""
    contacts = db.query(Contact).all()
    return [
        {
            "email": c.email,
            "name": c.name,
            "company": c.company,
            "status": c.status
        }
        for c in contacts
    ]


def create_sent_email(db: Session, sender: str, to: str, subject: str, body: str, cc: str = None) -> Email:
    """Record a newly sent email in the database."""
    contact = create_or_update_contact(db, email=to)

    email_record = Email(
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


def get_recent_emails(db: Session, limit: int = 10) -> List[dict]:
    """Retrieve the most recent sent emails, formatted as dicts for the agent."""
    emails = db.query(Email).order_by(Email.sent_at.desc()).limit(limit).all()
    
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
