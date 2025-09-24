#!/usr/bin/env python3
"""
Manually add the completed bartender assessment to the global index.
"""

import boto3
import json
from datetime import datetime

def add_bartender_to_index():
    """Add the bartender assessment to the global assessment index."""
    
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    index_key = 'assessments_index.json'
    assessment_id = 'bartender_20250924_150056_0112'
    
    print(f"📋 Adding {assessment_id} to global assessment index...")
    
    try:
        # Get existing index
        response = s3_client.get_object(Bucket=bucket_name, Key=index_key)
        existing_index = json.loads(response['Body'].read().decode('utf-8'))
        
        # Check if assessment results exist
        analysis_key = f"assessments/{assessment_id}/analysis_results.json"
        try:
            analysis_response = s3_client.get_object(Bucket=bucket_name, Key=analysis_key)
            analysis_results = json.loads(analysis_response['Body'].read().decode('utf-8'))
            print(f"✅ Found analysis results for {assessment_id}")
        except Exception as e:
            print(f"❌ No analysis results found: {str(e)}")
            return
        
        # Parse assessment ID
        parts = assessment_id.split('_')
        role = parts[0]
        date = parts[1] 
        time = parts[2]
        
        # Get status from results
        status = 'unknown'
        if analysis_results.get('llm_analysis', {}).get('overall_assessment', {}).get('recommendation'):
            status = analysis_results['llm_analysis']['overall_assessment']['recommendation'].lower()
        
        # Create assessment entry
        assessment_entry = {
            "id": assessment_id,
            "role": role,
            "date": date,
            "time": time,
            "status": status,
            "analyzed_at": analysis_results.get('analyzed_at', datetime.utcnow().isoformat()),
            "file_path": f"assessments/{assessment_id}/analysis_results.json"
        }
        
        # Remove any existing entry with same ID
        existing_index["assessments"] = [
            a for a in existing_index["assessments"] 
            if a.get("id") != assessment_id
        ]
        
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
        s3_client.put_object(
            Bucket=bucket_name,
            Key=index_key,
            Body=json.dumps(existing_index, indent=2),
            ContentType='application/json'
        )
        
        print(f"✅ Successfully added {assessment_id} to global index")
        print(f"📊 Status: {status.upper()}")
        print(f"📅 Analyzed at: {assessment_entry['analyzed_at']}")
        print(f"📈 Total assessments: {existing_index['total_count']}")
        
    except Exception as e:
        print(f"❌ Error adding to index: {str(e)}")

if __name__ == "__main__":
    add_bartender_to_index()
