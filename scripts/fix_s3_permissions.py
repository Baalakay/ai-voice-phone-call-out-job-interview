#!/usr/bin/env python3
"""
Fix S3 Bucket Permissions for Audio Files

Makes audio files publicly readable so Twilio can access them during calls.
"""

import boto3
import json

def fix_s3_public_access():
    """Make audio files publicly readable."""
    
    bucket_name = "innovativesol-gravywork-assets-dev"
    s3_client = boto3.client('s3')
    
    print(f"🔧 Fixing S3 permissions for bucket: {bucket_name}")
    
    # Create bucket policy to allow public read access to audio files
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/audio/*"
            }
        ]
    }
    
    try:
        # Apply bucket policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print("✅ Bucket policy updated - audio files now publicly readable")
        
        # Test access to a sample file
        test_url = f"https://{bucket_name}.s3.amazonaws.com/audio/bartender/intro.mp3"
        print(f"🔗 Test URL: {test_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating bucket policy: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 S3 Audio Files Permission Fix")
    print("=" * 50)
    
    success = fix_s3_public_access()
    
    if success:
        print("\n🚀 S3 permissions fixed! Audio files are now publicly accessible.")
    else:
        print("\n⚠️  Failed to update permissions. Check AWS credentials and bucket access.")
