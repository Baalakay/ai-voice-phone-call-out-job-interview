#!/usr/bin/env python3
"""
Test script for AI Skills Assessment POC

This script allows manual testing of the assessment components without deploying to AWS.
"""

import json
import sys
import os

# Add the functions directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'src'))

import json

# Load assessment templates
with open(os.path.join(os.path.dirname(__file__), '..', 'functions', 'src', 'data', 'assessment_templates.json'), 'r') as f:
    ASSESSMENT_TEMPLATES = json.load(f)

# Import prompts functions
from prompts.assessment_prompts import get_assessment_prompt, get_system_prompt

def test_templates():
    """Test loading assessment templates."""
    print("=== Testing Assessment Templates ===")
    
    for skill_type, template in ASSESSMENT_TEMPLATES.items():
        print(f"\nSkill Type: {template['name']}")
        print(f"Language: {template['language_requirement']}")
        print(f"Time: {template['total_time_minutes']} minutes")
        print(f"Questions: {len(template['questions_sequence'])}")
        print(f"Sequence: {' -> '.join(template['questions_sequence'])}")

def test_prompts():
    """Test Bedrock assessment prompts."""
    print("\n=== Testing Bedrock Prompts ===")
    
    # Sample transcript
    sample_transcript = """
Experience 1: I worked at The Ritz-Carlton downtown for about 2 years.
Experience 2: That was from 2019 to 2021.
Experience 3: I was responsible for greeting guests, seating them at appropriate tables, managing reservations using OpenTable, and handling phone calls for reservations.
Knowledge Pos: Yes, I've used OpenTable and Resy. I create reservations, check guest notes, and manage the waitlist.
Knowledge Seating: I balance server sections and try to spread tables based on how busy each server is.
Knowledge Phone: I collect their name, party size, date and time they want, and their phone number.
"""
    
    # Test host assessment prompt
    prompt = get_assessment_prompt('host', sample_transcript)
    system_prompt = get_system_prompt()
    
    print("System Prompt Preview:")
    print(system_prompt[:200] + "...")
    
    print("\nAssessment Prompt Preview:")
    print(prompt[:500] + "...")

def test_assessment_data():
    """Test assessment data structures."""
    print("\n=== Testing Assessment Data ===")
    
    bartender_template = ASSESSMENT_TEMPLATES['bartender']
    
    # Test experience criteria
    print("Bartender Experience Criteria:")
    print(f"Minimum duties: {bartender_template['experience_criteria']['minimum_duties']}")
    print(f"Total duties available: {len(bartender_template['experience_criteria']['core_duties'])}")
    
    # Test knowledge checks
    print(f"\nKnowledge checks: {len(bartender_template['knowledge_checks'])}")
    for check_name, check_data in bartender_template['knowledge_checks'].items():
        print(f"  - {check_name}: {check_data['question'][:60]}...")

def simulate_assessment_flow():
    """Simulate a complete assessment flow."""
    print("\n=== Simulating Assessment Flow ===")
    
    skill_type = "host"
    assessment_id = "host_20250108_1234"
    
    print(f"Assessment ID: {assessment_id}")
    print(f"Skill Type: {skill_type}")
    
    template = ASSESSMENT_TEMPLATES[skill_type]
    print(f"Using template: {template['name']}")
    
    # Simulate question sequence
    questions = template['questions_sequence']
    print(f"\nQuestion Sequence ({len(questions)} questions):")
    
    for i, question_key in enumerate(questions):
        audio_url = f"https://bucket.s3.amazonaws.com/audio/{skill_type}/{question_key}.mp3"
        next_url = f"https://api.execute-api.us-east-1.amazonaws.com/question/{i+1}?assessment_id={assessment_id}&skill_type={skill_type}"
        
        print(f"  {i}: {question_key}")
        print(f"      Audio: {audio_url}")
        if i < len(questions) - 1:
            print(f"      Next: {next_url}")
        print()

def create_sample_assessment_result():
    """Create a sample assessment result JSON."""
    print("\n=== Sample Assessment Result ===")
    
    sample_result = {
        'assessment_id': 'bartender_20250108_1234',
        'skill_type': 'bartender',
        'template_used': 'Bartender',
        'transcript': 'Sample responses from the candidate...',
        'individual_responses': {
            'experience_1': 'I worked at Murphy\'s Pub downtown',
            'knowledge_glassware': 'Cosmopolitan goes in a martini glass, Old Fashioned in a rocks glass'
        },
        'analysis': 'APPROVED - Strong bartending experience with good technical knowledge...',
        'status': 'completed',
        'timestamp': '2025-01-08T12:30:00Z'
    }
    
    print(json.dumps(sample_result, indent=2))

if __name__ == "__main__":
    print("🎯 AI Skills Assessment POC - Test Suite")
    print("=" * 50)
    
    try:
        test_templates()
        test_prompts()
        test_assessment_data()
        simulate_assessment_flow()
        create_sample_assessment_result()
        
        print("\n✅ All tests completed successfully!")
        print("\n🚀 Ready for deployment and real testing!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
