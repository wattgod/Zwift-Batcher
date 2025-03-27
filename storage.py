import boto3
from botocore.exceptions import ClientError
import os
from config import Config

class Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        self.bucket = Config.AWS_BUCKET_NAME

    def upload_file(self, file_path, s3_key=None):
        """Upload a file to S3."""
        if s3_key is None:
            s3_key = os.path.basename(file_path)
        
        try:
            self.s3.upload_file(file_path, self.bucket, s3_key)
            return f"https://{self.bucket}.s3.{Config.AWS_REGION}.amazonaws.com/{s3_key}"
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None

    def download_file(self, s3_key, local_path):
        """Download a file from S3."""
        try:
            self.s3.download_file(self.bucket, s3_key, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False

    def delete_file(self, s3_key):
        """Delete a file from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False

    def get_presigned_url(self, s3_key, expiration=3600):
        """Generate a presigned URL for file download."""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None 