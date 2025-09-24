#!/usr/bin/env python3
"""
Test Single Audio File Generation with ElevenLabs
"""

import json
import os
import sys
import requests
from pathlib import Path

class ElevenLabsTTS:
    """ElevenLabs Text-to-Speech service."""
    
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id  # Rachel (professional female voice)
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def generate_audio(self, text: str, output_path: str) -> bool:
        """Generate audio file from text."""
        try:
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "use_speaker_boost": True
                }
            }
            
            print(f"🎙️  Generating audio...")
            print(f"Text: {text[:50]}...")
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Audio generated: {output_path}")
                print(f"📊 File size: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ ElevenLabs API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating audio: {str(e)}")
            return False

def test_elevenlabs_generation(api_key: str):
    """Test ElevenLabs with a single sample script."""
    
    print("🧪 Testing ElevenLabs TTS with Sample Script")
    print("=" * 50)
    
    # Sample text from bartender intro
    test_text = "Hi, I'm calling about your bartender application. This interview is conducted in English since bartenders must be able to interact with guests in English. If you are not comfortable continuing in English, you may end the interview here."
    
    # Initialize TTS service
    tts_service = ElevenLabsTTS(api_key)
    
    # Generate test audio file
    output_path = "test_audio/bartender/intro.mp3"
    success = tts_service.generate_audio(test_text, output_path)
    
    if success:
        print("\n🎯 SUCCESS! ElevenLabs is working correctly.")
        print(f"📁 Test file created: {output_path}")
        print("\n📊 Character Usage:")
        print(f"   Text length: {len(test_text)} characters")
        print(f"   Estimated cost: ~$0.{len(test_text)//100:02d} (very small)")
        
        # Test file exists and has content
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   Audio file size: {file_size:,} bytes")
            
            if file_size > 1000:  # Should be at least 1KB for audio
                return True
        
    print("\n❌ Test failed. Please check your API key and try again.")
    return False

if __name__ == "__main__":
    api_key = "sk_6ebd5ddbbd2cef4b79ce5166abb8b29667d6a5d6e9e6fba7"
    test_elevenlabs_generation(api_key)
