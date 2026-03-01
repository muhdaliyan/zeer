"""
Application controller for zeer CLI.

This module orchestrates the main application flow, coordinating provider selection,
API key configuration, model discovery, and the interactive chat session.

Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 4.2, 5.1, 5.2, 5.3, 5.4, 6.1, 6.5, 6.6
"""

import asyncio
import getpass
import sys
from typing import Optional

from src.cli_interface import (
    display_branding, display_error, prompt_choice,
    display_success, display_info, display_separator,
    display_user_message, display_assistant_message,
    RunningIndicator, prompt_slash_command, display_input_prompt,
    display_input_prompt_with_slash_detection, clear_screen
)
from colorama import Fore, Style
from src.validation import validate_provider_selection, validate_api_key, validate_model_selection
from src.session import SessionManager
from src.model_manager import fetch_models, display_models
from src.chat_session import ChatSession
from src.error_handler import handle_network_error, handle_api_error, is_recoverable, format_error_message
from src.provider_base import AIProvider, Model
from src.providers.openai_provider import OpenAIProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.claude_provider import ClaudeProvider
from src.providers.openrouter_provider import OpenRouterProvider
from src.providers.ollama_provider import OllamaProvider
from src.tools import create_default_registry, ToolRegistry
from src.skills_manager import SkillsManager
from src.image_handler import save_images, display_image_in_terminal

import requests


