"""
Simplified AI Skills Assessment webhook handler - all code in one file to avoid import issues.
"""

import json
import os
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
environment = os.environ.get('ENVIRONMENT', 'dev')
output_bucket = os.environ.get('OUTPUT_BUCKET')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+14722368895')
TWILIO_WEBHOOK_URL = os.environ.get('TWILIO_WEBHOOK_URL')

# Load complete assessment templates from JSON file
def load_assessment_templates():
    """Load the complete assessment templates with question sequences."""
    import json
    import os
    
    # Try multiple possible paths for the assessment templates
    current_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(current_dir, '..', 'data', 'assessment_templates.json'),
        os.path.join(current_dir, 'data', 'assessment_templates.json'),
        '/var/task/functions/src/data/assessment_templates.json',
        'assessment_templates.json'
    ]
    
    for templates_path in possible_paths:
        try:
            print(f"Trying to load templates from: {templates_path}")
            with open(templates_path, 'r') as f:
                templates = json.load(f)
                print(f"Successfully loaded templates from: {templates_path}")
                return templates
        except FileNotFoundError:
            print(f"Templates not found at: {templates_path}")
            continue
        except Exception as e:
            print(f"Error loading templates from {templates_path}: {str(e)}")
            continue
    
    # If all paths fail, use the full templates inline
    print("Using inline templates as fallback")
    return {
        "bartender": {
            "questions_sequence": [
                "intro", "experience_1", "experience_2", "experience_3", 
                "knowledge_glassware_1", "knowledge_glassware_2", "knowledge_margarita", "knowledge_old_fashioned", 
                "knowledge_tools", "knowledge_service", "goodbye"
            ]
        },
        "banquet_server": {
            "questions_sequence": [
                "intro", "experience_1", "experience_2", "experience_3",
                "knowledge_setup", "knowledge_wine", "knowledge_clearing", "knowledge_scenario",
                "english_greeting", "english_complaint", "goodbye"
            ]
        },
        "host": {
            "questions_sequence": [
                "intro", "experience_1", "experience_2", "experience_3",
                "knowledge_pos", "knowledge_seating", "knowledge_phone", 
                "knowledge_reservation", "knowledge_walkin", "goodbye"
            ]
        }
    }

# Load assessment templates at module level
ASSESSMENT_TEMPLATES = load_assessment_templates()

def get_assessment_state(assessment_id, skill_type):
    """Get the current state of an assessment from S3."""
    import boto3
    import json
    
    s3_client = boto3.client('s3')
    bucket_name = os.environ.get('OUTPUT_BUCKET', 'innovativesol-gravywork-assets-dev')
    state_key = f"assessments/{assessment_id}/state.json"
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=state_key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        # Initialize new assessment state
        questions_sequence = ASSESSMENT_TEMPLATES.get(skill_type, {}).get('questions_sequence', ['intro', 'experience_1', 'goodbye'])
        initial_state = {
            'assessment_id': assessment_id,
            'skill_type': skill_type,
            'questions_sequence': questions_sequence,
            'current_question_index': 0,
            'responses': {},
            'status': 'in_progress',
            'created_at': datetime.utcnow().isoformat()
        }
        save_assessment_state(initial_state)
        return initial_state

def save_assessment_state(state):
    """Save assessment state to S3."""
    import boto3
    import json
    
    s3_client = boto3.client('s3')
    bucket_name = os.environ.get('OUTPUT_BUCKET', 'innovativesol-gravywork-assets-dev')
    state_key = f"assessments/{state['assessment_id']}/state.json"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=state_key,
            Body=json.dumps(state, indent=2),
            ContentType='application/json'
        )
        return True
    except Exception as e:
        print(f"Error saving assessment state: {str(e)}")
        return False

def get_current_question(state):
    """Get the current question for the assessment."""
    questions_sequence = state['questions_sequence']
    current_index = state['current_question_index']
    
    if current_index < len(questions_sequence):
        return questions_sequence[current_index]
    return None

