from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.llmService import generate_rca
from src.ragPipeline import retrieve_relevant_docs, setup_knowledge_base

doc_collection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global doc_collection
    doc_collection = setup_knowledge_base()
    yield


app = FastAPI(
    title="AI DevOps Log Analyzer",
    description="Automated RAG pipeline for root cause analysis of system logs.",
    lifespan=lifespan,
)


class LogPayload(BaseModel):
    error_line: str
    context: str


@app.get("/health")
def health():
    if doc_collection is None:
        raise HTTPException(status_code=503, detail="Knowledge base not loaded")
    return {"status": "ok", "documents": len(doc_collection)}


@app.post("/api/v1/analyze")
async def analyze_log_endpoint(payload: LogPayload):
    if doc_collection is None:
        raise HTTPException(status_code=503, detail="Knowledge base not loaded")

    print(f"Received analysis request for: {payload.error_line}")
    try:
        official_docs = retrieve_relevant_docs(payload.error_line, doc_collection)
        rca_report = generate_rca(payload.context, official_docs)
        return {
            "status": "success",
            "error_analyzed": payload.error_line,
            "rca_report": rca_report,
        }
    except Exception as e:
        print(f"CRITICAL API ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
