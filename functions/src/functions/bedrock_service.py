from typing import Dict, Any, Optional, List

import boto3
from botocore.config import Config

from ..config.llm_config import get_default_llm_config, create_inference_config, LLMConfig, get_llm_config


class BedrockService:
    """
    AWS Bedrock service wrapper with configurable LLM settings.
    
    Uses centralized LLM configuration for consistent model parameters
    across the application. Defaults to Claude Sonnet 4 global inference profile.
    """

    def __init__(self, llm_config: Optional[LLMConfig] = None) -> None:
        """
        Initialize Bedrock service with LLM configuration.
        
        Args:
            llm_config: Optional LLM configuration. If None, uses default Claude Sonnet 4.
        """
        self.config = llm_config or get_default_llm_config()
        
        client_config = Config(
            connect_timeout=20,
            read_timeout=60,
            retries={"max_attempts": 2, "mode": "standard"},
        )
        
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.config.region,
            config=client_config,
        )

    @classmethod
    def with_config(cls, config_name: str = "claude-sonnet-4") -> "BedrockService":
        """
        Create BedrockService with named configuration.
        
        Args:
            config_name: Name of the LLM configuration to use
            
        Returns:
            BedrockService instance with specified configuration
        """
        llm_config = get_llm_config(config_name)
        return cls(llm_config)

    def invoke_converse_api(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        override_model_id: Optional[str] = None,
        override_inference_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke Bedrock Converse API with configured model and parameters.
        
        Args:
            messages: List of messages for the conversation
            system_prompt: Optional system prompt
            override_model_id: Override the configured model ID for this call
            override_inference_config: Override inference configuration for this call
            
        Returns:
            Bedrock API response
        """
        # Use configured model ID unless overridden
        model_id = override_model_id or self.config.model_id
        
        # Use configured inference settings unless overridden
        inference_config = override_inference_config or create_inference_config(self.config)
        
        args: Dict[str, Any] = {
            'modelId': model_id,
            'messages': messages,
            'inferenceConfig': inference_config,
        }
        
        if system_prompt:
            args['system'] = [{"text": system_prompt}]
            
        return self.bedrock_runtime.converse(**args)

    def simple_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Simple text generation with configured model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
        
        response = self.invoke_converse_api(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Extract text from response
        if 'output' in response and 'message' in response['output']:
            content = response['output']['message']['content']
            if content and len(content) > 0 and 'text' in content[0]:
                return content[0]['text']
        
        return ""

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dictionary with current model configuration details
        """
        return {
            'model_id': self.config.model_id,
            'temperature': self.config.temperature,
            'region': self.config.region,
            'max_tokens': self.config.max_tokens,
            'top_p': self.config.top_p,
            'top_k': self.config.top_k,
            'stop_sequences': self.config.stop_sequences,
        }
