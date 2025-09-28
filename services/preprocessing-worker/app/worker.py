"""
Preprocessing Worker - Pub/Sub message listener for file processing events
"""
import os
import json
import time
from datetime import datetime
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

class PreprocessingWorker:
    """Worker that listens for file processing events and triggers processing"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ai-startup-analyst-ba7f9')
        self.subscription_name = os.getenv('PUBSUB_SUBSCRIPTION_NAME', 'file-processing-sub')
        
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            self.project_id, self.subscription_name
        )
        
        # Initialize database connection
        from enhanced_ingestion_service.app.database import SessionLocal
        self.SessionLocal = SessionLocal
        
        print(f"🔄 Preprocessing Worker initialized")
        print(f"   Project: {self.project_id}")
        print(f"   Subscription: {self.subscription_name}")
    
    def process_message(self, message):
        """Process individual Pub/Sub message"""
        try:
            print(f"📨 Received message: {message.message_id}")
            
            # Parse message data
            message_data = json.loads(message.data.decode('utf-8'))
            message_type = message.attributes.get('message_type', 'unknown')
            
            print(f"   Type: {message_type}")
            print(f"   Data: {message_data}")
            
            if message_type == 'file_processing':
                self.handle_file_processing(message_data)
            elif message_type == 'curation_ready':
                self.handle_curation_ready(message_data)
            elif message_type == 'analysis_ready':
                self.handle_analysis_ready(message_data)
            else:
                print(f"⚠️  Unknown message type: {message_type}")
            
            # Acknowledge the message
            message.ack()
            print(f"✅ Message {message.message_id} processed successfully")
            
        except Exception as e:
            print(f"❌ Error processing message {message.message_id}: {e}")
            # Don't acknowledge - message will be retried
            message.nack()
    
    def handle_file_processing(self, data):
        """Handle file processing completion"""
        try:
            file_id = data.get('file_id')
            print(f"🔄 Processing file completion event for {file_id}")
            
            # Update database status
            db = self.SessionLocal()
            try:
                from enhanced_ingestion_service.app.database import RawFileRecord
                file_record = db.query(RawFileRecord).filter(RawFileRecord.id == file_id).first()
                
                if file_record:
                    file_record.status = 'processing'
                    file_record.processing_started_at = datetime.utcnow()
                    db.commit()
                    print(f"✅ Updated file {file_id} status to processing")
                else:
                    print(f"⚠️  File {file_id} not found in database")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error handling file processing: {e}")
    
    def handle_curation_ready(self, data):
        """Handle curation ready event"""
        try:
            file_id = data.get('file_id')
            print(f"📋 File {file_id} is ready for curation")
            
            # Update database and send notifications
            db = self.SessionLocal()
            try:
                from enhanced_ingestion_service.app.database import RawFileRecord
                file_record = db.query(RawFileRecord).filter(RawFileRecord.id == file_id).first()
                
                if file_record:
                    file_record.status = 'completed'
                    file_record.processing_completed_at = datetime.utcnow()
                    db.commit()
                    print(f"✅ File {file_id} marked as completed and ready for curation")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error handling curation ready: {e}")
    
    def handle_analysis_ready(self, data):
        """Handle analysis ready event"""
        try:
            dataset_id = data.get('dataset_id')
            print(f"🤖 Dataset {dataset_id} is ready for AI analysis")
            
            # Trigger AI analysis job
            self.trigger_ai_analysis(dataset_id)
            
        except Exception as e:
            print(f"❌ Error handling analysis ready: {e}")
    
    def trigger_ai_analysis(self, dataset_id: str):
        """Trigger AI analysis for a ready dataset"""
        try:
            db = self.SessionLocal()
            try:
                from enhanced_ingestion_service.app.database import save_ai_analysis_job
                
                job_data = {
                    "dataset_id": dataset_id,
                    "analysis_type": "startup_evaluation",
                    "ai_model_used": "gemini-2.5-flash",
                    "status": "pending"
                }
                
                job = save_ai_analysis_job(db, job_data)
                print(f"✅ Created AI analysis job {job.id} for dataset {dataset_id}")
                
                # Here you would trigger the actual AI analysis service
                # For now, we just log the event
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error triggering AI analysis: {e}")
    
    def start_listening(self):
        """Start listening for Pub/Sub messages"""
        print(f"👂 Starting to listen for messages on {self.subscription_path}")
        
        # Configure flow control
        flow_control = pubsub_v1.types.FlowControl(max_messages=10)
        
        # Start listening
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.process_message,
            flow_control=flow_control
        )
        
        print(f"🎧 Listening for messages...")
        
        try:
            # Keep the main thread running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("🛑 Stopping worker...")
            streaming_pull_future.cancel()
            streaming_pull_future.result()  # Block until the shutdown is complete
            print("✅ Worker stopped")

def main():
    """Main worker function"""
    try:
        worker = PreprocessingWorker()
        worker.start_listening()
    except Exception as e:
        print(f"❌ Worker failed to start: {e}")
        raise

if __name__ == "__main__":
    main()