class AppController:
    """
    Main application controller that orchestrates the zeer CLI flow.
    
    This class manages the sequential flow from provider selection through
    to the interactive chat session, handling errors and retries along the way.
    """
    
    # Supported providers mapping
    PROVIDERS = {
        "openai": {"name": "OpenAI", "class": OpenAIProvider},
        "gemini": {"name": "Gemini", "class": GeminiProvider},
        "claude": {"name": "Claude", "class": ClaudeProvider},
        "openrouter": {"name": "OpenRouter", "class": OpenRouterProvider},
        "ollama": {"name": "Ollama", "class": OllamaProvider}
    }
    
    def __init__(self):
        """Initialize the application controller."""
        self.session_manager = SessionManager()
        self.provider: Optional[AIProvider] = None
        self.chat_session: Optional[ChatSession] = None
        self.tool_registry: ToolRegistry = create_default_registry()
        self.skills_manager: SkillsManager = SkillsManager("skills")
    
    def run(self) -> None:
        """
        Main entry point that coordinates the entire application flow.
        
        Flow:
        1. Display branding
        2. Check for saved credentials
        3. Provider selection
        4. API key input
        5. Model discovery
        6. Model selection
        7. Chat loop
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 4.2, 5.1, 5.2, 5.3, 5.4, 6.1, 6.5, 6.6
        """
        try:
            # Display branding
            display_branding()
            
            # Display open source message
            from colorama import Fore, Style
            print(f"{Fore.LIGHTBLACK_EX}Open source project • Run locally • Contribute on GitHub{Style.RESET_ALL}")
            print()
            
            # Check for saved credentials
            saved_creds = self.session_manager.load_saved_credentials()
            provider_name = None
            api_key = None
            saved_model = None
            
            if saved_creds:
                # Auto-use existing credentials and show welcome message
                provider_name = saved_creds.get('last_provider')
                if provider_name and 'providers' in saved_creds and provider_name in saved_creds['providers']:
                    provider_data = saved_creds['providers'][provider_name]
                    api_key = provider_data.get('api_key')
                    saved_model = provider_data.get('model')
                    self.session_manager.store_provider(provider_name)
                    self.session_manager.store_api_key(api_key, provider_name)
                    
                    # Show provider and model info
                    provider_display = self.PROVIDERS[provider_name]['name']
                    print(f"Welcome back! Using {Fore.MAGENTA}{provider_display}{Style.RESET_ALL}", end="")
                    if saved_model:
                        self.session_manager.store_model(saved_model)
                        print(f" with model {Fore.MAGENTA}{saved_model}{Style.RESET_ALL}")
                    else:
                        print()
                    
                    # For Ollama, empty string is valid (local usage)
                    if provider_name == "ollama" and api_key == "":
                        pass  # Empty key is valid for local Ollama
                    elif not api_key:
                        # Invalid saved data for other providers
                        provider_name = None
                    else:
                        print()
                else:
                    provider_name = None  # Invalid saved data
            
            # Provider selection flow (if not using saved)
            if not provider_name:
                provider_name = self._select_provider()
                if not provider_name:
                    # User skipped provider selection
                    display_info("No provider selected. Use /providers command to select one later.")
                    # Start chat loop without provider
                    self.provider = None
                    self.chat_session = None
                    self._chat_loop(show_welcome=False)
                    return
            
            # API key input flow (if not using saved)
            # Ollama doesn't require API key for local usage
            if api_key is None:  # Check for None, empty string is valid for Ollama
                if provider_name == "ollama":
                    # For Ollama, API key is optional (local usage)
                    api_key = self._input_api_key_optional()
                    if api_key is None:  # User cancelled
                        return
                    # Empty string is valid for local Ollama
                else:
                    api_key = self._input_api_key()
                    if not api_key:
                        return
            
            # Initialize provider
            self.provider = self._initialize_provider(provider_name, api_key)
            if not self.provider:
                return
            
            # Model discovery and selection flow (skip if using saved model)
            if saved_model:
                # Fetch models to get context_window info
                try:
                    models = asyncio.run(fetch_models(self.provider))
                    model = next((m for m in models if m.id == saved_model), None)
                    if not model:
                        # Create a basic model object if not found
                        model = type('Model', (), {'id': saved_model, 'name': saved_model, 'context_window': None})()
                except:
                    # Fallback if fetch fails
                    model = type('Model', (), {'id': saved_model, 'name': saved_model, 'context_window': None})()
            else:
                model = self._select_model()
                if not model:
                    return
                
                # Ask if user wants to save credentials with model
                save_creds = prompt_choice(
                    "Would you like to save these credentials for next time?",
                    ["Yes, save credentials", "No, use only for this session"]
                )
                
                if save_creds == "Yes, save credentials":
                    self.session_manager.save_credentials(provider_name, api_key, model.id)
                    display_success("Credentials saved securely")
            
            # Initialize chat session
            if model:
                self.chat_session = ChatSession(self.provider, model.id, model.context_window, self.tool_registry, self.skills_manager)
            else:
                # No model selected - create a placeholder session
                self.chat_session = None
            
            # Start chat loop (no initial message)
            self._chat_loop(show_welcome=False)
            
        except KeyboardInterrupt:
            print("\n\nExiting zeer. Goodbye!")
        except Exception as e:
            display_error(f"Unexpected error: {str(e)}")
        finally:
            # Clean up session
            self.session_manager.clear_session()
    
    def _select_provider(self) -> Optional[str]:
        """
        Handle provider selection with retry on invalid input.
        
        Returns:
            Selected provider name (lowercase), or None if user exits or skips
            
        Requirements: 2.1, 2.2, 2.3, 2.4
        """
        provider_options = [info["name"] for info in self.PROVIDERS.values()]
        provider_options.append("Skip for now")  # Add skip option
        
        while True:
            try:
                # Use searchable selection for providers
                from src.cli_interface import prompt_searchable_choice
                try:
                    selected_name = prompt_searchable_choice(
                        "Select an AI provider",
                        provider_options
                    )
                except KeyboardInterrupt:
                    display_info("Provider selection cancelled")
                    return None
                
                # Check if user selected skip
                if selected_name == "Skip for now":
                    display_info("Skipped provider selection. Starting with no provider.")
                    return None
                
                # Convert display name back to key
                for key, info in self.PROVIDERS.items():
                    if info["name"] == selected_name:
                        self.session_manager.store_provider(key)
                        display_success(f"Selected provider: {selected_name}")
                        return key
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return None
    
    def _input_api_key(self) -> Optional[str]:
        """
        Handle API key input with validation.
        
        Returns:
            Valid API key, or None if user exits
            
        Requirements: 3.1, 3.2, 3.4
        """
        provider_name = self.PROVIDERS[self.session_manager.get_provider()]["name"]
        
        while True:
            try:
                from colorama import Fore, Style
                print(f"\n{Fore.YELLOW}Enter your {provider_name} API key:{Style.RESET_ALL}")
                api_key = input(f"{Fore.CYAN}API Key:{Style.RESET_ALL} ").strip()
                
                if validate_api_key(api_key):
                    self.session_manager.store_api_key(api_key)
                    display_success("API key validated")
                    return api_key
                
                display_error("API key cannot be empty or contain only whitespace.")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return None
    
    def _input_api_key_optional(self) -> Optional[str]:
        """
        Handle optional API key input for Ollama (can be empty for local usage).
        
        Returns:
            API key (can be empty string for local), or None if user exits
        """
        from colorama import Fore, Style
        
        try:
            print(f"\n{Fore.YELLOW}Ollama API key (press Enter to skip for local usage):{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}Leave blank to use local Ollama server at http://localhost:11434{Style.RESET_ALL}")
            api_key = input(f"{Fore.CYAN}API Key (optional):{Style.RESET_ALL} ").strip()
            
            if api_key:
                self.session_manager.store_api_key(api_key, "ollama")
                display_success("API key saved for Ollama cloud")
            else:
                # Empty key is valid for local Ollama
                self.session_manager.store_api_key("", "ollama")
                display_success("Using local Ollama server")
            
            return api_key  # Can be empty string
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None
    
    def _initialize_provider(self, provider_name: str, api_key: str) -> Optional[AIProvider]:
        """
        Create and initialize a provider instance.
        
        Args:
            provider_name: The provider key (lowercase)
            api_key: The API key for authentication
            
        Returns:
            Initialized AIProvider instance, or None on failure
        """
        try:
            provider_class = self.PROVIDERS[provider_name]["class"]
            provider = provider_class(api_key)
            
            # For Ollama, check connection immediately and show helpful message
            if provider_name == "ollama":
                self._check_ollama_connection(provider)
            
            return provider
        except Exception as e:
            display_error(f"Failed to initialize provider: {str(e)}")
            return None
    
    def _check_ollama_connection(self, provider) -> None:
        """
        Check Ollama connection and show helpful setup messages.
        
        Args:
            provider: The Ollama provider instance
            
        Raises:
            Exception: If connection fails with helpful instructions
        """
        from colorama import Fore, Style
        from src.cli_interface import RunningIndicator
        
        # Show connecting indicator
        indicator = RunningIndicator()
        indicator.start()
        
        try:
            # Try to connect and list models
            asyncio.run(provider.validate_api_key())
            
            # Check if any models are available
            models = asyncio.run(provider.get_models())
            
            indicator.stop()
            
            if models:
                display_success(f"Connected to Ollama • {len(models)} model(s) available")
            else:
                # No models found
                print(f"\n{Fore.YELLOW}⚠ Ollama is running but no models found{Style.RESET_ALL}\n")
                print(f"{Fore.CYAN}Pull a model to get started:{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}1. ollama pull llama3.2{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}2. ollama pull mistral{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}3. ollama pull codellama{Style.RESET_ALL}")
                print(f"\n{Fore.LIGHTBLACK_EX}Browse models: https://ollama.ai/library{Style.RESET_ALL}\n")
                raise Exception("No models available. Pull a model first.")
                
        except Exception as e:
            indicator.stop()
            error_msg = str(e).lower()
            
            # Connection refused - Ollama not running
            if "connection" in error_msg or "refused" in error_msg:
                print(f"\n{Fore.YELLOW}⚠ Ollama is not installed or not running{Style.RESET_ALL}\n")
                print(f"{Fore.CYAN}Setup:{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}1. Download and install Ollama from: {Fore.BLUE}https://ollama.ai{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}2. Open the Ollama app (it will start automatically){Style.RESET_ALL}")
                print(f"  {Fore.WHITE}3. Pull a model: {Fore.GREEN}ollama pull llama3.2{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}4. Restart zeer and select Ollama{Style.RESET_ALL}\n")
                raise Exception("Ollama not installed or not running.")
            
            # Unauthorized - needs login for cloud models
            elif "unauthorized" in error_msg or "authentication" in error_msg or "ollama_error" in error_msg:
                print(f"\n{Fore.YELLOW}⚠ Authentication required{Style.RESET_ALL}\n")
                print(f"{Fore.CYAN}To use cloud models:{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}1. Download and install Ollama: {Fore.BLUE}https://ollama.ai{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}2. Open Ollama app and sign in{Style.RESET_ALL}")
                print(f"  {Fore.WHITE}3. Restart zeer and select Ollama{Style.RESET_ALL}\n")
                raise Exception("Please install Ollama app and sign in.")
            
            # No models available
            elif "no models" in error_msg:
                raise e
            
            # Other errors
            else:
                raise e
    
    def _select_model(self) -> Optional[Model]:
        """
        Handle model discovery and selection with error handling and retry.
        
        Returns:
            Selected Model object, or None if user exits or skips
            
        Requirements: 4.2, 5.1, 5.2, 5.3, 5.4
        """
        while True:
            try:
                # Fetch models with loading indicator
                from src.cli_interface import RunningIndicator
                indicator = RunningIndicator()
                indicator.start()
                
                try:
                    models = asyncio.run(fetch_models(self.provider))
                finally:
                    indicator.stop()
                
                if not models:
                    display_error("No models available from this provider.")
                    return None
                
                # Create model options for selection
                # Put custom option at the top in purple
                model_options = []
                
                # Add custom model option at the top (will be colored in the UI)
                from colorama import Fore, Style
                model_options.append(f"{Fore.MAGENTA}Enter custom model ID{Style.RESET_ALL}")
                
                # For Ollama, name and id are the same, so show description if available
                for m in models:
                    if m.name == m.id:
                        # Same name and id (like Ollama), show with description if available
                        if m.description:
                            model_options.append(f"{m.id} - {m.description}")
                        else:
                            model_options.append(m.id)
                    else:
                        # Different name and id (like other providers)
                        model_options.append(f"{m.name} ({m.id})")
                
                model_options.append("Skip for now")  # Add skip option at the end
                
                # Use searchable prompt for model selection (better for large lists)
                from src.cli_interface import prompt_searchable_choice
                try:
                    selected_option = prompt_searchable_choice(
                        "Select a model (type to search)",
                        model_options,
                        "e.g., 'free', 'gpt', 'claude'..."
                    )
                except KeyboardInterrupt:
                    display_info("Model selection cancelled")
                    return None
                
                # Check if user selected skip
                if selected_option == "Skip for now":
                    display_info("Skipped model selection. You can select a model later using /models command.")
                    return None
                
                # Check if user wants to enter custom model ID (strip color codes for comparison)
                if "Enter custom model ID" in selected_option:
                    print(f"\n{Fore.CYAN}Enter model ID (e.g., gemini-3.1-pro-preview):{Style.RESET_ALL}")
                    custom_id = input("> ").strip()
                    if custom_id:
                        # Validate the model before saving
                        provider_name = self.session_manager.get_provider()
                        
                        if provider_name == "ollama":
                            # For Ollama, check if model is available using show()
                            try:
                                from src.cli_interface import RunningIndicator
                                indicator = RunningIndicator()
                                indicator.start()
                                
                                try:
                                    from ollama import Client
                                    client = Client(host="http://localhost:11434")
                                    client.show(custom_id)
                                    indicator.stop()
                                    display_success(f"Model '{custom_id}' is available")
                                except Exception as show_error:
                                    indicator.stop()
                                    error_msg = str(show_error).lower()
                                    
                                    if "not found" in error_msg or "does not exist" in error_msg:
                                        if ":cloud" in custom_id:
                                            print(f"\n{Fore.YELLOW}⚠ Model '{custom_id}' not available{Style.RESET_ALL}\n")
                                            print(f"{Fore.CYAN}To use this model:{Style.RESET_ALL}")
                                            print(f"  {Fore.WHITE}1. Run: {Fore.GREEN}ollama run {custom_id}{Style.RESET_ALL}")
                                            print(f"  {Fore.WHITE}2. Restart zeer{Style.RESET_ALL}\n")
                                        else:
                                            print(f"\n{Fore.YELLOW}⚠ Model '{custom_id}' not found{Style.RESET_ALL}\n")
                                            print(f"{Fore.CYAN}To use this model:{Style.RESET_ALL}")
                                            print(f"  {Fore.WHITE}1. Pull: {Fore.GREEN}ollama pull {custom_id}{Style.RESET_ALL}")
                                            print(f"  {Fore.WHITE}2. Restart zeer{Style.RESET_ALL}\n")
                                        continue
                            except Exception:
                                pass
                        
                        elif provider_name in ["openai", "gemini", "claude", "openrouter"]:
                            # For other providers, try a test message to validate
                            try:
                                from src.cli_interface import RunningIndicator
                                indicator = RunningIndicator()
                                indicator.start()
                                
                                try:
                                    # Create a test context with minimal message
                                    test_context = ChatContext(
                                        messages=[Message(role="user", content="test")],
                                        model=custom_id,
                                        provider=provider_name
                                    )
                                    # Try to send a test message
                                    asyncio.run(self.provider.send_message("test", test_context))
                                    indicator.stop()
                                    display_success(f"Model '{custom_id}' is available")
                                except Exception as test_error:
                                    indicator.stop()
                                    error_msg = str(test_error).lower()
                                    
                                    if "not found" in error_msg or "does not exist" in error_msg or "invalid" in error_msg:
                                        print(f"\n{Fore.YELLOW}⚠ Model '{custom_id}' not found{Style.RESET_ALL}\n")
                                        print(f"{Fore.CYAN}Please check:{Style.RESET_ALL}")
                                        print(f"  {Fore.WHITE}1. Model ID is correct{Style.RESET_ALL}")
                                        print(f"  {Fore.WHITE}2. You have access to this model{Style.RESET_ALL}")
                                        print(f"  {Fore.WHITE}3. Your API key has proper permissions{Style.RESET_ALL}\n")
                                        continue
                            except Exception:
                                pass
                        
                        # Create a custom model object
                        custom_model = Model(
                            id=custom_id,
                            name=custom_id,
                            description="Custom model",
                            context_window=1000000  # Default to 1M tokens
                        )
                        self.session_manager.store_model(custom_model.id)
                        display_success(f"Selected custom model: {custom_model.name}")
                        return custom_model
                    else:
                        display_error("Model ID cannot be empty")
                        continue
                
                # Find the selected model by matching the display text
                selected_model = None
                for m in models:
                    # Check if this model matches the selected option
                    if m.name == m.id:
                        # Ollama format
                        if m.description:
                            if selected_option == f"{m.id} - {m.description}":
                                selected_model = m
                                break
                        else:
                            if selected_option == m.id:
                                selected_model = m
                                break
                    else:
                        # Other providers format
                        if selected_option == f"{m.name} ({m.id})":
                            selected_model = m
                            break
                
                if not selected_model:
                    display_error("Could not find selected model")
                    continue
                
                self.session_manager.store_model(selected_model.id)
                display_success(f"Selected model: {selected_model.name}")
                return selected_model
                
            except requests.exceptions.HTTPError as e:
                message, recoverable = handle_api_error(e)
                display_error(message)
                
                if recoverable:
                    retry = input("\nWould you like to retry? (y/n): ").strip().lower()
                    if retry != 'y':
                        return None
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                message, recoverable = handle_network_error(e)
                display_error(message)
                
                if recoverable:
                    retry = input("\nWould you like to retry? (y/n): ").strip().lower()
                    if retry != 'y':
                        return None
                else:
                    return None
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return None
            except Exception as e:
                display_error(f"Unexpected error: {str(e)}")
                return None
    
    def _chat_loop(self, show_welcome: bool = True) -> None:
        """
        Run the interactive chat loop.
        
        Handles user input, message transmission, response display, and exit commands.
        Supports Ctrl+C, 'exit' command, and slash commands.
        
        Args:
            show_welcome: Whether to show the welcome message (only on first load)
        
        Requirements: 6.1, 6.5, 6.6
        """
        from colorama import Fore, Style
        import time
        
        # Track last Ctrl+C time for double-press exit
        last_ctrl_c_time = 0
        ctrl_c_timeout = 2.0  # 2 seconds to press again
        
        if show_welcome:
            display_separator()
            print(f"{Fore.CYAN}Type your messages or press / for commands{Style.RESET_ALL}")
            display_separator()
        
        while True:
            try:
                # Get user input with automatic slash detection
                user_message, is_slash = display_input_prompt_with_slash_detection()
                
                # If slash command was selected from menu
                if is_slash:
                    if not user_message:
                        # User cancelled
                        continue
                    # Process the command
                    command = user_message.lower()
                else:
                    command = user_message.lower() if user_message.startswith('/') else None
                
                # Handle slash commands
                if command and command.startswith('/'):
                    
                    if command in ['/exit', '/quit']:
                        print(f"\n{Fore.CYAN}Exiting chat. Goodbye!{Style.RESET_ALL}")
                        break
                    
                    elif command == '/clear':
                        clear_screen()
                        display_branding()
                        if self.chat_session:
                            self.chat_session.clear_history()
                        display_success("Conversation history cleared")
                        continue
                    
                    elif command == '/reset':
                        # Confirm reset
                        from src.cli_interface import prompt_choice
                        print()
                        confirm = prompt_choice(
                            "This will clear conversation history AND delete all saved credentials. Continue?",
                            ["Yes, reset everything", "Cancel"]
                        )
                        
                        if confirm == "Yes, reset everything":
                            clear_screen()
                            display_branding()
                            
                            # Clear conversation history
                            if self.chat_session:
                                self.chat_session.clear_history()
                            
                            # Delete saved credentials
                            self.session_manager.delete_saved_credentials()
                            
                            # Clear session
                            self.session_manager.clear_session()
                            
                            # Reset provider and chat session
                            self.provider = None
                            self.chat_session = None
                            
                            display_success("Everything reset. All credentials deleted.")
                            print(f"\n{Fore.YELLOW}Use {Fore.CYAN}/providers{Fore.YELLOW} to select a provider and start chatting.{Style.RESET_ALL}\n")
                        else:
                            display_info("Reset cancelled")
                        continue
                    
                    elif command == '/models':
                        print()
                        try:
                            # Check if provider exists
                            if not self.provider:
                                display_error("No provider selected. Please select a provider first.")
                                print(f"\n{Fore.YELLOW}Use {Fore.CYAN}/providers{Fore.YELLOW} command to select a provider.{Style.RESET_ALL}\n")
                                continue
                            
                            # Confirm if there's an existing chat session
                            if self.chat_session and self.chat_session.get_message_count() > 2:  # More than system messages
                                print(f"{Fore.YELLOW}⚠ Warning: Changing models will clear your current chat session.{Style.RESET_ALL}")
                                confirm = input(f"{Fore.CYAN}Continue? (y/n):{Style.RESET_ALL} ").strip().lower()
                                if confirm != 'y' and confirm != 'yes':
                                    display_info("Cancelled. Keeping current model.")
                                    continue
                            
                            model = self._select_model()
                            if model:
                                self.chat_session = ChatSession(self.provider, model.id, model.context_window, self.tool_registry, self.skills_manager)
                                # Update saved model
                                self.session_manager.save_credentials(
                                    self.session_manager.get_provider(),
                                    self.session_manager.get_api_key(),
                                    model.id
                                )
                        except KeyboardInterrupt:
                            # ESC pressed - go back to chat
                            display_info("Cancelled. Returning to chat...")
                        continue
                    
                    elif command == '/providers':
                        print()
                        try:
                            provider_name = self._select_provider()
                            if provider_name:
                                # Check if we already have API key for this provider in memory or saved
                                api_key = self.session_manager.get_api_key(provider_name)
                                
                                # For Ollama, empty string is valid (local usage)
                                has_valid_key = (provider_name == "ollama" and api_key == "") or (api_key and api_key.strip())
                                
                                if not has_valid_key:
                                    # Check saved credentials
                                    saved_creds = self.session_manager.load_saved_credentials()
                                    if saved_creds and 'providers' in saved_creds and provider_name in saved_creds['providers']:
                                        api_key = saved_creds['providers'][provider_name].get('api_key')
                                        if api_key or (provider_name == "ollama" and api_key == ""):
                                            self.session_manager.store_api_key(api_key, provider_name)
                                            display_success(f"Using saved API key for {self.PROVIDERS[provider_name]['name']}")
                                            has_valid_key = True
                                
                                if not has_valid_key:
                                    # Ask for API key (optional for Ollama)
                                    if provider_name == "ollama":
                                        api_key = self._input_api_key_optional()
                                        if api_key is None:  # User cancelled
                                            continue
                                        # Empty string is valid for local Ollama
                                    else:
                                        api_key = self._input_api_key()
                                
                                if api_key is not None:  # Check for None (cancelled), empty string is valid for Ollama
                                    self.provider = self._initialize_provider(provider_name, api_key)
                                    if self.provider:
                                        model = self._select_model()
                                        if model:
                                            self.chat_session = ChatSession(self.provider, model.id, model.context_window, self.tool_registry, self.skills_manager)
                                            # Save new credentials
                                            self.session_manager.save_credentials(provider_name, api_key, model.id)
                        except KeyboardInterrupt:
                            # ESC pressed - go back to chat
                            display_info("Cancelled. Returning to chat...")
                        continue
                    
                    elif command == '/help':
                        print(f"\n{Fore.CYAN}Available commands:{Style.RESET_ALL}")
                        print(f"  {Fore.YELLOW}/models{Style.RESET_ALL}    - Switch to a different model")
                        print(f"  {Fore.YELLOW}/providers{Style.RESET_ALL} - Switch to a different provider")
                        print(f"  {Fore.YELLOW}/clear{Style.RESET_ALL}     - Clear conversation history")
                        print(f"  {Fore.YELLOW}/reset{Style.RESET_ALL}     - Reset everything (history + saved credentials)")
                        print(f"  {Fore.YELLOW}/skills{Style.RESET_ALL}    - List available agent skills")
                        print(f"  {Fore.YELLOW}/tools{Style.RESET_ALL}     - List available tools")
                        print(f"  {Fore.YELLOW}/servers{Style.RESET_ALL}   - Show running background servers")
                        print(f"  {Fore.YELLOW}/mode{Style.RESET_ALL}      - Toggle execution mode (deliberate/fast)")
                        print(f"  {Fore.YELLOW}/exit{Style.RESET_ALL}      - Exit the application")
                        print(f"  {Fore.YELLOW}/help{Style.RESET_ALL}      - Show this help message")
                        print(f"  {Fore.YELLOW}/{Style.RESET_ALL}          - Show command menu\n")
                        continue
                    
                    elif command == '/skills':
                        self._display_skills()
                        continue
                    
                    elif command == '/tools':
                        self._display_tools()
                        continue
                    
                    elif command == '/servers':
                        self._display_servers()
                        continue
                    
                    elif command == '/mode':
                        self._toggle_execution_mode()
                        continue
                    
                    else:
                        display_error(f"Unknown command: {user_message}. Type / for available commands.")
                        continue
                
                # Check for exit command (without slash)
                if user_message.lower() in ['exit', 'quit', 'bye']:
                    print(f"\n{Fore.CYAN}Exiting chat. Goodbye!{Style.RESET_ALL}")
                    break
                
                # Skip empty messages
                if not user_message:
                    continue
                
                # Check if no model is selected
                if not self.chat_session:
                    display_error("No model selected. Please select a provider and model first.")
                    print(f"\n{Fore.YELLOW}Use {Fore.CYAN}/providers{Fore.YELLOW} to select a provider, then {Fore.CYAN}/models{Fore.YELLOW} to select a model.{Style.RESET_ALL}\n")
                    continue
                
                # Display user message (just spacing, no duplicate text)
                display_user_message(user_message)
                
                # Start running indicator
                indicator = RunningIndicator()
                indicator.start()
                
                try:
                    # Send message and get response (pass indicator for control during tool execution)
                    response = asyncio.run(self.chat_session.send_message(user_message, indicator))
                    
                    # Stop indicator and get elapsed time
                    elapsed_time = indicator.stop()
                    
                    # Check if user cancelled during thinking
                    if indicator.is_cancelled():
                        print(f"{Fore.YELLOW}✗ Operation cancelled{Style.RESET_ALL}\n")
                        continue
                    
                    # Handle generated images if any
                    if response.images:
                        saved_paths = save_images(response.images)
                        for path in saved_paths:
                            display_image_in_terminal(path)
                    
                    # Display assistant response with metadata
                    display_assistant_message(
                        response.content,
                        self.session_manager.get_model(),
                        response.usage,
                        elapsed_time,
                        self.chat_session.context_window
                    )
                except KeyboardInterrupt:
                    # Stop indicator and cancel operation, but don't exit
                    indicator.stop()
                    # Small delay to ensure cancellation message is visible
                    import time
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    # Make sure to stop indicator on error
                    indicator.stop()
                    raise  # Re-raise the exception to be handled below
                
            except requests.exceptions.HTTPError as e:
                message, recoverable = handle_api_error(e)
                display_error(message)
                # Don't exit - let user continue
                print(f"\n{Fore.YELLOW}You can try again or use /help for commands.{Style.RESET_ALL}\n")
                    
            except requests.exceptions.RequestException as e:
                message, recoverable = handle_network_error(e)
                display_error(message)
                # Don't exit - let user continue
                print(f"\n{Fore.YELLOW}You can try again or use /help for commands.{Style.RESET_ALL}\n")
                    
            except KeyboardInterrupt:
                # Double Ctrl+C to exit
                current_time = time.time()
                if current_time - last_ctrl_c_time < ctrl_c_timeout:
                    # Second Ctrl+C within timeout - exit
                    print(f"\n\n{Fore.CYAN}Exiting chat...{Style.RESET_ALL}")
                    break
                else:
                    # First Ctrl+C - show temporary message below input area
                    last_ctrl_c_time = current_time
                    import sys
                    
                    # Show message
                    sys.stdout.write(f"\n{Fore.YELLOW}Press Ctrl+C again within 2 seconds to exit{Style.RESET_ALL}")
                    sys.stdout.flush()
                    
                    # Wait 2 seconds
                    time.sleep(2.0)
                    
                    # Clear the message line
                    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
                    sys.stdout.write('\033[F')  # Move up one line
                    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear that line too
                    sys.stdout.flush()
                    
                    # Reset the timer since 2 seconds passed
                    last_ctrl_c_time = 0
                    continue
                
            except Exception as e:
                display_error(str(e))
                # Make all errors recoverable - don't exit
                print(f"\n{Fore.YELLOW}You can continue chatting or use /help for commands.{Style.RESET_ALL}\n")
    
    def _display_skills(self) -> None:
        """Display available agent skills in a grid format."""
        from rich.console import Console
        from rich.columns import Columns
        from rich.panel import Panel
        
        console = Console()
        skills = self.skills_manager.list_skills()
        
        if not skills:
            console.print("[yellow]No skills available. Create skills in the 'skills/' directory.[/yellow]")
            return
        
        console.print("\n[cyan bold]Available Agent Skills[/cyan bold]\n")
        
        # Create panels for each skill
        skill_panels = []
        for skill in skills:
            panel = Panel(
                f"[yellow]{skill.name}[/yellow]",
                border_style="cyan",
                padding=(0, 1)
            )
            skill_panels.append(panel)
        
        # Display in columns (grid layout)
        columns = Columns(skill_panels, equal=True, expand=True)
        console.print(columns)
        
        console.print(f"\n[dim]Total: {len(skills)} skills • agentskills.io specification[/dim]\n")
    
    def _display_tools(self) -> None:
        """Display available tools in a table format."""
        from rich.table import Table
        from rich.console import Console
        
        console = Console()
        tools = self.tool_registry.list_tools()
        
        # Create table
        table = Table(title="[cyan]Available Tools[/cyan]", show_header=True, header_style="bold cyan")
        table.add_column("Tool", style="yellow", width=25)
        table.add_column("Description", style="white", width=60)
        
        for tool in tools:
            # Truncate description if too long
            desc = tool.description[:120] + "..." if len(tool.description) > 120 else tool.description
            table.add_row(tool.name, desc)
        
        console.print()
        console.print(table)
        console.print()
        console.print(f"[dim]Total: {len(tools)} tools available[/dim]\n")
        print(f"{Fore.LIGHTBLACK_EX}Tools can be called by AI agents during conversations{Style.RESET_ALL}\n")
    
    def _display_servers(self) -> None:
        """Display running background servers."""
        from rich.table import Table
        from rich.console import Console
        from src.process_manager import get_process_manager
        
        console = Console()
        manager = get_process_manager()
        processes = manager.list_processes()
        
        if not processes:
            console.print()
            console.print(f"[yellow]No servers currently running[/yellow]\n")
            return
        
        # Create table
        table = Table(title="[cyan]Running Background Servers[/cyan]", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="yellow", width=20)
        table.add_column("Status", style="green", width=10)
        table.add_column("URL", style="cyan", width=30)
        table.add_column("Started", style="white", width=15)
        table.add_column("ID", style="dim", width=10)
        
        for proc in processes:
            # Check if process is still running
            status = "running" if proc.process.poll() is None else "stopped"
            status_color = "green" if status == "running" else "red"
            
            # Format start time
            start_time = proc.started_at.strftime('%H:%M:%S')
            
            # Get URL or show N/A
            url = proc.url if proc.url else "N/A"
            
            table.add_row(
                proc.name,
                f"[{status_color}]{status}[/{status_color}]",
                url,
                start_time,
                proc.id
            )
        
        console.print()
        console.print(table)
        console.print()
        console.print(f"[dim]Total: {len(processes)} server(s) running[/dim]")
        console.print(f"[dim]Use 'stop server' in chat to stop a server[/dim]\n")
    
    def _toggle_execution_mode(self) -> None:
        """Toggle between deliberate and fast execution modes."""
        from src.config import get_config
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        config = get_config()
        
        current_mode = config.get("execution_mode", "deliberate")
        
        # Show current mode and options
        print()
        console.print(Panel(
            f"[cyan]Current mode:[/cyan] [yellow]{current_mode}[/yellow]\n\n"
            f"[cyan]Deliberate mode:[/cyan] Creates files one-by-one with pauses for better quality\n"
            f"[cyan]Fast mode:[/cyan] Creates all files at once for maximum speed",
            title="[bold cyan]Execution Mode[/bold cyan]",
            border_style="cyan"
        ))
        
        # Ask user to select mode
        choice = prompt_choice(
            "Select execution mode",
            ["Deliberate (recommended for quality)", "Fast (maximum speed)", "Cancel"]
        )
        
        if choice == "Cancel":
            display_info("Mode unchanged")
            return
        
        # Update config
        if "Deliberate" in choice:
            config.set("execution_mode", "deliberate")
            display_success("Switched to deliberate mode - files will be created thoughtfully")
        else:
            config.set("execution_mode", "fast")
            display_success("Switched to fast mode - files will be created quickly")
        
        print()
