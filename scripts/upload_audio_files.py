#!/usr/bin/env python3
"""
S3 Audio Upload Script for AI Skills Assessment POC

Uploads generated audio files to the deployed S3 bucket with proper structure.
"""

import boto3
import os
from pathlib import Path

def upload_audio_files(bucket_name: str = "innovativesol-gravywork-assets-dev", local_dir: str = "audio_files"):
    """Upload audio files to S3 with proper structure."""
    
    s3_client = boto3.client('s3')
    
    if not os.path.exists(local_dir):
        print(f"❌ Audio directory not found: {local_dir}")
        print("Run generate_audio_files.py first to create audio files")
        return
    
    total_uploaded = 0
    
    print(f"📦 Uploading audio files to S3...")
    print(f"Bucket: {bucket_name}")
    print(f"Source: {local_dir}/")
    print("=" * 60)
    
    for skill_dir in Path(local_dir).iterdir():
        if skill_dir.is_dir():
            skill_name = skill_dir.name
            print(f"\n📂 Uploading {skill_name} files...")
            
            for audio_file in skill_dir.glob('*.mp3'):
                s3_key = f"audio/{skill_name}/{audio_file.name}"
                
                try:
                    s3_client.upload_file(str(audio_file), bucket_name, s3_key)
                    print(f"  ✅ {s3_key}")
                    total_uploaded += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed to upload {s3_key}: {str(e)}")
    
    print(f"\n🎯 Upload complete! {total_uploaded} files uploaded to S3")
    print(f"\n📍 Files available at:")
    print(f"   https://{bucket_name}.s3.amazonaws.com/audio/")
    
    # List the S3 structure
    print(f"\n📋 S3 Structure:")
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix="audio/"):
            for obj in page.get('Contents', []):
                print(f"   s3://{bucket_name}/{obj['Key']}")
    except Exception as e:
        print(f"   Error listing S3 contents: {str(e)}")

if __name__ == "__main__":
    upload_audio_files()
