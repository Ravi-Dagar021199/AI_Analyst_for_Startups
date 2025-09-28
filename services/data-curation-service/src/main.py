"""
Data Curation Service
Provides user interface and API for reviewing, editing, and curating processed data
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Data Curation Service",
    description="User interface for data review and curation before AI analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class DatasetCreateRequest(BaseModel):
    source_files: List[str]  # File IDs to include
    dataset_name: str
    dataset_description: Optional[str] = ""

class DatasetUpdateRequest(BaseModel):
    curated_content: str
    excluded_sections: Optional[List[str]] = []
    added_content: Optional[str] = ""
    user_notes: Optional[str] = ""
    content_tags: Optional[List[str]] = []
    priority_sections: Optional[List[str]] = []

class CurationResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    status: str
    content_summary: str
    files_included: List[Dict[str, Any]]
    external_data_available: bool
    curation_progress: float  # 0.0 to 1.0

@app.post("/datasets/create", response_model=CurationResponse)
async def create_dataset(
    request: DatasetCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new dataset from processed files for curation
    """
    try:
        # This would integrate with your database
        from enhanced_ingestion_service.app.database import SessionLocal, get_processed_content, create_curated_dataset
        
        db = SessionLocal()
        try:
            # Gather processed content from source files
            unified_content_parts = []
            files_included = []
            external_data_available = False
            
            for file_id in request.source_files:
                processed_content = get_processed_content(db, file_id)
                if processed_content:
                    unified_content_parts.append(processed_content.unified_content)
                    files_included.append({
                        "file_id": file_id,
                        "content_length": len(processed_content.unified_content),
                        "has_external_data": bool(processed_content.external_data)
                    })
                    if processed_content.external_data:
                        external_data_available = True
            
            # Create unified content
            raw_unified_content = "\n\n" + "="*50 + "\n\n".join(unified_content_parts)
            
            # Create dataset record
            dataset_data = {
                "source_files": request.source_files,
                "dataset_name": request.dataset_name,
                "dataset_description": request.dataset_description,
                "raw_unified_content": raw_unified_content,
                "curated_content": raw_unified_content,  # Initially same as raw
                "curation_status": "in_progress"
            }
            
            dataset = create_curated_dataset(db, dataset_data)
            
            return CurationResponse(
                dataset_id=dataset.id,
                dataset_name=dataset.dataset_name,
                status=dataset.curation_status,
                content_summary=f"Combined content from {len(files_included)} files",
                files_included=files_included,
                external_data_available=external_data_available,
                curation_progress=0.0
            )
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset creation failed: {str(e)}")

