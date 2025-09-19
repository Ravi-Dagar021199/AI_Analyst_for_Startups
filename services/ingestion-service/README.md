# Ingestion Service

This service is responsible for ingesting user-uploaded files, saving them to Google Cloud Storage, and triggering the analysis pipeline.

## Environment Variables

- `GCS_BUCKET_NAME`: The name of your Google Cloud Storage bucket.
- `PUBSUB_TOPIC_ID`: The ID of the Pub/Sub topic to publish to.

## Endpoints

- `POST /upload`: Uploads a file.

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
