"""
Twilio Service for AI Skills Assessment

Twilio voice calling service wrapper with configurable settings.
Uses centralized Twilio configuration similar to BedrockService pattern.
"""

import os
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.base.exceptions import TwilioRestException

from ..config.twilio_config import get_twilio_config, TwilioConfig


class TwilioService:
    """
    Twilio voice service wrapper with configurable settings.
    
    Uses centralized Twilio configuration for consistent voice calling
    across the application. Defaults to development (test) credentials.
    """

    def __init__(self, twilio_config: Optional[TwilioConfig] = None, environment: str = "development") -> None:
        """
        Initialize Twilio service with configuration.
        
        Args:
            twilio_config: Optional Twilio configuration. If None, uses environment default.
            environment: "development" (test) or "production" (live) credentials
        """
        self.config = twilio_config or get_twilio_config(environment)
        
        # Initialize Twilio client with appropriate authentication
        if self.config.api_key_sid and self.config.api_key_secret:
            # Production: Use API Key authentication (more secure)
            self.client = Client(
                self.config.api_key_sid,
                self.config.api_key_secret,
                self.config.account_sid
            )
        else:
            # Development: Use Account SID + Auth Token
            self.client = Client(self.config.account_sid, self.config.auth_token)

    @classmethod
    def for_production(cls) -> "TwilioService":
        """Create TwilioService with production credentials."""
        return cls(environment="production")

    @classmethod
    def for_development(cls) -> "TwilioService":
        """Create TwilioService with development (test) credentials."""
        return cls(environment="development")

    def initiate_assessment_call(
        self,
        worker_phone: str,
        webhook_url: str,
        assessment_id: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an assessment call to a worker.
        
        Args:
            worker_phone: Worker's phone number (e.g., "+1234567890")
            webhook_url: URL to receive TwiML responses
            assessment_id: Unique identifier for this assessment
            from_number: Optional override for Twilio number (uses config default: +14722368895)
            
        Returns:
            Dict with call information and status
        """
        try:
            # Use provided number or default from config
            calling_number = from_number or self.config.from_phone_number
            
            call = self.client.calls.create(
                to=worker_phone,
                from_=calling_number,
                url=f"{webhook_url}?assessment_id={assessment_id}",
                method="POST",
                record=True,  # Record the call for transcript backup
                # Optional: Set timeout and other call parameters
                timeout=30,  # Ring for 30 seconds max
                status_callback=f"{webhook_url}/status",  # Optional status updates
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method="POST"
            )
            
            return {
                'success': True,
                'call_sid': call.sid,
                'assessment_id': assessment_id,
                'status': 'initiated',
                'worker_phone': worker_phone
            }
            
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code,
                'assessment_id': assessment_id
            }

    def generate_question_twiml(
        self,
        audio_url: str,
        next_action_url: str,
        question_number: int = 1
    ) -> str:
        """
        Generate TwiML for playing a question and collecting speech response.
        
        Args:
            audio_url: S3 URL to pre-recorded question audio
            next_action_url: URL to POST speech results to
            question_number: Question number for timeout adjustment
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        # Adjust speech timeout based on question complexity
        timeout = self.config.speech_timeout
        if question_number == 1:
            timeout = "5"  # Longer for first question (experience/background)
        
        # Create gather element for speech collection
        gather = Gather(
            input='speech',
            speech_timeout=timeout,
            speech_model=self.config.speech_model,
            profanity_filter=self.config.profanity_filter,
            action=next_action_url,
            method='POST'
        )
        
        # Play the pre-recorded question
        gather.play(audio_url)
        response.append(gather)
        
        # Fallback if no response received
        response.say("I didn't receive your response. Let me try the next question.")
        
        return str(response)

    def generate_intro_twiml(self, audio_url: str, first_question_url: str) -> str:
        """Generate TwiML for assessment introduction."""
        response = VoiceResponse()
        
        # Play intro message
        response.play(audio_url)
        
        # Small pause before first question
        response.pause(length=1)
        
        # Redirect to first question
        response.redirect(first_question_url)
        
        return str(response)

    def generate_completion_twiml(self, audio_url: str) -> str:
        """Generate TwiML for assessment completion."""
        response = VoiceResponse()
        
        # Play completion message
        response.play(audio_url)
        
        # Hang up
        response.hangup()
        
        return str(response)

    def get_call_details(self, call_sid: str) -> Dict[str, Any]:
        """
        Get details about a specific call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Dict with call details
        """
        try:
            call = self.client.calls.get(call_sid)
            return {
                'success': True,
                'call_sid': call_sid,
                'status': call.status,
                'duration': call.duration,
                'from_': call.from_,
                'to': call.to,
                'direction': call.direction,
                'answered_by': call.answered_by,
                'price': call.price,
                'price_unit': call.price_unit
            }
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'call_sid': call_sid
            }

    def get_call_recording_url(self, call_sid: str) -> Optional[str]:
        """
        Get recording URL for a completed call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Recording URL if available, None otherwise
        """
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)
            if recordings:
                # Return the most recent recording URL
                return f"https://api.twilio.com{recordings[0].uri.replace('.json', '.mp3')}"
        except TwilioRestException:
            pass
        return None

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about current Twilio service configuration.
        
        Returns:
            Dictionary with current service configuration details
        """
        return {
            'account_sid': self.config.account_sid,
            'using_api_key': bool(self.config.api_key_sid),
            'speech_timeout': self.config.speech_timeout,
            'speech_model': self.config.speech_model,
            'profanity_filter': self.config.profanity_filter,
            'webhook_url': self.config.voice_webhook_url
        }