@app.get("/datasets/{dataset_id}")
async def get_dataset_for_curation(dataset_id: str):
    """
    Get dataset details for curation interface
    """
    try:
        from enhanced_ingestion_service.app.database import SessionLocal
        
        db = SessionLocal()
        try:
            from enhanced_ingestion_service.app.database import CuratedDataset
            dataset = db.query(CuratedDataset).filter(CuratedDataset.id == dataset_id).first()
            
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            return {
                "dataset_id": dataset.id,
                "dataset_name": dataset.dataset_name,
                "dataset_description": dataset.dataset_description,
                "raw_content": dataset.raw_unified_content,
                "curated_content": dataset.curated_content,
                "excluded_sections": dataset.excluded_sections or [],
                "added_content": dataset.added_content or "",
                "user_notes": dataset.user_notes or "",
                "content_tags": dataset.content_tags or [],
                "priority_sections": dataset.priority_sections or [],
                "status": dataset.curation_status,
                "created_at": dataset.created_at.isoformat(),
                "updated_at": dataset.updated_at.isoformat()
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset: {str(e)}")

@app.put("/datasets/{dataset_id}/curate")
async def update_dataset_curation(
    dataset_id: str,
    request: DatasetUpdateRequest,
    background_tasks: BackgroundTasks
):
    """
    Update curated dataset with user modifications
    """
    try:
        from enhanced_ingestion_service.app.database import SessionLocal, update_curated_dataset
        
        db = SessionLocal()
        try:
            updates = {
                "curated_content": request.curated_content,
                "excluded_sections": request.excluded_sections,
                "added_content": request.added_content,
                "user_notes": request.user_notes,
                "content_tags": request.content_tags,
                "priority_sections": request.priority_sections,
                "curation_status": "completed"
            }
            
            dataset = update_curated_dataset(db, dataset_id, updates)
            
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            # Calculate curation progress
            progress = _calculate_curation_progress(dataset)
            
            # If curation is complete, publish "ready for AI" event
            if progress >= 1.0:
                background_tasks.add_task(
                    _publish_analysis_ready_event,
                    dataset_id,
                    dataset.curated_content
                )
            
            return {
                "dataset_id": dataset.id,
                "status": dataset.curation_status,
                "curation_progress": progress,
                "message": "Dataset curation updated successfully"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update curation: {str(e)}")

@app.get("/datasets/")
async def list_datasets(status: Optional[str] = None, limit: int = 50):
    """
    List all curated datasets
    """
    try:
        from enhanced_ingestion_service.app.database import SessionLocal, get_curated_datasets
        
        db = SessionLocal()
        try:
            datasets = get_curated_datasets(db, status=status, limit=limit)
            
            dataset_list = []
            for dataset in datasets:
                dataset_list.append({
                    "dataset_id": dataset.id,
                    "dataset_name": dataset.dataset_name,
                    "status": dataset.curation_status,
                    "files_count": len(dataset.source_files),
                    "content_length": len(dataset.curated_content),
                    "created_at": dataset.created_at.isoformat(),
                    "updated_at": dataset.updated_at.isoformat()
                })
            
            return {
                "total": len(dataset_list),
                "datasets": dataset_list
            }
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")

@app.post("/datasets/{dataset_id}/approve")
async def approve_for_analysis(
    dataset_id: str,
    background_tasks: BackgroundTasks
):
    """
    Mark dataset as ready for AI analysis
    """
    try:
        from enhanced_ingestion_service.app.database import SessionLocal, update_curated_dataset
        
        db = SessionLocal()
        try:
            updates = {
                "curation_status": "ready_for_ai",
                "curation_completed_at": datetime.utcnow()
            }
            
            dataset = update_curated_dataset(db, dataset_id, updates)
            
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            # Publish analysis ready event
            background_tasks.add_task(
                _publish_analysis_ready_event,
                dataset_id,
                dataset.curated_content
            )
            
            return {
                "dataset_id": dataset_id,
                "status": "ready_for_ai",
                "message": "Dataset approved for AI analysis"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve dataset: {str(e)}")

def _calculate_curation_progress(dataset) -> float:
    """
    Calculate curation progress based on user activity
    """
    progress = 0.0
    
    # Base progress for having content
    if dataset.curated_content:
        progress += 0.4
    
    # Progress for user modifications
    if dataset.added_content:
        progress += 0.2
    
    if dataset.excluded_sections:
        progress += 0.2
    
    if dataset.user_notes:
        progress += 0.1
    
    if dataset.content_tags:
        progress += 0.1
    
    return min(progress, 1.0)

async def _publish_analysis_ready_event(dataset_id: str, curated_content: str):
    """
    Publish event that dataset is ready for AI analysis
    """
    try:
        from enhanced_ingestion_service.app.pubsub_client import PubSubManager
        
        pubsub = PubSubManager()
        await pubsub.publish_analysis_ready_event({
            "dataset_id": dataset_id,
            "content_preview": curated_content[:500] + "..." if len(curated_content) > 500 else curated_content,
            "content_length": len(curated_content),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Failed to publish analysis ready event: {e}")

@app.get("/")
def read_root():
    return {
        "service": "Data Curation Service",
        "version": "1.0.0",
        "features": [
            "Dataset creation from processed files",
            "User-friendly curation interface",
            "Content editing and annotation",
            "Section exclusion and addition",
            "Progress tracking",
            "Analysis readiness approval"
        ],
        "endpoints": {
            "POST /datasets/create": "Create new dataset for curation",
            "GET /datasets/{id}": "Get dataset for curation",
            "PUT /datasets/{id}/curate": "Update dataset curation",
            "GET /datasets/": "List all datasets",
            "POST /datasets/{id}/approve": "Approve dataset for AI analysis"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}