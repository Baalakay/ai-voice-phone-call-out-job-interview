"""
Assessment Handler for AI Skills Assessment Platform

Handles Twilio webhooks for voice-based skills assessment workflow.
Integrates with TwilioService, BedrockService, and real GravyWork assessment criteria.
"""

import json
import os
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import parse_qs, unquote_plus

# Import with try/catch for Lambda environment
try:
    from functions.twilio_service import TwilioService
    from functions.bedrock_service import BedrockService
    from config.twilio_config import get_twilio_config
    from prompts.assessment_prompts import get_assessment_prompt, get_system_prompt
except ImportError:
    # Fallback for local development
    from ..functions.twilio_service import TwilioService
    from ..functions.bedrock_service import BedrockService
    from ..config.twilio_config import get_twilio_config
    from ..prompts.assessment_prompts import get_assessment_prompt, get_system_prompt

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
environment = os.environ.get('ENVIRONMENT', 'dev')
output_bucket = os.environ.get('OUTPUT_BUCKET')

# Initialize services
twilio_env = "production" if environment == "prod" else "development"
twilio_service = TwilioService(environment=twilio_env)
bedrock_service = BedrockService()

# Load assessment templates
def load_assessment_templates() -> Dict[str, Any]:
    """Load assessment templates from JSON file."""
    try:
        with open('functions/src/data/assessment_templates.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load assessment templates: {str(e)}")
        # Return minimal fallback
        return {
            "banquet_server": {"name": "Banquet Server", "questions_sequence": ["intro", "goodbye"]},
            "bartender": {"name": "Bartender", "questions_sequence": ["intro", "goodbye"]},
            "host": {"name": "Host", "questions_sequence": ["intro", "goodbye"]}
        }

ASSESSMENT_TEMPLATES = load_assessment_templates()

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler for assessment webhooks.
    Routes requests based on path and method.
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Parse request details
        path = event.get('rawPath', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
        
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
            return create_error_response(404, "Endpoint not found")
            
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
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
        # Parse request
        body = json.loads(event.get('body', '{}'))
        worker_phone = body.get('worker_phone')
        skill_type = body.get('skill_type', 'bartender')
        worker_id = body.get('worker_id', '')
        
        # Validate required fields
        if not worker_phone:
            return create_error_response(400, "worker_phone is required")
        
        if skill_type not in ASSESSMENT_TEMPLATES:
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
        # Parse Twilio webhook data
        twilio_data = parse_twilio_webhook(event)
        assessment_id = twilio_data.get('assessment_id')
        skill_type = twilio_data.get('skill_type', 'bartender')
        call_sid = twilio_data.get('CallSid')
        
        logger.info(f"Initial webhook for assessment: {assessment_id}, skill: {skill_type}, call: {call_sid}")
        
        # Validate skill type
        if skill_type not in ASSESSMENT_TEMPLATES:
            return create_error_twiml(f"Invalid skill type: {skill_type}")
        
        template = ASSESSMENT_TEMPLATES[skill_type]
        
        # Create assessment record
        assessment_data = {
            'assessment_id': assessment_id,
            'skill_type': skill_type,
            'call_sid': call_sid,
            'status': 'started',
            'timestamp': datetime.utcnow().isoformat(),
            'worker_phone': twilio_data.get('To'),
            'from_phone': twilio_data.get('From'),
            'template_name': template['name'],
            'language_requirement': template['language_requirement'],
            'total_questions': len(template['questions_sequence'])
        }
        
        # Save initial assessment data
        save_assessment_data(assessment_id, 'metadata.json', assessment_data)
        
        # Generate intro TwiML
        intro_audio_url = f"https://{output_bucket}.s3.amazonaws.com/audio/{skill_type}/intro.mp3"
        webhook_base_url = twilio_service.config.voice_webhook_url
        first_question_url = f"{webhook_base_url}/question/0?assessment_id={assessment_id}&skill_type={skill_type}"
        
        twiml = twilio_service.generate_intro_twiml(
            audio_url=intro_audio_url,
            first_question_url=first_question_url
        )
        
        return create_twiml_response(twiml)
        
    except Exception as e:
        logger.error(f"Initial webhook error: {str(e)}")
        return create_error_twiml("Sorry, there was a technical issue. Goodbye.")

def handle_question_flow(event: Dict[str, Any], question_index: str) -> Dict[str, Any]:
    """Handle question flow - present question and collect response."""
    try:
        twilio_data = parse_twilio_webhook(event)
        assessment_id = twilio_data.get('assessment_id')
        skill_type = twilio_data.get('skill_type', 'bartender')
        call_sid = twilio_data.get('CallSid')
        question_idx = int(question_index)
        
        logger.info(f"Question {question_idx} for assessment: {assessment_id}, skill: {skill_type}")
        
        # Validate skill type and get template
        if skill_type not in ASSESSMENT_TEMPLATES:
            return create_error_twiml("Invalid assessment type")
            
        template = ASSESSMENT_TEMPLATES[skill_type]
        questions_sequence = template['questions_sequence']
        
        # Save previous response if exists
        if 'SpeechResult' in twilio_data and question_idx > 0:
            prev_question = questions_sequence[question_idx - 1] if question_idx > 0 else 'intro'
            save_speech_response(assessment_id, prev_question, twilio_data['SpeechResult'])
        
        # Check if we're at the end of questions
        if question_idx >= len(questions_sequence):
            # All questions completed, move to completion
            webhook_base_url = twilio_service.config.voice_webhook_url
            completion_url = f"{webhook_base_url}/complete/{assessment_id}?skill_type={skill_type}"
            twiml = f'<Response><Redirect>{completion_url}</Redirect></Response>'
            return create_twiml_response(twiml)
        
        current_question = questions_sequence[question_idx]
        
        # Handle special cases
        if current_question == 'intro':
            # Skip intro (already played), move to first real question
            next_question_url = f"{twilio_service.config.voice_webhook_url}/question/{question_idx + 1}?assessment_id={assessment_id}&skill_type={skill_type}"
            twiml = f'<Response><Redirect>{next_question_url}</Redirect></Response>'
            return create_twiml_response(twiml)
        elif current_question == 'goodbye':
            # Final goodbye
            webhook_base_url = twilio_service.config.voice_webhook_url
            completion_url = f"{webhook_base_url}/complete/{assessment_id}?skill_type={skill_type}"
            twiml = f'<Response><Redirect>{completion_url}</Redirect></Response>'
            return create_twiml_response(twiml)
        
        # Generate question TwiML
        audio_url = f"https://{output_bucket}.s3.amazonaws.com/audio/{skill_type}/{current_question}.mp3"
        webhook_base_url = twilio_service.config.voice_webhook_url
        next_action_url = f"{webhook_base_url}/question/{question_idx + 1}?assessment_id={assessment_id}&skill_type={skill_type}"
        
        # Use speech timeout from template
        speech_timeout = template.get('speech_timeout', '4')
        
        twiml = twilio_service.generate_question_twiml(
            audio_url=audio_url,
            next_action_url=next_action_url,
            question_number=question_idx + 1
        )
        
        return create_twiml_response(twiml)
        
    except Exception as e:
        logger.error(f"Question flow error: {str(e)}")
        return create_error_twiml("Let's continue with the next question.")

def handle_completion(event: Dict[str, Any], assessment_id: str) -> Dict[str, Any]:
    """Handle assessment completion and analysis."""
    try:
        twilio_data = parse_twilio_webhook(event)
        skill_type = twilio_data.get('skill_type', 'bartender')
        
        # Save final response if exists
        if 'SpeechResult' in twilio_data:
            # Get the last question from the sequence
            template = ASSESSMENT_TEMPLATES[skill_type]
            questions_sequence = template['questions_sequence']
            if len(questions_sequence) > 2:  # Has questions beyond intro/goodbye
                last_question = questions_sequence[-2]  # Second to last (before goodbye)
                save_speech_response(assessment_id, last_question, twilio_data['SpeechResult'])
        
        # Trigger async assessment analysis
        trigger_assessment_analysis(assessment_id, skill_type)
        
        # Generate completion TwiML
        goodbye_url = f"https://{output_bucket}.s3.amazonaws.com/audio/{skill_type}/goodbye.mp3"
        
        twiml = twilio_service.generate_completion_twiml(goodbye_url)
        return create_twiml_response(twiml)
        
    except Exception as e:
        logger.error(f"Completion error: {str(e)}")
        return create_error_twiml("Thank you for your time. Goodbye.")

def trigger_assessment_analysis(assessment_id: str, skill_type: str):
    """Trigger async assessment analysis using Bedrock."""
    try:
        # Load all responses
        responses = load_all_responses(assessment_id)
        if not responses:
            logger.warning(f"No responses found for assessment {assessment_id}")
            return
            
        # Compile transcript
        transcript = compile_transcript(responses, skill_type)
        
        # Analyze with Bedrock using real GravyWork criteria
        assessment_prompt = get_assessment_prompt(skill_type, transcript)
        system_prompt = get_system_prompt()
        
        analysis = bedrock_service.simple_generate(
            prompt=assessment_prompt,
            system_prompt=system_prompt
        )
        
        # Save assessment result
        result = {
            'assessment_id': assessment_id,
            'skill_type': skill_type,
            'template_used': ASSESSMENT_TEMPLATES[skill_type]['name'],
            'transcript': transcript,
            'individual_responses': responses,
            'analysis': analysis,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            'bedrock_model': bedrock_service.get_model_info()['model_id']
        }
        
        save_assessment_data(assessment_id, 'result.json', result)
        logger.info(f"Assessment analysis completed for {assessment_id}")
        
    except Exception as e:
        logger.error(f"Assessment analysis error for {assessment_id}: {str(e)}")

# Helper functions
def parse_twilio_webhook(event: Dict[str, Any]) -> Dict[str, str]:
    """Parse Twilio webhook POST data."""
    body = event.get('body', '')
    if event.get('isBase64Encoded', False):
        import base64
        body = base64.b64decode(body).decode('utf-8')
    
    # Parse form data
    parsed_data = parse_qs(body)
    result = {}
    
    for key, value_list in parsed_data.items():
        result[key] = unquote_plus(value_list[0]) if value_list else ''
    
    # Add query parameters
    query_params = event.get('queryStringParameters') or {}
    result.update(query_params)
    
    return result

def save_assessment_data(assessment_id: str, filename: str, data: Any):
    """Save assessment data to S3."""
    s3_key = f"assessments/{assessment_id}/{filename}"
    s3_client.put_object(
        Bucket=output_bucket,
        Key=s3_key,
        Body=json.dumps(data, default=str, indent=2),
        ContentType='application/json'
    )

def save_speech_response(assessment_id: str, question_key: str, speech_text: str):
    """Save individual speech response."""
    filename = f"responses/{question_key}_response.txt"
    s3_key = f"assessments/{assessment_id}/{filename}"
    s3_client.put_object(
        Bucket=output_bucket,
        Key=s3_key,
        Body=speech_text,
        ContentType='text/plain'
    )

def load_all_responses(assessment_id: str) -> Dict[str, str]:
    """Load all speech responses for assessment."""
    responses = {}
    
    try:
        # List response files
        prefix = f"assessments/{assessment_id}/responses/"
        paginator = s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=output_bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith('_response.txt'):
                    # Extract question key from filename
                    filename = key.split('/')[-1]
                    question_key = filename.replace('_response.txt', '')
                    
                    # Load response text
                    response = s3_client.get_object(Bucket=output_bucket, Key=key)
                    responses[question_key] = response['Body'].read().decode('utf-8')
                    
    except Exception as e:
        logger.error(f"Error loading responses for {assessment_id}: {str(e)}")
    
    return responses

def compile_transcript(responses: Dict[str, str], skill_type: str) -> str:
    """Compile responses into a full transcript following question order."""
    template = ASSESSMENT_TEMPLATES[skill_type]
    questions_sequence = template['questions_sequence']
    
    transcript_parts = []
    
    for question_key in questions_sequence:
        if question_key in responses and question_key not in ['intro', 'goodbye']:
            response = responses[question_key]
            # Make question key more readable
            readable_key = question_key.replace('_', ' ').title()
            transcript_parts.append(f"{readable_key}: {response}")
    
    return "\n\n".join(transcript_parts)

def create_twiml_response(twiml: str) -> Dict[str, Any]:
    """Create proper HTTP response with TwiML."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/xml',
            'Cache-Control': 'no-cache'
        },
        'body': twiml
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create error HTTP response."""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'success': False, 'error': message})
    }

def create_error_twiml(message: str) -> Dict[str, Any]:
    """Create TwiML error response."""
    error_twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{message}</Say>
        <Hangup/>
    </Response>"""
    
    return create_twiml_response(error_twiml)

def handle_status_callback(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Twilio status callbacks."""
    try:
        twilio_data = parse_twilio_webhook(event)
        call_sid = twilio_data.get('CallSid', '')
        call_status = twilio_data.get('CallStatus', '')
        
        logger.info(f"Status callback - Call: {call_sid}, Status: {call_status}")
        
        # Could trigger additional processing based on status
        # For now, just acknowledge
        
        return {
            'statusCode': 200,
            'body': 'OK'
        }
        
    except Exception as e:
        logger.error(f"Status callback error: {str(e)}")
        return create_error_response(500, str(e))
