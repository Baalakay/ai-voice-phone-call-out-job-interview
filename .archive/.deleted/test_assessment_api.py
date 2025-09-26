#!/usr/bin/env python3
"""
Test AI Skills Assessment API

This script tests the deployed assessment API endpoints to verify everything is working.
"""

import requests
import json
import time

API_BASE_URL = "https://eih1khont2.execute-api.us-east-1.amazonaws.com"

def test_api_health():
    """Test basic API connectivity."""
    print("🔍 Testing API Health...")
    
    try:
        # Test a simple endpoint
        response = requests.get(f"{API_BASE_URL}/webhook", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 405]:  # 405 is expected for GET on POST endpoint
            print("   ✅ API is responding")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {str(e)}")
        return False

def test_initiate_assessment():
    """Test assessment initiation endpoint."""
    print("\n🎯 Testing Assessment Initiation...")
    
    test_payload = {
        "worker_phone": "+15555551234",  # Test phone number
        "skill_type": "bartender",
        "worker_id": "test_worker_123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/initiate", 
            json=test_payload,
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Assessment initiation working")
                return True
            else:
                print("   ⚠️  API responding but assessment failed")
                return False
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_audio_files_accessible():
    """Test that S3 audio files are accessible."""
    print("\n🎵 Testing Audio File Accessibility...")
    
    # Test a few sample audio files
    test_files = [
        "audio/bartender/intro.mp3",
        "audio/host/experience_1.mp3", 
        "audio/banquet_server/knowledge_setup.mp3"
    ]
    
    s3_base_url = "https://innovativesol-gravywork-assets-dev.s3.amazonaws.com"
    
    accessible_count = 0
    
    for file_path in test_files:
        try:
            response = requests.head(f"{s3_base_url}/{file_path}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {file_path}")
                accessible_count += 1
            else:
                print(f"   ❌ {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {file_path} - Error: {str(e)}")
    
    if accessible_count == len(test_files):
        print("   ✅ All audio files accessible")
        return True
    else:
        print(f"   ⚠️  {accessible_count}/{len(test_files)} audio files accessible")
        return False

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n" + "="*60)
    print("🧪 AI SKILLS ASSESSMENT POC - TEST REPORT")
    print("="*60)
    
    tests = [
        ("API Health", test_api_health),
        ("Audio Files", test_audio_files_accessible),
        ("Assessment Initiation", test_initiate_assessment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n▶️  Running {test_name} test...")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 RESULTS: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🚀 ALL TESTS PASSED! Your POC is ready for final Twilio configuration.")
        print("\nNext steps:")
        print("1. Set TWILIO_AUTH_TOKEN in Lambda environment")
        print("2. Configure Twilio webhooks as shown in the guide")
        print("3. Call (472) 236-8895 to test live assessment")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above before proceeding.")
    
    return passed == len(results)

if __name__ == "__main__":
    generate_test_report()
