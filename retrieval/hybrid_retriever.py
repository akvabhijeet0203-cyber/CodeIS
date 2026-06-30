


from __future__ import annotations

from typing import List, Dict, Any, Optional

from config import (
    TOP_K_SEMANTIC, TOP_K_BM25, TOP_K_FINAL,
    SEMANTIC_WEIGHT, BM25_WEIGHT,
)
from ingestion.vector_store import get_vector_store
from retrieval.bm25_retriever import get_bm25_retriever
from utils.logger import get_logger

log = get_logger(__name__)


class HybridRetriever:
    """
    Hybrid retrieval pipeline:
    1. Semantic search via ChromaDB
    2. BM25 keyword search
    3. Score fusion (weighted combination)
    4. De-duplicate and return top-K
    """

    def __init__(self):
        self._store = get_vector_store()
        self._bm25  = get_bm25_retriever(self._store)

    #  Public API 

    def retrieve(
        self,
        query:       str,
        top_k:       int = TOP_K_FINAL,
        filter_part: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Main retrieval entry point.
        Returns up to top_k fused and ranked chunks.
        """
        log.debug(f"Retrieving for query: '{query[:80]}...'")

        # 1. Semantic search
        semantic_hits = self._store.semantic_search(
            query, top_k=TOP_K_SEMANTIC, filter_part=filter_part
        )

        # 2. BM25 search
        bm25_hits = self._bm25.search(query, top_k=TOP_K_BM25)

        # 3. Fuse scores
        fused = self._fuse(semantic_hits, bm25_hits)

        # 4. Return top_k
        results = fused[:top_k]
        log.debug(f"  Retrieved {len(results)} chunks after fusion.")
        return results

    def retrieve_multi_hop(
        self,
        query: str,
        top_k: int = TOP_K_FINAL,
    ) -> List[Dict[str, Any]]:
        """
        Multi-hop retrieval: runs retrieval independently across each
        IS 875 part and pools results, then re-ranks.
        Useful for queries that need data from multiple parts.
        """
        parts = [
            "IS 875 Part 1 - Dead Loads",
            "IS 875 Part 2 - Imposed Loads",
            "IS 875 Part 3 - Wind Loads",
        ]

        all_hits: List[Dict] = []
        per_part_k = max(2, top_k // len(parts))

        for part in parts:
            hits = self.retrieve(query, top_k=per_part_k, filter_part=part)
            all_hits.extend(hits)

        # Re-rank pooled results by fused_score
        all_hits.sort(key=lambda x: x.get("fused_score", 0), reverse=True)

        # De-duplicate
        seen = set()
        deduped = []
        for hit in all_hits:
            cid = hit["chunk_id"]
            if cid not in seen:
                seen.add(cid)
                deduped.append(hit)

        return deduped[:top_k]

    #  Score fusion 

    def _fuse(
        self,
        semantic_hits: List[Dict],
        bm25_hits: List[Dict],
    ) -> List[Dict]:
        """
        Weighted score fusion:
            fused = SEMANTIC_WEIGHT * semantic_score + BM25_WEIGHT * bm25_norm_score
        Falls back to 0 if a chunk only appears in one list.
        """
        # Build lookup dicts  chunk_id → hit
        sem_map  = {h["chunk_id"]: h for h in semantic_hits}
        bm25_map = {h["chunk_id"]: h for h in bm25_hits}

        all_ids = set(sem_map) | set(bm25_map)
        fused: List[Dict] = []

        for cid in all_ids:
            sem_hit  = sem_map.get(cid)
            bm25_hit = bm25_map.get(cid)

            sem_score  = sem_hit["semantic_score"]  if sem_hit  else 0.0
            bm25_score = bm25_hit["bm25_score_norm"] if bm25_hit else 0.0

            fused_score = SEMANTIC_WEIGHT * sem_score + BM25_WEIGHT * bm25_score

            # Use whichever hit has the data
            base = sem_hit if sem_hit else bm25_hit
            fused.append({
                **base,
                "semantic_score": sem_score,
                "bm25_score":     bm25_score,
                "fused_score":    round(fused_score, 4),
            })

        fused.sort(key=lambda x: x["fused_score"], reverse=True)
        return fused


#  Singleton 
_retriever: HybridRetriever | None = None

def get_hybrid_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever
