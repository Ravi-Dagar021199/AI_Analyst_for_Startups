import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import our Gemini client and database
from gemini_client import analyze_startup_materials
from .data_collector import data_collector
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
    allow_origins=["http://localhost:5000", "https://localhost:5000"],  # Production: specify frontend domain only
    allow_credentials=False,  # Disabled for security - enable only if authentication required
    allow_methods=["GET", "POST"],  # Only required methods
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
        
        # Enhanced data collection with security controls
        print("🔍 Collecting external data sources...")
        enhanced_content = request.text
        data_sources_found = 0
        enhanced_analysis_performed = False
        
        try:
            # Enhanced analysis for substantial content
            if len(request.text) > 100:
                print("🔍 Performing enhanced startup analysis...")
                
                # Collect intelligent analysis
                external_data = data_collector.collect_comprehensive_data(request.text)
                
                if external_data.get('data_sources') and len(external_data['data_sources']) > 0:
                    enhanced_analysis_performed = True
                    data_sources_found = len(external_data['data_sources'])
                    
                    # Add intelligent context to analysis
                    enhanced_content += "\n\n--- ENHANCED INTELLIGENCE ANALYSIS ---\n"
                    for source in external_data['data_sources']:
                        enhanced_content += f"\n[{source.source_type.upper()}] {source.title}\n"
                        enhanced_content += f"Analysis: {source.content}\n"
                        enhanced_content += f"Confidence: {source.confidence:.1f}/1.0\n\n"
                    
                    print(f"✅ Enhanced analysis complete: {data_sources_found} intelligence sources")
                else:
                    print("ℹ️ No enhanced intelligence generated - using standard analysis")
                        
        except Exception as e:
            print(f"Enhanced analysis failed (continuing with standard analysis): {e}")
        
        # Process enhanced text with Gemini AI
        analysis_result = analyze_startup_materials(enhanced_content)
        
        # Prepare data for database storage
        db_data = {
            "id": analysis_id,
            "title": request.title,
            "source": request.source,
            "text_content": request.text,
            "founder_profile": analysis_result.founder_profile if isinstance(analysis_result.founder_profile, dict) else analysis_result.founder_profile.dict(),
            "market_opportunity": analysis_result.market_opportunity if isinstance(analysis_result.market_opportunity, dict) else analysis_result.market_opportunity.dict(),
            "unique_differentiator": analysis_result.unique_differentiator if isinstance(analysis_result.unique_differentiator, dict) else analysis_result.unique_differentiator.dict(),
            "business_metrics": analysis_result.business_metrics if isinstance(analysis_result.business_metrics, dict) else analysis_result.business_metrics.dict(),
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
                "processed_by": db_analysis.processed_by,
                "enhanced_analysis": enhanced_analysis_performed,
                "data_sources_found": data_sources_found
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

@app.post("/ingest-file/", response_model=AnalysisResponse)
async def ingest_file(
    file: UploadFile = File(..., max_file_size=10485760),  # 10MB limit
    title: str = Form(None),
    source: str = Form("file_upload"),
    db: Session = Depends(get_db)
):
    """
    Data Collection Agent: Ingest file-based founder materials and analyze using Gemini AI.
    Supports PDF, Word documents, and text files.
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Extract text from file based on type
        text_content = ""
        file_content = await file.read()
        
        if file.filename and file.filename.endswith(('.txt', '.md')):
            # Extract text from text/markdown file
            text_content = file_content.decode('utf-8')
        elif file.filename and file.filename.endswith('.pdf'):
            # Extract text from PDF file - handle binary data properly
            try:
                import io
                import re
                
                print(f"📄 Processing PDF file: {file.filename} ({len(file_content)} bytes)")
                
                # Primary approach: Use PyPDF2 for reliable text extraction
                text_content = ""
                try:
                    import PyPDF2
                    pdf_file = io.BytesIO(file_content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                # Clean the text - remove null bytes and control characters
                                page_text = page_text.replace('\x00', '').replace('\ufeff', '')
                                # Remove excessive whitespace but keep structure
                                page_text = re.sub(r'\s+', ' ', page_text).strip()
                                text_content += page_text + "\n"
                                print(f"  ✓ Page {page_num + 1}: {len(page_text)} characters")
                        except Exception as page_error:
                            print(f"  ⚠️  Page {page_num + 1}: Error extracting text - {page_error}")
                            continue
                            
                    print(f"✅ PyPDF2 extraction complete: {len(text_content)} total characters")
                    
                except ImportError:
                    print("⚠️  PyPDF2 not available, trying alternative extraction...")
                    # Alternative approach: Extract text from PDF binary data
                    try:
                        # Decode binary content safely, removing null bytes
                        raw_text = file_content.replace(b'\x00', b'').decode('latin-1', errors='ignore')
                        
                        # Extract text between PDF text markers
                        text_patterns = [
                            r'BT\s*.*?\s*ET',  # Text blocks
                            r'\((.*?)\)',      # Text in parentheses
                            r'Tj\s*(.*?)\s*Tj', # Text operators
                        ]
                        
                        extracted_parts = []
                        for pattern in text_patterns:
                            matches = re.findall(pattern, raw_text, re.DOTALL)
                            extracted_parts.extend(matches)
                        
                        if extracted_parts:
                            # Clean and join extracted text
                            text_content = ' '.join(extracted_parts)
                            text_content = re.sub(r'[^\w\s\.,;:!?()-]', ' ', text_content)
                            text_content = re.sub(r'\s+', ' ', text_content).strip()
                            print(f"✅ Alternative extraction: {len(text_content)} characters")
                        
                    except Exception as alt_error:
                        print(f"Alternative extraction failed: {alt_error}")
                
                # Final fallback: Extract only printable ASCII characters
                if not text_content.strip():
                    print("🔧 Trying fallback extraction...")
                    try:
                        # Remove null bytes and extract printable characters
                        safe_content = file_content.replace(b'\x00', b'').decode('ascii', errors='ignore')
                        text_content = ''.join(char for char in safe_content if char.isprintable() and ord(char) > 31)
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
                        print(f"✅ Fallback extraction: {len(text_content)} characters")
                    except Exception as fallback_error:
                        print(f"Fallback extraction failed: {fallback_error}")
                        text_content = ""
                        
            except Exception as pdf_error:
                print(f"❌ PDF processing error: {str(pdf_error)}")
                error_msg = f"Failed to process PDF file. "
                error_msg += "This might be a heavily encrypted, corrupted, or image-only PDF. "
                error_msg += "Please try: (1) saving as a new PDF, (2) converting to text format, or (3) using a different PDF viewer to re-export the file."
                raise HTTPException(status_code=400, detail=error_msg)
        elif file.filename and file.filename.endswith(('.doc', '.docx')):
            # Extract text from Word document
            try:
                from docx import Document
                import io
                doc_file = io.BytesIO(file_content)
                doc = Document(doc_file)
                text_content = ""
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
            except ImportError:
                raise HTTPException(status_code=400, detail="Word document processing not available. Please convert to PDF or text format.")
            except Exception as doc_error:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from Word document: {str(doc_error)}")
        else:
            raise HTTPException(status_code=400, detail="Supports PDF (.pdf), Word (.doc, .docx), text (.txt) and markdown (.md) files.")
        
        # Clean the final text content to remove any remaining problematic characters
        if text_content:
            # Remove null bytes and other problematic characters
            text_content = text_content.replace('\x00', '').replace('\ufeff', '')
            # Remove non-printable characters except common whitespace
            import re
            text_content = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', text_content)
            # Clean up excessive whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Debug: Print cleaned content info  
        print(f"📝 Cleaned text length: {len(text_content)} characters")
        print(f"📝 First 200 chars: {repr(text_content[:200])}")
        
        if not text_content.strip():
            error_msg = "No readable text content found in the uploaded file. "
            if file.filename and file.filename.endswith('.pdf'):
                error_msg += "This might be a scanned PDF, image-based document, or password-protected PDF. "
                error_msg += "Please try: (1) a text-based PDF with selectable text, (2) converting scanned PDF using OCR, or (3) saving as a text file."
            else:
                error_msg += "Please check that your file contains readable text content."
            raise HTTPException(status_code=400, detail=error_msg)
        
        if len(text_content.strip()) < 10:
            raise HTTPException(status_code=400, detail="The extracted text is too short. Please ensure your file contains substantial text content for analysis.")
        
        # Enhanced analysis for file uploads
        enhanced_content = text_content
        enhanced_analysis_performed = False
        data_sources_found = 0
        
        try:
            if len(text_content) > 100:
                print("🔍 Performing enhanced file analysis...")
                external_data = data_collector.collect_comprehensive_data(text_content)
                
                if external_data.get('data_sources') and len(external_data['data_sources']) > 0:
                    enhanced_analysis_performed = True
                    data_sources_found = len(external_data['data_sources'])
                    
                    enhanced_content += "\n\n--- ENHANCED INTELLIGENCE ANALYSIS ---\n"
                    for source in external_data['data_sources']:
                        enhanced_content += f"\n[{source.source_type.upper()}] {source.title}\n"
                        enhanced_content += f"Analysis: {source.content}\n"
                        enhanced_content += f"Confidence: {source.confidence:.1f}/1.0\n\n"
                    
                    print(f"✅ Enhanced file analysis complete: {data_sources_found} intelligence sources")
        except Exception as e:
            print(f"Enhanced file analysis failed (continuing with standard analysis): {e}")
        
        # Process enhanced text with Gemini AI
        analysis_result = analyze_startup_materials(enhanced_content)
        
        # Prepare data for database storage
        db_data = {
            "id": analysis_id,
            "title": title or file.filename,
            "source": source,
            "text_content": text_content,
            "founder_profile": analysis_result.founder_profile if isinstance(analysis_result.founder_profile, dict) else analysis_result.founder_profile.dict(),
            "market_opportunity": analysis_result.market_opportunity if isinstance(analysis_result.market_opportunity, dict) else analysis_result.market_opportunity.dict(),
            "unique_differentiator": analysis_result.unique_differentiator if isinstance(analysis_result.unique_differentiator, dict) else analysis_result.unique_differentiator.dict(),
            "business_metrics": analysis_result.business_metrics if isinstance(analysis_result.business_metrics, dict) else analysis_result.business_metrics.dict(),
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
                "text_length": str(len(text_content)),
                "processed_by": db_analysis.processed_by,
                "file_name": file.filename,
                "enhanced_analysis": enhanced_analysis_performed,
                "data_sources_found": data_sources_found
            }
        }
        
        return AnalysisResponse(**analysis_record)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "data-collection-agent"}
