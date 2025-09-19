import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import storage, pubsub_v1
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize clients
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

# Get config from environment
bucket_name = os.getenv("GCS_BUCKET_NAME")
project_id = os.getenv("FIREBASE_PROJECT_ID") # Assuming same project
topic_id = os.getenv("PUBSUB_TOPIC_ID")

bucket = storage_client.bucket(bucket_name)
topic_path = publisher.topic_path(project_id, topic_id)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    try:
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file, content_type=file.content_type)

        # Prepare message for Pub/Sub
        message_data = {
            "bucket": bucket_name,
            "name": file.filename
        }
        message_bytes = json.dumps(message_data).encode('utf-8')

        # Publish message
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result() # Wait for publish to complete

        return {"message": f"File {file.filename} uploaded and message published."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Ingestion Service is running"}
