"""
OpenRouter provider implementation for zeer CLI.
"""

import requests
import json
from typing import List
from colorama import Fore, Style
from src.provider_base import AIProvider, Model, Message, Response, ChatContext


class OpenRouterProvider(AIProvider):
    """OpenRouter provider implementation."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        """Initialize OpenRouter provider with API key."""
        super().__init__(api_key)
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by attempting to fetch models.
        
        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_models(self) -> List[Model]:
        """
        Fetch available models from OpenRouter.
        
        Returns:
            List of Model objects
        """
        response = requests.get(
            f"{self.BASE_URL}/models",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        for model_data in data.get("data", []):
            model_id = model_data.get("id", "")
            
            # Get context window
            context_window = model_data.get("context_length")
            
            models.append(Model(
                id=model_id,
                name=model_data.get("name", model_id),
                description=model_data.get("description"),
                context_window=context_window
            ))
        
        return models
    
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to OpenRouter and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Returns:
            Response object with the AI's reply
        """
        # Build messages array from context (OpenAI-compatible format)
        messages = []
        for msg in context.messages:
            # Handle tool call messages (stored with special format)
            if msg.role == "assistant" and msg.content.startswith("__TOOL_CALLS__:"):
                # Reconstruct assistant message with tool_calls
                tool_calls_json = msg.content.replace("__TOOL_CALLS__:", "")
                tool_calls = json.loads(tool_calls_json)
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls
                })
            elif msg.role == "tool" and "__TOOL_CALL_ID__:" in msg.content:
                # Reconstruct tool message with tool_call_id
                parts = msg.content.split(":", 2)
                tool_call_id = parts[1]
                content = parts[2] if len(parts) > 2 else ""
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": content
                })
            else:
                # Skip special markers
                if msg.content.startswith("__TOOL_CALLS__:") or msg.content.startswith("__TOOL_CALL_ID__:"):
                    continue
                # Regular message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Build request payload
        payload = {
            "model": context.model,
            "messages": messages
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            payload["tools"] = context.tools
            # Some OpenRouter models need explicit tool choice
            payload["tool_choice"] = "auto"
        
        # Make API request
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        
        # Better error handling
        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            raise Exception(f"OpenRouter API error ({response.status_code}): {error_msg}")
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response content
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No response from OpenRouter")
        
        choice = choices[0]
        message_data = choice.get("message", {})
        
        # Check for tool calls
        tool_calls = message_data.get("tool_calls")
        
        # Validate tool calls JSON if present
        if tool_calls:
            validated_tool_calls = []
            for tool_call in tool_calls:
                try:
                    if "function" in tool_call and "arguments" in tool_call["function"]:
                        # Try to parse arguments to validate JSON
                        args = tool_call["function"]["arguments"]
                        if isinstance(args, str):
                            # Validate JSON by parsing
                            json.loads(args)
                        validated_tool_calls.append(tool_call)
                except json.JSONDecodeError as e:
                    # Skip this malformed tool call
                    print(f"\n{Fore.YELLOW}Warning: Skipping malformed tool call: {e}{Style.RESET_ALL}")
                    continue
                except Exception as e:
                    # Skip any other errors
                    print(f"\n{Fore.YELLOW}Warning: Skipping invalid tool call: {e}{Style.RESET_ALL}")
                    continue
            
            # If we have valid tool calls, use them; otherwise set to None
            tool_calls = validated_tool_calls if validated_tool_calls else None
            
            if not tool_calls:
                print(f"\n{Fore.YELLOW}Note: Model attempted tool calls but all were malformed. Returning text response.{Style.RESET_ALL}")
        
        # Get text content (might be empty if only tool calls)
        text_content = message_data.get("content") or ""
        
        # Extract usage information
        usage = None
        if "usage" in data:
            usage_data = data["usage"]
            usage = {
                "promptTokens": usage_data.get("prompt_tokens", 0),
                "completionTokens": usage_data.get("completion_tokens", 0),
                "totalTokens": usage_data.get("total_tokens", 0)
            }
        
        return Response(
            content=text_content,
            model=context.model,
            usage=usage,
            tool_calls=tool_calls
        )
    
    def get_name(self) -> str:
        """Get the provider name."""
        return "OpenRouter"
