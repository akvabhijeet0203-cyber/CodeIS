
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any

from rank_bm25 import BM25Okapi

from config import TOP_K_BM25, DATA_DIR
from utils.logger import get_logger
from utils.text_utils import normalise_text

log = get_logger(__name__)

BM25_CACHE = DATA_DIR / "bm25_index.pkl"


class BM25Retriever:
    """
    Wraps BM25Okapi with persistence.
    Index is built once from all chunk texts and cached to disk.
    """

    def __init__(self):
        self._bm25:   BM25Okapi | None = None
        self._chunks: List[Dict]       = []  

    #  Index management 

    def build_index(self, chunks: List[Dict]):
        """
        Build BM25 index from a list of chunk dicts.
        Each dict must have at least: chunk_id, text, metadata.
        """
        log.info(f"Building BM25 index over {len(chunks)} chunks...")
        self._chunks = chunks
        tokenised    = [self._tokenise(c["text"]) for c in chunks]
        self._bm25   = BM25Okapi(tokenised)
        self._save()
        log.success("BM25 index built and saved.")

    def load_or_build(self, chunks: List[Dict]):
        """Load cached index from disk; build if cache missing or stale."""
        if BM25_CACHE.exists():
            try:
                self._load()
                # Validate: chunk count should match
                if len(self._chunks) == len(chunks):
                    log.info(f"BM25 index loaded from cache ({len(self._chunks)} docs).")
                    return
                else:
                    log.warning("BM25 cache stale (chunk count mismatch). Rebuilding.")
            except Exception as e:
                log.warning(f"BM25 cache load failed ({e}). Rebuilding.")
        self.build_index(chunks)

    def _save(self):
        with open(BM25_CACHE, "wb") as f:
            pickle.dump({"bm25": self._bm25, "chunks": self._chunks}, f)

    def _load(self):
        with open(BM25_CACHE, "rb") as f:
            data = pickle.load(f)
        self._bm25   = data["bm25"]
        self._chunks = data["chunks"]

    #  Retrieval

    def search(self, query: str, top_k: int = TOP_K_BM25) -> List[Dict[str, Any]]:
        """Return top_k chunks by BM25 score."""
        if self._bm25 is None:
            raise RuntimeError("BM25 index not built. Call build_index() or load_or_build().")

        tokens = self._tokenise(query)
        scores = self._bm25.get_scores(tokens)

        # Get top_k indices
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]

        results = []
        max_score = scores[top_indices[0]] if top_indices else 1.0
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            chunk = self._chunks[idx].copy()
            chunk["bm25_score"] = float(scores[idx])
            # Normalise to [0, 1] for hybrid fusion
            chunk["bm25_score_norm"] = float(scores[idx]) / (max_score + 1e-9)
            results.append(chunk)

        return results

    # Helpers 

    @staticmethod
    def _tokenise(text: str) -> List[str]:
        """Simple whitespace tokenisation + lowercase."""
        return normalise_text(text).lower().split()


#  Load all chunks from ChromaDB for BM25 building 

def load_all_chunks_from_store(store) -> List[Dict]:
    """
    Pull every document from ChromaDB to build the BM25 corpus.
    ChromaDB doesn't have a 'get all' API with a nice limit,
    so we page through using offset.
    """
    PAGE = 500
    offset = 0
    all_chunks = []

    while True:
        result = store._collection.get(
            limit   = PAGE,
            offset  = offset,
            include = ["documents", "metadatas"],
        )
        ids   = result.get("ids", [])
        docs  = result.get("documents", [])
        metas = result.get("metadatas", [])

        if not ids:
            break

        for chunk_id, text, meta in zip(ids, docs, metas):
            all_chunks.append({
                "chunk_id": chunk_id,
                "text":     text,
                "metadata": meta,
            })

        offset += PAGE
        if len(ids) < PAGE:
            break

    log.info(f"Loaded {len(all_chunks)} chunks from ChromaDB for BM25.")
    return all_chunks


# Singleton 
_retriever: BM25Retriever | None = None

def get_bm25_retriever(store=None) -> BM25Retriever:
    global _retriever
    if _retriever is None:
        _retriever = BM25Retriever()
        if store is not None:
            chunks = load_all_chunks_from_store(store)
            _retriever.load_or_build(chunks)
    return _retriever
