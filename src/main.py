from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.ragPipeline import setup_knowledge_base, retrieve_relevant_docs
from src.llmService import generate_rca

# Initialize the API
app = FastAPI(
    title="AI DevOps Log Analyzer",
    description="Automated RAG pipeline for root cause analysis of system logs."
)

# Load the vector database into memory when the server starts
doc_collection = setup_knowledge_base()

# Define the expected JSON payload using Pydantic
class LogPayload(BaseModel):
    error_line: str
    context: str

@app.post("/api/v1/analyze")
async def analyze_log_endpoint(payload: LogPayload):
    """
    Receives an error line and context, queries the vector DB, 
    and returns an AI-generated Root Cause Analysis.
    """
    print(f"📥 Received analysis request for: {payload.error_line}")
    try:
        # 1. Retrieve Docs
        official_docs = retrieve_relevant_docs(payload.error_line, doc_collection)
        
        # 2. Generate RCA
        rca_report = generate_rca(payload.context, official_docs)
        
        # 3. Return JSON response
        return {
            "status": "success",
            "error_analyzed": payload.error_line,
            "rca_report": rca_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))