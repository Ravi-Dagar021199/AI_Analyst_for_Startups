"""
Google Cloud Storage client for file management
"""
import os
from typing import Optional
from google.cloud import storage
from datetime import datetime

class GCSManager:
    """Google Cloud Storage manager for file operations"""
    
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'ai-startup-analyst-uploads-ba7f9')
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_file(
        self, 
        file_content: bytes, 
        file_id: str, 
        original_filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to Google Cloud Storage
        Returns: GCS path of uploaded file
        """
        try:
            # Create blob path with timestamp and file_id
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            blob_name = f"raw-files/{timestamp}_{file_id}_{original_filename}"
            
            blob = self.bucket.blob(blob_name)
            
            # Set content type if provided
            if content_type:
                blob.content_type = content_type
            
            # Upload file content
            blob.upload_from_string(file_content)
            
            # Return the GCS path
            return f"gs://{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            raise Exception(f"GCS upload failed: {str(e)}")
    
    async def download_file(self, gcs_path: str) -> bytes:
        """
        Download file from Google Cloud Storage
        """
        try:
            # Extract blob name from GCS path
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            
            # Download file content
            return blob.download_as_bytes()
            
        except Exception as e:
            raise Exception(f"GCS download failed: {str(e)}")
    
    async def delete_file(self, gcs_path: str) -> bool:
        """
        Delete file from Google Cloud Storage
        """
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
            
        except Exception as e:
            print(f"GCS delete failed: {str(e)}")
            return False
    
    async def list_files(self, prefix: str = "raw-files/") -> list:
        """
        List files in GCS bucket with given prefix
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [f"gs://{self.bucket_name}/{blob.name}" for blob in blobs]
            
        except Exception as e:
            raise Exception(f"GCS list failed: {str(e)}")