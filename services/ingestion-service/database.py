"""
Database configuration and models for AI Startup Analyst platform.
Production-ready PostgreSQL integration.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "sslmode": "prefer",
        "connect_timeout": 60,
        "application_name": "ai_startup_analyst"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StartupAnalysisDB(Base):
    """Database model for startup analysis results."""
    __tablename__ = "startup_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    source = Column(String, default="web_interface")
    text_content = Column(Text, nullable=False)
    
    # Analysis results
    founder_profile = Column(JSON)
    market_opportunity = Column(JSON)
    unique_differentiator = Column(JSON)
    business_metrics = Column(JSON)
    overall_score = Column(Float)
    key_insights = Column(JSON)
    risk_flags = Column(JSON)
    
    # Metadata
    processed_by = Column(String, default="gemini-2.5-flash")
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String, nullable=True)  # For future user association


class UserSession(Base):
    """Track user sessions for analytics."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    session_start = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    analyses_count = Column(Integer, default=0)


def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_analysis_by_id(db, analysis_id: str):
    """Get analysis by ID."""
    return db.query(StartupAnalysisDB).filter(StartupAnalysisDB.id == analysis_id).first()


def get_all_analyses(db, limit: int = 100):
    """Get all analyses with limit."""
    return db.query(StartupAnalysisDB).order_by(StartupAnalysisDB.created_at.desc()).limit(limit).all()


def save_analysis(db, analysis_data: dict):
    """Save analysis to database with retry logic."""
    try:
        db_analysis = StartupAnalysisDB(**analysis_data)
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    except Exception as e:
        db.rollback()
        # Retry once with a fresh connection
        try:
            db.close()
            db = SessionLocal()
            db_analysis = StartupAnalysisDB(**analysis_data)
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            return db_analysis
        except Exception as retry_error:
            db.rollback()
            raise retry_error
        finally:
            db.close()