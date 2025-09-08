"""
LLM Configuration for AWS Bedrock

Central configuration for language model settings including model ARNs,
temperature, region, and other inference parameters.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for LLM inference parameters."""
    model_id: str
    temperature: float
    region: str
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[list] = None


# Default LLM configurations
DEFAULT_CONFIGS = {
    "claude-sonnet-4": LLMConfig(
        model_id="global.anthropic.claude-sonnet-4-20250514-v1:0",
        temperature=0.7,
        region="us-east-1",
        # Use model defaults for token limits
        max_tokens=None,
        top_p=0.9,
    ),
    
    "claude-sonnet-3": LLMConfig(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        temperature=0.7,
        region="us-east-1",
        max_tokens=None,
        top_p=0.9,
    ),
    
    "claude-haiku-3": LLMConfig(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        temperature=0.5,
        region="us-east-1",
        max_tokens=None,
        top_p=0.9,
    ),
}


def get_llm_config(config_name: str = "claude-sonnet-4") -> LLMConfig:
    """
    Get LLM configuration by name with environment variable overrides.
    
    Args:
        config_name: Name of the configuration to load (default: claude-sonnet-4)
        
    Returns:
        LLMConfig: Configuration object with resolved values
        
    Environment Variable Overrides:
        LLM_MODEL_ID: Override the model ID
        LLM_TEMPERATURE: Override the temperature (float)
        LLM_REGION: Override the AWS region
        LLM_MAX_TOKENS: Override max tokens (int, optional)
        LLM_TOP_P: Override top_p (float, optional)
        LLM_TOP_K: Override top_k (int, optional)
    """
    if config_name not in DEFAULT_CONFIGS:
        raise ValueError(f"Unknown LLM config: {config_name}. Available: {list(DEFAULT_CONFIGS.keys())}")
    
    base_config = DEFAULT_CONFIGS[config_name]
    
    # Create a new config with environment overrides
    return LLMConfig(
        model_id=os.environ.get("LLM_MODEL_ID", base_config.model_id),
        temperature=float(os.environ.get("LLM_TEMPERATURE", base_config.temperature)),
        region=os.environ.get("LLM_REGION", base_config.region),
        max_tokens=_get_optional_int_env("LLM_MAX_TOKENS", base_config.max_tokens),
        top_p=_get_optional_float_env("LLM_TOP_P", base_config.top_p),
        top_k=_get_optional_int_env("LLM_TOP_K", base_config.top_k),
        stop_sequences=_get_optional_list_env("LLM_STOP_SEQUENCES", base_config.stop_sequences),
    )


def _get_optional_int_env(env_var: str, default: Optional[int]) -> Optional[int]:
    """Get optional integer from environment variable."""
    value = os.environ.get(env_var)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_optional_float_env(env_var: str, default: Optional[float]) -> Optional[float]:
    """Get optional float from environment variable."""
    value = os.environ.get(env_var)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_optional_list_env(env_var: str, default: Optional[list]) -> Optional[list]:
    """Get optional list from environment variable (comma-separated)."""
    value = os.environ.get(env_var)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def create_inference_config(config: LLMConfig) -> Dict[str, Any]:
    """
    Create inference configuration dictionary for Bedrock API calls.
    
    Args:
        config: LLM configuration object
        
    Returns:
        Dict containing inference parameters for Bedrock
    """
    inference_config = {
        "temperature": config.temperature,
    }
    
    # Only add optional parameters if they're specified
    if config.max_tokens is not None:
        inference_config["maxTokens"] = config.max_tokens
    
    if config.top_p is not None:
        inference_config["topP"] = config.top_p
        
    if config.top_k is not None:
        inference_config["topK"] = config.top_k
        
    if config.stop_sequences is not None:
        inference_config["stopSequences"] = config.stop_sequences
    
    return inference_config


# Convenience function to get the default config
def get_default_llm_config() -> LLMConfig:
    """Get the default LLM configuration (Claude Sonnet 4)."""
    return get_llm_config("claude-sonnet-4")
