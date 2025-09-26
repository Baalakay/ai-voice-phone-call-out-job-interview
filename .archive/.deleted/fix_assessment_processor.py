#!/usr/bin/env python3

import boto3
import json
from datetime import datetime

def update_global_index_directly():
    """Update the global assessment index with all completed assessments."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    # Find all assessments with analysis_results.json
    assessments = []
    
    # List all assessment directories
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix='assessments/',
        Delimiter='/'
    )
    
    for prefix_info in response.get('CommonPrefixes', []):
        assessment_id = prefix_info['Prefix'].rstrip('/').split('/')[-1]
        
        # Check if this assessment has analysis_results.json
        try:
            analysis_key = f'assessments/{assessment_id}/analysis_results.json'
            s3_client.head_object(Bucket=bucket_name, Key=analysis_key)
            
            # Get the analysis results to extract status
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=analysis_key)
                results = json.loads(response['Body'].read().decode('utf-8'))
                
                # Parse assessment ID for metadata
                parts = assessment_id.split('_')
                if len(parts) >= 4:
                    role = '_'.join(parts[:-3])
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
                
                analyzed_at = results.get('analyzed_at', datetime.utcnow().isoformat())
                
                assessment_entry = {
                    "id": assessment_id,
                    "role": role.replace('_', ' '),
                    "date": date,
                    "time": time,
                    "status": status,
                    "analyzed_at": analyzed_at,
                    "file_path": f"assessments/{assessment_id}/analysis_results.json"
                }
                
                assessments.append(assessment_entry)
                print(f"✅ Added assessment: {assessment_id} ({status})")
                
            except Exception as e:
                print(f"❌ Error reading analysis for {assessment_id}: {str(e)}")
                continue
                
        except s3_client.exceptions.NoSuchKey:
            print(f"⏳ Skipping {assessment_id} - no analysis results")
            continue
    
    # Create new index
    new_index = {
        "assessments": assessments,
        "last_updated": datetime.utcnow().isoformat(),
        "total_count": len(assessments)
    }
    
    # Sort by analyzed_at (newest first)
    new_index["assessments"].sort(key=lambda x: x.get("analyzed_at", ""), reverse=True)
    
    # Save updated index
    s3_client.put_object(
        Bucket=bucket_name,
        Key='assessments_index.json',
        Body=json.dumps(new_index, indent=2),
        ContentType='application/json'
    )
    
    print(f"🎯 FIXED! Updated global assessment index with {len(assessments)} assessments")
    return len(assessments)

if __name__ == "__main__":
    count = update_global_index_directly()
    print(f"✅ SUCCESS: {count} assessments now visible in UI")
