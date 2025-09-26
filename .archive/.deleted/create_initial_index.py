#!/usr/bin/env python3
"""
Create initial assessment index from existing assessment files.
This is a one-time script to populate the global index with existing assessments.
"""

import boto3
import json
from datetime import datetime

def create_initial_assessment_index():
    """Create the initial assessment index from existing files."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    # Known existing assessments
    existing_assessments = [
        'banquet_server_20250918_203206_3465',
        'banquet_server_20250923_135428_0112', 
        'bartender_20250918_150629_0112'
    ]
    
    index_entries = []
    
    print("🔍 Creating initial assessment index...")
    
    for assessment_id in existing_assessments:
        try:
            # Get the analysis results
            response = s3_client.get_object(
                Bucket=bucket_name,
                Key=f"assessments/{assessment_id}/analysis_results.json"
            )
            
            results = json.loads(response['Body'].read().decode('utf-8'))
            
            # Parse assessment ID for metadata
            parts = assessment_id.split('_')
            if len(parts) >= 4:
                # Handle roles like "banquet_server" (2 parts)
                role = '_'.join(parts[:-3])  # Everything except last 3 parts
                date = parts[-3]
                time = parts[-2]
            else:
                # Fallback for simple roles
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
            
            index_entries.append(assessment_entry)
            print(f"✅ Added {assessment_id} ({role}, {status})")
            
        except Exception as e:
            print(f"❌ Error processing {assessment_id}: {str(e)}")
    
    # Create the index structure
    index = {
        "assessments": index_entries,
        "last_updated": datetime.utcnow().isoformat(),
        "total_count": len(index_entries)
    }
    
    # Sort by analyzed_at (newest first)
    index["assessments"].sort(
        key=lambda x: x.get("analyzed_at", ""), 
        reverse=True
    )
    
    # Save to S3
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key="assessments_index.json",
            Body=json.dumps(index, indent=2),
            ContentType='application/json'
        )
        
        print(f"🎯 Created assessment index with {len(index_entries)} assessments")
        print(f"📍 Saved to: s3://{bucket_name}/assessments_index.json")
        
        # Also make it publicly accessible by updating bucket policy if needed
        print(f"🔗 Index will be accessible at: https://{bucket_name}.s3.amazonaws.com/assessments_index.json")
        
    except Exception as e:
        print(f"❌ Error saving index: {str(e)}")

if __name__ == "__main__":
    create_initial_assessment_index()
