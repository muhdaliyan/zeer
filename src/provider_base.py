"""
Provider abstraction for zeer CLI.

This module defines the abstract base class for AI providers and data models
for communication between the CLI and provider implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Model:
    """Represents an AI model from a provider."""
    id: str
    name: str
    description: Optional[str] = None
    context_window: Optional[int] = None


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # "user", "assistant", or "tool"
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Response:
    """Represents a response from an AI provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None  # promptTokens, completionTokens, totalTokens
    tool_calls: Optional[List[Dict[str, Any]]] = None  # Tool calls from the model
    images: Optional[List[Dict[str, Any]]] = None  # Generated images (base64 data, mime type, etc.)
    streamed: bool = False  # Flag to indicate if content was already streamed to console


@dataclass
class ChatContext:
    """Represents the context of a chat session."""
    messages: List[Message]
    model: str
    provider: str
    tools: Optional[List[Dict[str, Any]]] = None  # Available tools for the model


class AIProvider(ABC):
    """Abstract base class for AI provider implementations."""
    
    def __init__(self, api_key: str):
        """
        Initialize the provider with an API key.
        
        Args:
            api_key: The API key for authentication
        """
        self.api_key = api_key
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """
        Validate the API key format and connectivity.
        
        Returns:
            True if the API key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_models(self) -> List[Model]:
        """
        Fetch the list of available models from the provider.
        
        Returns:
            List of Model objects representing available models
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to the AI model and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context including history
            
        Returns:
            Response object containing the AI's reply
        """
        pass
    
    async def send_message_stream(self, message: str, context: ChatContext):
        """
        Send a message to the AI model and stream the response.
        
        Args:
            message: The user's message
            context: The conversation context including history
            
        Yields:
            Chunks of the response (text or tool calls)
        """
        # Default implementation: fall back to non-streaming
        response = await self.send_message(message, context)
        yield response
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the provider's name.
        
        Returns:
            The provider name as a string
        """
        pass
