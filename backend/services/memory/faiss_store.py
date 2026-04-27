"""
services/memory/faiss_store.py — Private: FAISS vector database.
Only used internally by MemoryService.
"""
import logging
from typing import Any

import faiss
import numpy as np

from core.config import FAISS_DIM, TOP_K_MEMORY

logger = logging.getLogger(__name__)


class FAISSMemoryDB:
    """
    In-memory FAISS vector database for agent memory.
    Stores embeddings + metadata for all past interactions.
    """

    def __init__(self, dim: int = FAISS_DIM):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata: list[dict[str, Any]] = []
        self.dim = dim
        logger.info(f"[memory.faiss] Initialized with dim={dim}")

    def upsert(self, entry: dict) -> None:
        embedding = np.array([entry["embedding"]], dtype=np.float32)
        self.index.add(embedding)
        self.metadata.append(entry)
        logger.debug(f"[memory.faiss] Upserted entry. Total={self.index.ntotal}")

    def search(self, query_embedding: list[float], top_k: int = TOP_K_MEMORY) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        k = min(top_k, self.index.ntotal)
        query = np.array([query_embedding], dtype=np.float32)
        _, indices = self.index.search(query, k)
        results = [self.metadata[i] for i in indices[0] if 0 <= i < len(self.metadata)]
        logger.debug(f"[memory.faiss] Search returned {len(results)} results")
        return results

    def get_all(self) -> list[dict]:
        return [{k: v for k, v in e.items() if k != "embedding"} for e in self.metadata]

    @property
    def count(self) -> int:
        return self.index.ntotal
