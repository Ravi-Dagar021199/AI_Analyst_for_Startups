"""
Google Cloud Pub/Sub client for event-driven processing
"""
import os
import json
from typing import Dict, Any
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import PushConfig
from concurrent.futures import TimeoutError

class PubSubManager:
    """Google Cloud Pub/Sub manager for event messaging"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ai-startup-analyst-ba7f9')
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        # Topic and subscription names
        self.topics = {
            'file_uploaded': f'projects/{self.project_id}/topics/file-uploaded',
            'processing_ready': f'projects/{self.project_id}/topics/processing-ready',
            'curation_ready': f'projects/{self.project_id}/topics/curation-ready',
            'analysis_ready': f'projects/{self.project_id}/topics/analysis-ready'
        }
        
        # Initialize topics and subscriptions
        self._ensure_topics_exist()
    
    def _ensure_topics_exist(self):
        """Create topics if they don't exist"""
        try:
            for topic_name, topic_path in self.topics.items():
                try:
                    self.publisher.create_topic(request={"name": topic_path})
                    print(f"✅ Created topic: {topic_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"ℹ️  Topic already exists: {topic_name}")
                    else:
                        print(f"❌ Error creating topic {topic_name}: {e}")
        except Exception as e:
            print(f"❌ Error initializing topics: {e}")
    
    async def publish_processing_task(self, message_data: Dict[str, Any]):
        """
        Publish file processing task to Pub/Sub
        """
        try:
            message_json = json.dumps(message_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topics['processing_ready'],
                message_json,
                file_id=message_data.get('file_id', ''),
                message_type='file_processing'
            )
            
            # Get the result (message ID)
            message_id = future.result()
            print(f"✅ Published processing task: {message_id}")
            
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to publish processing task: {e}")
            raise
    
    async def publish_curation_ready_event(self, message_data: Dict[str, Any]):
        """
        Publish curation ready event
        """
        try:
            message_json = json.dumps(message_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topics['curation_ready'],
                message_json,
                file_id=message_data.get('file_id', ''),
                message_type='curation_ready'
            )
            
            message_id = future.result()
            print(f"✅ Published curation ready event: {message_id}")
            
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to publish curation ready event: {e}")
            raise
    
    async def publish_analysis_ready_event(self, message_data: Dict[str, Any]):
        """
        Publish analysis ready event
        """
        try:
            message_json = json.dumps(message_data).encode('utf-8')
            
            future = self.publisher.publish(
                self.topics['analysis_ready'],
                message_json,
                dataset_id=message_data.get('dataset_id', ''),
                message_type='analysis_ready'
            )
            
            message_id = future.result()
            print(f"✅ Published analysis ready event: {message_id}")
            
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to publish analysis ready event: {e}")
            raise
    
    def create_subscription(self, topic_name: str, subscription_name: str, push_endpoint: str = None):
        """
        Create a subscription for a topic
        """
        try:
            topic_path = self.topics.get(topic_name)
            if not topic_path:
                raise ValueError(f"Unknown topic: {topic_name}")
            
            subscription_path = self.subscriber.subscription_path(
                self.project_id, subscription_name
            )
            
            # Configure push or pull
            push_config = None
            if push_endpoint:
                push_config = PushConfig(push_endpoint=push_endpoint)
            
            subscription = self.subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                    "push_config": push_config or PushConfig(),
                }
            )
            
            print(f"✅ Created subscription: {subscription_name}")
            return subscription
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Subscription already exists: {subscription_name}")
                return self.subscriber.subscription_path(self.project_id, subscription_name)
            else:
                print(f"❌ Error creating subscription {subscription_name}: {e}")
                raise
    
    def listen_for_messages(self, subscription_name: str, callback_function, timeout: float = None):
        """
        Listen for messages on a subscription
        """
        try:
            subscription_path = self.subscriber.subscription_path(
                self.project_id, subscription_name
            )
            
            # Configure flow control
            flow_control = pubsub_v1.types.FlowControl(max_messages=100)
            
            streaming_pull_future = self.subscriber.subscribe(
                subscription_path,
                callback=callback_function,
                flow_control=flow_control
            )
            
            print(f"🔄 Listening for messages on {subscription_name}...")
            
            if timeout:
                try:
                    streaming_pull_future.result(timeout=timeout)
                except TimeoutError:
                    streaming_pull_future.cancel()
                    print(f"⏱️  Listening timeout reached for {subscription_name}")
            else:
                # Listen indefinitely
                try:
                    streaming_pull_future.result()
                except KeyboardInterrupt:
                    streaming_pull_future.cancel()
                    print(f"🛑 Stopped listening for {subscription_name}")
            
            return streaming_pull_future
            
        except Exception as e:
            print(f"❌ Error listening for messages: {e}")
            raise