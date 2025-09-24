#!/usr/bin/env python3
"""
Test script for LLM assessment analysis functionality.
"""
import sys
import os
import json
from datetime import datetime

# Add the functions directory to Python path
functions_src_path = os.path.join(os.path.dirname(__file__), '..', 'functions', 'src')
sys.path.insert(0, functions_src_path)

# Set up environment variables for testing
os.environ.setdefault('S3_BUCKET_NAME', 'innovativesol-gravywork-assets-dev')
os.environ.setdefault('PROJECT_NAME', 'gravywork-processor')

try:
    from services.assessment_analyzer import create_assessment_analyzer
    from config.llm_config import get_llm_config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires AWS credentials and the full project environment.")
    print("Run this from within the Lambda environment or with proper AWS setup.")
    sys.exit(1)

def create_mock_assessment_data():
    """Create mock assessment data for testing."""
    return {
        'assessment_id': 'test-assessment-123',
        'skill_type': 'bartender',
        'status': 'completed',
        'started_at': '2025-01-18T10:00:00Z',
        'completed_at': '2025-01-18T10:08:00Z',
        'responses': {
            'experience_1': {
                'recording_url': 'https://api.twilio.com/test/recording1.mp3',
                'timestamp': '2025-01-18T10:01:00Z'
            },
            'experience_2': {
                'recording_url': 'https://api.twilio.com/test/recording2.mp3', 
                'timestamp': '2025-01-18T10:02:00Z'
            },
            'knowledge_cosmopolitan_glass': {
                'recording_url': 'https://api.twilio.com/test/recording3.mp3',
                'timestamp': '2025-01-18T10:05:00Z'
            },
            'knowledge_old_fashioned_glass': {
                'recording_url': 'https://api.twilio.com/test/recording4.mp3',
                'timestamp': '2025-01-18T10:06:00Z'
            }
        }
    }

def create_mock_transcripts():
    """Create mock transcripts for testing prompt generation."""
    return {
        'experience_1': "I worked as a bartender at Murphy's Pub for two years. I made cocktails, served beer and wine, cleaned glasses, and helped with inventory. I worked mostly evening shifts and handled busy weekend crowds.",
        
        'experience_2': "Before that I worked at a hotel bar for about 8 months. I learned how to make classic cocktails like martinis and manhattans. I also handled cash register and credit card payments from guests.",
        
        'experience_3': "I also have some experience helping at my friend's restaurant bar during busy events. I mostly just helped with pouring beer and wine, but I got to see how a professional kitchen works with the bar.",
        
        'knowledge_cosmopolitan_glass': "A cosmopolitan should be served in a martini glass, the wide triangular one. That's the classic way to serve it.",
        
        'knowledge_old_fashioned_glass': "An old fashioned goes in a rocks glass, you know, the short heavy glass. Sometimes called a lowball glass I think.",
        
        'knowledge_margarita': "For a margarita you muddle the lime first, then add tequila, triple sec or cointreau, and lime juice. Shake it with ice and strain into a salt-rimmed glass.",
        
        'knowledge_old_fashioned': "An old fashioned is whiskey or bourbon with sugar, bitters, and a little water or soda. You muddle it together and serve it over ice with an orange peel.",
        
        'knowledge_tools': "Essential bar tools are shaker, strainer, jigger for measuring, muddler, bar spoon, and bottle opener. You also need good knives for cutting garnishes.",
        
        'knowledge_service': "You always greet customers right away, even if you're busy with another order. Make eye contact, be friendly, and let them know you'll be with them soon if you can't serve them immediately."
    }

def test_prompt_generation():
    """Test the assessment prompt generation."""
    print("🧪 Testing Assessment Prompt Generation...")
    
    try:
        analyzer = create_assessment_analyzer()
        
        # Load assessment templates
        templates = analyzer._load_assessment_templates()
        if 'bartender' not in templates:
            print("❌ Failed to load bartender template")
            return False
        
        # Create mock transcripts
        transcripts = create_mock_transcripts()
        criteria = templates['bartender']
        
        # Generate prompt
        prompt = analyzer._build_assessment_prompt(transcripts, criteria, 'bartender')
        
        print("✅ Prompt generated successfully!")
        print(f"📊 Prompt length: {len(prompt)} characters")
        print("\n📝 Sample of generated prompt:")
        print("=" * 50)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt generation failed: {str(e)}")
        return False

def test_template_loading():
    """Test loading assessment templates."""
    print("🧪 Testing Assessment Template Loading...")
    
    try:
        analyzer = create_assessment_analyzer()
        templates = analyzer._load_assessment_templates()
        
        if not templates:
            print("❌ No templates loaded")
            return False
        
        expected_roles = ['bartender', 'banquet_server', 'host']
        for role in expected_roles:
            if role in templates:
                print(f"✅ {role.title()} template loaded")
                
                # Check template structure
                template = templates[role]
                required_keys = ['name', 'questions_sequence', 'experience_criteria', 'knowledge_checks']
                
                for key in required_keys:
                    if key in template:
                        print(f"  ✅ {key} present")
                    else:
                        print(f"  ⚠️  {key} missing")
            else:
                print(f"❌ {role.title()} template missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Template loading failed: {str(e)}")
        return False

def test_service_initialization():
    """Test service initialization."""
    print("🧪 Testing Service Initialization...")
    
    try:
        analyzer = create_assessment_analyzer()
        transcribe_service = analyzer.transcribe_service
        
        print("✅ AssessmentAnalyzer created successfully")
        print("✅ TranscribeService initialized")
        
        # Test service info
        transcribe_info = transcribe_service.get_service_info()
        print(f"📊 Transcribe service: {transcribe_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting LLM Assessment Analysis Tests\n")
    
    tests = [
        test_service_initialization,
        test_template_loading,
        test_prompt_generation,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! LLM assessment system is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
