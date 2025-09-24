#!/usr/bin/env python3
"""
Generate "Press Pound Key" instruction using ElevenLabs Rachel voice
for consistent voice experience throughout the assessment.
"""

import requests
import boto3
import os

def generate_pound_key_audio():
    """Generate the pound key instruction using ElevenLabs."""
    
    # ElevenLabs configuration
    api_key = "sk_6ebd5ddbbd2cef4b79ce5166abb8b29667d6a5d6e9e6fba7"  # User's key
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
    
    # Text for the instruction
    text = "When you are finished speaking, press the pound key on your phone."
    
    print(f"🎤 Generating pound key instruction with ElevenLabs Rachel voice...")
    
    # ElevenLabs API call
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Save locally first
        local_file = "/tmp/pound_key_instruction.mp3"
        with open(local_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Generated audio file: {local_file}")
        
        # Upload to S3
        s3_client = boto3.client('s3')
        bucket_name = 'innovativesol-gravywork-assets-dev'
        
        # Upload to each skill type directory
        skill_types = ['bartender', 'banquet_server', 'host']
        
        for skill_type in skill_types:
            s3_key = f"audio/{skill_type}/pound_key_instruction.mp3"
            
            s3_client.upload_file(
                local_file,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'audio/mpeg'
                }
            )
            
            print(f"📁 Uploaded: s3://{bucket_name}/{s3_key}")
        
        # Also upload to general audio directory
        general_key = "audio/pound_key_instruction.mp3"
        s3_client.upload_file(
            local_file,
            bucket_name,
            general_key,
            ExtraArgs={
                'ContentType': 'audio/mpeg'
            }
        )
        
        print(f"📁 Uploaded: s3://{bucket_name}/{general_key}")
        print("🎯 Pound key instruction is now available with Rachel voice!")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ElevenLabs API error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎤 ElevenLabs Pound Key Instruction Generator")
    print("=" * 50)
    
    if generate_pound_key_audio():
        print("\n🚀 Success! The pound key instruction now uses Rachel voice.")
        print("This will provide a consistent voice experience throughout the assessment.")
    else:
        print("\n❌ Failed to generate pound key instruction")
