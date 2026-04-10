import logging
from datetime import datetime
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .config import EMBEDDING_MODEL, FAISS_DIM, TOP_K_MEMORY, TOP_K_RANKED, MAX_MEMORY_TOKENS

logger = logging.getLogger(__name__)

# Load embedding model once at module init
_embedding_model = SentenceTransformer(EMBEDDING_MODEL)
logger.info(f"[memory] Loaded embedding model: {EMBEDDING_MODEL}")


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_text(text: str) -> list[float]:
    """Encode text into a dense embedding vector."""
    return _embedding_model.encode(text).tolist()


# ---------------------------------------------------------------------------
# FAISS Vector DB
# ---------------------------------------------------------------------------

class FAISSMemoryDB:
    """
    In-memory FAISS vector database for agent memory.
    Stores embeddings + metadata for all past interactions.
    """

    def __init__(self, dim: int = FAISS_DIM):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata: list[dict[str, Any]] = []
        self.dim = dim
        logger.info(f"[FAISSMemoryDB] Initialized with dim={dim}")

    def upsert(self, entry: dict) -> None:
        """Add a new memory entry with its embedding to the index."""
        embedding = np.array([entry["embedding"]], dtype=np.float32)
        self.index.add(embedding)
        self.metadata.append(entry)
        logger.debug(f"[FAISSMemoryDB] Upserted entry. Total={self.index.ntotal}")

    def search(self, query_embedding: list[float], top_k: int = TOP_K_MEMORY) -> list[dict]:
        """Return top_k most similar entries by L2 distance."""
        if self.index.ntotal == 0:
            return []

        k = min(top_k, self.index.ntotal)
        query = np.array([query_embedding], dtype=np.float32)
        _, indices = self.index.search(query, k)

        results = []
        for i in indices[0]:
            if 0 <= i < len(self.metadata):
                results.append(self.metadata[i])

        logger.debug(f"[FAISSMemoryDB] Search returned {len(results)} results")
        return results

    def get_all(self) -> list[dict]:
        """Return all stored memory entries (without embeddings for serialization)."""
        return [
            {k: v for k, v in entry.items() if k != "embedding"}
            for entry in self.metadata
        ]

    @property
    def count(self) -> int:
        return self.index.ntotal


# Singleton instance
vector_db = FAISSMemoryDB()


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_memories(
    user_input: str,
    memory_context: list[dict],
    top_k: int = TOP_K_RANKED,
) -> list[dict]:
    """
    Rank memories by cosine similarity to current input, with timestamp as
    tiebreaker for equally-scored entries.
    """
    if not memory_context:
        return []

    input_embedding = embed_text(user_input)

    scored = []
    for mem in memory_context:
        emb = mem.get("embedding")
        if emb is None:
            continue
        sim = cosine_similarity([input_embedding], [emb])[0][0]
        scored.append((mem, float(sim)))

    # Sort by similarity desc, then by timestamp desc (most recent first)
    scored.sort(key=lambda x: (x[1], x[0].get("timestamp", datetime.min)), reverse=True)

    return [m[0] for m in scored[:top_k]]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_memories(memories: list[dict], max_tokens: int = MAX_MEMORY_TOKENS) -> str:
    """Format ranked memories into a compact text block respecting a token budget."""
    output = []
    tokens = 0

    for mem in memories:
        user_in = mem.get("user_input", "")
        intent = mem.get("intent", "")
        text = f"[{mem.get('timestamp', '')}] {user_in} → intent: {intent}"
        t = len(text.split())

        if tokens + t > max_tokens:
            break

        output.append(text)
        tokens += t

    return "\n".join(output)


# ---------------------------------------------------------------------------
# Retrieval & Storage
# ---------------------------------------------------------------------------

def retrieve_memory(user_input: str) -> list[dict]:
    """Search FAISS for memories relevant to the current user input."""
    query_embedding = embed_text(user_input)
    return vector_db.search(query_embedding, top_k=TOP_K_MEMORY)


def store_memory(user_input: str, output: dict, results: list[dict]) -> None:
    """Persist current interaction to the FAISS memory store."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "intent": output.get("intent", "unknown"),
        "confidence": output.get("confidence", 0.0),
        "actions": output.get("actions", []),
        "results": [
            {"tool": r.get("tool"), "status": r.get("status")}
            for r in results
        ],
        "embedding": embed_text(user_input),
    }
    vector_db.upsert(entry)
    logger.info(f"[memory] Stored interaction. Total memories: {vector_db.count}")
