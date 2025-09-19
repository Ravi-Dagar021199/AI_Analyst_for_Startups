import os
import json
from concurrent.futures import TimeoutError
from fastapi import FastAPI
from google.cloud import pubsub_v1
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
project_id = os.getenv("FIREBASE_PROJECT_ID")
subscription_id = os.getenv("PUBSUB_SUBSCRIPTION_ID")
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print(f"Received message: {message.data}")
    try:
        data = json.loads(message.data)
        print(f"File to analyze: gs://{data['bucket']}/{data['name']}")
        # Analysis logic will go here
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

# Start the subscriber in the background
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

@app.get("/")
def read_root():
    return {"message": "Analysis Service is running and listening for messages."}

# Gracefully shutdown the subscriber on exit
@app.on_event("shutdown")
def shutdown_event():
    streaming_pull_future.cancel()
    streaming_pull_future.result() # Wait for the shutdown to complete
