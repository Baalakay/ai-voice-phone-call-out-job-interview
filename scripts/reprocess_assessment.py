#!/usr/bin/env python3
"""
Reprocess a specific assessment with the current detailed analysis system.
This will regenerate the analysis with proper category breakdown.
"""

import boto3
import json
import sys

def reprocess_assessment(assessment_id):
    """Trigger reprocessing of a specific assessment."""
    lambda_client = boto3.client('lambda')
    
    # The assessment processor function name
    function_name = 'gravywork-vscode-assessment-processor'
    
    # Create the event payload
    # Extract skill type from ID (handle compound roles like banquet_server)
    parts = assessment_id.split('_')
    if len(parts) >= 4:
        # Handle roles like "banquet_server" (2 parts)
        skill_type = '_'.join(parts[:-3])  # Everything except last 3 parts
    else:
        skill_type = parts[0]
    
    event_payload = {
        'assessment_id': assessment_id,
        'skill_type': skill_type
    }
    
    print(f"🔄 Reprocessing assessment: {assessment_id}")
    print(f"📋 Skill type: {event_payload['skill_type']}")
    
    try:
        # Invoke the assessment processor
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous
            Payload=json.dumps(event_payload)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        
        print(f"📋 Full response: {json.dumps(response_payload, indent=2)}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload.get('body', '{}'))
            if body.get('success'):
                print(f"✅ Assessment reprocessed successfully!")
                print(f"🎯 New analysis saved with detailed category breakdown")
                print(f"🔗 View updated results: https://innovativesol-gravywork-assets-dev.s3.amazonaws.com/web/analysis.html")
            else:
                print(f"❌ Reprocessing failed: {body.get('error', 'Unknown error')}")
        else:
            print(f"❌ Lambda error (Status {response_payload.get('statusCode')}): {response_payload.get('body', 'No error details')}")
            
    except Exception as e:
        print(f"❌ Error invoking Lambda: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reprocess_assessment.py <assessment_id>")
        print("Example: python reprocess_assessment.py banquet_server_20250918_203206_3465")
        sys.exit(1)
    
    assessment_id = sys.argv[1]
    reprocess_assessment(assessment_id)
