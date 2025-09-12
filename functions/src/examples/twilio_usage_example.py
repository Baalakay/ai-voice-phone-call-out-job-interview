"""
Example usage of the TwilioService for AI Skills Assessment.

This file demonstrates how to use the TwilioService with the Twilio
configuration system. Remove this file if not needed.
"""

from ..functions.twilio_service import TwilioService
from ..config.twilio_config import get_twilio_config


def example_development_call():
    """Example assessment call using development (test) credentials."""
    
    # Create service with development configuration (no charges)
    twilio = TwilioService.for_development()
    
    # Initiate assessment call (uses configured number: +14722368895)
    result = twilio.initiate_assessment_call(
        worker_phone="+15551234567",  # Test number for development
        webhook_url="https://your-api-gateway-url.com/dev/twilio/webhook",
        assessment_id="test_bartender_001"
    )
    
    print(f"Call initiation result: {result}")
    print(f"Service info: {twilio.get_service_info()}")


def example_production_call():
    """Example assessment call using production credentials."""
    
    # Create service with production configuration (real charges)
    twilio = TwilioService.for_production()
    
    result = twilio.initiate_assessment_call(
        worker_phone="+15551234567",
        webhook_url="https://your-api-gateway-url.com/prod/twilio/webhook",
        assessment_id="prod_bartender_001"
        # Uses configured Gravy Work number: (472) 236-8895
    )
    
    print(f"Production call result: {result}")


def example_twiml_generation():
    """Example TwiML generation for different assessment stages."""
    
    twilio = TwilioService.for_development()
    
    # Generate intro TwiML
    intro_twiml = twilio.generate_intro_twiml(
        audio_url="https://your-s3-bucket.s3.amazonaws.com/audio/bartender/intro.mp3",
        first_question_url="https://your-api-gateway-url.com/dev/question/1"
    )
    print("Intro TwiML:")
    print(intro_twiml)
    print()
    
    # Generate question TwiML
    question_twiml = twilio.generate_question_twiml(
        audio_url="https://your-s3-bucket.s3.amazonaws.com/audio/bartender/experience_question.mp3",
        next_action_url="https://your-api-gateway-url.com/dev/process_response/1",
        question_number=1
    )
    print("Question 1 TwiML:")
    print(question_twiml)
    print()
    
    # Generate completion TwiML
    completion_twiml = twilio.generate_completion_twiml(
        audio_url="https://your-s3-bucket.s3.amazonaws.com/audio/bartender/goodbye.mp3"
    )
    print("Completion TwiML:")
    print(completion_twiml)


def example_call_tracking():
    """Example of tracking call status and retrieving recordings."""
    
    twilio = TwilioService.for_development()
    
    # Get call details (use actual call SID from previous call)
    call_sid = "CA1234567890abcdef1234567890abcdef"
    call_details = twilio.get_call_details(call_sid)
    print(f"Call details: {call_details}")
    
    # Get recording URL
    recording_url = twilio.get_call_recording_url(call_sid)
    if recording_url:
        print(f"Recording available at: {recording_url}")
    else:
        print("No recording available yet")


def example_in_lambda_webhook_handler():
    """Example of how to use TwilioService in webhook Lambda handler."""
    
    def lambda_webhook_handler(event, context):
        """Lambda handler for Twilio webhooks."""
        
        # Parse webhook data
        assessment_id = event.get('queryStringParameters', {}).get('assessment_id')
        call_sid = event.get('body', {}).get('CallSid')
        
        # Initialize Twilio service
        environment = event.get('requestContext', {}).get('stage', 'dev')
        twilio_env = "production" if environment == "prod" else "development"
        twilio = TwilioService(environment=twilio_env)
        
        # Determine which question to ask based on current step
        question_step = event.get('body', {}).get('question_step', '1')
        
        if question_step == '1':
            # First question: Experience
            twiml = twilio.generate_question_twiml(
                audio_url="https://s3-bucket/audio/bartender/experience.mp3",
                next_action_url=f"https://api-url/{environment}/question/2?assessment_id={assessment_id}",
                question_number=1
            )
        elif question_step == '2':
            # Second question: Customer Service
            twiml = twilio.generate_question_twiml(
                audio_url="https://s3-bucket/audio/bartender/customer_service.mp3",
                next_action_url=f"https://api-url/{environment}/complete?assessment_id={assessment_id}",
                question_number=2
            )
        else:
            # Assessment complete
            twiml = twilio.generate_completion_twiml(
                audio_url="https://s3-bucket/audio/bartender/goodbye.mp3"
            )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/xml'},
            'body': twiml
        }


def example_complete_assessment_flow():
    """Example showing complete assessment workflow."""
    
    print("=== Complete AI Skills Assessment Flow ===")
    
    # Step 1: Initialize assessment
    twilio = TwilioService.for_development()
    assessment_id = "demo_bartender_123"
    
    # Step 2: Start the call (using Gravy Work number: (472) 236-8895)
    call_result = twilio.initiate_assessment_call(
        worker_phone="+15551234567",
        webhook_url=f"https://api-url/dev/webhook?assessment_id={assessment_id}",
        assessment_id=assessment_id
    )
    
    if call_result['success']:
        print(f"✅ Call initiated: {call_result['call_sid']}")
        
        # Step 3: Call connects, webhook receives intro request
        intro_twiml = twilio.generate_intro_twiml(
            audio_url="https://s3-bucket/audio/bartender/intro.mp3",
            first_question_url=f"https://api-url/dev/question/1?assessment_id={assessment_id}"
        )
        print("📞 Intro TwiML generated")
        
        # Step 4: First question
        q1_twiml = twilio.generate_question_twiml(
            audio_url="https://s3-bucket/audio/bartender/experience.mp3",
            next_action_url=f"https://api-url/dev/process/1?assessment_id={assessment_id}",
            question_number=1
        )
        print("❓ Question 1 TwiML generated")
        
        # Step 5: Process first response (this would trigger Bedrock analysis)
        print("🤖 First response would be processed by BedrockService")
        
        # Step 6: Second question
        q2_twiml = twilio.generate_question_twiml(
            audio_url="https://s3-bucket/audio/bartender/customer_service.mp3", 
            next_action_url=f"https://api-url/dev/complete?assessment_id={assessment_id}",
            question_number=2
        )
        print("❓ Question 2 TwiML generated")
        
        # Step 7: Final completion
        completion_twiml = twilio.generate_completion_twiml(
            audio_url="https://s3-bucket/audio/bartender/goodbye.mp3"
        )
        print("👋 Assessment completion TwiML generated")
        
        print(f"✅ Complete assessment flow ready for {assessment_id}")
        
    else:
        print(f"❌ Call failed: {call_result['error']}")


if __name__ == "__main__":
    # Run examples
    print("=== Development Call Example ===")
    example_development_call()
    
    print("\n=== TwiML Generation Examples ===")
    example_twiml_generation()
    
    print("\n=== Complete Assessment Flow ===")
    example_complete_assessment_flow()
