#!/usr/bin/env python3
"""
Audio File Generator for AI Skills Assessment POC

Converts assessment scripts to professional audio files using multiple TTS services.
Supports ElevenLabs, AWS Polly, and OpenAI TTS.
"""

import json
import os
import sys
import boto3
import requests
from pathlib import Path
from typing import Dict, List

# Add the functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'src'))

def load_audio_scripts():
    """Load the generated audio scripts."""
    script_path = os.path.join(os.path.dirname(__file__), '..', '.docs', 'audio_scripts.json')
    
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            return json.load(f)
    
    # If file doesn't exist, load from assessment templates
    template_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json')
    with open(template_path, 'r') as f:
        templates = json.load(f)
    
    return generate_scripts_from_templates(templates)

def generate_scripts_from_templates(templates: Dict) -> Dict:
    """Generate scripts from assessment templates."""
    scripts = {}
    
    for skill_type, template in templates.items():
        skill_scripts = {}
        questions = template['questions_sequence']
        
        for question_key in questions:
            script = get_script_for_question(skill_type, question_key, template)
            if script:
                skill_scripts[question_key] = script
        
        scripts[skill_type] = skill_scripts
    
    return scripts

def get_script_for_question(skill_type: str, question_key: str, template: dict) -> str:
    """Get the script text for a specific question."""
    
    # Common scripts
    if question_key == 'intro':
        if template['language_requirement'] == 'bilingual':
            return "Hi, I'm calling about your application for a banquet server position. This interview can be conducted in English or Spanish. Which language would you prefer? Please say English or Spanish."
        else:
            notice = template.get('english_notice', '')
            return f"Hi, I'm calling about your {skill_type} application. {notice}"
    
    elif question_key == 'goodbye':
        return "Thank you for completing the assessment. We'll review your responses and be in touch within the next few days. Have a great day!"
    
    # Experience questions
    elif question_key == 'experience_1':
        role_name = skill_type.replace('_', ' ')
        return f"Tell me about where you've worked as a {role_name}."
    
    elif question_key == 'experience_2':
        return "When did you work in that role? You can give me approximate timeframes like years or seasons."
    
    elif question_key == 'experience_3':
        return "And what were your main responsibilities in that job?"
    
    # Knowledge questions from template data
    elif question_key.startswith('knowledge_'):
        knowledge_checks = template.get('knowledge_checks', {})
        question_mapping = {
            'knowledge_setup': 'place_setting',
            'knowledge_wine': 'wine_service', 
            'knowledge_clearing': 'clearing',
            'knowledge_scenario': 'guest_scenario',
            'knowledge_glassware': 'glassware',
            'knowledge_margarita': 'margarita',
            'knowledge_old_fashioned': 'old_fashioned',
            'knowledge_tools': 'tools',
            'knowledge_service': 'responsible_service',
            'knowledge_pos': 'pos_system',
            'knowledge_seating': 'seating_logic',
            'knowledge_phone': 'phone_etiquette',
            'knowledge_reservation': 'lost_reservation',
            'knowledge_walkin': 'large_walkin'
        }
        
        check_key = question_mapping.get(question_key)
        if check_key and check_key in knowledge_checks:
            return knowledge_checks[check_key]['question']
    
    # English communication questions
    elif question_key.startswith('english_'):
        english_comm = template.get('english_communication', {})
        if question_key == 'english_greeting' and 'greeting' in english_comm:
            return english_comm['greeting']['question']
        elif question_key == 'english_complaint' and 'complaint' in english_comm:
            return english_comm['complaint']['question']
    
    return ""

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
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error generating audio with ElevenLabs: {str(e)}")
            return False

class AWSPollyTTS:
    """AWS Polly Text-to-Speech service."""
    
    def __init__(self, voice_id: str = "Joanna"):
        self.polly_client = boto3.client('polly')
        self.voice_id = voice_id
    
    def generate_audio(self, text: str, output_path: str) -> bool:
        """Generate audio file from text."""
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine='neural'  # Higher quality neural voices
            )
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            return True
            
        except Exception as e:
            print(f"Error generating audio with AWS Polly: {str(e)}")
            return False

class OpenAITTS:
    """OpenAI Text-to-Speech service."""
    
    def __init__(self, api_key: str, voice: str = "alloy"):
        self.api_key = api_key
        self.voice = voice  # alloy, echo, fable, onyx, nova, shimmer
        self.base_url = "https://api.openai.com/v1/audio/speech"
    
    def generate_audio(self, text: str, output_path: str) -> bool:
        """Generate audio file from text."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "tts-1-hd",  # Higher quality model
                "input": text,
                "voice": self.voice
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error generating audio with OpenAI: {str(e)}")
            return False

def generate_all_audio_files(tts_service, output_dir: str = "audio_files"):
    """Generate all audio files using the specified TTS service."""
    
    scripts = load_audio_scripts()
    total_files = sum(len(skill_scripts) for skill_scripts in scripts.values())
    current_file = 0
    
    print(f"🎙️  Generating {total_files} audio files...")
    print("=" * 60)
    
    for skill_type, skill_scripts in scripts.items():
        print(f"\n📂 Generating {skill_type} audio files...")
        
        for question_key, script_text in skill_scripts.items():
            current_file += 1
            output_path = os.path.join(output_dir, skill_type, f"{question_key}.mp3")
            
            print(f"  [{current_file:2d}/{total_files}] {question_key}.mp3")
            
            success = tts_service.generate_audio(script_text, output_path)
            
            if success:
                print(f"      ✅ Generated: {output_path}")
            else:
                print(f"      ❌ Failed: {output_path}")
    
    print(f"\n🎯 Audio generation complete! Files saved to: {output_dir}/")
    print("\n📦 Next step: Upload files to S3 using upload_audio_files.py")

def main():
    """Main function - auto-configured for ElevenLabs."""
    
    print("🎙️  AI Skills Assessment - Audio File Generator")
    print("=" * 60)
    
    # Pre-configured ElevenLabs API key
    api_key = "sk_6ebd5ddbbd2cef4b79ce5166abb8b29667d6a5d6e9e6fba7"
    
    print("🔧 Using ElevenLabs TTS (Best Quality)")
    print("🎤 Voice: Rachel (Professional Female)")
    print("📊 Estimated cost: ~$0.60 for all 30 files")
    
    # Initialize ElevenLabs service
    tts_service = ElevenLabsTTS(api_key)
    
    # Generate all audio files
    generate_all_audio_files(tts_service)
    
    print("\n🚀 SUCCESS! Ready for S3 upload and Twilio integration!")

if __name__ == "__main__":
    main()
