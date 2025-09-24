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
    # Instructions text - this will be played during recording timeout
    instructions_text = "Please answer the question and press the pound key when finished, or press star to repeat the question."
    
    # Generate the audio file
    if generate_audio(instructions_text, "instructions"):
        # Upload to S3 in the audio folder
        if upload_to_s3("instructions.mp3", "audio/instructions.mp3"):
            print("\n✓ Successfully generated and uploaded instructions audio")
            print(f"URL: https://{S3_BUCKET}.s3.us-east-1.amazonaws.com/audio/instructions.mp3")
        else:
            print("✗ Failed to upload to S3")
    else:
        print("✗ Failed to generate audio")
    
    # Clean up local file
    if os.path.exists("instructions.mp3"):
        os.remove("instructions.mp3")
        print("✓ Cleaned up local file")

if __name__ == "__main__":
    main()
