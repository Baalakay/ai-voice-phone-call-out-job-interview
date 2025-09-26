"""
Main Lambda handler for AI Skills Assessment Platform.

Routes requests between S3 processing (original template) and assessment webhooks (new).
"""

import json
import os
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import parse_qs, unquote_plus

# Import assessment modules with correct SST Lambda paths
try:
    # Full module paths from functions/ root
    from src.functions.twilio_service import TwilioService
    from src.functions.bedrock_service import BedrockService  
    from src.config.twilio_config import get_twilio_config
    from src.prompts.assessment_prompts import get_assessment_prompt, get_system_prompt
    import_source = "sst_full_paths"
except ImportError as e1:
    try:
        # Fallback - direct imports from same directory
        from .twilio_service import TwilioService
        from .bedrock_service import BedrockService
        from ..config.twilio_config import get_twilio_config  
        from ..prompts.assessment_prompts import get_assessment_prompt, get_system_prompt
        import_source = "relative_imports"
    except ImportError as e2:
        # If all imports fail, set to None and handle gracefully
        TwilioService = None
        BedrockService = None
        import_source = f"failed: {str(e1)} | {str(e2)}"

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
environment = os.environ.get('ENVIRONMENT', 'dev')
output_bucket = os.environ.get('OUTPUT_BUCKET')

# Initialize services (if available)
twilio_service = None
bedrock_service = None
ASSESSMENT_TEMPLATES = {}

# Log import status for debugging
logger.info(f"Import status: {import_source}")
logger.info(f"TwilioService available: {TwilioService is not None}")
logger.info(f"BedrockService available: {BedrockService is not None}")

if TwilioService and BedrockService:
    try:
        twilio_env = "production" if environment == "prod" else "development"
        twilio_service = TwilioService(environment=twilio_env)
        bedrock_service = BedrockService()
        logger.info("Successfully initialized Twilio and Bedrock services")
        
        # Load assessment templates
        try:
            import pkg_resources
            template_path = pkg_resources.resource_filename(__name__, '../data/assessment_templates.json')
        except:
            template_path = 'functions/src/data/assessment_templates.json'
            
        try:
            with open(template_path, 'r') as f:
                ASSESSMENT_TEMPLATES = json.load(f)
                logger.info(f"Loaded {len(ASSESSMENT_TEMPLATES)} assessment templates")
        except Exception as e:
            logger.error(f"Failed to load assessment templates: {str(e)}")
            ASSESSMENT_TEMPLATES = {}
    except Exception as e:
        logger.error(f"Failed to initialize assessment services: {str(e)}")
else:
    logger.error("TwilioService or BedrockService not available for initialization")

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
            return handle_assessment_request(event, context)
        
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

