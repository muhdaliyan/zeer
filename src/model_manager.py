"""
Model management module for zeer CLI.

This module provides functions for fetching and displaying AI models
from providers.
"""

from typing import List
from src.provider_base import AIProvider, Model


async def fetch_models(provider: AIProvider) -> List[Model]:
    """
    Fetch the list of available models from a provider.
    
    Args:
        provider: The AIProvider instance to fetch models from
        
    Returns:
        List of Model objects representing available models
        
    Raises:
        Exception: If the API request fails
    """
    models = await provider.get_models()
    return models


def display_models(models: List[Model]) -> str:
    """
    Format a list of models for display in the terminal.
    
    Handles empty model lists gracefully by returning an appropriate message.
    For non-empty lists, formats each model with its name and available metadata.
    
    Args:
        models: List of Model objects to display
        
    Returns:
        Formatted string representation of the models
    """
    if not models:
        return "No models available from this provider."
    
    output_lines = []
    output_lines.append("\nAvailable Models:")
    output_lines.append("-" * 60)
    
    for idx, model in enumerate(models, start=1):
        # Display model number, ID, and name
        model_line = f"{idx}. {model.name}"
        
        # Add description if available
        if model.description:
            model_line += f"\n   Description: {model.description}"
        
        # Add context window if available
        if model.context_window:
            model_line += f"\n   Context Window: {model.context_window:,} tokens"
        
        output_lines.append(model_line)
    
    output_lines.append("-" * 60)
    
    return "\n".join(output_lines)
