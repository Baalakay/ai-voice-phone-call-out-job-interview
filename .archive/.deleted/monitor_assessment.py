#!/usr/bin/env python3
"""
Monitor assessment processing in real-time.
"""
import boto3
import json
import time
from datetime import datetime, timedelta
import sys

def get_recent_logs(log_group, minutes=10):
    """Get recent logs from CloudWatch."""
    logs_client = boto3.client('logs')
    
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)
        
        response = logs_client.filter_log_events(
            logGroupName=log_group,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )
        
        events = response.get('events', [])
        return events[-20:] if len(events) > 20 else events  # Last 20 events
        
    except Exception as e:
        print(f"❌ Error getting logs from {log_group}: {str(e)}")
        return []

def check_s3_assessments():
    """Check for recent assessments in S3."""
    s3_client = boto3.client('s3')
    bucket = 'innovativesol-gravywork-assets-dev'
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix='assessments/',
            MaxKeys=10
        )
        
        objects = response.get('Contents', [])
        
        # Sort by last modified (most recent first)
        objects.sort(key=lambda x: x['LastModified'], reverse=True)
        
        print("📁 Recent Assessment Files in S3:")
        for obj in objects[:5]:  # Show last 5
            key = obj['Key']
            modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S UTC')
            size = obj['Size']
            print(f"  📄 {key} ({size} bytes) - {modified}")
        
        return objects
        
    except Exception as e:
        print(f"❌ Error checking S3: {str(e)}")
        return []

def get_assessment_result(assessment_id):
    """Get specific assessment result from S3."""
    s3_client = boto3.client('s3')
    bucket = 'innovativesol-gravywork-assets-dev'
    key = f'assessments/{assessment_id}/analysis_results.json'
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        result = json.loads(response['Body'].read())
        return result
    except Exception as e:
        print(f"❌ No analysis results yet for {assessment_id}: {str(e)}")
        return None

def monitor_assessment(assessment_id=None, duration_minutes=5):
    """Monitor assessment processing."""
    print(f"🔍 Monitoring Assessment Processing for {duration_minutes} minutes...")
    print("=" * 60)
    
    log_groups = [
        '/aws/lambda/gravywork-processor-dev',  # Main webhook handler
        '/aws/lambda/gravywork-assessment-processor-dev'  # LLM analyzer
    ]
    
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    last_check = start_time
    
    while datetime.utcnow() < end_time:
        print(f"\n⏰ {datetime.utcnow().strftime('%H:%M:%S')} - Checking logs and S3...")
        
        # Check logs from both Lambda functions
        for log_group in log_groups:
            print(f"\n📋 {log_group.split('/')[-1]}:")
            events = get_recent_logs(log_group, minutes=2)
            
            if events:
                for event in events[-3:]:  # Show last 3 events
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
                    message = event['message'].strip()
                    if any(keyword in message.lower() for keyword in ['assessment', 'transcrib', 'analysis', 'error']):
                        print(f"  {timestamp}: {message}")
            else:
                print("  No recent relevant logs")
        
        # Check S3 for new files
        print(f"\n📁 S3 Assessment Files:")
        s3_objects = check_s3_assessments()
        
        # If specific assessment ID provided, check for results
        if assessment_id:
            result = get_assessment_result(assessment_id)
            if result:
                print(f"\n🎉 ANALYSIS COMPLETE for {assessment_id}!")
                print(f"📊 Recommendation: {result.get('llm_analysis', {}).get('overall_recommendation', 'Unknown')}")
                print(f"📝 Reasoning: {result.get('llm_analysis', {}).get('overall_reasoning', 'No reasoning provided')}")
                break
        
        # Wait before next check
        time.sleep(30)
        
    print(f"\n⏹️  Monitoring completed at {datetime.utcnow().strftime('%H:%M:%S')}")

def main():
    """Main monitoring function."""
    assessment_id = None
    duration = 5
    
    if len(sys.argv) > 1:
        assessment_id = sys.argv[1]
        print(f"🎯 Monitoring specific assessment: {assessment_id}")
    
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
    
    print("🚀 Starting Assessment Monitoring")
    print(f"⏱️  Duration: {duration} minutes")
    print(f"🎯 Assessment ID: {assessment_id or 'Any new assessment'}")
    print()
    
    try:
        monitor_assessment(assessment_id, duration)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {str(e)}")

if __name__ == "__main__":
    main()
