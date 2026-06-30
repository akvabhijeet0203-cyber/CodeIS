
# Orchestrates the full ingestion pipeline:
#   PDF Parse → Chunk → Embed → Store in ChromaDB


import argparse
import time

from config import IS875_FILES
from ingestion.pdf_parser import parse_all_parts
from ingestion.chunker import chunk_all_documents
from ingestion.vector_store import get_vector_store
from utils.logger import get_logger

log = get_logger(__name__)


def run_ingestion(force_reingest: bool = False):
    """
    Full pipeline:
    1. Parse PDFs
    2. Chunk documents
    3. Embed + store in ChromaDB

    Args:
        force_reingest: If True, clears existing DB before ingesting.
    """
    start = time.time()
    log.info("=" * 60)
    log.info("CodeIS — Ingestion Pipeline")
    log.info("=" * 60)

    # Check vector store 
    store = get_vector_store()

    if store.is_populated() and not force_reingest:
        log.info(f"Vector store already has {store.count()} chunks. Skipping ingestion.")
        log.info("Use --force flag to re-ingest.")
        return

    if force_reingest:
        log.warning("Force flag set — clearing existing vector store.")
        store.clear()

    # Parse PDFs
    log.info("Step 1/3 — Parsing IS 875 PDFs...")
    documents = parse_all_parts(IS875_FILES)

    if not documents:
        log.error("No documents were parsed. Check that PDFs exist in data/is875/")
        log.error("Expected files:")
        for key, path in IS875_FILES.items():
            log.error(f"  {path}")
        return

    log.success(f"Parsed {len(documents)} documents.")
    for doc in documents:
        log.info(f"  {doc.part_name}: {len(doc.pages)} pages")

    # Chunk
    log.info("Step 2/3 — Chunking documents...")
    chunks = chunk_all_documents(documents)
    log.success(f"Total chunks: {len(chunks)}")

    # Print chunk stats
    token_counts = [c.token_count for c in chunks]
    avg_tokens   = sum(token_counts) / len(token_counts) if token_counts else 0
    log.info(f"  Avg tokens/chunk: {avg_tokens:.0f}")
    log.info(f"  Min tokens: {min(token_counts)}")
    log.info(f"  Max tokens: {max(token_counts)}")

    # Filter out empty/too-short chunks
    chunks = [c for c in chunks if c.token_count >= 10]
    log.info(f"  After filtering short chunks: {len(chunks)}")

    # Embed + Store 
    log.info("Step 3/3 — Embedding and storing chunks in ChromaDB...")
    store.upsert_chunks(chunks)

    elapsed = time.time() - start
    log.success(f"Ingestion complete in {elapsed:.1f}s. DB has {store.count()} chunks.")
    log.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodeIS ingestion pipeline")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion even if DB is already populated",
    )
    args = parser.parse_args()
    run_ingestion(force_reingest=args.force)
