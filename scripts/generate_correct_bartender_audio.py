#!/usr/bin/env python3
"""
Generate CORRECT Bartender audio files based on exact Atlassian wiki requirements.
"""

import requests
import boto3
import time

def generate_audio_with_elevenlabs(text, filename, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Generate audio using ElevenLabs API."""
    api_key = "sk_6ebd5ddbbd2cef4b79ce5166abb8b29667d6a5d6e9e6fba7"
    
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
        
        # Save to temp file
        temp_file = f"/tmp/{filename}"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        
        return temp_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ElevenLabs API error for {filename}: {str(e)}")
        return None

def upload_to_s3(local_file, s3_key, bucket_name='innovativesol-gravywork-assets-dev'):
    """Upload audio file to S3 with proper content type."""
    s3_client = boto3.client('s3')
    
    try:
        s3_client.upload_file(
            local_file,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'audio/mpeg'}
        )
        return True
    except Exception as e:
        print(f"❌ S3 upload error for {s3_key}: {str(e)}")
        return False

def main():
    print("🍸 Correcting Bartender Assessment Audio - Exact Wiki Requirements")
    print("=" * 70)
    
    # EXACT scripts from Atlassian wiki for Bartender role
    bartender_scripts = {
        "intro": """Hello! Welcome to the GravyWork skills assessment for Bartender position. This interview is conducted in English since bartenders must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here. This assessment will take approximately 5 minutes. I'll ask you several questions about your experience and knowledge. Please speak clearly after each question, and press the pound key when you are finished with each answer. If you need to hear a question repeated, press the star key.""",
        
        "experience_1": "Tell me about where you've worked as a bartender.",
        
        "experience_2": "When did you work in that role?",
        
        "experience_3": "And what were your main responsibilities?",
        
        "knowledge_glassware": "In what glass would you typically serve a Cosmopolitan? How about an Old Fashioned?",
        
        "knowledge_margarita": "What are the basic ingredients in a Margarita?",
        
        "knowledge_old_fashioned": "What are the basics of an Old Fashioned?",
        
        "knowledge_tools": "What tools would you use to shake and strain a cocktail?",
        
        "knowledge_service": "If a guest is overly intoxicated, how do you handle it?",
        
        "goodbye": "Thank you for completing the GravyWork Bartender skills assessment. Your responses have been recorded and will be reviewed by our team. We will contact you soon with next steps. Have a great day!"
    }
    
    print(f"📊 Generating {len(bartender_scripts)} corrected bartender audio files...")
    
    generated_count = 0
    uploaded_count = 0
    
    for question_key, script_text in bartender_scripts.items():
        filename = f"{question_key}.mp3"
        print(f"\n🎤 Generating: {filename}")
        print(f"📝 Script: {script_text[:100]}...")
        
        # Generate audio
        temp_file = generate_audio_with_elevenlabs(script_text, filename)
        if temp_file:
            generated_count += 1
            print(f"    ✅ Generated: {filename}")
            
            # Upload to S3 (replace existing)
            s3_key = f"audio/bartender/{filename}"
            if upload_to_s3(temp_file, s3_key):
                uploaded_count += 1
                print(f"    📁 Uploaded: s3://innovativesol-gravywork-assets-dev/{s3_key}")
                
                # Clean up temp file
                import os
                os.remove(temp_file)
            else:
                print(f"    ❌ Upload failed: {s3_key}")
            
            # Rate limiting - ElevenLabs free tier
            time.sleep(1)
        else:
            print(f"    ❌ Generation failed: {filename}")
    
    print(f"\n🎉 Complete! Generated {generated_count}/{len(bartender_scripts)} files, uploaded {uploaded_count}")
    print("🍸 Bartender assessment now matches exact Atlassian wiki requirements!")
    
    print("\n📋 Corrected Bartender Question Sequence:")
    for i, (key, script) in enumerate(bartender_scripts.items(), 1):
        print(f"{i:2d}. {key}: {script[:60]}...")

if __name__ == "__main__":
    main()
