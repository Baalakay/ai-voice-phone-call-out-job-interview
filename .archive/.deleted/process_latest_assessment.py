#!/usr/bin/env python3
"""
Process the latest bartender assessment with the fixed assessment processor.
"""

import boto3
import json

def process_latest_assessment():
    """Trigger processing of the latest bartender assessment."""
    
    assessment_id = "bartender_20250924_153226_0112"
    skill_type = "bartender"
    
    print(f"🔄 Processing latest bartender assessment: {assessment_id}")
    print(f"📋 This should now work with the fixed self-contained processor")
    
    # Invoke the assessment processor Lambda
    lambda_client = boto3.client('lambda')
    
    payload = {
        "assessment_id": assessment_id,
        "skill_type": skill_type
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='gravywork-vscode-assessment-processor',
            InvocationType='Event',  # Asynchronous
            Payload=json.dumps(payload)
        )
        
        print(f"✅ Processing triggered successfully")
        print(f"📋 Status Code: {response['StatusCode']}")
        print(f"📋 Assessment ID: {assessment_id}")
        print(f"📋 Expected outcomes:")
        print(f"   - LLM analysis should complete without import errors")
        print(f"   - Assessment should appear in UI automatically")
        print(f"   - Global index should be updated")
        print(f"")
        print(f"⏳ Processing will take ~2-3 minutes...")
        print(f"🔍 Check the analysis dashboard to see results")
        
    except Exception as e:
        print(f"❌ Error triggering processing: {str(e)}")

if __name__ == "__main__":
    process_latest_assessment()
