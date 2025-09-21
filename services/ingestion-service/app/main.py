import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our Gemini client
from gemini_client import analyze_startup_materials

load_dotenv()

app = FastAPI(title="AI Startup Analyst - Data Collection Service")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for demo (in production, use proper database)
analysis_storage: Dict[str, Any] = {}

# Request/Response models
class TextIngestionRequest(BaseModel):
    text: str
    title: str = "Startup Material"
    source: str = "manual_input"

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    created_at: str
    analysis: Dict[str, Any]
    metadata: Dict[str, str]

@app.post("/ingest-text/", response_model=AnalysisResponse)
async def ingest_text(request: TextIngestionRequest):
    """
    Data Collection Agent: Ingest text-based founder materials and analyze using Gemini AI.
    This implements the core functionality described in the project requirements.
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Process text with Gemini AI
        analysis_result = analyze_startup_materials(request.text)
        
        # Create analysis record
        analysis_record = {
            "analysis_id": analysis_id,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
            "analysis": analysis_result.dict(),
            "metadata": {
                "title": request.title,
                "source": request.source,
                "text_length": str(len(request.text)),
                "processed_by": "gemini-2.5-pro"
            }
        }
        
        # Store in memory (in production, use proper database)
        analysis_storage[analysis_id] = analysis_record
        
        return AnalysisResponse(**analysis_record)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Retrieve a specific analysis by ID.
    """
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_storage[analysis_id]

@app.get("/analyses/")
async def list_analyses():
    """
    List all analyses (for development/demo purposes).
    """
    return {
        "total": len(analysis_storage),
        "analyses": list(analysis_storage.values())
    }

@app.get("/")
def read_root():
    return {
        "message": "AI Startup Analyst - Data Collection Agent",
        "description": "Ingests founder materials and generates structured investment insights using Gemini AI",
        "endpoints": {
            "POST /ingest-text/": "Analyze startup materials",
            "GET /analysis/{id}": "Retrieve specific analysis",
            "GET /analyses/": "List all analyses"
        },
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "data-collection-agent"}
