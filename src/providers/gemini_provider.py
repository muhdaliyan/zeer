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
            # Use v1beta endpoint to validate (same as get_models)
            response = requests.get(
                f"{self.BASE_URL_BETA}/models",
                params={"key": self.api_key},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_models(self) -> List[Model]:
        """
        Fetch available models from Gemini API dynamically.
        
        This fetches the latest models from Google's Gemini API, including:
        - Gemini 3.x series (3.1 Pro, 3 Flash, 3 Pro)
        - Gemini 2.5 series (Flash, Flash-Lite, Pro)
        - Specialized models (embeddings, audio, image generation)
        
        Returns:
            List of Model objects with latest available models
        """
        try:
            # Use v1beta endpoint to get ALL models including Gemini 3.x
            response = requests.get(
                f"{self.BASE_URL_BETA}/models",
                params={"key": self.api_key},
                timeout=15  # Increased timeout for reliability
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
                    
                    # Get display name, fallback to model ID
                    display_name = model_data.get("displayName", model_id)
                    
                    # Get description
                    description = model_data.get("description", "")
                    
                    models.append(Model(
                        id=model_id,
                        name=display_name,
                        description=description,
                        context_window=context_window
                    ))
            
            # Sort models: prioritize newer versions (3.x > 2.5 > 2.0 > 1.x)
            # and stable over preview/experimental
            def model_sort_key(model: Model) -> tuple:
                model_id = model.id.lower()
                
                # Extract version number
                version = 0
                if "gemini-3" in model_id:
                    version = 300
                elif "gemini-2.5" in model_id:
                    version = 250
                elif "gemini-2.0" in model_id:
                    version = 200
                elif "gemini-1.5" in model_id:
                    version = 150
                elif "gemini-1.0" in model_id:
                    version = 100
                
                # Prioritize stable over preview/experimental
                stability = 0
                if "experimental" in model_id:
                    stability = 1
                elif "preview" in model_id:
                    stability = 2
                else:
                    stability = 3
                
                # Prioritize pro > flash > flash-lite
                tier = 0
                if "pro" in model_id:
                    tier = 3
                elif "flash-lite" in model_id:
                    tier = 1
                elif "flash" in model_id:
                    tier = 2
                
                return (-version, -stability, -tier, model_id)
            
            models.sort(key=model_sort_key)
            
            return models
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Gemini models: {str(e)}")
    
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
                try:
                    tool_calls = json.loads(tool_calls_json)
                except json.JSONDecodeError:
                    # Skip malformed tool calls
                    continue
                
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
                
                # Only add if we have parts
                if parts:
                    contents.append({
                        "role": "model",
                        "parts": parts
                    })
            elif msg.role == "tool" and "__TOOL_CALL_ID__:" in msg.content:
                # Reconstruct tool response message
                parts_split = msg.content.split(":", 2)
                if len(parts_split) < 2:
                    continue
                    
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
                
                # Skip empty messages
                if not msg.content or not msg.content.strip():
                    continue
                
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
        
        try:
            response = requests.post(
                api_url,
                params={"key": self.api_key},
                json=payload,
                timeout=60
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        
        # Better error handling
        if response.status_code != 200:
            try:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
            except:
                error_msg = response.text
            raise Exception(f"Gemini API error ({response.status_code}): {error_msg}")
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse response JSON: {str(e)}")
        
        # Extract response content
        candidates = data.get("candidates", [])
        if not candidates:
            # Debug: show what we got
            import json as json_module
            raise ValueError(f"No candidates in response. Full response: {json_module.dumps(data, indent=2)[:500]}")
        
        candidate = candidates[0]
        
        # Check if candidate has content
        if "content" not in candidate:
            # Model might have been blocked or returned no content
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            safety_ratings = candidate.get("safetyRatings", [])
            raise ValueError(f"No content in response. Finish reason: {finish_reason}, Safety: {safety_ratings}")
        
        # Check if parts exist in content
        content = candidate.get("content", {})
        if "parts" not in content:
            # Sometimes Gemini returns empty content with just role
            # This can happen when the model has nothing to say after tool calls
            # Return an empty response instead of erroring
            import json as json_module
            
            # Check if this is just an empty model response (common after tool calls)
            if content.get("role") == "model" and len(content) == 1:
                # Return empty response - the model is waiting for more context
                return Response(
                    content="",
                    model=context.model,
                    usage=None,
                    tool_calls=None,
                    images=None
                )
            
            # Otherwise, this is an unexpected format
            raise ValueError(f"No 'parts' in content. Content structure: {json_module.dumps(content, indent=2)[:500]}")
        
        parts = content["parts"]
        
        # Check if parts is empty
        if not parts:
            raise ValueError("Empty parts array in response")
        
        # Check if model wants to call a function or generated images
        function_calls = []
        text_content = ""
        images = []
        
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
            elif "inlineData" in part:
                # Image data generated by the model
                inline_data = part["inlineData"]
                images.append({
                    "data": inline_data.get("data", ""),  # base64 encoded image
                    "mimeType": inline_data.get("mimeType", "image/png")
                })
        
        # Extract usage information if available
        usage = None
        if "usageMetadata" in data:
            metadata = data["usageMetadata"]
            usage = {
                "promptTokens": metadata.get("promptTokenCount", 0),
                "completionTokens": metadata.get("candidatesTokenCount", 0),
                "totalTokens": metadata.get("totalTokenCount", 0)
            }
        
        # Return response with tool calls and/or images if any
        if function_calls:
            return Response(
                content=text_content,
                model=context.model,
                usage=usage,
                tool_calls=function_calls,
                images=images if images else None
            )
        
        return Response(
            content=text_content,
            model=context.model,
            usage=usage,
            images=images if images else None
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
