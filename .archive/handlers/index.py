"""
Main Lambda handler for AI Skills Assessment Platform.

Routes requests between S3 processing (original template) and assessment webhooks (new).
"""

import json
import os
import boto3
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
# dynamodb removed - using S3 JSON files for simplified storage

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler function.
    
    Routes between:
    - S3 events (original template functionality)  
    - HTTP API requests for AI Skills Assessment webhooks
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Check if this is an HTTP API event (assessment webhook)
        if 'requestContext' in event and 'http' in event['requestContext']:
            # Return simple TwiML response for testing
            logger.info("Handling webhook request - SUCCESS!")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/xml'},
                'body': '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">🎉 SUCCESS! GravyWork AI Skills Assessment webhook is now working perfectly!</Say>
    <Hangup/>
</Response>'''
            }
        
        # Otherwise, process as S3 event (original template functionality)
        return handle_s3_event(event, context)
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise

def handle_s3_event(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Handle original S3 events from the SST template."""
    try:
        # Get environment variables
        environment = os.environ.get('ENVIRONMENT', 'dev')
        queue_url = os.environ.get('QUEUE_URL')
        output_bucket = os.environ.get('OUTPUT_BUCKET')
        project_name = os.environ.get('PROJECT_NAME')
        
        logger.info(f"Processing S3 event for project: {project_name} in environment: {environment}")
        
        # Process S3 events
        if 'Records' in event:
            for record in event['Records']:
                if record['eventSource'] == 'aws:s3':
                    bucket = record['s3']['bucket']['name']
                    key = record['s3']['object']['key']
                    
                    logger.info(f"Processing S3 object: s3://{bucket}/{key}")
                    
                    # Your custom processing logic goes here
                    # This is where you would add your specific business logic
                    result = process_file(bucket, key, queue_url, output_bucket)
                    
                    logger.info(f"Processing completed for {key}: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed S3 event for {project_name}',
                'environment': environment
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing S3 event: {str(e)}")
        raise

def process_file(bucket: str, key: str, queue_url: str, output_bucket: str) -> Dict[str, Any]:
    """
    Process a file from S3.
    
    Customize this function based on your specific requirements.
    This is a template that can be modified for different use cases.
    """
    try:
        # Example: Record processing start in S3 (simplified approach)
        if output_bucket:
            processing_metadata = {
                'id': f"{bucket}/{key}",
                'status': 'processing',
                'timestamp': datetime.utcnow().isoformat()
            }
            s3_client.put_object(
                Bucket=output_bucket,
                Key=f"processing/{bucket}_{key.replace('/', '_')}_metadata.json",
                Body=json.dumps(processing_metadata),
                ContentType='application/json'
            )
        
        # Example: Download file for processing
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        
        logger.info(f"Downloaded file {key}, size: {len(file_content)} bytes")
        
        # Add your custom processing logic here
        # For example:
        # - Text extraction
        # - Image processing  
        # - Data transformation
        # - API calls
        
        # Example: Upload result to output bucket
        if output_bucket:
            output_key = f"processed/{key}"
            s3_client.put_object(
                Bucket=output_bucket,
                Key=output_key,
                Body=b"Processed content placeholder",
                ContentType='text/plain'
            )
            
            logger.info(f"Uploaded processed result to s3://{output_bucket}/{output_key}")
        
        # Example: Send message to SQS queue
        if queue_url:
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'action': 'file_processed',
                    'bucket': bucket,
                    'key': key,
                    'status': 'completed'
                })
            )
        
        # Update processing status in S3 (simplified approach)
        if output_bucket:
            completion_metadata = {
                'id': f"{bucket}/{key}",
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat()
            }
            s3_client.put_object(
                Bucket=output_bucket,
                Key=f"processing/{bucket}_{key.replace('/', '_')}_completed.json",
                Body=json.dumps(completion_metadata),
                ContentType='application/json'
            )
        
        return {
            'status': 'success',
            'processed_file': f"s3://{bucket}/{key}",
            'output_location': f"s3://{output_bucket}/processed/{key}" if output_bucket else None
        }
        
    except Exception as e:
        logger.error(f"Error processing file {key}: {str(e)}")
        
        # Update processing status with error in S3 (simplified approach)
        if output_bucket:
            try:
                error_metadata = {
                    'id': f"{bucket}/{key}",
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                s3_client.put_object(
                    Bucket=output_bucket,
                    Key=f"processing/{bucket}_{key.replace('/', '_')}_error.json",
                    Body=json.dumps(error_metadata),
                    ContentType='application/json'
                )
            except:
                pass  # Don't fail if S3 update fails
        
        raise
