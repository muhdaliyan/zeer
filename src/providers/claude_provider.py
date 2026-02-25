"""
Anthropic Claude provider implementation for zeer CLI.
"""

import requests
import json
from typing import List
from src.provider_base import AIProvider, Model, Message, Response, ChatContext


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider implementation."""
    
    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    
    def __init__(self, api_key: str):
        """Initialize Claude provider with API key."""
        super().__init__(api_key)
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json"
        }
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by attempting a simple API call.
        
        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            # Try to make a minimal request to validate the key
            response = requests.post(
                f"{self.BASE_URL}/messages",
                headers=self.headers,
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "Hi"}]
                },
                timeout=10
            )
            # 200 or 400 (bad request) means the key is valid
            # 401 means invalid key
            return response.status_code != 401
        except Exception:
            return False
    
    async def get_models(self) -> List[Model]:
        """
        Get available Claude models.
        
        Note: Claude API doesn't have a models endpoint, so we return
        a hardcoded list of known models.
        
        Returns:
            List of Model objects
        """
        # Hardcoded list of Claude models as of the design
        models = [
            Model(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                description="Most capable Claude model for complex tasks",
                context_window=200000
            ),
            Model(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                description="Balanced performance and speed",
                context_window=200000
            ),
            Model(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                description="Fastest and most compact model",
                context_window=200000
            ),
            Model(
                id="claude-2.1",
                name="Claude 2.1",
                description="Previous generation Claude model",
                context_window=200000
            ),
            Model(
                id="claude-2.0",
                name="Claude 2.0",
                description="Previous generation Claude model",
                context_window=100000
            )
        ]
        
        return models
    
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to Claude and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Returns:
            Response object with the AI's reply
        """
        # Build messages array from context
        messages = []
        for msg in context.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Build request payload
        payload = {
            "model": context.model,
            "max_tokens": 4096,
            "messages": messages
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            claude_tools = self._convert_tools_to_claude_format(context.tools)
            if claude_tools:
                payload["tools"] = claude_tools
        
        # Make API request
        response = requests.post(
            f"{self.BASE_URL}/messages",
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract response content
        content_blocks = data.get("content", [])
        if not content_blocks:
            raise ValueError("No response from Claude")
        
        # Check for tool use
        tool_calls = []
        text_content = ""
        
        for block in content_blocks:
            if block.get("type") == "tool_use":
                # Claude wants to use a tool
                tool_calls.append({
                    "id": block["id"],
                    "type": "function",
                    "function": {
                        "name": block["name"],
                        "arguments": json.dumps(block["input"])
                    }
                })
            elif block.get("type") == "text":
                text_content += block.get("text", "")
        
        # Extract usage information if available
        usage = None
        if "usage" in data:
            usage_data = data["usage"]
            usage = {
                "promptTokens": usage_data.get("input_tokens", 0),
                "completionTokens": usage_data.get("output_tokens", 0),
                "totalTokens": usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
            }
        
        # Return response with tool calls if any
        if tool_calls:
            return Response(
                content=text_content,
                model=context.model,
                usage=usage,
                tool_calls=tool_calls
            )
        
        return Response(
            content=text_content,
            model=context.model,
            usage=usage
        )
    
    def _convert_tools_to_claude_format(self, openai_tools):
        """Convert OpenAI tool format to Claude tool format."""
        if not openai_tools:
            return None
        
        claude_tools = []
        
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                claude_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func.get("parameters", {})
                })
        
        return claude_tools if claude_tools else None
    
    def get_name(self) -> str:
        """Get the provider name."""
        return "Claude"