def advance_to_next_question(state):
    """Advance to the next question in the sequence."""
    state['current_question_index'] += 1
    return state

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler function.
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Check if this is an HTTP API event (assessment webhook)
        if 'requestContext' in event and 'http' in event['requestContext']:
            return handle_http_request(event)
        
        # Otherwise, process as S3 event (original template functionality)
        return handle_s3_event(event, context)
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise

def handle_http_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle HTTP API requests for AI Skills Assessment."""
    try:
        path = event.get('rawPath', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
        
        logger.info(f"HTTP request - Path: {path}, Method: {method}")
        
        if path == '/initiate':
            return handle_initiate_assessment(event)
        elif path == '/webhook':
            return handle_initial_webhook(event)
        elif path == '/webhook/recording':
            return handle_recording_completion(event)
        elif path == '/webhook/gather':
            return handle_gather_response(event)
        else:
            # Default test response
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/xml'},
                'body': '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">🎉 GravyWork AI Skills Assessment is working!</Say>
    <Hangup/>
</Response>'''
            }
            
    except Exception as e:
        logger.error(f"HTTP request handler error: {str(e)}")
        return create_error_response(500, str(e))

def handle_initiate_assessment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment initiation requests."""
    try:
        # Check if Twilio is configured
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            return create_error_response(500, "Twilio credentials not configured")
            
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
        
        # Make Twilio call
        result = make_twilio_call(
            worker_phone=worker_phone,
            webhook_url=f"{TWILIO_WEBHOOK_URL}/webhook?assessment_id={assessment_id}&skill_type={skill_type}",
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

def make_twilio_call(worker_phone: str, webhook_url: str, assessment_id: str) -> Dict[str, Any]:
    """Make a call using Twilio API."""
    try:
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Ensure phone number is in correct E.164 format
        if not worker_phone.startswith('+'):
            worker_phone = '+' + worker_phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        
        logger.info(f"Making Twilio call to {worker_phone} for assessment {assessment_id}")
        logger.info(f"Using Twilio Account SID: {TWILIO_ACCOUNT_SID}")
        logger.info(f"From number: {TWILIO_PHONE_NUMBER}")
        
        call = client.calls.create(
            to=worker_phone,
            from_=TWILIO_PHONE_NUMBER,
            url=webhook_url,
            method='POST'
        )
        
        logger.info(f"Twilio call created successfully: {call.sid}")
        
        return {
            'success': True,
            'call_sid': call.sid,
            'status': call.status
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Twilio call error: {error_msg}")
        
        # Check for common Twilio trial account issues
        if "unverified" in error_msg.lower() and "trial accounts" in error_msg.lower():
            return {
                'success': False,
                'error': f"Phone number verification required. This Twilio account is in trial mode and can only call verified numbers. Please either: (1) Verify your phone number in the Twilio Console at https://console.twilio.com/us1/develop/phone-numbers/manage/verified, or (2) Upgrade to a paid Twilio account. Original error: {error_msg}"
            }
        else:
            return {
                'success': False,
                'error': error_msg
            }

def handle_initial_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle initial webhook call from Twilio - start multi-question assessment."""
    try:
        # Parse query parameters 
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_id = query_params.get('assessment_id', '')
        skill_type = query_params.get('skill_type', 'bartender')
        
        logger.info(f"Initial webhook - Assessment: {assessment_id}, Skill: {skill_type}")
        
        if not assessment_id:
            return create_twiml_response("Assessment ID missing. Please contact support.", hangup=True)
        
        # Get or initialize assessment state
        state = get_assessment_state(assessment_id, skill_type)
        current_question = get_current_question(state)
        
        logger.info(f"Starting question: {current_question} (index: {state['current_question_index']})")
        
        # Generate TwiML for the current question
        return generate_question_twiml(assessment_id, skill_type, current_question, state)
    
    except Exception as e:
        logger.error(f"Error in initial webhook: {str(e)}")
        return create_twiml_response("Sorry, there was an error. Please try again later.", hangup=True)

def generate_question_twiml(assessment_id, skill_type, question_key, state):
    """Generate TwiML for a specific question in the assessment."""
    if not question_key:
        # Assessment complete
        return generate_completion_twiml(assessment_id, skill_type)
    
    if skill_type in ASSESSMENT_TEMPLATES:
        # Use professional ElevenLabs audio files from S3
        question_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/{question_key}.mp3"
        
        if question_key == "intro":
            # For intro, no recording needed - just play and move to next question
            next_state = advance_to_next_question(state)
            save_assessment_state(next_state)
            next_question = get_current_question(next_state)
            
            if next_question:
                next_question_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/{next_question}.mp3"
                
                instructions_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/instructions.mp3"
                
                twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{question_url}</Play>
    <Pause length="1"/>
    <Play>{next_question_url}</Play>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={next_question}&amp;timeout=true" method="POST"/>
    <Play>{instructions_url}</Play>
    <Record timeout="120" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={next_question}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
            else:
                return generate_completion_twiml(assessment_id, skill_type)
        
        elif question_key == "goodbye":
            # Final message - no recording needed
            return generate_completion_twiml(assessment_id, skill_type)
        
        else:
            # Regular question - single recording with proper timeout handling
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{question_url}</Play>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={question_key}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
    
    else:
        # Fallback TwiML
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Hello! Welcome to the GravyWork skills assessment.</Say>
    <Pause length="1"/>
    <Say voice="Polly.Joanna">Please describe your experience. When you are finished speaking, press the pound key.</Say>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question=fallback" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/xml'},
        'body': twiml
    }

def handle_gather_response(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle gather response for star key repeat functionality."""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_id = query_params.get('assessment_id', '')
        skill_type = query_params.get('skill_type', 'bartender')
        current_question = query_params.get('question', '')
        
        # Parse Twilio form data from POST body
        body = event.get('body', '')
        logger.info(f"Gather response for assessment {assessment_id}, question: {current_question}")
        
        if body:
            # Check if body is base64 encoded
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            # Parse form data to check what key was pressed
            import urllib.parse
            parsed_body = urllib.parse.parse_qs(body)
            digits = parsed_body.get('Digits', [''])[0]
            
            logger.info(f"User pressed: {digits}")
            
            if digits == '*':
                # User wants to repeat the question - generate repeat TwiML without advancing state
                logger.info(f"Repeating question: {current_question}")
                question_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/{current_question}.mp3"
                
                instructions_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/instructions.mp3"
                
                repeat_twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{question_url}</Play>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={current_question}&amp;timeout=true" method="POST"/>
    <Play>{instructions_url}</Play>
    <Record timeout="120" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={current_question}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/xml'},
                    'body': repeat_twiml
                }
            else:
                # Continue to recording for any other key or no key
                question_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/{current_question}.mp3"
                twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={current_question}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/xml'},
                    'body': twiml
                }
        
        # If no digits, continue to recording
        question_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/{current_question}.mp3"
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record timeout="5" transcribe="false" maxLength="120" finishOnKey="#" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={current_question}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/xml'},
            'body': twiml
        }
        
    except Exception as e:
        logger.error(f"Error in gather response: {str(e)}")
        return create_twiml_response("Please continue with your answer.", hangup=False)

