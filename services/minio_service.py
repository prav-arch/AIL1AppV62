"""
Minio Service for storage integration
This module provides functionalities to interact with Minio object storage
"""

import os
import logging
from typing import Dict, List, Optional, BinaryIO, Tuple
import urllib3
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

# Set up logger
logger = logging.getLogger(__name__)

# Disable SSL warnings since we're using http without certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MinioService:
    """Minio service for object storage operations"""
    
    def __init__(self):
        """Initialize the Minio service"""
        # Minio server connection settings
        self.endpoint_url = os.environ.get('MINIO_ENDPOINT_URL', 'http://localhost:8000')
        self.access_key = os.environ.get('MINIO_ACCESS_KEY', 'dpcoeadmin')
        self.secret_key = os.environ.get('MINIO_SECRET_KEY', 'dpcoeadmin')
        self.default_bucket = os.environ.get('MINIO_DEFAULT_BUCKET', 'l1appuploads')
        
        # Create Minio client
        self.client = self._create_client()
        
        # Ensure default bucket exists
        self.ensure_bucket_exists(self.default_bucket)
    
    def _create_client(self):
        """Create and return an S3 client configured for Minio"""
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4'),
                verify=False  # Disable SSL verification
            )
            logger.info(f"Successfully created Minio client with endpoint {self.endpoint_url}")
            return client
        except Exception as e:
            logger.error(f"Error creating Minio client: {str(e)}")
            return None
    
    def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """Ensure that the bucket exists, creating it if needed"""
        if not self.client:
            logger.error("No Minio client available")
            return False
            
        try:
            # Check if bucket exists
            self.client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' already exists")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            
            # Bucket doesn't exist, create it
            if error_code == '404' or error_code == 'NoSuchBucket':
                try:
                    logger.info(f"Creating bucket '{bucket_name}'")
                    self.client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Successfully created bucket '{bucket_name}'")
                    return True
                except Exception as create_error:
                    logger.error(f"Error creating bucket '{bucket_name}': {str(create_error)}")
                    return False
            else:
                logger.error(f"Error checking bucket '{bucket_name}': {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error with bucket '{bucket_name}': {str(e)}")
            return False
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None, 
                   bucket_name: Optional[str] = None, metadata: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Upload a file to a Minio bucket
        
        Args:
            file_path: Local path to the file to upload
            object_name: Name of the object in the bucket (defaults to file basename)
            bucket_name: Name of the bucket (defaults to default bucket)
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (success, object_url)
        """
        if not self.client:
            logger.error("No Minio client available")
            return False, ""
            
        bucket = bucket_name or self.default_bucket
        object_name = object_name or os.path.basename(file_path)
        
        # Ensure the bucket exists
        if not self.ensure_bucket_exists(bucket):
            logger.error(f"Cannot upload file - bucket '{bucket}' does not exist")
            return False, ""
        
        try:
            # Upload the file with metadata if provided
            logger.info(f"Uploading file '{file_path}' to bucket '{bucket}' as '{object_name}'")
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Upload the file
            self.client.upload_file(
                file_path, 
                bucket, 
                object_name,
                ExtraArgs=extra_args
            )
            
            # Generate the URL
            object_url = f"{self.endpoint_url}/{bucket}/{object_name}"
            logger.info(f"File uploaded successfully: {object_url}")
            return True, object_url
        except Exception as e:
            logger.error(f"Error uploading file '{file_path}' to '{bucket}/{object_name}': {str(e)}")
            return False, ""
    
    def upload_fileobj(self, file_obj: BinaryIO, object_name: str,
                      bucket_name: Optional[str] = None, metadata: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Upload a file-like object to a Minio bucket
        
        Args:
            file_obj: File-like object to upload
            object_name: Name of the object in the bucket
            bucket_name: Name of the bucket (defaults to default bucket)
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (success, object_url)
        """
        if not self.client:
            logger.error("No Minio client available")
            return False, ""
            
        bucket = bucket_name or self.default_bucket
        
        # Ensure the bucket exists
        if not self.ensure_bucket_exists(bucket):
            logger.error(f"Cannot upload file - bucket '{bucket}' does not exist")
            return False, ""
        
        try:
            # Upload the file with metadata if provided
            logger.info(f"Uploading file object to bucket '{bucket}' as '{object_name}'")
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Upload the file object
            self.client.upload_fileobj(
                file_obj, 
                bucket, 
                object_name,
                ExtraArgs=extra_args
            )
            
            # Generate the URL
            object_url = f"{self.endpoint_url}/{bucket}/{object_name}"
            logger.info(f"File uploaded successfully: {object_url}")
            return True, object_url
        except Exception as e:
            logger.error(f"Error uploading file object to '{bucket}/{object_name}': {str(e)}")
            return False, ""
    
    def get_file_url(self, object_name: str, bucket_name: Optional[str] = None) -> str:
        """Get the URL for a file in the bucket"""
        bucket = bucket_name or self.default_bucket
        return f"{self.endpoint_url}/{bucket}/{object_name}"
    
    def list_objects(self, bucket_name: Optional[str] = None, prefix: str = "") -> List[Dict]:
        """
        List objects in a bucket
        
        Args:
            bucket_name: Name of the bucket (defaults to default bucket)
            prefix: Prefix to filter objects by
            
        Returns:
            List of object information dictionaries
        """
        if not self.client:
            logger.error("No Minio client available")
            return []
            
        bucket = bucket_name or self.default_bucket
        objects = []
        
        try:
            # List objects in the bucket
            logger.info(f"Listing objects in bucket '{bucket}' with prefix '{prefix}'")
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            
            # Process the results
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': self.get_file_url(obj['Key'], bucket)
                    })
            
            logger.info(f"Found {len(objects)} objects in bucket '{bucket}'")
            return objects
        except Exception as e:
            logger.error(f"Error listing objects in bucket '{bucket}': {str(e)}")
            return []
    
    def delete_object(self, object_name: str, bucket_name: Optional[str] = None) -> bool:
        """
        Delete an object from a bucket
        
        Args:
            object_name: Name of the object to delete
            bucket_name: Name of the bucket (defaults to default bucket)
            
        Returns:
            Success status
        """
        if not self.client:
            logger.error("No Minio client available")
            return False
            
        bucket = bucket_name or self.default_bucket
        
        try:
            # Delete the object
            logger.info(f"Deleting object '{object_name}' from bucket '{bucket}'")
            self.client.delete_object(Bucket=bucket, Key=object_name)
            logger.info(f"Object '{object_name}' deleted successfully from bucket '{bucket}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting object '{object_name}' from bucket '{bucket}': {str(e)}")
            return False
    
    def get_bucket_stats(self, bucket_name: Optional[str] = None) -> Dict:
        """
        Get statistics for a bucket
        
        Args:
            bucket_name: Name of the bucket (defaults to default bucket)
            
        Returns:
            Dictionary with bucket statistics
        """
        bucket = bucket_name or self.default_bucket
        objects = self.list_objects(bucket)
        
        # Calculate statistics
        total_size = sum(obj['size'] for obj in objects)
        file_count = len(objects)
        
        # Format size for display
        size_str = self._format_size(total_size)
        
        return {
            'name': bucket,
            'size': size_str,
            'files': file_count,
            'raw_size': total_size
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to a human-readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"