def handle_assessment_request(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle HTTP API requests for AI Skills Assessment.
    Routes requests based on path and method.
    """
    try:
        # Parse request details
        path = event.get('rawPath', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
        
        logger.info(f"Assessment request - Path: {path}, Method: {method}")
        
        # Route to appropriate handler
        if path == '/webhook':
            return handle_initial_webhook(event)
        elif path.startswith('/question/'):
            question_id = path.split('/')[-1]
            return handle_question_flow(event, question_id)
        elif path.startswith('/complete/'):
            assessment_id = path.split('/')[-1]
            return handle_completion(event, assessment_id)
        elif path == '/webhook/status':
            return handle_status_callback(event)
        elif path == '/initiate':
            return handle_initiate_assessment(event)
        else:
            # Default webhook test response
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/xml'},
                'body': '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">🎉 SUCCESS! GravyWork AI Skills Assessment webhook is working!</Say>
    <Hangup/>
</Response>'''
            }
            
    except Exception as e:
        logger.error(f"Assessment request handler error: {str(e)}")
        return create_error_response(500, str(e))

def handle_initiate_assessment(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle assessment initiation requests.
    
    Expected POST body:
    {
        "worker_phone": "+1234567890",
        "skill_type": "bartender",
        "worker_id": "optional_worker_id"
    }
    """
    try:
        if not twilio_service:
            return create_error_response(500, "Assessment services not initialized")
            
        # Parse request
        body = json.loads(event.get('body', '{}'))
        worker_phone = body.get('worker_phone')
        skill_type = body.get('skill_type', 'bartender')
        worker_id = body.get('worker_id', '')
        
        # Validate required fields
        if not worker_phone:
            return create_error_response(400, "worker_phone is required")
        
        if ASSESSMENT_TEMPLATES and skill_type not in ASSESSMENT_TEMPLATES:
            return create_error_response(400, f"Invalid skill_type. Available: {list(ASSESSMENT_TEMPLATES.keys())}")
        
        # Generate assessment ID
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        assessment_id = f"{skill_type}_{timestamp}_{worker_phone.replace('+', '').replace('-', '')[-4:]}"
        
        # Get webhook URL from environment
        webhook_base_url = twilio_service.config.voice_webhook_url
        if not webhook_base_url:
            return create_error_response(500, "Webhook URL not configured")
        
        # Initiate assessment call
        result = twilio_service.initiate_assessment_call(
            worker_phone=worker_phone,
            webhook_url=f"{webhook_base_url}/webhook?assessment_id={assessment_id}&skill_type={skill_type}",
            assessment_id=assessment_id
        )
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'assessment_id': assessment_id,
                    'call_sid': result['call_sid'],
                    'worker_phone': worker_phone,
                    'skill_type': skill_type,
                    'status': 'initiated'
                })
            }
        else:
            return create_error_response(500, f"Call failed: {result['error']}")
            
    except json.JSONDecodeError:
        return create_error_response(400, "Invalid JSON body")
    except Exception as e:
        logger.error(f"Initiate assessment error: {str(e)}")
        return create_error_response(500, str(e))

def handle_initial_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle initial webhook call from Twilio."""
    try:
        # Parse query parameters 
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_id = query_params.get('assessment_id', '')
        skill_type = query_params.get('skill_type', 'bartender')
        
        logger.info(f"Initial webhook - Assessment: {assessment_id}, Skill: {skill_type}")
        
        if not assessment_id:
            return create_twiml_response("Assessment ID missing. Please contact support.", hangup=True)
        
        # Generate welcome TwiML with first question
        if ASSESSMENT_TEMPLATES and skill_type in ASSESSMENT_TEMPLATES:
            template = ASSESSMENT_TEMPLATES[skill_type]
            first_question_id = template['questions'][0]['id']
            
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Welcome to the GravyWork skills assessment for {template['title']}. This will take about 5 minutes. Let's begin.</Say>
    <Redirect>/question/{first_question_id}?assessment_id={assessment_id}&amp;skill_type={skill_type}</Redirect>
</Response>'''
        else:
            twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Welcome to the GravyWork skills assessment. Let's begin with your first question.</Say>
    <Pause length="1"/>
    <Say voice="alice">Please describe your experience in customer service. After you hear the beep, speak your answer.</Say>
    <Record timeout="30" transcribe="false" maxLength="120"/>
    <Say voice="alice">Thank you for your response. The assessment is now complete.</Say>
    <Hangup/>
</Response>'''
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/xml'},
            'body': twiml
        }
        
    except Exception as e:
        logger.error(f"Initial webhook error: {str(e)}")
        return create_twiml_response("We're experiencing technical difficulties. Please try again later.", hangup=True)

def handle_question_flow(event: Dict[str, Any], question_id: str) -> Dict[str, Any]:
    """Handle individual question flow."""
    # Simplified implementation for now
    return create_twiml_response("Question flow not fully implemented yet.", hangup=True)

def handle_completion(event: Dict[str, Any], assessment_id: str) -> Dict[str, Any]:
    """Handle assessment completion."""
    # Simplified implementation for now  
    return create_twiml_response("Assessment complete. Thank you!", hangup=True)

def handle_status_callback(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Twilio status callbacks."""
    logger.info("Received status callback")
    return {'statusCode': 200, 'body': 'OK'}

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'error': True,
            'message': message
        })
    }

def create_twiml_response(message: str, hangup: bool = False) -> Dict[str, Any]:
    """Create TwiML response."""
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    {f'<Hangup/>' if hangup else ''}
</Response>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': twiml
    }
