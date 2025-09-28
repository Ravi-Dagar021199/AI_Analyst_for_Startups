"""
Enhanced Data Ingestion Service Main Application
"""
import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .processors import (
    DocumentProcessor, 
    VideoProcessor, 
    ImageProcessor,
    ExternalDataCollector
)
from .database import get_db, create_tables, save_raw_file_record, save_processing_result
from .pubsub_client import PubSubManager
from .gcs_client import GCSManager

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Data Ingestion Service",
    description="Robust multi-modal data ingestion with OCR, video transcription, and external data integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    create_tables()
    gcs_manager = GCSManager()
    pubsub_manager = PubSubManager()
    doc_processor = DocumentProcessor()
    video_processor = VideoProcessor()
    image_processor = ImageProcessor()
    external_data_collector = ExternalDataCollector()
    print("✅ All services initialized successfully")
except Exception as e:
    print(f"❌ Service initialization error: {e}")

# Request/Response models
class FileUploadResponse(BaseModel):
    file_id: str
    status: str
    message: str
    processing_started: bool
    estimated_completion: str

class BulkUploadResponse(BaseModel):
    batch_id: str
    total_files: int
    accepted_files: int
    rejected_files: List[str]
    processing_started: bool

class ExternalDataRequest(BaseModel):
    sources: List[str]  # URLs or API endpoints
    data_type: str  # 'website', 'api', 'social_media'
    context: str  # Context for better data extraction