def handle_recording_completion(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle recording completion webhook from Twilio - multi-question flow."""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_id = query_params.get('assessment_id', '')
        skill_type = query_params.get('skill_type', 'bartender')
        current_question = query_params.get('question', '')
        
        # Parse Twilio form data from POST body
        body = event.get('body', '')
        
        # Check if body is base64 encoded
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse form data
        import urllib.parse
        parsed_body = urllib.parse.parse_qs(body)
        digits = parsed_body.get('Digits', [''])[0]
        recording_url = parsed_body.get('RecordingUrl', [''])[0]
        recording_duration = parsed_body.get('RecordingDuration', ['0'])[0]
        recording_duration_int = int(recording_duration) if recording_duration.isdigit() else 0
        
        # If recording duration equals timeout (5 seconds) and no digits pressed, treat as timeout
        # This happens when user stays silent and Twilio times out after 5 seconds
        is_timeout = recording_duration_int == 5 and not digits
        
        logger.info(f"Recording completed for assessment {assessment_id}, question: {current_question}, timeout: {is_timeout}")
        
        # Get current assessment state
        state = get_assessment_state(assessment_id, skill_type)
        
        # Check if star key was pressed to repeat question
        if digits == '*':
            logger.info(f"Star key pressed during recording - repeating question: {current_question}")
            # Return the same question without saving or advancing
            return generate_question_twiml(assessment_id, skill_type, current_question, state)
        
        # If this is a timeout (silence), play instructions and continue recording
        if is_timeout:
            logger.info(f"Recording timeout - playing instructions and continuing recording for question: {current_question}")
            # Return TwiML to play instructions and continue recording
            instructions_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/instructions.mp3"
            
            timeout_twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{instructions_url}</Play>
    <Record timeout="120" transcribe="false" maxLength="120" finishOnKey="#*" action="{TWILIO_WEBHOOK_URL}/webhook/recording?assessment_id={assessment_id}&amp;skill_type={skill_type}&amp;question={current_question}" method="POST"/>
    <Say voice="Polly.Joanna">I didn't receive your response. Please try again.</Say>
    <Hangup/>
</Response>'''
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/xml'},
                'body': timeout_twiml
            }
        
        # Save the recording URL for this question (only if not timeout)
        if recording_url and current_question:
            state['responses'][current_question] = {
                'recording_url': recording_url,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.info(f"Saved response for question {current_question}")
        
        # Advance to next question (only if not a timeout)
        next_state = advance_to_next_question(state)
        next_question = get_current_question(next_state)
        
        logger.info(f"Next question: {next_question} (index: {next_state['current_question_index']})")
        
        # Save updated state
        save_assessment_state(next_state)
        
        # Generate TwiML for next question or completion
        return generate_question_twiml(assessment_id, skill_type, next_question, next_state)
        
    except Exception as e:
        logger.error(f"Error in recording completion: {str(e)}")
        return create_twiml_response("Thank you for your response. We're processing your assessment.", hangup=True)

def generate_completion_twiml(assessment_id, skill_type):
    """Generate completion TwiML with professional ElevenLabs audio."""
    try:
        if skill_type in ASSESSMENT_TEMPLATES:
            goodbye_url = f"https://innovativesol-gravywork-assets-dev.s3.us-east-1.amazonaws.com/audio/{skill_type}/goodbye.mp3"
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{goodbye_url}</Play>
    <Hangup/>
</Response>'''
        else:
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Thank you for completing the assessment. We will contact you soon.</Say>
    <Hangup/>
</Response>'''
        
        # Mark assessment as completed and trigger analysis
        try:
            state = get_assessment_state(assessment_id, skill_type)
            state['status'] = 'completed'
            state['completed_at'] = datetime.utcnow().isoformat()
            save_assessment_state(state)
            logger.info(f"Assessment {assessment_id} marked as completed")
            
            # Trigger async assessment analysis
            import boto3
            lambda_client = boto3.client('lambda')
            
            lambda_client.invoke(
                FunctionName="gravywork-dev-assessment-processor",
                InvocationType='Event',  # Async invocation
                Payload=json.dumps({
                    'assessment_id': assessment_id,
                    'skill_type': skill_type
                })
            )
            
            logger.info(f"Triggered assessment analysis for {assessment_id} ({skill_type})")
            
        except Exception as e:
            logger.error(f"Failed to complete assessment processing: {str(e)}")
            # Continue with TwiML response even if analysis trigger fails
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/xml'},
            'body': twiml
        }
        
    except Exception as e:
        logger.error(f"Error in completion TwiML: {str(e)}")
        return create_twiml_response("Thank you for completing the assessment.", hangup=True)

def handle_s3_event(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Handle original S3 events from the SST template."""
    try:
        logger.info(f"Processing S3 event for project in environment: {environment}")
        
        # Process S3 events (original template functionality)
        if 'Records' in event:
            for record in event['Records']:
                if record['eventSource'] == 'aws:s3':
                    bucket = record['s3']['bucket']['name']
                    key = record['s3']['object']['key']
                    logger.info(f"Processing S3 object: s3://{bucket}/{key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed S3 event',
                'environment': environment
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing S3 event: {str(e)}")
        raise

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
