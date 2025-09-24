#!/usr/bin/env python3
"""
Generate ALL 32 audio files using ElevenLabs API from the definitive template.
"""

import requests
import boto3
import json
import time
import os

def generate_audio_with_elevenlabs(text, filename, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Generate audio using ElevenLabs API."""
    api_key = "sk_a2a87a92eb8d2045c5a9381f5b38192fa56313f26f86666d"
    
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
        print(f"🎙️ Generating {filename}...")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Save to temp file
        temp_file = f"/tmp/{filename}"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Generated {filename}")
        return temp_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ElevenLabs API error for {filename}: {str(e)}")
        return None

def upload_to_s3(local_file, s3_key, bucket_name='innovativesol-gravywork-assets-dev'):
    """Upload file to S3."""
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(local_file, bucket_name, s3_key)
        print(f"📤 Uploaded {s3_key}")
        return True
        
    except Exception as e:
        print(f"❌ S3 upload error for {s3_key}: {str(e)}")
        return False

def main():
    print("🎙️ GENERATING ALL 32 AUDIO FILES FROM DEFINITIVE TEMPLATE")
    print("="*70)
    
    # Load the regenerated audio scripts
    with open('.docs/audio_scripts.json', 'r') as f:
        scripts = json.load(f)
    
    generated_count = 0
    uploaded_count = 0
    failed_files = []
    
    for role_key, role_scripts in scripts.items():
        print(f"\n📋 PROCESSING {role_key.upper().replace('_', ' ')} ({len(role_scripts)} files)")
        print("-" * 50)
        
        for question_key, script_text in role_scripts.items():
            filename = f"{question_key}.mp3"
            s3_key = f"audio/{role_key}/{filename}"
            
            # Generate audio
            temp_file = generate_audio_with_elevenlabs(script_text, filename)
            
            if temp_file:
                generated_count += 1
                
                # Upload to S3
                if upload_to_s3(temp_file, s3_key):
                    uploaded_count += 1
                    
                    # Clean up temp file
                    os.remove(temp_file)
                else:
                    failed_files.append(s3_key)
            else:
                failed_files.append(s3_key)
            
            # Small delay to avoid API rate limits
            time.sleep(1)
    
    # Summary
    print("\n" + "="*70)
    print("📊 GENERATION SUMMARY")
    print("-" * 30)
    print(f"✅ Generated: {generated_count}/32 files")
    print(f"📤 Uploaded:  {uploaded_count}/32 files")
    
    if failed_files:
        print(f"❌ Failed:    {len(failed_files)} files")
        print("\nFailed files:")
        for file in failed_files:
            print(f"  • {file}")
    else:
        print("🎉 ALL FILES SUCCESSFULLY GENERATED AND UPLOADED!")
    
    print(f"\n🔗 Files uploaded to: s3://innovativesol-gravywork-assets-dev/audio/")
    print("🎯 Ready for voice assessment testing!")

if __name__ == "__main__":
    main()
