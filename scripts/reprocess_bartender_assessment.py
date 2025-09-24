#!/usr/bin/env python3
"""
Reprocess the bartender assessment with updated LLM evaluation criteria.
"""

import boto3
import json

def reprocess_bartender_assessment():
    """Trigger reprocessing of the bartender assessment with updated criteria."""
    
    assessment_id = "bartender_20250924_150056_0112"
    skill_type = "bartender"
    
    print(f"🔄 Reprocessing bartender assessment: {assessment_id}")
    print(f"📋 This will use the updated LLM evaluation criteria with flexible scoring")
    
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
        
        print(f"✅ Reprocessing triggered successfully")
        print(f"📋 Status Code: {response['StatusCode']}")
        print(f"📋 Assessment ID: {assessment_id}")
        print(f"📋 Expected improvements:")
        print(f"   - knowledge_tools should now score 7/10 (Acceptable) instead of 3/10 (Red Flag)")
        print(f"   - Overall Knowledge category score should improve")
        print(f"   - Final recommendation may change from FAIL to REVIEW or PASS")
        print(f"")
        print(f"⏳ Processing will take ~2-3 minutes...")
        print(f"🔍 Check the analysis dashboard to see updated results")
        
    except Exception as e:
        print(f"❌ Error triggering reprocessing: {str(e)}")

if __name__ == "__main__":
    reprocess_bartender_assessment()
