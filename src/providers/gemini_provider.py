"""
Google Gemini provider implementation for zeer CLI.
"""

import requests
import json
from typing import List
from src.provider_base import AIProvider, Model, Message, Response, ChatContext


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1"
    BASE_URL_BETA = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str):
        """Initialize Gemini provider with API key."""
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
                params={"key": self.api_key},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_models(self) -> List[Model]:
        """
        Fetch available models from Gemini.
        
        Returns:
            List of Model objects
        """
        response = requests.get(
            f"{self.BASE_URL}/models",
            params={"key": self.api_key},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        for model_data in data.get("models", []):
            model_name = model_data.get("name", "")
            # Extract model ID from full name (e.g., "models/gemini-pro" -> "gemini-pro")
            model_id = model_name.split("/")[-1] if "/" in model_name else model_name
            
            # Only include models that support generateContent
            supported_methods = model_data.get("supportedGenerationMethods", [])
            if "generateContent" in supported_methods:
                # Get context window from inputTokenLimit
                context_window = model_data.get("inputTokenLimit")
                
                models.append(Model(
                    id=model_id,
                    name=model_data.get("displayName", model_id),
                    description=model_data.get("description"),
                    context_window=context_window
                ))
        
        return models
    
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to Gemini and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Returns:
            Response object with the AI's reply
        """
        # Build contents array from context
        import json
        contents = []
        for msg in context.messages:
            # Handle tool call messages (stored with special format)
            if msg.role == "assistant" and msg.content.startswith("__TOOL_CALLS__:"):
                # Reconstruct assistant message with function calls
                tool_calls_json = msg.content.replace("__TOOL_CALLS__:", "")
                tool_calls = json.loads(tool_calls_json)
                
                # Convert to Gemini format
                parts = []
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    func_args = json.loads(tool_call["function"]["arguments"])
                    
                    part = {
                        "functionCall": {
                            "name": func_name,
                            "args": func_args
                        }
                    }
                    
                    # Add thought_signature if present (required for Gemini 3+)
                    if "thought_signature" in tool_call:
                        part["thoughtSignature"] = tool_call["thought_signature"]
                    
                    parts.append(part)
                
                contents.append({
                    "role": "model",
                    "parts": parts
                })
            elif msg.role == "tool" and "__TOOL_CALL_ID__:" in msg.content:
                # Reconstruct tool response message
                parts_split = msg.content.split(":", 2)
                tool_call_id = parts_split[1]
                content = parts_split[2] if len(parts_split) > 2 else ""
                
                # Gemini expects functionResponse in a user role message (not "function")
                # Extract function name from tool_call_id
                func_name = tool_call_id.replace("call_", "")
                
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": func_name,
                            "response": {
                                "content": content
                            }
                        }
                    }]
                })
            else:
                # Gemini uses "user" and "model" roles
                role = "model" if msg.role == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        # Build request payload
        payload = {"contents": contents}
        
        # Add tools if available (convert from OpenAI format to Gemini format)
        if hasattr(context, 'tools') and context.tools:
            gemini_tools = self._convert_tools_to_gemini_format(context.tools)
            if gemini_tools:
                payload["tools"] = gemini_tools
                # Configure tool calling to be more aggressive
                payload["tool_config"] = {
                    "function_calling_config": {
                        "mode": "AUTO"  # AUTO allows model to decide when to use tools
                    }
                }
        
        # Add generation config to encourage longer, more complete responses
        payload["generationConfig"] = {
            "temperature": 0.7,
            "maxOutputTokens": 8192  # Allow longer responses for multiple tool calls
        }
        
        # Make API request
        # Use v1beta for tool calling support
        api_url = f"{self.BASE_URL_BETA}/models/{context.model}:generateContent"
        response = requests.post(
            api_url,
            params={"key": self.api_key},
            json=payload,
            timeout=60
        )
        
        # Better error handling
        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            raise Exception(f"Gemini API error ({response.status_code}): {error_msg}")
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response content
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No response from Gemini")
        
        candidate = candidates[0]
        
        # Check if candidate has content
        if "content" not in candidate:
            # Model might have been blocked or returned no content
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            raise ValueError(f"No content in response. Finish reason: {finish_reason}")
        
        parts = candidate["content"]["parts"]
        
        # Check if model wants to call a function
        function_calls = []
        text_content = ""
        
        for part in parts:
            if "functionCall" in part:
                # Gemini wants to call a function
                func_call = part["functionCall"]
                func_name = func_call["name"]
                
                # Extract thought_signature if present (required for Gemini 3+)
                thought_signature = part.get("thoughtSignature")
                
                function_call_obj = {
                    "id": f"call_{func_name}",  # Use function name in ID for tracking
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "arguments": json.dumps(func_call.get("args", {}))
                    }
                }
                
                # Store thought_signature if present (needed for next turn)
                if thought_signature:
                    function_call_obj["thought_signature"] = thought_signature
                
                function_calls.append(function_call_obj)
            elif "text" in part:
                text_content += part["text"]
        
        # Extract usage information if available
        usage = None
        if "usageMetadata" in data:
            metadata = data["usageMetadata"]
            usage = {
                "promptTokens": metadata.get("promptTokenCount", 0),
                "completionTokens": metadata.get("candidatesTokenCount", 0),
                "totalTokens": metadata.get("totalTokenCount", 0)
            }
        
        # Return response with tool calls if any
        if function_calls:
            return Response(
                content=text_content,
                model=context.model,
                usage=usage,
                tool_calls=function_calls
            )
        
        return Response(
            content=text_content,
            model=context.model,
            usage=usage
        )
    
    def _convert_tools_to_gemini_format(self, openai_tools):
        """Convert OpenAI tool format to Gemini function declarations format."""
        if not openai_tools:
            return None
        
        function_declarations = []
        
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                
                # Convert parameters schema
                parameters = func.get("parameters", {})
                
                # Build Gemini-compatible parameters
                gemini_params = {
                    "type": "object",  # lowercase for Gemini
                    "properties": {}
                }
                
                # Convert property types
                for prop_name, prop_def in parameters.get("properties", {}).items():
                    prop_type = prop_def.get("type", "string").lower()  # lowercase
                    gemini_params["properties"][prop_name] = {
                        "type": prop_type,
                        "description": prop_def.get("description", "")
                    }
                
                # Add required fields if present
                if parameters.get("required"):
                    gemini_params["required"] = parameters["required"]
                
                function_declarations.append({
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": gemini_params
                })
        
        return [{"function_declarations": function_declarations}] if function_declarations else None
    
    def get_name(self) -> str:
        """Get the provider name."""
        return "Gemini"
