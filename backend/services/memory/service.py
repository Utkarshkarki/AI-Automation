"""
services/memory/service.py — PUBLIC API for the Memory domain.

This is the ONLY file other modules are allowed to import from this package.

To extract into a standalone microservice later:
  1. Deploy services/memory/ as its own FastAPI app.
  2. Replace this class body with HTTP calls to that new service.
  3. Nothing else in the codebase needs to change.
"""
import logging
from datetime import datetime

from sklearn.metrics.pairwise import cosine_similarity

from core.config import MAX_MEMORY_TOKENS, TOP_K_MEMORY, TOP_K_RANKED

from .embeddings import embed_text
from .faiss_store import FAISSMemoryDB

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Public facade for all memory operations.
    Instantiated once in main.py and injected wherever needed.
    """

    def __init__(self):
        self._db = FAISSMemoryDB()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(self, user_input: str) -> list[dict]:
        """Search FAISS for memories relevant to the current user input."""
        query_embedding = embed_text(user_input)
        return self._db.search(query_embedding, top_k=TOP_K_MEMORY)

    def rank(self, user_input: str, memories: list[dict], top_k: int = TOP_K_RANKED) -> list[dict]:
        """Re-rank raw memories by cosine similarity + recency tiebreak."""
        if not memories:
            return []

        input_embedding = embed_text(user_input)
        scored = []
        for mem in memories:
            emb = mem.get("embedding")
            if emb is None:
                continue
            sim = cosine_similarity([input_embedding], [emb])[0][0]
            scored.append((mem, float(sim)))

        scored.sort(
            key=lambda x: (x[1], x[0].get("timestamp", datetime.min)),
            reverse=True,
        )
        return [m[0] for m in scored[:top_k]]

    def format(self, memories: list[dict], max_tokens: int = MAX_MEMORY_TOKENS) -> str:
        """Format ranked memories into a compact text block within a token budget."""
        output = []
        tokens = 0
        for mem in memories:
            text = (
                f"[{mem.get('timestamp', '')}] "
                f"{mem.get('user_input', '')} → intent: {mem.get('intent', '')}"
            )
            t = len(text.split())
            if tokens + t > max_tokens:
                break
            output.append(text)
            tokens += t
        return "\n".join(output)

    def store(self, user_input: str, output: dict, results: list[dict]) -> None:
        """Persist the current interaction to the FAISS memory store."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": output.get("intent", "unknown"),
            "confidence": output.get("confidence", 0.0),
            "actions": output.get("actions", []),
            "results": [
                {"tool": r.get("tool"), "status": r.get("status")} for r in results
            ],
            "embedding": embed_text(user_input),
        }
        self._db.upsert(entry)
        logger.info(f"[memory.service] Stored. Total memories: {self._db.count}")

    def get_all(self) -> list[dict]:
        """Return all stored entries (embeddings stripped for serialization)."""
        return self._db.get_all()

    @property
    def count(self) -> int:
        return self._db.count
