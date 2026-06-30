

from __future__ import annotations

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, EMBEDDING_DEVICE
from utils.logger import get_logger

log = get_logger(__name__)


_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        log.info(f"Loading embedding model: {EMBEDDING_MODEL} on {EMBEDDING_DEVICE}")
        _model = SentenceTransformer(EMBEDDING_MODEL, device=EMBEDDING_DEVICE)
        log.success("Embedding model loaded.")
    return _model


def embed_texts(texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
    """
    Embed a list of texts and return a (N, D) numpy array.
    Uses batching so large ingestion sets don't OOM.
    """
    model = get_embedding_model()
    log.info(f"Embedding {len(texts)} texts in batches of {batch_size}...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,   
    )
    log.success(f"Embeddings shape: {embeddings.shape}")
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string. Returns a 1-D numpy array."""
    model = get_embedding_model()
    vec = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vec
