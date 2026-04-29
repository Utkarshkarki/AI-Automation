"""
services/auth/models.py — SQLAlchemy ORM models for authentication.
"""
from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

# We import the Base from the shared database location
from services.email.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships to other domains can be mapped here or accessed dynamically
    # For now we'll define standard relationships but keep them decoupled where possible
