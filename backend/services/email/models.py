"""
services/email/models.py — SQLAlchemy ORM models for the email domain.
Defines the schema for Emails, Contacts, Campaigns, Templates, Events, and Users.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("Email", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("Email", back_populates="contact")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="campaigns")
    emails = relationship("Email", back_populates="campaign")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    subject = Column(String)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("Email", back_populates="template")


class Email(Base):
    """Core table for all sent emails."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    sender_email = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    cc_email = Column(String)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, default="sent")  # sent, failed, bounced

    sent_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="emails")
    contact = relationship("Contact", back_populates="emails")
    campaign = relationship("Campaign", back_populates="emails")
    template = relationship("Template", back_populates="emails")
    events = relationship("Event", back_populates="email")


class Event(Base):
    """Tracks opens, clicks, replies for an email."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    event_type = Column(String, nullable=False)  # open, click, reply
    metadata_json = Column(Text)  # e.g. {"url": "https://...", "ip": "..."}
    occurred_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email", back_populates="events")
