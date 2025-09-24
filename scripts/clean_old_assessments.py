#!/usr/bin/env python3
"""
Remove old assessments from S3 bucket and assessment index.
Keep only assessments from today (2025-09-24) and later.
"""

import boto3
import json
from datetime import datetime

def clean_old_assessments():
    """Remove old assessments and update index."""
    s3_client = boto3.client('s3')
    bucket_name = 'innovativesol-gravywork-assets-dev'
    
    # Define cutoff date - keep only today and later
    cutoff_date = "20250924"
    
    print(f"🧹 Cleaning old assessments (before {cutoff_date})...")
    
    # Get current index
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key="assessments_index.json")
        index = json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Error reading index: {str(e)}")
        return
    
    # Identify old assessments to remove
    old_assessments = []
    new_assessments = []
    
    for assessment in index["assessments"]:
        assessment_id = assessment["id"]
        # Extract date from assessment ID
        parts = assessment_id.split('_')
        if len(parts) >= 3:
            date = parts[-3] if len(parts) >= 4 else parts[1]
            if date < cutoff_date:
                old_assessments.append(assessment)
            else:
                new_assessments.append(assessment)
        else:
            old_assessments.append(assessment)  # Remove malformed IDs
    
    print(f"📊 Found {len(old_assessments)} old assessments to remove")
    print(f"📊 Keeping {len(new_assessments)} recent assessments")
    
    # Remove old assessment files from S3
    for assessment in old_assessments:
        assessment_id = assessment["id"]
        print(f"🗑️ Removing {assessment_id}...")
        
        # List and delete all files in the assessment folder
        try:
            prefix = f"assessments/{assessment_id}/"
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    print(f"   Deleted: {obj['Key']}")
            
            print(f"✅ Removed {assessment_id} completely")
            
        except Exception as e:
            print(f"❌ Error removing {assessment_id}: {str(e)}")
    
    # Update index with only new assessments
    updated_index = {
        "assessments": new_assessments,
        "last_updated": datetime.utcnow().isoformat(),
        "total_count": len(new_assessments)
    }
    
    # Sort by analyzed_at (newest first)
    updated_index["assessments"].sort(
        key=lambda x: x.get("analyzed_at", ""), 
        reverse=True
    )
    
    # Save updated index
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key="assessments_index.json",
            Body=json.dumps(updated_index, indent=2),
            ContentType='application/json'
        )
        
        print(f"✅ Updated index - now contains {updated_index['total_count']} assessments")
        
    except Exception as e:
        print(f"❌ Error updating index: {str(e)}")

if __name__ == "__main__":
    clean_old_assessments()
