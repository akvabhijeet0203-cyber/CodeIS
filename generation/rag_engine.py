
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

from retrieval.hybrid_retriever import get_hybrid_retriever
from generation.llm_client import get_llm_client
from generation.prompts import SYSTEM_PROMPT, build_user_prompt, build_multihop_user_prompt
from config import TOP_K_FINAL
from utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class RAGResponse:
    query:          str
    answer:         str
    source_chunks:  List[Dict[str, Any]]
    is_multi_hop:   bool    = False
    latency_s:      float   = 0.0
    # Derived fields for UI display
    cited_clauses:  List[str] = field(default_factory=list)
    confidence:     float     = 0.0

    def to_dict(self) -> dict:
        return {
            "query":         self.query,
            "answer":        self.answer,
            "cited_clauses": self.cited_clauses,
            "confidence":    round(self.confidence, 3),
            "is_multi_hop":  self.is_multi_hop,
            "latency_s":     round(self.latency_s, 2),
            "sources": [
                {
                    "chunk_id":      c.get("chunk_id"),
                    "clause_number": c.get("metadata", {}).get("clause_number"),
                    "part_name":     c.get("metadata", {}).get("part_name"),
                    "page_numbers":  c.get("metadata", {}).get("page_numbers"),
                    "fused_score":   round(c.get("fused_score", 0), 3),
                    "text_snippet":  c.get("text", "")[:200] + "...",
                }
                for c in self.source_chunks
            ],
        }


class RAGEngine:
    """
    Orchestrates the full RAG pipeline for a single query.
    """

    def __init__(self):
        self._retriever = get_hybrid_retriever()
        self._llm       = get_llm_client()

    # Public API 

    def query(
        self,
        question:     str,
        top_k:        int  = TOP_K_FINAL,
        multi_hop:    bool = False,
        filter_part:  Optional[str] = None,
    ) -> RAGResponse:
        """
        Run a RAG query.

        Args:
            question:    Engineer's natural-language question.
            top_k:       Number of chunks to retrieve.
            multi_hop:   If True, retrieves from all IS 875 parts independently.
            filter_part: Restrict retrieval to a specific part (single-hop only).

        Returns:
            RAGResponse with answer, sources, and metadata.
        """
        t0 = time.time()
        log.info(f"RAG query: '{question[:80]}...'")

        #  Retrieve
        if multi_hop:
            chunks = self._retriever.retrieve_multi_hop(question, top_k=top_k)
        else:
            chunks = self._retriever.retrieve(
                question, top_k=top_k, filter_part=filter_part
            )

        log.debug(f"  Retrieved {len(chunks)} chunks.")

        if not chunks:
            return RAGResponse(
                query         = question,
                answer        = (
                    "No relevant context was found in the IS 875 database. "
                    "Please ensure the ingestion pipeline has been run and the PDF "
                    "files are present in data/is875/."
                ),
                source_chunks = [],
                latency_s     = time.time() - t0,
            )

        # Build prompt 
        if multi_hop:
            user_prompt = build_multihop_user_prompt(question, chunks)
        else:
            user_prompt = build_user_prompt(question, chunks)

        # Generate 
        answer = self._llm.generate(
            system_prompt = SYSTEM_PROMPT,
            user_prompt   = user_prompt,
        )

        # Post-process
        cited_clauses = self._extract_cited_clauses(chunks)
        confidence    = self._compute_confidence(chunks)

        response = RAGResponse(
            query         = question,
            answer        = answer,
            source_chunks = chunks,
            is_multi_hop  = multi_hop,
            latency_s     = time.time() - t0,
            cited_clauses = cited_clauses,
            confidence    = confidence,
        )

        log.info(f"  Answer generated in {response.latency_s:.2f}s. "
                 f"Confidence: {confidence:.2f}")
        return response

    # Helpers 

    @staticmethod
    def _extract_cited_clauses(chunks: List[Dict]) -> List[str]:
        """Extract unique clause references from retrieved chunks."""
        seen = set()
        clauses = []
        for c in chunks:
            meta   = c.get("metadata", {})
            clause = meta.get("clause_number", "")
            part   = meta.get("part_name", "")
            ref    = f"Clause {clause} ({part})"
            if ref not in seen:
                seen.add(ref)
                clauses.append(ref)
        return clauses

    @staticmethod
    def _compute_confidence(chunks: List[Dict]) -> float:
        """
        Confidence score: average fused_score of top-3 retrieved chunks.
        Maps to [0, 1] — higher is better.
        """
        if not chunks:
            return 0.0
        scores = [c.get("fused_score", c.get("semantic_score", 0)) for c in chunks[:3]]
        return sum(scores) / len(scores)


# Singleton 
_engine: RAGEngine | None = None

def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
