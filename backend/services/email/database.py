"""
services/email/database.py — Database connection and session management.
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file will be created in the backend folder
DB_PATH = Path(__file__).parent.parent.parent / "email_outreach.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# For SQLite, check_same_thread=False is needed if passing sessions across threads
# though we mostly use them within standard request contexts.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Create all tables defined in models."""
    import services.email.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
