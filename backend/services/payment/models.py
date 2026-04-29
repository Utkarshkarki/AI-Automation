"""
services/payment/models.py — SQLAlchemy ORM models for payments.
"""
from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from services.email.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price_inr = Column(Integer, nullable=False) # in paise
    max_contacts = Column(Integer, nullable=False)
    max_emails = Column(Integer, nullable=False)
    max_campaigns = Column(Integer, nullable=False)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    razorpay_order_id = Column(String)
    razorpay_payment_id = Column(String)
    
    status = Column(String, default="pending") # pending, active, failed, cancelled
    
    started_at = Column(DateTime)
    expires_at = Column(DateTime)
