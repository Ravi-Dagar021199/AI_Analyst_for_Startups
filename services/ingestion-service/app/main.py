import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import our Gemini client and database
from gemini_client import analyze_startup_materials
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import get_db, create_tables, save_analysis, get_analysis_by_id, get_all_analyses

load_dotenv()

# Create database tables on startup
try:
    create_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Database initialization error: {e}")

app = FastAPI(title="AI Startup Analyst - Data Collection Service")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production PostgreSQL database storage enabled

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
async def ingest_text(request: TextIngestionRequest, db: Session = Depends(get_db)):
    """
    Data Collection Agent: Ingest text-based founder materials and analyze using Gemini AI.
    Production-ready with PostgreSQL persistence.
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Process text with Gemini AI
        analysis_result = analyze_startup_materials(request.text)
        
        # Prepare data for database storage
        db_data = {
            "id": analysis_id,
            "title": request.title,
            "source": request.source,
            "text_content": request.text,
            "founder_profile": analysis_result.founder_profile.dict(),
            "market_opportunity": analysis_result.market_opportunity.dict(),
            "unique_differentiator": analysis_result.unique_differentiator.dict(),
            "business_metrics": analysis_result.business_metrics.dict(),
            "overall_score": analysis_result.overall_score,
            "key_insights": analysis_result.key_insights,
            "risk_flags": analysis_result.risk_flags,
            "processed_by": "gemini-2.5-flash",
            "status": "completed"
        }
        
        # Save to PostgreSQL database
        db_analysis = save_analysis(db, db_data)
        
        # Format response
        analysis_record = {
            "analysis_id": db_analysis.id,
            "status": db_analysis.status,
            "created_at": db_analysis.created_at.isoformat(),
            "analysis": analysis_result.dict(),
            "metadata": {
                "title": db_analysis.title,
                "source": db_analysis.source,
                "text_length": str(len(request.text)),
                "processed_by": db_analysis.processed_by
            }
        }
        
        return AnalysisResponse(**analysis_record)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific analysis by ID from PostgreSQL database.
    """
    db_analysis = get_analysis_by_id(db, analysis_id)
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Format response
    return {
        "analysis_id": db_analysis.id,
        "status": db_analysis.status,
        "created_at": db_analysis.created_at.isoformat(),
        "analysis": {
            "founder_profile": db_analysis.founder_profile,
            "market_opportunity": db_analysis.market_opportunity,
            "unique_differentiator": db_analysis.unique_differentiator,
            "business_metrics": db_analysis.business_metrics,
            "overall_score": db_analysis.overall_score,
            "key_insights": db_analysis.key_insights,
            "risk_flags": db_analysis.risk_flags
        },
        "metadata": {
            "title": db_analysis.title,
            "source": db_analysis.source,
            "processed_by": db_analysis.processed_by
        }
    }

@app.get("/analyses/")
async def list_analyses(db: Session = Depends(get_db), limit: int = 50):
    """
    List all analyses from PostgreSQL database.
    """
    db_analyses = get_all_analyses(db, limit)
    
    analyses = []
    for db_analysis in db_analyses:
        analyses.append({
            "analysis_id": db_analysis.id,
            "status": db_analysis.status,
            "created_at": db_analysis.created_at.isoformat(),
            "title": db_analysis.title,
            "overall_score": db_analysis.overall_score
        })
    
    return {
        "total": len(analyses),
        "analyses": analyses
    }

@app.get("/")
def read_root():
    return {
        "message": "AI Startup Analyst - Data Collection Agent",
        "description": "Production-ready platform for startup analysis using Gemini AI and PostgreSQL",
        "endpoints": {
            "POST /ingest-text/": "Analyze startup materials with AI",
            "GET /analysis/{id}": "Retrieve specific analysis",
            "GET /analyses/": "List all analyses",
            "GET /health": "Health check endpoint"
        },
        "version": "1.0.0",
        "database": "PostgreSQL",
        "ai_model": "Gemini 2.5 Flash",
        "status": "production-ready"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "data-collection-agent"}
