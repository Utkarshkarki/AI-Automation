"""
services/email/repository.py — Data access layer for the email domain.
Encapsulates all database queries and interactions.
"""
from typing import List

from sqlalchemy.orm import Session

from .models import Contact, Email


def get_or_create_contact(db: Session, email: str) -> Contact:
    """Find a contact by email or create a new one."""
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        contact = Contact(email=email)
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


def create_sent_email(db: Session, sender: str, to: str, subject: str, body: str, cc: str = None) -> Email:
    """Record a newly sent email in the database."""
    contact = get_or_create_contact(db, to)

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
