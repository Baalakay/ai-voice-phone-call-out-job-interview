"""
Example usage of the configured BedrockService.

This file demonstrates how to use the BedrockService with the new
LLM configuration system. Remove this file if not needed.
"""

from ..functions.bedrock_service import BedrockService
from ..config.llm_config import get_llm_config


def example_basic_usage():
    """Example of basic BedrockService usage with default Claude Sonnet 4."""
    
    # Create service with default configuration (Claude Sonnet 4)
    bedrock = BedrockService()
    
    # Simple text generation
    response = bedrock.simple_generate(
        prompt="Explain quantum computing in simple terms.",
        system_prompt="You are a helpful technical assistant."
    )
    
    print(f"Response: {response}")
    print(f"Model info: {bedrock.get_model_info()}")


def example_with_different_model():
    """Example using a different model configuration."""
    
    # Use Claude Haiku for faster responses
    bedrock = BedrockService.with_config("claude-haiku-3")
    
    response = bedrock.simple_generate(
        prompt="What is the weather like today?",
        system_prompt="You are a helpful assistant."
    )
    
    print(f"Haiku response: {response}")


def example_with_custom_config():
    """Example with custom LLM configuration."""
    
    # Get base config and modify it
    custom_config = get_llm_config("claude-sonnet-4")
    custom_config.temperature = 0.1  # More deterministic
    
    bedrock = BedrockService(custom_config)
    
    response = bedrock.simple_generate(
        prompt="Write a formal business email greeting.",
        system_prompt="You are a professional business communications expert."
    )
    
    print(f"Custom config response: {response}")


def example_conversation():
    """Example of a multi-turn conversation."""
    
    bedrock = BedrockService()
    
    messages = [
        {
            "role": "user",
            "content": [{"text": "What's the capital of France?"}]
        },
        {
            "role": "assistant",
            "content": [{"text": "The capital of France is Paris."}]
        },
        {
            "role": "user",
            "content": [{"text": "What's the population of that city?"}]
        }
    ]
    
    response = bedrock.invoke_converse_api(
        messages=messages,
        system_prompt="You are a knowledgeable geography assistant."
    )
    
    # Extract response text
    if 'output' in response and 'message' in response['output']:
        content = response['output']['message']['content']
        if content and len(content) > 0 and 'text' in content[0]:
            print(f"Conversation response: {content[0]['text']}")


def example_in_lambda_handler():
    """Example of how to use in your Lambda handler."""
    
    def lambda_handler(event, context):
        # Initialize with default config
        bedrock = BedrockService()
        
        # Process some extracted text (e.g., from Textract)
        extracted_text = event.get('extracted_text', '')
        
        if extracted_text:
            analysis = bedrock.simple_generate(
                prompt=f"Analyze this document and provide a summary:\n\n{extracted_text}",
                system_prompt="You are a document analysis expert. Provide concise, accurate summaries."
            )
            
            return {
                'statusCode': 200,
                'body': {
                    'analysis': analysis,
                    'model_used': bedrock.get_model_info()['model_id']
                }
            }
        
        return {
            'statusCode': 400,
            'body': {'error': 'No text provided for analysis'}
        }


if __name__ == "__main__":
    # Run examples
    print("=== Basic Usage ===")
    example_basic_usage()
    
    print("\n=== Different Model ===")
    example_with_different_model()
    
    print("\n=== Custom Config ===")
    example_with_custom_config()
    
    print("\n=== Conversation ===")
    example_conversation()
