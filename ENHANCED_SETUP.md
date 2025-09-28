# Enhanced AI Startup Analyst - Setup and Deployment Guide

## 🚀 Quick Setup

### Prerequisites
- Docker & Docker Compose
- Google Cloud Project with enabled APIs:
  - Cloud Storage
  - Cloud Vision
  - Cloud Speech-to-Text
  - Cloud Pub/Sub
  - Cloud Firestore
- PostgreSQL database
- Redis (for caching)

### Environment Setup

1. **Clone and navigate to the repository:**
```bash
git clone <repository-url>
cd AI_Analyst_for_Startups
```

2. **Set up environment variables:**
```bash
# Create environment file
cp .env.example .env

# Configure the following variables:
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_startup_analyst
GOOGLE_CLOUD_PROJECT=your-project-id
GCS_BUCKET_NAME=your-bucket-name
GEMINI_API_KEY=your-gemini-api-key
```

3. **Set up Google Cloud credentials:**
```bash
# Place your service account key
cp your-service-account-key.json serviceAccountKey.json
```

### Quick Start with Docker

1. **Start the enhanced system:**
```bash
docker-compose -f docker-compose.enhanced.yml up -d
```

2. **Initialize database:**
```bash
docker-compose exec enhanced-ingestion python -c "
from app.database import create_tables
create_tables()
print('Database initialized')
"
```

3. **Create Pub/Sub subscriptions:**
```bash
docker-compose exec enhanced-ingestion python -c "
from app.pubsub_client import PubSubManager
pubsub = PubSubManager()
pubsub.create_subscription('processing_ready', 'file-processing-sub')
pubsub.create_subscription('curation_ready', 'curation-ready-sub')
pubsub.create_subscription('analysis_ready', 'analysis-ready-sub')
print('Pub/Sub subscriptions created')
"
```

## 📊 System Architecture

### Enhanced Services

1. **Enhanced Ingestion Service** (Port 8002)
   - Multi-modal file processing
   - OCR and transcription
   - External data collection
   - Google Cloud integration

2. **Data Curation Service** (Port 3003)
   - User curation interface
   - Dataset management
   - Content editing and annotation

3. **Preprocessing Worker**
   - Pub/Sub message processing
   - Async task handling
   - Status updates

4. **Frontend Updates**
   - Enhanced upload interface
   - Multi-modal support
   - Curation dashboard

### Data Flow

```
User Upload → Enhanced Ingestion → Processing Pipeline → Curation Interface → AI Analysis
     ↓              ↓                      ↓                    ↓              ↓
   GCS Storage   Pub/Sub Events      Content Extraction    User Review    Final Report
```

## 🛠️ Development

### Running Individual Services

1. **Enhanced Ingestion Service:**
```bash
cd services/enhanced-ingestion-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

2. **Data Curation Service:**
```bash
cd services/data-curation-service
npm install
npm run dev
```

3. **Preprocessing Worker:**
```bash
cd services/preprocessing-worker
pip install -r requirements.txt
python app/worker.py
```

### Database Migrations

```bash
# Create migration
cd services/enhanced-ingestion-service
alembic init alembic
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

### Testing

```bash
# Test file upload
curl -X POST "http://localhost:8002/upload/single" \
  -F "file=@test-document.pdf" \
  -F "title=Test Document" \
  -F "context=Test upload" \
  -F "extract_external_data=true"

# Check processing status
curl "http://localhost:8002/files/status/{file_id}"

# Test curation API
curl "http://localhost:3003/datasets/"
```

## 📁 File Processing Capabilities

### Supported Formats

| Category | Formats | Processing Method |
|----------|---------|-------------------|
| Documents | PDF, DOC, DOCX, TXT, MD | Text extraction + OCR |
| Presentations | PPT, PPTX | Slide content parsing |
| Images | JPG, PNG, TIFF, BMP | OCR text extraction |
| Videos | MP4, AVI, MOV, MKV | Audio extraction + transcription |
| Audio | MP3, WAV, M4A, FLAC | Speech-to-text transcription |

### Processing Features

- **OCR**: Google Cloud Vision + Tesseract fallback
- **Transcription**: Google Cloud Speech-to-Text
- **External Data**: Intelligent context-based collection
- **Content Unification**: Merge all extracted content
- **Quality Scoring**: Processing confidence metrics

## 🎯 Usage Examples

### 1. Upload Startup Pitch Deck
```bash
curl -X POST "http://localhost:8002/upload/single" \
  -F "file=@startup-pitch.pdf" \
  -F "title=Startup XYZ Pitch Deck" \
  -F "context=Series A funding pitch presentation" \
  -F "extract_external_data=true"
```

