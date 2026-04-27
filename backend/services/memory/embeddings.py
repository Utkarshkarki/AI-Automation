"""
services/memory/embeddings.py — Private: sentence embedding model.
Only used internally by MemoryService and FAISSMemoryDB.
"""
import logging

from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Loaded once at process start — expensive operation
_model = SentenceTransformer(EMBEDDING_MODEL)
logger.info(f"[memory.embeddings] Loaded model: {EMBEDDING_MODEL}")


def embed_text(text: str) -> list[float]:
    """Encode a string into a 384-dim dense vector."""
    return _model.encode(text).tolist()
