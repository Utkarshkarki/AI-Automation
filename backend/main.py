"""
main.py — FastAPI application entry point.

All services are instantiated ONCE here and injected via FastAPI's
dependency injection system. This is the composition root of the monolith.

When extracting a service to a microservice:
  1. Remove its instantiation here.
  2. Point its Service class at the remote HTTP endpoint instead.
  3. Routes below don't change at all.
"""
import logging
import os

from dotenv import load_dotenv

# Load .env before anything else so os.getenv() in core/config.py picks them up
load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.loop import AgentLoop
from agent.tools import build_executors
from services.email.database import SessionLocal
from services.email.repository import create_or_update_contact
from services.email.service import EmailService
from services.llm.service import LLMService
from services.memory.service import MemoryService
from services.metrics.service import MetricsService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Composition Root — instantiate all services exactly once
# ---------------------------------------------------------------------------

email_svc = EmailService()
llm_svc = LLMService()
memory_svc = MemoryService()
metrics_svc = MetricsService()

# Wire email service into the tool registry
build_executors(email_svc)

# Build the orchestrator with injected services
agent_loop = AgentLoop(llm=llm_svc, memory=memory_svc, metrics=metrics_svc)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Email Outreach Agent API",
    description="Modular monolith AI agent for email outreach — FAISS memory, Gmail SMTP, Ollama LLM.",
    version="5.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    input: str


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("✉️  Email Outreach Agent v5.0 — Starting up")

    # Initialize SQLite Database
    from services.email.database import init_db
    init_db()
    logger.info("✅ SQLite Database initialized")

    health = llm_svc.check_health()
    if not health["ollama_running"]:
        logger.warning("⚠️  Ollama is NOT running. Start it with: ollama serve")
    elif not health["model_available"]:
        model = health["model"]
        logger.warning(f"⚠️  Model '{model}' not found. Pull it: ollama pull {model}")
    else:
        logger.info(f"✅ Ollama ready | Model: {health['model']}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown():
    logger.info("[main] Shutting down.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Check API, Ollama connectivity, and memory entry count."""
    ollama = llm_svc.check_health()
    return {
        "api": "ok",
        "memory_entries": memory_svc.count,
        **ollama,
    }


@app.post("/run")
def run(req: RunRequest):
    """Run the agent loop with the given user input."""
    if not req.input or not req.input.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty.")
    try:
        return agent_loop.run(req.input.strip())
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"Unhandled error in /run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    """Return intent and tool usage metrics."""
    return metrics_svc.get_snapshot()


@app.get("/memory")
def memory():
    """Return all stored memory entries (embeddings excluded)."""
    return {
        "count": memory_svc.count,
        "entries": memory_svc.get_all(),
    }


@app.get("/api/contacts")
def get_contacts():
    """Return all contacts/leads from the database."""
    with SessionLocal() as db:
        from services.email.repository import list_all_contacts
        contacts = list_all_contacts(db)
    return {"contacts": contacts}


@app.get("/api/templates")
def get_templates():
    """Return all email templates from the database."""
    with SessionLocal() as db:
        from services.email.repository import list_templates
        templates = list_templates(db)
    return {"templates": templates}


@app.get("/api/campaigns")
def get_campaigns():
    """Return all campaigns from the database."""
    with SessionLocal() as db:
        from services.email.repository import list_campaigns
        campaigns = list_campaigns(db)
    return {"campaigns": campaigns}

import csv
import io

@app.post("/api/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """Upload a CSV file of leads and save them to the database."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    count = 0
    with SessionLocal() as db:
        for row in reader:
            email = row.get("email")
            if not email:
                continue
            
            # Map standard CSV columns to our schema
            kwargs = {
                "name": row.get("name"),
                "company": row.get("company"),
                "website": row.get("website"),
                "linkedin": row.get("linkedin"),
                "industry": row.get("industry"),
                "pain_points": row.get("pain_points"),
                "recent_news": row.get("recent_news"),
            }
            # Remove None values
            kwargs = {k: v for k, v in kwargs.items() if v}
            
            create_or_update_contact(db, email=email, **kwargs)
            count += 1
            
    return {"status": "success", "message": f"Uploaded {count} leads"}