### 2. Bulk Upload Demo Materials
```bash
curl -X POST "http://localhost:8002/upload/bulk" \
  -F "files=@pitch.pdf" \
  -F "files=@demo.mp4" \
  -F "files=@financials.xlsx" \
  -F "context=Complete startup demo package"
```

### 3. Create Curated Dataset
```bash
curl -X POST "http://localhost:3003/datasets/create" \
  -H "Content-Type: application/json" \
  -d '{
    "source_files": ["file-id-1", "file-id-2"],
    "dataset_name": "Startup XYZ Analysis",
    "dataset_description": "Complete analysis dataset"
  }'
```

### 4. Update Curation
```bash
curl -X PUT "http://localhost:3003/datasets/{dataset_id}/curate" \
  -H "Content-Type: application/json" \
  -d '{
    "curated_content": "Edited and refined content...",
    "added_content": "Additional context...",
    "user_notes": "Important points to highlight",
    "content_tags": ["fintech", "series-a", "high-priority"]
  }'
```

## 🔧 Configuration

### Enhanced Ingestion Service

```python
# app/config.py
class Settings:
    database_url: str = os.getenv("DATABASE_URL")
    gcs_bucket_name: str = os.getenv("GCS_BUCKET_NAME")
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    enable_ocr: bool = True
    enable_transcription: bool = True
    enable_external_data: bool = True
    max_file_size: int = 100_000_000  # 100MB
```

### Data Curation Service

```typescript
// config/settings.ts
export const curationSettings = {
  maxDatasetSize: 50_000_000, // 50MB
  autoSaveInterval: 30000, // 30 seconds
  supportedTags: ['fintech', 'healthtech', 'edtech', 'ai', 'saas'],
  qualityThreshold: 0.7
};
```

## 🚦 Monitoring & Debugging

### Health Checks
```bash
# Check service health
curl http://localhost:8002/health
curl http://localhost:3003/health

# Check processing status
curl http://localhost:8002/files/status/{file_id}
```

### Logs
```bash
# View service logs
docker-compose logs -f enhanced-ingestion
docker-compose logs -f data-curation
docker-compose logs -f preprocessing-worker
```

### Database Queries
```sql
-- Check file processing status
SELECT id, original_filename, status, created_at 
FROM raw_files 
ORDER BY created_at DESC LIMIT 10;

-- Check processed content
SELECT file_id, LENGTH(unified_content), status 
FROM processed_content 
WHERE status = 'completed';

-- Check curation datasets
SELECT id, dataset_name, curation_status, created_at 
FROM curated_datasets 
ORDER BY created_at DESC;
```

## 🛡️ Security & Production

### Security Checklist
- [ ] Secure service account key storage
- [ ] Environment variable encryption
- [ ] API rate limiting
- [ ] Input validation and sanitization
- [ ] CORS configuration
- [ ] Database connection security

### Production Deployment
```bash
# Production docker-compose
docker-compose -f docker-compose.enhanced.yml -f docker-compose.prod.yml up -d

# With SSL and reverse proxy
# Configure nginx/traefik for HTTPS
# Set production environment variables
# Enable monitoring and alerts
```

## 📈 Performance Optimization

### Database Indexing
```sql
CREATE INDEX idx_raw_files_status ON raw_files(status);
CREATE INDEX idx_processed_content_file_id ON processed_content(file_id);
CREATE INDEX idx_curated_datasets_status ON curated_datasets(curation_status);
```

### Caching Strategy
- Redis for frequent API responses
- GCS for processed file caching
- Database query result caching

### Scaling Considerations
- Horizontal scaling of workers
- Load balancing for API services
- Database read replicas
- CDN for static assets

## 🚨 Troubleshooting

### Common Issues

1. **OCR not working**
   - Check Tesseract installation
   - Verify Google Cloud Vision API credentials
   - Check image file format support

2. **Video transcription fails**
   - Verify ffmpeg installation
   - Check audio extraction
   - Confirm Google Cloud Speech API setup

3. **Database connection errors**
   - Verify DATABASE_URL
   - Check PostgreSQL service status
   - Confirm database exists and user has permissions

4. **Pub/Sub message processing**
   - Check subscription configuration
   - Verify worker service is running
   - Monitor message acknowledgment

### Performance Issues

1. **Slow file processing**
   - Increase worker instances
   - Optimize processing pipeline
   - Use faster storage

2. **Memory usage**
   - Implement streaming for large files
   - Add garbage collection
   - Monitor container resources

3. **Database performance**
   - Add appropriate indexes
   - Optimize queries
   - Consider connection pooling

This enhanced system provides a robust foundation for multi-modal startup analysis with comprehensive data processing, user curation capabilities, and production-ready architecture.