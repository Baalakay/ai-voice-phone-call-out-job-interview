#!/usr/bin/env python3
"""
Debug script to see exactly what prompt is being sent to the LLM.
"""

import boto3
import json
import sys
import os

# Add the functions path to sys.path
sys.path.insert(0, '/workspaces/gravy-work-poc/functions/src')

def debug_prompt_for_assessment(assessment_id):
    """Debug what prompt would be generated for this assessment."""
    
    # Get the assessment data
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=f"assessments/{assessment_id}/analysis_results.json"
        )
        results = json.loads(response['Body'].read().decode('utf-8'))
        transcripts = results['transcripts']
        skill_type = results['skill_type']
        
        print(f"🔍 DEBUGGING ASSESSMENT: {assessment_id}")
        print(f"📋 SKILL TYPE: {skill_type}")
        print(f"🎤 TRANSCRIPTS:")
        for key, value in transcripts.items():
            print(f"  {key}: \"{value}\"")
        
        # Import the prompt building function
        from functions.assessment_processor_simple import build_assessment_prompt_simple
        
        # Generate the prompt
        prompt = build_assessment_prompt_simple(transcripts, skill_type)
        
        print(f"\n📝 GENERATED PROMPT:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        # Check if the transcripts are actually in the prompt
        print(f"\n🔍 CHECKING IF ACTUAL TRANSCRIPTS ARE IN PROMPT:")
        for key, value in transcripts.items():
            if value in prompt:
                print(f"✅ Found '{key}': \"{value}\" in prompt")
            else:
                print(f"❌ Missing '{key}': \"{value}\" from prompt")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_llm_prompt.py <assessment_id>")
        print("Example: python debug_llm_prompt.py banquet_server_20250924_124417_0112")
        sys.exit(1)
    
    assessment_id = sys.argv[1]
    debug_prompt_for_assessment(assessment_id)
