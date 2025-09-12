
"""
Twilio Configuration for AI Skills Assessment
Central configuration for Twilio voice calling and speech recognition.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TwilioConfig:
    """Configuration for Twilio voice services."""
    account_sid: str
    auth_token: str
    api_key_sid: Optional[str] = None
    api_key_secret: Optional[str] = None
    voice_webhook_url: str = ""
    from_phone_number: str = "+14722368895"  # Gravy Work Twilio number: (472) 236-8895
    speech_timeout: str = "4"  # Default 4 seconds for thoughtful responses
    speech_model: str = "phone_call"
    profanity_filter: bool = False


# Default configurations for different environments
DEFAULT_CONFIGS = {
    "development": TwilioConfig(
        account_sid="AC4e658dd5cf5c6e36514e5bae7f4c1bf7",  # Your Live Account SID
        auth_token="db19869a6764956183410a5169a41ab0",  # Your Auth Token  
        from_phone_number="+14722368895",  # Your Twilio number: (472) 236-8895
        speech_timeout="4",
    ),
    
    "production": TwilioConfig(
        account_sid="AC4e658dd5cf5c6e36514e5bae7f4c1bf7",  # Your Live Account SID
        auth_token="db19869a6764956183410a5169a41ab0",  # Your Auth Token 
        api_key_sid="SKe44f958c6a509ba4bc6575e0977267a3",  # Your API Key (more secure)
        api_key_secret="425sxqNn0UtBXEKLk62rm6iF72wDoRon",  # Your API Secret
        from_phone_number="+14722368895",  # Your Twilio number: (472) 236-8895
        speech_timeout="4",
    ),
}


def get_twilio_config(environment: str = "development") -> TwilioConfig:
    """
    Get Twilio configuration with environment variable overrides.
    
    Args:
        environment: "development" or "production"
        
    Returns:
        TwilioConfig with resolved values
        
    Environment Variable Overrides:
        TWILIO_ACCOUNT_SID: Override account SID
        TWILIO_AUTH_TOKEN: Override auth token (required)
        TWILIO_API_KEY_SID: Override API key SID
        TWILIO_API_KEY_SECRET: Override API key secret
        TWILIO_WEBHOOK_URL: Override webhook URL
        TWILIO_FROM_NUMBER: Override from phone number
        TWILIO_SPEECH_TIMEOUT: Override speech timeout
    """
    if environment not in DEFAULT_CONFIGS:
        raise ValueError(f"Unknown Twilio environment: {environment}. Available: {list(DEFAULT_CONFIGS.keys())}")
    
    base_config = DEFAULT_CONFIGS[environment]
    
    return TwilioConfig(
        account_sid=os.environ.get("TWILIO_ACCOUNT_SID", base_config.account_sid),
        auth_token=os.environ.get("TWILIO_AUTH_TOKEN", base_config.auth_token),
        api_key_sid=os.environ.get("TWILIO_API_KEY_SID", base_config.api_key_sid),
        api_key_secret=os.environ.get("TWILIO_API_KEY_SECRET", base_config.api_key_secret),
        voice_webhook_url=os.environ.get("TWILIO_WEBHOOK_URL", "https://eih1khont2.execute-api.us-east-1.amazonaws.com/webhook"),
        from_phone_number=os.environ.get("TWILIO_FROM_NUMBER", base_config.from_phone_number),
        speech_timeout=os.environ.get("TWILIO_SPEECH_TIMEOUT", base_config.speech_timeout),
        speech_model=os.environ.get("TWILIO_SPEECH_MODEL", base_config.speech_model),
        profanity_filter=os.environ.get("TWILIO_PROFANITY_FILTER", "false").lower() == "true",
    )


def get_development_config() -> TwilioConfig:
    """Get development Twilio configuration (test credentials)."""
    return get_twilio_config("development")


def get_production_config() -> TwilioConfig:
    """Get production Twilio configuration (live credentials with API key).""" 
    return get_twilio_config("production")