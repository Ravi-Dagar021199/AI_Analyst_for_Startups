"""
Enhanced database models for multi-modal data ingestion and curation
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/ai_startup_analyst')

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RawFileRecord(Base):
    """Raw uploaded files before processing"""
    __tablename__ = "raw_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, nullable=True)  # For bulk uploads
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    gcs_path = Column(String, nullable=False)  # Path in Google Cloud Storage
    
    # User-provided metadata
    title = Column(String, nullable=True)
    context = Column(Text, nullable=True)
    
    # Processing configuration
    processing_requirements = Column(JSON, nullable=False)  # What processing is needed
    extract_external_data = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)

class ProcessedContent(Base):
    """Processed and extracted content from files"""
    __tablename__ = "processed_content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, nullable=False)  # References RawFileRecord.id
    
    # Extracted content by type
    extracted_text = Column(Text, nullable=True)
    ocr_text = Column(Text, nullable=True)
    transcript_text = Column(Text, nullable=True)
    presentation_content = Column(JSON, nullable=True)  # Structured presentation data
    
    # Unified content for AI processing
    unified_content = Column(Text, nullable=False)
    content_summary = Column(Text, nullable=True)
    
    # External data
    external_data = Column(JSON, nullable=True)
    external_data_sources = Column(JSON, nullable=True)
    
    # Processing metadata
    processing_method = Column(JSON, nullable=True)  # Which methods were used
    processing_duration = Column(Float, nullable=True)  # Processing time in seconds
    content_quality_score = Column(Float, nullable=True)  # Quality of extraction (0-1)
    
    # Status
    status = Column(String, default="processed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CuratedDataset(Base):
    """User-curated datasets ready for AI analysis"""
    __tablename__ = "curated_datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)  # Future user system integration
    
    # Dataset composition
    source_files = Column(JSON, nullable=False)  # List of file IDs that comprise this dataset
    dataset_name = Column(String, nullable=False)
    dataset_description = Column(Text, nullable=True)
    
    # Curated content
    raw_unified_content = Column(Text, nullable=False)  # Original unified content
    curated_content = Column(Text, nullable=False)  # User-edited content
    excluded_sections = Column(JSON, nullable=True)  # Sections user removed
    added_content = Column(Text, nullable=True)  # Content user manually added
    
    # External data integration
    external_data_included = Column(JSON, nullable=True)
    external_data_excluded = Column(JSON, nullable=True)
    
    # User annotations
    user_notes = Column(Text, nullable=True)
    content_tags = Column(JSON, nullable=True)  # User-defined tags
    priority_sections = Column(JSON, nullable=True)  # Sections marked as high priority
    
    # Curation tracking
    curation_status = Column(String, default="in_progress")  # in_progress, completed, ready_for_ai
    curation_started_at = Column(DateTime, default=datetime.utcnow)
    curation_completed_at = Column(DateTime, nullable=True)
    
    # Quality metrics
    content_completeness_score = Column(Float, nullable=True)  # How complete is the dataset
    relevance_score = Column(Float, nullable=True)  # How relevant to analysis goals
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExternalDataSource(Base):
    """Track external data sources and their collection status"""
    __tablename__ = "external_data_sources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # website, api, database, social_media
    
    # Content
    collected_data = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)
    
    # Collection metadata
    collection_method = Column(String, nullable=True)  # scraping, api, manual
    collection_timestamp = Column(DateTime, nullable=False)
    data_quality_score = Column(Float, nullable=True)
    
    # Association
    related_files = Column(JSON, nullable=True)  # File IDs this data is relevant to
    related_datasets = Column(JSON, nullable=True)  # Dataset IDs this data is included in
    
    # Status
    status = Column(String, default="collected")  # collected, validated, integrated, excluded
    created_at = Column(DateTime, default=datetime.utcnow)

class AIAnalysisJob(Base):
    """Track AI analysis jobs and their results"""
    __tablename__ = "ai_analysis_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, nullable=False)  # References CuratedDataset.id
    
    # Analysis configuration
    analysis_type = Column(String, nullable=False)  # startup_evaluation, market_analysis, etc.
    ai_model_used = Column(String, nullable=False)  # gemini-2.5-flash, gpt-4, etc.
    analysis_parameters = Column(JSON, nullable=True)
    
    # Results
    analysis_results = Column(JSON, nullable=True)
    report_generated = Column(Text, nullable=True)
    confidence_scores = Column(JSON, nullable=True)
    
    # Performance metrics
    processing_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Database operations
def save_raw_file_record(db, file_data: dict):
    """Save raw file record"""
    try:
        record = RawFileRecord(**file_data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise e

def save_processing_result(db, processing_data: dict):
    """Save processed content"""
    try:
        record = ProcessedContent(**processing_data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise e

def create_curated_dataset(db, dataset_data: dict):
    """Create new curated dataset"""
    try:
        dataset = CuratedDataset(**dataset_data)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset
    except Exception as e:
        db.rollback()
        raise e

def update_curated_dataset(db, dataset_id: str, updates: dict):
    """Update curated dataset"""
    try:
        dataset = db.query(CuratedDataset).filter(CuratedDataset.id == dataset_id).first()
        if dataset:
            for key, value in updates.items():
                setattr(dataset, key, value)
            dataset.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(dataset)
        return dataset
    except Exception as e:
        db.rollback()
        raise e

def get_files_by_status(db, status: str, limit: int = 100):
    """Get files by processing status"""
    return db.query(RawFileRecord).filter(RawFileRecord.status == status).limit(limit).all()

def get_processed_content(db, file_id: str):
    """Get processed content for a file"""
    return db.query(ProcessedContent).filter(ProcessedContent.file_id == file_id).first()

def get_curated_datasets(db, user_id: str = None, status: str = None, limit: int = 100):
    """Get curated datasets with optional filtering"""
    query = db.query(CuratedDataset)
    
    if user_id:
        query = query.filter(CuratedDataset.user_id == user_id)
    if status:
        query = query.filter(CuratedDataset.curation_status == status)
    
    return query.order_by(CuratedDataset.created_at.desc()).limit(limit).all()

def save_ai_analysis_job(db, job_data: dict):
    """Save AI analysis job"""
    try:
        job = AIAnalysisJob(**job_data)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        raise e

def update_analysis_job_status(db, job_id: str, status: str, **updates):
    """Update analysis job status and other fields"""
    try:
        job = db.query(AIAnalysisJob).filter(AIAnalysisJob.id == job_id).first()
        if job:
            job.status = status
            for key, value in updates.items():
                setattr(job, key, value)
            db.commit()
            db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        raise e