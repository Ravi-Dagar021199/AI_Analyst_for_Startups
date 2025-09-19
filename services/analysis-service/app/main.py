import os
import json
from concurrent.futures import TimeoutError
from fastapi import FastAPI
from google.cloud import pubsub_v1, vision, firestore
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize clients
project_id = os.getenv("FIREBASE_PROJECT_ID")
vertexai.init(project=project_id, location="us-central1")

subscriber = pubsub_v1.SubscriberClient()
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client(project=project_id)
model = GenerativeModel("gemini-1.5-flash-001")

# Get config from environment
subscription_id = os.getenv("PUBSUB_SUBSCRIPTION_ID")
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def generate_memo(text: str) -> str:
    prompt = f"""Act as a senior investment analyst. Based on the following text extracted from a startup's pitch deck, generate a concise investment memo. Structure the memo with these four sections:

1.  **Founder Profile:** Assess the founder's experience and founder-market fit.
2.  **Market Opportunity:** Evaluate the problem, market size, and competitive landscape.
3.  **Unique Differentiator:** Identify what makes the solution unique and defensible (e.g., business model, IP).
4.  **Business Metrics:** Analyze key performance indicators (KPIs) like revenue, traction, and costs. If specific metrics are missing, note that.

Extracted Text:
---
{text}
---
"""
    response = model.generate_content(prompt)
    return response.text

def callback(message):
    print(f"Received message: {message.data}")
    try:
        data = json.loads(message.data)
        bucket_name = data['bucket']
        file_name = data['name']
        
        gcs_uri = f"gs://{bucket_name}/{file_name}"
        print(f"Analyzing file: {gcs_uri}")

        # 1. Extract text with Vision API
        image = vision.Image()
        image.source.image_uri = gcs_uri
        response = vision_client.document_text_detection(image=image)
        extracted_text = response.full_text_annotation.text if response.full_text_annotation else ""

        if not extracted_text:
            print("No text found in document.")
            message.ack()
            return

        # 2. Generate memo with Gemini API
        print("Generating investment memo...")
        memo = generate_memo(extracted_text)
        print("Generated Memo:")
        print(memo)

        # 3. Store result in Firestore
        doc_ref = db.collection('analysis_results').document(file_name)
        doc_ref.set({
            'file_name': file_name,
            'extracted_text': extracted_text,
            'investment_memo': memo,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        print(f"Result saved to Firestore collection 'analysis_results' with document ID: {file_name}")

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
    streaming_pull_future.result()
