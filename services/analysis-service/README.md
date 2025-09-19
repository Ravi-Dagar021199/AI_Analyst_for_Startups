# Analysis Service

This service is the core of the AI analysis pipeline. It listens for messages from the ingestion service, fetches the corresponding file, and uses AI to generate an investment memo.

## Environment Variables

- `FIREBASE_PROJECT_ID`: The ID of your Firebase project.
- `PUBSUB_SUBSCRIPTION_ID`: The ID of the Pub/Sub subscription to listen to.

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
