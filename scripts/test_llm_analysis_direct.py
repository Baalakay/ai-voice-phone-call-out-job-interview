#!/usr/bin/env python3
"""
Test LLM analysis directly without phone calls (for debugging).
"""
import json
import uuid
from datetime import datetime
import sys
import os

# Add the functions directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'src'))

# Set up environment variables
os.environ.setdefault('S3_BUCKET_NAME', 'innovativesol-gravywork-assets-dev')
os.environ.setdefault('PROJECT_NAME', 'gravywork-processor')

def create_mock_assessment_state():
    """Create a mock assessment state with realistic responses."""
    assessment_id = f"test-{uuid.uuid4().hex[:8]}"
    
    return {
        'assessment_id': assessment_id,
        'skill_type': 'bartender',
        'status': 'completed',
        'started_at': datetime.utcnow().isoformat(),
        'completed_at': datetime.utcnow().isoformat(),
        'current_question_index': 11,  # Completed
        'responses': {
            'experience_1': {
                'recording_url': 'https://api.twilio.com/mock/recording1.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "I worked as a bartender at Murphy's Irish Pub for two and a half years. I made cocktails, served beer and wine, handled the cash register, and cleaned glasses. I worked mostly evening shifts and weekend crowds."
            },
            'experience_2': {
                'recording_url': 'https://api.twilio.com/mock/recording2.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "Before that I worked at the Marriott hotel bar for about 8 months. I learned classic cocktails like martinis, manhattans, and old fashioneds. I also did inventory and helped train new staff."
            },
            'experience_3': {
                'recording_url': 'https://api.twilio.com/mock/recording3.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "I also helped at my friend's restaurant during busy events. I mostly poured beer and wine, but I got to see how the kitchen and bar work together during service."
            },
            'knowledge_cosmopolitan_glass': {
                'recording_url': 'https://api.twilio.com/mock/recording4.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "A cosmopolitan should be served in a martini glass, the triangular cocktail glass. That's the classic presentation."
            },
            'knowledge_old_fashioned_glass': {
                'recording_url': 'https://api.twilio.com/mock/recording5.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "An old fashioned goes in a rocks glass, also called a lowball glass. It's the short, heavy glass."
            },
            'knowledge_margarita': {
                'recording_url': 'https://api.twilio.com/mock/recording6.mp3',
                'timestamp': datetime.utcnow().isoformat(),
                'mock_transcript': "For a margarita, you muddle fresh lime, add tequila and triple sec or cointreau, shake with ice, and strain into a salt-rimmed glass."
            }
        }
    }

def test_prompt_generation():
    """Test prompt generation with mock data."""
    print("🧪 Testing Prompt Generation with Mock Data...")
    
    try:
        # Import here to avoid import issues
        from services.assessment_analyzer import create_assessment_analyzer
        
        analyzer = create_assessment_analyzer()
        
        # Load templates
        templates = analyzer._load_assessment_templates()
        if 'bartender' not in templates:
            print("❌ Bartender template not found")
            return False
        
        # Create mock transcripts
        mock_state = create_mock_assessment_state()
        mock_transcripts = {}
        
        for question_key, response in mock_state['responses'].items():
            mock_transcripts[question_key] = response['mock_transcript']
        
        # Generate prompt
        criteria = templates['bartender']
        prompt = analyzer._build_assessment_prompt(mock_transcripts, criteria, 'bartender')
        
        print("✅ Prompt generated successfully!")
        print(f"📊 Prompt length: {len(prompt)} characters")
        
        # Save prompt to file for review
        with open('/tmp/test_prompt.txt', 'w') as f:
            f.write(prompt)
        print("📄 Full prompt saved to: /tmp/test_prompt.txt")
        
        # Show a sample
        print("\n📝 Prompt Sample (first 1000 chars):")
        print("=" * 50)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_transcription():
    """Test transcription service with mock data."""
    print("🧪 Testing Mock Transcription...")
    
    try:
        from services.transcribe_service import create_transcribe_service
        
        transcribe_service = create_transcribe_service()
        info = transcribe_service.get_service_info()
        
        print("✅ Transcribe service initialized")
        print(f"📊 Service info: {info}")
        
        # Test batch transcription with mock data
        mock_state = create_mock_assessment_state()
        
        # Simulate transcription results
        mock_transcripts = {}
        for question_key, response in mock_state['responses'].items():
            mock_transcripts[question_key] = response['mock_transcript']
        
        print(f"✅ Mock transcription completed for {len(mock_transcripts)} responses")
        
        for question, transcript in mock_transcripts.items():
            print(f"  📝 {question}: {transcript[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcription test failed: {str(e)}")
        return False

def main():
    """Run mock assessment tests."""
    print("🚀 Starting Mock LLM Analysis Tests\n")
    
    tests = [
        test_mock_transcription,
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
        print("\n🎉 All mock tests passed! System components are working.")
        print("\n📋 Next Steps:")
        print("1. Make a real phone call to test end-to-end")
        print("2. Monitor with: python scripts/monitor_assessment.py")
        print("3. Check S3 for analysis results after call completion")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
