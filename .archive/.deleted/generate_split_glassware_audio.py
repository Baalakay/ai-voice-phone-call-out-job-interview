#!/usr/bin/env python3

import requests
import boto3
import os
from datetime import datetime

# ElevenLabs configuration
ELEVENLABS_API_KEY = "sk_6ebd5ddbbd2cef4b79ce5166abb8b29667d6a5d6e9e6fba7"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

# AWS S3 configuration
S3_BUCKET = "innovativesol-gravywork-assets-dev"

def generate_audio(text, filename):
    """Generate audio using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    print(f"Generating audio for: {filename}")
    print(f"Text: {text}")
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        # Save locally first
        with open(f"{filename}.mp3", "wb") as f:
            f.write(response.content)
        print(f"✓ Generated {filename}.mp3")
        return True
    else:
        print(f"✗ Failed to generate {filename}: {response.status_code} - {response.text}")
        return False

def upload_to_s3(local_filename, s3_key):
    """Upload file to S3 with correct content type."""
    s3_client = boto3.client('s3')
    
    try:
        s3_client.upload_file(
            local_filename, 
            S3_BUCKET, 
            s3_key,
            ExtraArgs={
                'ContentType': 'audio/mpeg'
            }
        )
        print(f"✓ Uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
        return True
    except Exception as e:
        print(f"✗ S3 upload failed: {str(e)}")
        return False

def main():
    print("🍹 Generating Split Glassware Questions Audio")
    print("=" * 50)
    
    # Define the new questions
    questions = {
        "knowledge_cosmopolitan_glass": "In what glass would you typically serve a Cosmopolitan?",
        "knowledge_old_fashioned_glass": "In what glass would you typically serve an Old Fashioned?"
    }
    
    success_count = 0
    total_count = len(questions)
    
    for question_key, question_text in questions.items():
        print(f"\n📝 Processing: {question_key}")
        
        # Generate audio
        if generate_audio(question_text, question_key):
            # Upload to S3
            s3_key = f"audio/bartender/{question_key}.mp3"
            if upload_to_s3(f"{question_key}.mp3", s3_key):
                success_count += 1
                print(f"✅ Complete: {question_key}")
            else:
                print(f"❌ S3 upload failed: {question_key}")
        else:
            print(f"❌ Audio generation failed: {question_key}")
        
        # Clean up local file
        if os.path.exists(f"{question_key}.mp3"):
            os.remove(f"{question_key}.mp3")
    
    print(f"\n🎯 Results: {success_count}/{total_count} questions processed successfully")
    
    if success_count == total_count:
        print("🎉 All audio files generated and uploaded successfully!")
        print("\nNext steps:")
        print("1. Deploy the updated Lambda function")
        print("2. Test the new split questions in a call")
    else:
        print("⚠️ Some audio files failed to generate")

if __name__ == "__main__":
    main()
