from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from generation.rag_engine import get_rag_engine
from ingestion.vector_store import get_vector_store
from config import QA_DIR
from utils.logger import get_logger

log = get_logger(__name__)

app = FastAPI(
    title       = "CodeIS API",
    description = "Intelligent Query System for IS 875 Codes using RAG",
    version     = "1.0.0",
)

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Request / Response schemas

class QueryRequest(BaseModel):
    question:    str
    top_k:       int  = 5
    multi_hop:   bool = False
    filter_part: Optional[str] = None   


class QueryResponse(BaseModel):
    query:          str
    answer:         str
    cited_clauses:  List[str]
    confidence:     float
    is_multi_hop:   bool
    latency_s:      float
    sources:        List[dict]


class FeedbackRequest(BaseModel):
    question:    str
    answer:      str
    helpful:     bool
    comment:     Optional[str] = None


class FeedbackResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status:       str
    chunk_count:  int
    llm_provider: str

# routes
@app.on_event("startup")
async def startup_event():
    import asyncio
    from ingestion.embedder import get_embedding_model
    from ingestion.vector_store import get_vector_store
    from retrieval.bm25_retriever import get_bm25_retriever
    loop = asyncio.get_event_loop()
    store = get_vector_store()
    await loop.run_in_executor(None, get_embedding_model)
    get_bm25_retriever(store)

@app.get("/", tags=["Health"])
def root():
    return {"message": "CodeIS API is running. Visit /docs for Swagger UI."}


@app.get("/status", response_model=StatusResponse, tags=["Health"])
def get_status():
    """Returns DB population status and LLM provider info."""
    from config import LLM_PROVIDER
    try:
        store = get_vector_store()
        count = store.count()
        status = "ready" if count > 0 else "empty"
    except Exception as e:
        log.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return StatusResponse(
        status       = status,
        chunk_count  = count,
        llm_provider = LLM_PROVIDER,
    )


@app.post("/query", response_model=QueryResponse, tags=["Query"])
def run_query(request: QueryRequest):
    """
    Main RAG query endpoint.
    Accepts a natural-language question about IS 875.
    Returns a grounded answer with clause citations.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        engine   = get_rag_engine()
        response = engine.query(
            question    = request.question,
            top_k       = request.top_k,
            multi_hop   = request.multi_hop,
            filter_part = request.filter_part,
        )
        return QueryResponse(**response.to_dict())
    except Exception as e:
        log.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def submit_feedback(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Collect user feedback on a response (helpful / not helpful).
    Feedback is appended to a JSONL log for later analysis.
    """
    background_tasks.add_task(_save_feedback, feedback.dict())
    return FeedbackResponse(message="Feedback received. Thank you!")


@app.get("/eval", tags=["Evaluation"])
def run_evaluation():
    """
    Run the evaluation suite against the 50 QA pairs.
    Returns aggregate metrics.
    """
    from evaluation.evaluator import Evaluator
    qa_file = QA_DIR / "qa_pairs.json"

    if not qa_file.exists():
        raise HTTPException(
            status_code = 404,
            detail      = "QA pairs file not found. Run: python evaluation/generate_qa.py",
        )

    try:
        evaluator = Evaluator()
        metrics   = evaluator.evaluate_from_file(qa_file)
        # Remove per_question from API response (too large)
        metrics.pop("per_question", None)
        return metrics
    except Exception as e:
        log.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background helpers

def _save_feedback(data: dict):
    feedback_log = QA_DIR / "feedback_log.jsonl"
    with open(feedback_log, "a") as f:
        f.write(json.dumps(data) + "\n")
    log.debug(f"Feedback saved: {data}")


# Run directlty

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
