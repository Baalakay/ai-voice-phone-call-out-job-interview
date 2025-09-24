#!/usr/bin/env python3
"""
Deploy GravyWork Skills Assessment Web UI to S3
Configures S3 bucket for static website hosting and uploads files.
"""

import boto3
import json
import os
from pathlib import Path

def deploy_website():
    """Deploy the web UI to S3 with static website hosting."""
    
    # Configuration
    bucket_name = 'innovativesol-gravywork-assets-dev'
    web_prefix = 'web/'
    
    print("🌐 GravyWork Web UI Deployment")
    print("=" * 50)
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # 1. Upload web files
        web_dir = Path('web')
        if not web_dir.exists():
            print("❌ Web directory not found!")
            return False
            
        files_to_upload = [
            ('index.html', 'text/html'),
            ('styles.css', 'text/css'),
            ('app.js', 'application/javascript')
        ]
        
        print("📁 Uploading web files...")
        for filename, content_type in files_to_upload:
            file_path = web_dir / filename
            if file_path.exists():
                s3_key = f"{web_prefix}{filename}"
                
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': 'max-age=3600'  # 1 hour cache
                    }
                )
                print(f"✅ Uploaded: {filename}")
            else:
                print(f"⚠️  File not found: {filename}")
        
        # 2. Configure bucket for static website hosting
        print("\n🌐 Configuring static website hosting...")
        
        website_configuration = {
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'index.html'}  # SPA fallback
        }
        
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration=website_configuration
        )
        print("✅ Static website hosting configured")
        
        # 3. Update bucket policy to allow public read access to web files
        print("🔓 Updating bucket policy for web access...")
        
        # Get current bucket policy
        try:
            current_policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
            current_policy = json.loads(current_policy_response['Policy'])
        except s3_client.exceptions.NoSuchBucketPolicy:
            current_policy = {
                "Version": "2012-10-17",
                "Statement": []
            }
        
        # Add web access statement if it doesn't exist
        web_statement = {
            "Sid": "PublicReadWebFiles",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/web/*"
        }
        
        # Check if statement already exists
        statement_exists = any(
            stmt.get('Sid') == 'PublicReadWebFiles' 
            for stmt in current_policy['Statement']
        )
        
        if not statement_exists:
            current_policy['Statement'].append(web_statement)
            
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(current_policy)
            )
            print("✅ Bucket policy updated for web access")
        else:
            print("✅ Web access policy already exists")
        
        # 4. Generate access URLs
        print("\n🚀 Deployment Complete!")
        print("=" * 50)
        
        # Static website URL
        region = 'us-east-1'
        website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com/web/"
        
        # Direct S3 URL
        direct_url = f"https://{bucket_name}.s3.amazonaws.com/web/index.html"
        
        print(f"🌐 Static Website URL: {website_url}")
        print(f"📁 Direct S3 URL: {direct_url}")
        print(f"🎯 API Endpoint: https://eih1khont2.execute-api.us-east-1.amazonaws.com")
        
        print("\n📋 Next Steps:")
        print("1. Visit the website URL to test the UI")
        print("2. Select a role and enter your phone number")
        print("3. Click 'Start Assessment Call' to test the flow")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🍽️ GravyWork Skills Assessment - Web UI Deployment")
    print("Deploying professional web interface to S3...")
    
    if deploy_website():
        print("\n🎉 Success! Your web UI is now live and ready to use!")
    else:
        print("\n💥 Deployment failed. Please check the errors above.")