@app.post("/upload/single", response_model=FileUploadResponse)
async def upload_single_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    context: str = Form(""),
    extract_external_data: bool = Form(False),
    db=Depends(get_db)
):
    """
    Upload and process a single file with comprehensive processing pipeline
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Determine file type and processing requirements
        file_extension = file.filename.lower().split('.')[-1]
        processing_requirements = _determine_processing_requirements(file_extension)
        
        # Upload file to Google Cloud Storage
        file_content = await file.read()
        gcs_path = await gcs_manager.upload_file(
            file_content, 
            file_id, 
            file.filename,
            content_type=file.content_type
        )
        
        # Save file record to database
        file_record = {
            "id": file_id,
            "original_filename": file.filename,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "gcs_path": gcs_path,
            "title": title or file.filename,
            "context": context,
            "processing_requirements": processing_requirements,
            "extract_external_data": extract_external_data,
            "status": "uploaded"
        }
        
        save_raw_file_record(db, file_record)
        
        # Start background processing
        background_tasks.add_task(
            process_file_async,
            file_id,
            gcs_path,
            processing_requirements,
            context,
            extract_external_data
        )
        
        return FileUploadResponse(
            file_id=file_id,
            status="processing",
            message="File uploaded successfully and processing started",
            processing_started=True,
            estimated_completion=_estimate_completion_time(processing_requirements)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload/bulk", response_model=BulkUploadResponse)
async def upload_bulk_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    context: str = Form(""),
    extract_external_data: bool = Form(False),
    db=Depends(get_db)
):
    """
    Upload and process multiple files in batch
    """
    try:
        batch_id = str(uuid.uuid4())
        accepted_files = 0
        rejected_files = []
        
        for file in files:
            try:
                # Validate each file
                if not file.filename or len(await file.read()) == 0:
                    rejected_files.append(f"{file.filename}: Empty file")
                    continue
                
                # Reset file pointer
                await file.seek(0)
                
                # Process file similar to single upload
                file_id = str(uuid.uuid4())
                file_extension = file.filename.lower().split('.')[-1]
                processing_requirements = _determine_processing_requirements(file_extension)
                
                file_content = await file.read()
                gcs_path = await gcs_manager.upload_file(
                    file_content, 
                    file_id, 
                    file.filename,
                    content_type=file.content_type
                )
                
                file_record = {
                    "id": file_id,
                    "batch_id": batch_id,
                    "original_filename": file.filename,
                    "file_size": len(file_content),
                    "content_type": file.content_type,
                    "gcs_path": gcs_path,
                    "context": context,
                    "processing_requirements": processing_requirements,
                    "extract_external_data": extract_external_data,
                    "status": "uploaded"
                }
                
                save_raw_file_record(db, file_record)
                
                # Add to background processing queue
                background_tasks.add_task(
                    process_file_async,
                    file_id,
                    gcs_path,
                    processing_requirements,
                    context,
                    extract_external_data
                )
                
                accepted_files += 1
                
            except Exception as e:
                rejected_files.append(f"{file.filename}: {str(e)}")
        
        return BulkUploadResponse(
            batch_id=batch_id,
            total_files=len(files),
            accepted_files=accepted_files,
            rejected_files=rejected_files,
            processing_started=accepted_files > 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")

@app.post("/external-data/collect")
async def collect_external_data(
    request: ExternalDataRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """
    Collect data from external sources (APIs, websites, etc.)
    """
    try:
        collection_id = str(uuid.uuid4())
        
        # Start background collection
        background_tasks.add_task(
            collect_external_data_async,
            collection_id,
            request.sources,
            request.data_type,
            request.context
        )
        
        return {
            "collection_id": collection_id,
            "status": "started",
            "sources_count": len(request.sources),
            "message": "External data collection started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"External data collection failed: {str(e)}")

async def process_file_async(
    file_id: str,
    gcs_path: str,
    processing_requirements: Dict[str, bool],
    context: str,
    extract_external_data: bool
):
    """
    Asynchronous file processing pipeline
    """
    try:
        print(f"🔄 Starting processing for file {file_id}")
        
        # Download file from GCS
        file_content = await gcs_manager.download_file(gcs_path)
        
        extracted_content = {}
        
        # Process based on requirements
        if processing_requirements.get("text_extraction"):
            print(f"📝 Extracting text from {file_id}")
            extracted_content["text"] = await doc_processor.extract_text(file_content)
            
        if processing_requirements.get("ocr_required"):
            print(f"👁️ Running OCR on {file_id}")
            extracted_content["ocr_text"] = await image_processor.extract_text_ocr(file_content)
            
        if processing_requirements.get("video_transcription"):
            print(f"🎵 Transcribing video/audio {file_id}")
            extracted_content["transcript"] = await video_processor.transcribe_video(file_content)
            
        if processing_requirements.get("presentation_parsing"):
            print(f"📊 Parsing presentation {file_id}")
            extracted_content.update(await doc_processor.extract_presentation_content(file_content))
        
        # Unify all extracted content
        unified_content = _unify_content(extracted_content)
        
        # Extract external data if requested
        external_data = {}
        if extract_external_data and unified_content:
            print(f"🌐 Collecting external data for {file_id}")
            external_data = await external_data_collector.collect_contextual_data(
                unified_content, context
            )
        
        # Save processing results
        processing_result = {
            "file_id": file_id,
            "extracted_text": extracted_content.get("text"),
            "ocr_text": extracted_content.get("ocr_text"),
            "transcript_text": extracted_content.get("transcript"),
            "presentation_content": extracted_content.get("slides_detail"),
            "unified_content": unified_content,
            "external_data": external_data,
            "processing_method": processing_requirements,
            "processing_completed_at": datetime.utcnow(),
            "status": "completed"
        }
        
        # Save to database
        from .database import SessionLocal
        db = SessionLocal()
        try:
            save_processing_result(db, processing_result)
            
            # Publish "ready for curation" event
            await pubsub_manager.publish_curation_ready_event({
                "file_id": file_id,
                "unified_content": unified_content[:500] + "..." if len(unified_content) > 500 else unified_content,
                "external_data_available": bool(external_data)
            })
            
            print(f"✅ Processing completed for file {file_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Processing failed for file {file_id}: {e}")

async def collect_external_data_async(
    collection_id: str,
    sources: List[str],
    data_type: str,
    context: str
):
    """
    Asynchronous external data collection
    """
    try:
        print(f"🌐 Starting external data collection {collection_id}")
        collected_data = await external_data_collector.collect_from_sources(
            sources, data_type, context
        )
        print(f"✅ External data collection completed {collection_id}")
        
    except Exception as e:
        print(f"❌ External data collection failed for {collection_id}: {e}")

def _determine_processing_requirements(file_extension: str) -> Dict[str, bool]:
    """
    Determine what processing is required based on file type
    """
    requirements = {
        "text_extraction": False,
        "ocr_required": False,
        "video_transcription": False,
        "presentation_parsing": False
    }
    
    if file_extension in ["txt", "md", "rtf"]:
        requirements["text_extraction"] = True
    elif file_extension in ["pdf"]:
        requirements["text_extraction"] = True
        requirements["ocr_required"] = True  # For image-based PDFs
    elif file_extension in ["doc", "docx"]:
        requirements["text_extraction"] = True
    elif file_extension in ["ppt", "pptx"]:
        requirements["presentation_parsing"] = True
    elif file_extension in ["jpg", "jpeg", "png", "tiff", "bmp"]:
        requirements["ocr_required"] = True
    elif file_extension in ["mp4", "avi", "mov", "mkv", "webm"]:
        requirements["video_transcription"] = True
    elif file_extension in ["mp3", "wav", "m4a", "flac"]:
        requirements["video_transcription"] = True  # Audio transcription
    
    return requirements

def _unify_content(extracted_content: Dict[str, Any]) -> str:
    """
    Unify all extracted content into a single coherent text
    """
    unified_parts = []
    
    if "text" in extracted_content and extracted_content["text"]:
        unified_parts.append("=== DOCUMENT TEXT ===")
        unified_parts.append(extracted_content["text"])
    
    if "ocr_text" in extracted_content and extracted_content["ocr_text"]:
        unified_parts.append("=== OCR EXTRACTED TEXT ===")
        unified_parts.append(extracted_content["ocr_text"])
    
    if "transcript" in extracted_content and extracted_content["transcript"]:
        unified_parts.append("=== VIDEO/AUDIO TRANSCRIPT ===")
        unified_parts.append(extracted_content["transcript"])
    
    if "slides_content" in extracted_content and extracted_content["slides_content"]:
        unified_parts.append("=== PRESENTATION CONTENT ===")
        unified_parts.append(extracted_content["slides_content"])
    
    return "\n\n".join(unified_parts) if unified_parts else "No content extracted"

def _estimate_completion_time(requirements: Dict[str, bool]) -> str:
    """
    Estimate processing completion time based on requirements
    """
    base_time = 30  # seconds
    
    if requirements.get("ocr_required"):
        base_time += 60
    if requirements.get("video_transcription"):
        base_time += 120
    if requirements.get("presentation_parsing"):
        base_time += 45
    
    return f"~{base_time // 60}m {base_time % 60}s"

@app.get("/files/status/{file_id}")
async def get_file_status(file_id: str, db=Depends(get_db)):
    """Get processing status of a file"""
    try:
        from .database import RawFileRecord, ProcessedContent
        
        file_record = db.query(RawFileRecord).filter(RawFileRecord.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        processed_content = db.query(ProcessedContent).filter(ProcessedContent.file_id == file_id).first()
        
        return {
            "file_id": file_id,
            "filename": file_record.original_filename,
            "status": file_record.status,
            "processing_requirements": file_record.processing_requirements,
            "content_available": bool(processed_content),
            "created_at": file_record.created_at.isoformat(),
            "processing_completed_at": file_record.processing_completed_at.isoformat() if file_record.processing_completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file status: {str(e)}")

@app.get("/")
def read_root():
    return {
        "service": "Enhanced Data Ingestion Service",
        "version": "2.0.0",
        "features": [
            "Multi-modal file processing",
            "OCR for image-based content",
            "Video/audio transcription",
            "External data integration",
            "Bulk upload support",
            "Async processing pipeline",
            "Google Cloud integration"
        ],
        "supported_formats": {
            "documents": ["PDF", "DOC", "DOCX", "TXT", "MD"],
            "presentations": ["PPT", "PPTX"],
            "images": ["JPG", "PNG", "TIFF", "BMP"],
            "videos": ["MP4", "AVI", "MOV", "MKV"],
            "audio": ["MP3", "WAV", "M4A", "FLAC"]
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}