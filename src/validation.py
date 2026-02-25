"""Input validation module for zeer CLI.

This module provides validation functions for user inputs throughout the application.
"""

from typing import List, Optional


def validate_provider_selection(user_input: str, valid_providers: List[str]) -> bool:
    """Validate that user input matches one of the supported providers.
    
    Args:
        user_input: The user's provider selection input
        valid_providers: List of valid provider names
    
    Returns:
        True if the input matches a valid provider (case-insensitive), False otherwise
    
    Requirements: 2.2
    - Validates selection is one of the supported providers
    - Rejects all other inputs
    """
    if not user_input:
        return False
    
    # Normalize input for case-insensitive comparison
    normalized_input = user_input.strip().lower()
    normalized_providers = [p.lower() for p in valid_providers]
    
    return normalized_input in normalized_providers


def validate_api_key(key: str) -> bool:
    """Validate that an API key is non-empty and not just whitespace.
    
    Args:
        key: The API key string to validate
    
    Returns:
        True if the key is valid (non-empty and contains non-whitespace), False otherwise
    
    Requirements: 3.3
    - Rejects empty strings
    - Rejects strings containing only whitespace characters
    """
    if not key:
        return False
    
    # Check if the key contains any non-whitespace characters
    return len(key.strip()) > 0


def validate_model_selection(user_input: str, available_models: List[str]) -> bool:
    """Validate that user input matches one of the available models.
    
    Args:
        user_input: The user's model selection input
        available_models: List of available model IDs or names
    
    Returns:
        True if the input matches an available model (case-insensitive), False otherwise
    
    Requirements: 5.2
    - Validates selection is from the available models
    - Rejects inputs that don't match available models
    """
    if not user_input:
        return False
    
    # Normalize input for case-insensitive comparison
    normalized_input = user_input.strip().lower()
    normalized_models = [m.lower() for m in available_models]
    
    return normalized_input in normalized_models
