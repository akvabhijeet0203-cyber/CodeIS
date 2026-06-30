
# Manages the ChromaDB vector store:

from __future__ import annotations

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from config import VECTORDB_DIR, CHROMA_COLLECTION_NAME, TOP_K_SEMANTIC
from ingestion.embedder import embed_texts, embed_query
from ingestion.chunker import Chunk
from utils.logger import get_logger

log = get_logger(__name__)


class VectorStore:
    """Thin wrapper around a ChromaDB persistent collection."""

    def __init__(self):
        self._client     = None
        self._collection = None

    # Lifecycle 

    def connect(self):
        """Open (or create) the persistent ChromaDB collection."""
        log.info(f"Connecting to ChromaDB at: {VECTORDB_DIR}")
        self._client = chromadb.PersistentClient(
            path=str(VECTORDB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        count = self._collection.count()
        log.success(f"Collection '{CHROMA_COLLECTION_NAME}' loaded. Documents: {count}")

    def is_populated(self) -> bool:
        return self._collection is not None and self._collection.count() > 0

    def clear(self):
        """Delete and recreate the collection (use before re-ingestion)."""
        if self._client:
            self._client.delete_collection(CHROMA_COLLECTION_NAME)
            self._collection = self._client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            log.warning("ChromaDB collection cleared.")

    # Ingestion

    def upsert_chunks(self, chunks: List[Chunk], batch_size: int = 100):
        """
        Embed and upsert all chunks into ChromaDB.
        Uses batching so large sets don't OOM.
        """
        if not self._collection:
            raise RuntimeError("Call connect() first.")

        total = len(chunks)
        log.info(f"Upserting {total} chunks into ChromaDB...")

        for start in range(0, total, batch_size):
            batch   = chunks[start : start + batch_size]
            texts   = [c.text for c in batch]
            ids     = [c.chunk_id for c in batch]
            metas   = [c.to_metadata() for c in batch]

            embeddings = embed_texts(texts, show_progress=False)
            embeddings_list = embeddings.tolist()

            self._collection.upsert(
                ids        = ids,
                documents  = texts,
                embeddings = embeddings_list,
                metadatas  = metas,
            )
            log.debug(f"  Upserted batch {start}–{start+len(batch)}")

        log.success(f"All {total} chunks upserted. Total in DB: {self._collection.count()}")

    # Retrieval 

    def semantic_search(
        self,
        query: str,
        top_k: int = TOP_K_SEMANTIC,
        filter_part: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return top_k semantically similar chunks.
        Optional filter_part: e.g. "IS 875 Part 3 - Wind Loads"
        """
        if not self._collection:
            raise RuntimeError("Call connect() first.")

        query_vec = embed_query(query).tolist()
        where     = {"part_name": filter_part} if filter_part else None

        results = self._collection.query(
            query_embeddings = [query_vec],
            n_results        = top_k,
            where            = where,
            include          = ["documents", "metadatas", "distances"],
        )

        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "chunk_id":      results["ids"][0][i],
                "text":          results["documents"][0][i],
                "metadata":      results["metadatas"][0][i],
                "distance":      results["distances"][0][i],
                # Convert cosine distance → similarity score [0,1]
                "semantic_score": 1 - results["distances"][0][i],
            })

        return hits

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single chunk by its ID."""
        result = self._collection.get(
            ids     = [chunk_id],
            include = ["documents", "metadatas"],
        )
        if result["ids"]:
            return {
                "chunk_id": result["ids"][0],
                "text":     result["documents"][0],
                "metadata": result["metadatas"][0],
            }
        return None

    def count(self) -> int:
        return self._collection.count() if self._collection else 0


# Singleton
_store: VectorStore | None = None

def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
        _store.connect()
    return _store
