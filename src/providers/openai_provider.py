"""
OpenAI provider implementation for zeer CLI.
"""

import requests
from typing import List
from src.provider_base import AIProvider, Model, Message, Response, ChatContext


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize OpenAI provider with API key."""
        super().__init__(api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by attempting to fetch models.
        
        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_models(self) -> List[Model]:
        """
        Fetch available models from OpenAI.
        
        Returns:
            List of Model objects
        """
        response = requests.get(
            f"{self.BASE_URL}/models",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        # Known context windows for OpenAI models
        context_windows = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385,
        }
        
        # Filter for chat models (gpt models)
        for model_data in data.get("data", []):
            model_id = model_data.get("id", "")
            if "gpt" in model_id.lower():
                # Try to match context window
                context_window = None
                for key, window in context_windows.items():
                    if key in model_id:
                        context_window = window
                        break
                
                models.append(Model(
                    id=model_id,
                    name=model_id,
                    description=None,
                    context_window=context_window
                ))
        
        return sorted(models, key=lambda m: m.id)
    
    async def send_message_stream(self, message: str, context: ChatContext):
        """
        Send a message to OpenAI and stream the response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Yields:
            Chunks of text or complete Response with tool calls
        """
        import json
        
        # Build messages array from context
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
                # Regular message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Make API request with tools and streaming
        payload = {
            "model": context.model,
            "messages": messages,
            "stream": True
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            payload["tools"] = context.tools
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=60,
            stream=True
        )
        response.raise_for_status()
        
        # Parse SSE stream
        accumulated_content = ""
        accumulated_tool_calls = {}  # index -> tool_call
        usage_info = None
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            
            # SSE format: "data: {json}"
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                
                if data_str == "[DONE]":
                    break
                
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                
                choices = data.get("choices", [])
                if not choices:
                    continue
                
                delta = choices[0].get("delta", {})
                
                # Stream text content
                if "content" in delta and delta["content"]:
                    content = delta["content"]
                    accumulated_content += content
                    yield {"type": "content", "content": content}
                
                # Accumulate tool calls
                if "tool_calls" in delta:
                    for tool_call_delta in delta["tool_calls"]:
                        index = tool_call_delta.get("index", 0)
                        
                        if index not in accumulated_tool_calls:
                            accumulated_tool_calls[index] = {
                                "id": tool_call_delta.get("id", ""),
                                "type": "function",
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            }
                        
                        # Update tool call
                        if "id" in tool_call_delta:
                            accumulated_tool_calls[index]["id"] = tool_call_delta["id"]
                        
                        if "function" in tool_call_delta:
                            func_delta = tool_call_delta["function"]
                            if "name" in func_delta:
                                accumulated_tool_calls[index]["function"]["name"] = func_delta["name"]
                            if "arguments" in func_delta:
                                accumulated_tool_calls[index]["function"]["arguments"] += func_delta["arguments"]
                
                # Extract usage if available
                if "usage" in data:
                    usage_info = {
                        "promptTokens": data["usage"].get("prompt_tokens", 0),
                        "completionTokens": data["usage"].get("completion_tokens", 0),
                        "totalTokens": data["usage"].get("total_tokens", 0)
                    }
        
        # Convert accumulated tool calls to list
        tool_calls_list = None
        if accumulated_tool_calls:
            tool_calls_list = [accumulated_tool_calls[i] for i in sorted(accumulated_tool_calls.keys())]
        
        # Yield final response
        if tool_calls_list:
            yield {
                "type": "tool_calls",
                "response": Response(
                    content=accumulated_content,
                    model=context.model,
                    usage=usage_info,
                    tool_calls=tool_calls_list
                )
            }
        else:
            yield {
                "type": "done",
                "response": Response(
                    content=accumulated_content,
                    model=context.model,
                    usage=usage_info
                )
            }
    
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to OpenAI and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Returns:
            Response object with the AI's reply
        """
        import json
        
        # Build messages array from context
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
                # Regular message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Make API request with tools
        payload = {
            "model": context.model,
            "messages": messages
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            payload["tools"] = context.tools
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        choice = data["choices"][0]
        
        # Check if model wants to call a tool
        if choice["message"].get("tool_calls"):
            return Response(
                content="",
                model=context.model,
                usage=self._extract_usage(data),
                tool_calls=choice["message"]["tool_calls"]
            )
        
        # Extract response content
        content = choice["message"]["content"]
        
        return Response(
            content=content,
            model=context.model,
            usage=self._extract_usage(data)
        )
    
    def _extract_usage(self, data):
        """Extract usage information from API response."""
        if "usage" in data:
            return {
                "promptTokens": data["usage"].get("prompt_tokens", 0),
                "completionTokens": data["usage"].get("completion_tokens", 0),
                "totalTokens": data["usage"].get("total_tokens", 0)
            }
        return None
    
    def get_name(self) -> str:
        """Get the provider name."""
        return "OpenAI"
