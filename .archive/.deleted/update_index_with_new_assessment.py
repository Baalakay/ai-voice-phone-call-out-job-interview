#!/usr/bin/env python3
"""
Update the global assessment index with the new assessment that was missed.
"""

import boto3
import json
from datetime import datetime

def update_index_with_new_assessment():
    """Add the new assessment to the global index."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    assessment_id = 'banquet_server_20250924_124417_0112'
    
    print(f"🔄 Adding {assessment_id} to global index...")
    
    # Get existing index
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key="assessments_index.json")
        existing_index = json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Error reading existing index: {str(e)}")
        return
    
    # Get the assessment results
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=f"assessments/{assessment_id}/analysis_results.json"
        )
        results = json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Error reading assessment results: {str(e)}")
        return
    
    # Parse assessment ID for metadata
    parts = assessment_id.split('_')
    if len(parts) >= 4:
        # Handle roles like "banquet_server" (2 parts)
        role = '_'.join(parts[:-3])  # Everything except last 3 parts
        date = parts[-3]
        time = parts[-2]
    else:
        role = parts[0] if len(parts) > 0 else 'unknown'
        date = parts[1] if len(parts) > 1 else 'unknown'
        time = parts[2] if len(parts) > 2 else 'unknown'
    
    # Get status from results
    status = 'unknown'
    if results.get('llm_analysis', {}).get('overall_assessment', {}).get('recommendation'):
        status = results['llm_analysis']['overall_assessment']['recommendation'].lower()
    elif results.get('llm_analysis', {}).get('overall_recommendation'):
        status = results['llm_analysis']['overall_recommendation'].lower()
    elif results.get('recommendation'):
        status = results['recommendation'].lower()
    
    # Create assessment entry
    assessment_entry = {
        "id": assessment_id,
        "role": role.replace('_', ' '),
        "date": date,
        "time": time,
        "status": status,
        "analyzed_at": results.get('analyzed_at', datetime.utcnow().isoformat()),
        "file_path": f"assessments/{assessment_id}/analysis_results.json"
    }
    
    # Check if it already exists
    existing_ids = [a.get("id") for a in existing_index["assessments"]]
    if assessment_id in existing_ids:
        print(f"✅ Assessment {assessment_id} already exists in index")
        return
    
    # Add new entry
    existing_index["assessments"].append(assessment_entry)
    
    # Update metadata
    existing_index["last_updated"] = datetime.utcnow().isoformat()
    existing_index["total_count"] = len(existing_index["assessments"])
    
    # Sort by analyzed_at (newest first)
    existing_index["assessments"].sort(
        key=lambda x: x.get("analyzed_at", ""), 
        reverse=True
    )
    
    # Save updated index
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key="assessments_index.json",
            Body=json.dumps(existing_index, indent=2),
            ContentType='application/json'
        )
        
        print(f"✅ Added {assessment_id} to global index")
        print(f"📊 Index now contains {existing_index['total_count']} assessments")
        print(f"🔗 New assessment: {role} - {status}")
        
    except Exception as e:
        print(f"❌ Error saving updated index: {str(e)}")

if __name__ == "__main__":
    update_index_with_new_assessment()
