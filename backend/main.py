import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.llm import check_ollama_health
from agent.loop import agent_loop
from agent.memory import vector_db
from agent.metrics import get_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Automation Agent API",
    description="Production-grade AI agent with FAISS memory, tool validation, and Ollama LLM.",
    version="4.0.0",
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
    logger.info("🤖 AI Automation Agent v4.0 — Starting up")
    health = check_ollama_health()
    if not health["ollama_running"]:
        logger.warning("⚠️  Ollama is NOT running. Start it with: ollama serve")
    elif not health["model_available"]:
        model = health["model"]
        logger.warning(f"⚠️  Model '{model}' not found. Pull it: ollama pull {model}")
    else:
        logger.info(f"✅ Ollama ready | Model: {health['model']}")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Check API and Ollama connectivity."""
    ollama = check_ollama_health()
    return {
        "api": "ok",
        "memory_entries": vector_db.count,
        **ollama,
    }


@app.post("/run")
def run(req: RunRequest):
    """Run the agent loop with the given user input."""
    if not req.input or not req.input.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty.")

    try:
        result = agent_loop(req.input.strip())
        return result
    except RuntimeError as e:
        # Ollama connectivity errors should surface clearly
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"Unhandled error in /run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    """Return intent and tool usage metrics."""
    return get_metrics()


@app.get("/memory")
def memory():
    """Return all stored memory entries (without embeddings)."""
    return {
        "count": vector_db.count,
        "entries": vector_db.get_all(),
    }
