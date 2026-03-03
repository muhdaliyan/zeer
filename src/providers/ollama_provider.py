"""
Ollama provider implementation for zeer CLI.
Supports both local models and Ollama cloud models.
"""

import json
from typing import List
from src.provider_base import AIProvider, Model, Message, Response, ChatContext

try:
    from ollama import Client, ResponseError
except ImportError:
    raise ImportError("ollama package is required. Install with: pip install ollama")


class OllamaProvider(AIProvider):
    """Ollama provider implementation for local and cloud models."""
    
    def __init__(self, api_key: str = None, host: str = "http://localhost:11434"):
        """
        Initialize Ollama provider.
        
        Args:
            api_key: Optional API key for Ollama cloud models (empty/None for local)
            host: Ollama server host (default: http://localhost:11434)
        """
        super().__init__(api_key or "")
        self.host = host
        
        # Initialize client with optional headers for cloud models
        headers = {}
        if api_key and api_key.strip():  # Only add auth header if key is provided
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = Client(host=host, headers=headers if headers else None)
    
    async def validate_api_key(self) -> bool:
        """
        Validate connection to Ollama server.
        For local Ollama, checks if server is running.
        For cloud, validates API key.
        
        Returns:
            True if connection is valid, False otherwise
        
        Raises:
            Exception: With error details for better handling
        """
        try:
            # Try to list models to verify connection
            self.client.list()
            return True
        except ResponseError as e:
            # Re-raise with error info for app controller to handle
            raise Exception(f"ollama_error: {e.error}")
        except Exception as e:
            # Re-raise connection errors
            raise Exception(f"connection_error: {str(e)}")
    
    async def get_models(self) -> List[Model]:
        """
        Fetch available models from Ollama.
        Returns both local and cloud models if authenticated.
        
        Returns:
            List of Model objects
        
        Raises:
            Exception: With error details for better handling
        """
        try:
            response = self.client.list()
            models = []
            
            # Response is a ListResponse object with 'models' attribute
            models_data = []
            if hasattr(response, 'models'):
                models_data = response.models
            elif isinstance(response, dict):
                models_data = response.get("models", [])
            
            for model_data in models_data:
                # The field is 'model' not 'name' in Ollama's response
                if hasattr(model_data, 'model'):
                    model_name = model_data.model
                    size = getattr(model_data, 'size', 0)
                    details = getattr(model_data, 'details', None)
                    family = getattr(details, 'family', None) if details else None
                else:
                    model_name = model_data.get("model", "")
                    size = model_data.get("size", 0)
                    details = model_data.get("details", {})
                    family = details.get("family") if details else None
                
                # Extract size (size is in bytes)
                size_gb = size / (1024**3) if size else None
                
                # Build description with available info
                description_parts = []
                if size_gb and size_gb > 0:
                    description_parts.append(f"{size_gb:.1f}GB")
                
                if family:
                    description_parts.append(family)
                
                description = " - ".join(description_parts) if description_parts else None
                
                models.append(Model(
                    id=model_name,
                    name=model_name,
                    description=description,
                    context_window=None  # Ollama doesn't expose this in list
                ))
            
            return sorted(models, key=lambda m: m.id)
            
        except ResponseError as e:
            # Re-raise with error info for app controller to handle
            raise Exception(f"ollama_error: {e.error}")
        except Exception as e:
            # Re-raise connection errors
            if "ollama_error" not in str(e):
                raise Exception(f"connection_error: {str(e)}")
            raise
    
    async def send_message_stream(self, message: str, context: ChatContext):
        """
        Send a message to Ollama and stream the response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Yields:
            Chunks of text or complete Response with tool calls
        """
        # Build messages array from context
        messages = []
        for msg in context.messages:
            # Handle tool call messages (stored with special format)
            if msg.role == "assistant" and msg.content.startswith("__TOOL_CALLS__:"):
                # Reconstruct assistant message with tool_calls
                tool_calls_json = msg.content.replace("__TOOL_CALLS__:", "")
                tool_calls = json.loads(tool_calls_json)
                
                # Convert to Ollama format (arguments should be dict, not string)
                ollama_tool_calls = []
                for tc in tool_calls:
                    func_args = tc["function"]["arguments"]
                    # Parse if it's a JSON string
                    if isinstance(func_args, str):
                        func_args = json.loads(func_args)
                    
                    # Get thought_signature if present
                    thought_sig = None
                    if "thought_signature" in tc:
                        thought_sig = tc["thought_signature"]
                    else:
                        # Generate one if missing (for backward compatibility)
                        import hashlib
                        signature_input = f"{tc['function']['name']}_{tc['function']['arguments']}"
                        thought_sig = hashlib.md5(signature_input.encode()).hexdigest()
                    
                    # Ollama client expects 'function' key for validation
                    tool_call_obj = {
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": func_args  # Dict, not string
                        }
                    }
                    
                    # Add thoughtSignature for models that support it
                    if thought_sig:
                        tool_call_obj["thoughtSignature"] = thought_sig
                    
                    ollama_tool_calls.append(tool_call_obj)
                
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": ollama_tool_calls
                })
            elif msg.role == "tool" and "__TOOL_CALL_ID__:" in msg.content:
                # Reconstruct tool message with tool_call_id
                parts = msg.content.split(":", 2)
                tool_call_id = parts[1]
                content = parts[2] if len(parts) > 2 else ""
                messages.append({
                    "role": "tool",
                    "content": content
                })
            else:
                # Regular message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Build request parameters
        chat_params = {
            "model": context.model,
            "messages": messages,
            "stream": True  # Enable streaming
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            chat_params["tools"] = context.tools
        
        try:
            # Make streaming API request
            response_stream = self.client.chat(**chat_params)
            
            accumulated_content = ""
            accumulated_tool_calls = None
            usage_info = None
            
            for chunk in response_stream:
                # Response is an object, not a dict - access attributes directly
                message_data = chunk.message if hasattr(chunk, 'message') else {}
                
                # Get content
                if hasattr(message_data, 'content'):
                    content = message_data.content or ""
                else:
                    content = message_data.get("content", "") if isinstance(message_data, dict) else ""
                
                # Stream text content as it arrives
                if content:
                    accumulated_content += content
                    yield {"type": "content", "content": content}
                
                # Check for tool calls
                if hasattr(message_data, 'tool_calls') and message_data.tool_calls:
                    # Convert Ollama tool calls to OpenAI format
                    tool_calls = []
                    for tool_call in message_data.tool_calls:
                        tool_call_obj = {
                            "id": f"call_{tool_call.function.name}",
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": json.dumps(tool_call.function.arguments) if isinstance(tool_call.function.arguments, dict) else tool_call.function.arguments
                            }
                        }
                        
                        # Preserve thought_signature if present
                        if hasattr(tool_call, 'thought_signature') and tool_call.thought_signature:
                            tool_call_obj["thought_signature"] = tool_call.thought_signature
                        else:
                            # Generate a default thought_signature
                            import hashlib
                            signature_input = f"{tool_call.function.name}_{json.dumps(tool_call.function.arguments)}"
                            tool_call_obj["thought_signature"] = hashlib.md5(signature_input.encode()).hexdigest()
                        
                        tool_calls.append(tool_call_obj)
                    
                    accumulated_tool_calls = tool_calls
                
                # Extract usage information if available
                if hasattr(chunk, 'prompt_eval_count') or hasattr(chunk, 'eval_count'):
                    prompt_tokens = getattr(chunk, 'prompt_eval_count', 0) or 0
                    completion_tokens = getattr(chunk, 'eval_count', 0) or 0
                    usage_info = {
                        "promptTokens": prompt_tokens,
                        "completionTokens": completion_tokens,
                        "totalTokens": prompt_tokens + completion_tokens
                    }
            
            # Yield final response with tool calls if any
            if accumulated_tool_calls:
                yield {
                    "type": "tool_calls",
                    "response": Response(
                        content=accumulated_content,
                        model=context.model,
                        usage=usage_info,
                        tool_calls=accumulated_tool_calls
                    )
                }
            else:
                # Yield final response
                yield {
                    "type": "done",
                    "response": Response(
                        content=accumulated_content,
                        model=context.model,
                        usage=usage_info
                    )
                }
                
        except ResponseError as e:
            error_msg = str(e.error).lower()
            
            # Handle specific error cases
            if "thought_signature" in error_msg or "thoughtsignature" in error_msg:
                from colorama import Fore, Style
                print(f"\n{Fore.YELLOW}⚠ This model doesn't support tool calling properly.{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Try: minimax-m2.5:cloud, qwen3.5:cloud, or llama3.2 (local){Style.RESET_ALL}\n")
                
                yield {
                    "type": "done",
                    "response": Response(
                        content="I tried to use a tool but this model doesn't support tool calling properly. Please try asking your question in a different way, or switch to a model that supports tools (like minimax-m2.5:cloud or qwen3.5:cloud).",
                        model=context.model,
                        usage=None
                    )
                }
            elif "unauthorized" in error_msg:
                raise Exception(
                    "Authentication required.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open Ollama app and sign in\n"
                    "3. Restart zeer"
                )
            elif "not found" in error_msg or "does not exist" in error_msg or "pull" in error_msg:
                if ":cloud" in context.model:
                    raise Exception(
                        f"Model '{context.model}' not available.\n\n"
                        f"1. Run: ollama run {context.model}\n"
                        f"2. Restart zeer"
                    )
                else:
                    raise Exception(
                        f"Model '{context.model}' not found.\n\n"
                        f"1. Pull the model: ollama pull {context.model}\n"
                        f"2. Restart zeer"
                    )
            elif "connection" in error_msg or "refused" in error_msg:
                raise Exception(
                    "Cannot connect to Ollama.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open the Ollama app\n"
                    "3. Restart zeer"
                )
            else:
                raise Exception(f"Ollama error: {e.error}")
        except Exception as e:
            if "Ollama" in str(e) or "ollama" in str(e):
                raise
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise Exception(
                    "Cannot connect to Ollama.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open the Ollama app\n"
                    "3. Restart zeer"
                )
            raise
    
    async def send_message(self, message: str, context: ChatContext) -> Response:
        """
        Send a message to Ollama and receive a response.
        
        Args:
            message: The user's message
            context: The conversation context
            
        Returns:
            Response object with the AI's reply
        """
        # Build messages array from context
        messages = []
        for msg in context.messages:
            # Handle tool call messages (stored with special format)
            if msg.role == "assistant" and msg.content.startswith("__TOOL_CALLS__:"):
                # Reconstruct assistant message with tool_calls
                tool_calls_json = msg.content.replace("__TOOL_CALLS__:", "")
                tool_calls = json.loads(tool_calls_json)
                
                # Convert to Ollama format (arguments should be dict, not string)
                ollama_tool_calls = []
                for tc in tool_calls:
                    func_args = tc["function"]["arguments"]
                    # Parse if it's a JSON string
                    if isinstance(func_args, str):
                        func_args = json.loads(func_args)
                    
                    # Get thought_signature if present
                    thought_sig = None
                    if "thought_signature" in tc:
                        thought_sig = tc["thought_signature"]
                    else:
                        # Generate one if missing (for backward compatibility)
                        import hashlib
                        signature_input = f"{tc['function']['name']}_{tc['function']['arguments']}"
                        thought_sig = hashlib.md5(signature_input.encode()).hexdigest()
                    
                    # Ollama client expects 'function' key for validation
                    tool_call_obj = {
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": func_args  # Dict, not string
                        }
                    }
                    
                    # Add thoughtSignature for models that support it
                    if thought_sig:
                        tool_call_obj["thoughtSignature"] = thought_sig
                    
                    ollama_tool_calls.append(tool_call_obj)
                
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": ollama_tool_calls
                })
            elif msg.role == "tool" and "__TOOL_CALL_ID__:" in msg.content:
                # Reconstruct tool message with tool_call_id
                parts = msg.content.split(":", 2)
                tool_call_id = parts[1]
                content = parts[2] if len(parts) > 2 else ""
                messages.append({
                    "role": "tool",
                    "content": content
                })
            else:
                # Regular message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Build request parameters
        chat_params = {
            "model": context.model,
            "messages": messages,
            "stream": False
        }
        
        # Add tools if available
        if hasattr(context, 'tools') and context.tools:
            chat_params["tools"] = context.tools
        
        try:
            # Make API request
            response = self.client.chat(**chat_params)
            
            # Response is an object, not a dict - access attributes directly
            message_data = response.message if hasattr(response, 'message') else {}
            
            # Get content
            if hasattr(message_data, 'content'):
                content = message_data.content or ""
            else:
                content = message_data.get("content", "") if isinstance(message_data, dict) else ""
            
            # Check if model wants to call a tool
            tool_calls = None
            if hasattr(message_data, 'tool_calls') and message_data.tool_calls:
                # Convert Ollama tool calls to OpenAI format
                tool_calls = []
                for tool_call in message_data.tool_calls:
                    # Ollama returns tool calls as objects
                    tool_call_obj = {
                        "id": f"call_{tool_call.function.name}",
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": json.dumps(tool_call.function.arguments) if isinstance(tool_call.function.arguments, dict) else tool_call.function.arguments
                        }
                    }
                    
                    # Preserve thought_signature if present, or generate a default one
                    # Some Ollama models (like Gemini) require this field
                    if hasattr(tool_call, 'thought_signature') and tool_call.thought_signature:
                        tool_call_obj["thought_signature"] = tool_call.thought_signature
                    else:
                        # Generate a default thought_signature for models that require it
                        import hashlib
                        signature_input = f"{tool_call.function.name}_{json.dumps(tool_call.function.arguments)}"
                        tool_call_obj["thought_signature"] = hashlib.md5(signature_input.encode()).hexdigest()
                    
                    tool_calls.append(tool_call_obj)
            
            # Extract usage information if available
            usage = None
            if hasattr(response, 'prompt_eval_count') or hasattr(response, 'eval_count'):
                prompt_tokens = getattr(response, 'prompt_eval_count', 0) or 0
                completion_tokens = getattr(response, 'eval_count', 0) or 0
                usage = {
                    "promptTokens": prompt_tokens,
                    "completionTokens": completion_tokens,
                    "totalTokens": prompt_tokens + completion_tokens
                }
            
            return Response(
                content=content,
                model=context.model,
                usage=usage,
                tool_calls=tool_calls
            )
            
        except ResponseError as e:
            error_msg = str(e.error).lower()
            
            # Handle specific error cases
            if "thought_signature" in error_msg or "thoughtsignature" in error_msg:
                # Don't throw error, just show warning and respond without tool result
                from colorama import Fore, Style
                print(f"\n{Fore.YELLOW}⚠ This model doesn't support tool calling properly.{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Try: minimax-m2.5:cloud, qwen3.5:cloud, or llama3.2 (local){Style.RESET_ALL}\n")
                
                # Return a response explaining the limitation
                return Response(
                    content="I tried to use a tool but this model doesn't support tool calling properly. Please try asking your question in a different way, or switch to a model that supports tools (like minimax-m2.5:cloud or qwen3.5:cloud).",
                    model=context.model,
                    usage=None
                )
            elif "unauthorized" in error_msg:
                raise Exception(
                    "Authentication required.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open Ollama app and sign in\n"
                    "3. Restart zeer"
                )
            elif "not found" in error_msg or "does not exist" in error_msg or "pull" in error_msg:
                # Check if it's a cloud model
                if ":cloud" in context.model:
                    raise Exception(
                        f"Model '{context.model}' not available.\n\n"
                        f"1. Run: ollama run {context.model}\n"
                        f"2. Restart zeer"
                    )
                else:
                    raise Exception(
                        f"Model '{context.model}' not found.\n\n"
                        f"1. Pull the model: ollama pull {context.model}\n"
                        f"2. Restart zeer"
                    )
            elif "connection" in error_msg or "refused" in error_msg:
                raise Exception(
                    "Cannot connect to Ollama.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open the Ollama app\n"
                    "3. Restart zeer"
                )
            else:
                raise Exception(f"Ollama error: {e.error}")
        except Exception as e:
            # Re-raise if already formatted
            if "Ollama" in str(e) or "ollama" in str(e):
                raise
            # Handle connection errors
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise Exception(
                    "Cannot connect to Ollama.\n\n"
                    "1. Download and install Ollama: https://ollama.ai\n"
                    "2. Open the Ollama app\n"
                    "3. Restart zeer"
                )
            raise
    
    def get_name(self) -> str:
        """Get the provider name."""
        return "Ollama"
