"""
Error handling module for zeer CLI.

This module provides centralized error handling functions for network errors,
API errors, authentication errors, and determines whether errors are recoverable.
"""

import requests
from typing import Tuple, Optional


def handle_network_error(error: Exception) -> Tuple[str, bool]:
    """
    Handle network-related errors with user-friendly messages.
    
    Args:
        error: The exception that occurred during network operation
        
    Returns:
        Tuple of (error_message, is_recoverable)
    """
    if isinstance(error, requests.exceptions.Timeout):
        return (
            "Connection timed out. Please check your internet connection and try again.",
            True
        )
    elif isinstance(error, requests.exceptions.ConnectionError):
        return (
            "Unable to connect to the server. Please check your internet connection.",
            True
        )
    elif isinstance(error, requests.exceptions.TooManyRedirects):
        return (
            "Too many redirects. The server configuration may be incorrect.",
            False
        )
    elif isinstance(error, requests.exceptions.RequestException):
        return (
            f"Network error occurred: {str(error)}",
            True
        )
    else:
        return (
            f"Unexpected network error: {str(error)}",
            False
        )


def handle_api_error(error: requests.exceptions.HTTPError) -> Tuple[str, bool]:
    """
    Handle API-specific errors with user-friendly messages.
    
    Args:
        error: The HTTPError that occurred during API operation
        
    Returns:
        Tuple of (error_message, is_recoverable)
    """
    status_code = error.response.status_code if error.response else None
    
    if status_code == 400:
        return (
            "Invalid request. Please check your input and try again.",
            True
        )
    elif status_code == 401:
        return handle_auth_error(error)
    elif status_code == 403:
        return (
            "Access forbidden. Your API key may not have the required permissions.",
            False
        )
    elif status_code == 404:
        return (
            "Resource not found. The requested endpoint may not exist.",
            False
        )
    elif status_code == 429:
        return (
            "Rate limit exceeded. Please wait a moment before trying again.",
            True
        )
    elif status_code and 500 <= status_code < 600:
        return (
            f"Server error ({status_code}). The provider's service may be experiencing issues. Please try again later.",
            True
        )
    else:
        return (
            f"API error occurred: {str(error)}",
            True
        )


def handle_auth_error(error: Exception) -> Tuple[str, bool]:
    """
    Handle authentication-related errors with user-friendly messages.
    
    Args:
        error: The exception that occurred during authentication
        
    Returns:
        Tuple of (error_message, is_recoverable)
    """
    if isinstance(error, requests.exceptions.HTTPError):
        if error.response and error.response.status_code == 401:
            return (
                "Authentication failed. Your API key may be invalid or expired. Please check your API key and try again.",
                True
            )
    
    return (
        "Authentication error occurred. Please verify your API key.",
        True
    )


def is_recoverable(error: Exception) -> bool:
    """
    Determine if an error is recoverable and the user should be offered a retry.
    
    Args:
        error: The exception to evaluate
        
    Returns:
        True if the error is recoverable, False otherwise
    """
    # Network errors are generally recoverable
    if isinstance(error, (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException
    )):
        return True
    
    # HTTP errors depend on status code
    if isinstance(error, requests.exceptions.HTTPError):
        if error.response:
            status_code = error.response.status_code
            
            # Client errors that are recoverable
            if status_code in [400, 401, 429]:
                return True
            
            # Server errors are recoverable (temporary issues)
            if 500 <= status_code < 600:
                return True
            
            # Other client errors (403, 404, etc.) are not recoverable
            return False
    
    # Value errors and other application errors are generally not recoverable
    if isinstance(error, (ValueError, KeyError, TypeError)):
        return False
    
    # Unknown errors - default to not recoverable for safety
    return False


def format_error_message(error: Exception) -> str:
    """
    Format an error into a user-friendly message.
    
    This is a convenience function that routes errors to the appropriate
    handler and returns just the message string.
    
    Args:
        error: The exception to format
        
    Returns:
        User-friendly error message string
    """
    if isinstance(error, requests.exceptions.HTTPError):
        message, _ = handle_api_error(error)
        return message
    elif isinstance(error, requests.exceptions.RequestException):
        message, _ = handle_network_error(error)
        return message
    else:
        return f"An error occurred: {str(error)}"
