#!/usr/bin/env python3
"""
Upload web files to S3 bucket.
This script uploads the updated web files including the new analysis.js that uses the global index.
"""

import boto3
import os
from pathlib import Path

def upload_web_files():
    """Upload all web files to S3."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    web_dir = Path('web')
    
    if not web_dir.exists():
        print(f"❌ Web directory not found: {web_dir}")
        return
    
    print(f"🚀 Uploading web files to s3://{bucket_name}/web/")
    
    # Define content types for different file extensions
    content_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml'
    }
    
    uploaded_count = 0
    
    for file_path in web_dir.rglob('*'):
        if file_path.is_file():
            # Calculate S3 key
            relative_path = file_path.relative_to(web_dir)
            s3_key = f"web/{relative_path.as_posix()}"
            
            # Determine content type
            file_extension = file_path.suffix.lower()
            content_type = content_types.get(file_extension, 'binary/octet-stream')
            
            try:
                # Upload file
                with open(file_path, 'rb') as f:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=f,
                        ContentType=content_type
                    )
                
                print(f"✅ Uploaded: {s3_key} ({content_type})")
                uploaded_count += 1
                
            except Exception as e:
                print(f"❌ Error uploading {file_path}: {str(e)}")
    
    print(f"\n🎯 Upload complete! {uploaded_count} files uploaded.")
    print(f"🔗 Analysis dashboard: https://{bucket_name}.s3.amazonaws.com/web/analysis.html")

if __name__ == "__main__":
    upload_web_files()
