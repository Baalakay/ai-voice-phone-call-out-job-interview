#!/usr/bin/env python3
"""
Audio Script Generator for AI Skills Assessment POC

Generates the exact scripts that need to be recorded for each role assessment.
Based on real GravyWork assessment templates from Atlassian wiki.
"""

import json
import os
import sys

# Add the functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'src'))

def load_assessment_templates():
    """Load assessment templates from JSON file."""
    template_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json')
    with open(template_path, 'r') as f:
        return json.load(f)

def create_audio_scripts():
    """Create audio scripts for all roles."""
    templates = load_assessment_templates()
    
    scripts = {}
    
    for skill_type, template in templates.items():
        skill_scripts = {}
        
        print(f"\n{'='*60}")
        print(f"AUDIO SCRIPTS FOR: {template['name'].upper()}")
        print(f"{'='*60}")
        
        # Create scripts based on question sequence
        questions = template['questions_sequence']
        
        for question_key in questions:
            script = get_script_for_question(skill_type, question_key, template)
            if script:
                skill_scripts[question_key] = script
                print(f"\n[{question_key}.mp3]")
                print(f'"{script}"')
        
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
    
    # Experience questions (common pattern)
    elif question_key == 'experience_1':
        role_name = skill_type.replace('_', ' ')
        return f"Tell me about where you've worked as a {role_name}."
    
    elif question_key == 'experience_2':
        return "When did you work in that role? You can give me approximate timeframes like years or seasons."
    
    elif question_key == 'experience_3':
        return "And what were your main responsibilities in that job?"
    
    # Knowledge questions by skill type
    elif question_key.startswith('knowledge_'):
        return get_knowledge_question_script(skill_type, question_key, template)
    
    # English communication questions
    elif question_key.startswith('english_'):
        return get_english_question_script(skill_type, question_key, template)
    
    return ""

def get_knowledge_question_script(skill_type: str, question_key: str, template: dict) -> str:
    """Get knowledge question scripts from template data."""
    
    knowledge_checks = template.get('knowledge_checks', {})
    
    # Map question keys to knowledge check keys
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
    
    return ""

def get_english_question_script(skill_type: str, question_key: str, template: dict) -> str:
    """Get English communication question scripts."""
    
    english_comm = template.get('english_communication', {})
    
    if question_key == 'english_greeting' and 'greeting' in english_comm:
        return english_comm['greeting']['question']
    elif question_key == 'english_complaint' and 'complaint' in english_comm:
        return english_comm['complaint']['question']
    
    return ""

def create_audio_production_guide():
    """Create a guide for audio production."""
    
    print(f"\n{'='*60}")
    print("AUDIO PRODUCTION GUIDE")
    print(f"{'='*60}")
    
    guide = """
VOICE CHARACTERISTICS:
- Professional, friendly, and warm tone
- Clear articulation and moderate pace
- Neutral American accent preferred
- Consistent volume and tone throughout

RECORDING SPECIFICATIONS:
- Format: MP3, 44.1kHz, 128kbps or higher
- No background noise or echo
- Consistent audio levels across all files
- 0.5 second silence at start and end of each file

FILE NAMING CONVENTION:
- Format: {skill_type}/{question_key}.mp3
- Examples: bartender/intro.mp3, host/knowledge_pos.mp3

DELIVERY NOTES:
- Pause slightly after questions to give candidates time to process
- Speak as if talking to a real person, not reading a script
- Maintain professional but approachable tone throughout
- For bilingual intro (banquet server), clearly enunciate language options

S3 UPLOAD STRUCTURE:
s3://your-bucket/audio/
├── banquet_server/
├── bartender/
└── host/

TOTAL FILES NEEDED: ~30 audio files across 3 roles
"""
    
    print(guide)

def save_scripts_to_file(scripts: dict):
    """Save all scripts to a file for reference."""
    
    output_file = os.path.join(os.path.dirname(__file__), '..', '.docs', 'audio_scripts.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(scripts, f, indent=2)
    
    print(f"\n✅ Scripts saved to: {output_file}")

if __name__ == "__main__":
    print("🎙️  AI Skills Assessment POC - Audio Script Generator")
    print("Based on real GravyWork assessment templates")
    
    try:
        scripts = create_audio_scripts()
        create_audio_production_guide()
        save_scripts_to_file(scripts)
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review the scripts above")
        print("2. Record audio files using professional voice talent") 
        print("3. Upload files to S3 using the specified structure")
        print("4. Test assessment flow with real audio")
        
    except Exception as e:
        print(f"\n❌ Script generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
