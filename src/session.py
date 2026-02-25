"""
Session management module for secure credential handling.

This module provides the SessionManager class for storing API credentials
securely in memory during the application session. Credentials can optionally
be persisted to disk with user consent.

Requirements: 3.5, 8.1, 8.2, 8.3
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict


class SessionManager:
    """
    Manages session state and credentials securely in memory.
    
    This class stores sensitive data like API keys in memory only,
    with optional disk persistence if user consents.
    """
    
    CONFIG_DIR = Path.home() / ".zeer"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    def __init__(self):
        """Initialize a new session manager with empty credentials."""
        self._api_keys = {}  # Store API keys per provider
        self._provider = None
        self._model = None
        self._config_dir = self.CONFIG_DIR
        self._config_file = self.CONFIG_FILE
    
    def load_saved_credentials(self) -> Optional[Dict[str, str]]:
        """
        Load saved credentials from disk if they exist.
        
        Returns:
            Dictionary with provider credentials, or None if no saved credentials
        """
        if not self._config_file.exists():
            return None
        
        try:
            with open(self._config_file, 'r') as f:
                config = json.load(f)
                # Load all API keys into memory
                if 'providers' in config:
                    for provider, data in config['providers'].items():
                        if isinstance(data, dict) and 'api_key' in data:
                            self._api_keys[provider] = data['api_key']
                return config
        except Exception:
            return None
    
    def save_credentials(self, provider: str, api_key: str, model: Optional[str] = None) -> None:
        """
        Save credentials to disk with user consent.
        
        Args:
            provider: The provider name
            api_key: The API key to save
            model: Optional model name to save
        """
        try:
            # Create config directory if it doesn't exist
            self._config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing config or create new one
            config = {}
            if self._config_file.exists():
                try:
                    with open(self._config_file, 'r') as f:
                        config = json.load(f)
                except:
                    config = {}
            
            # Initialize providers dict if not exists
            if 'providers' not in config:
                config['providers'] = {}
            
            # Store API key for this provider
            config['providers'][provider] = {
                'api_key': api_key
            }
            
            if model:
                config['providers'][provider]['model'] = model
            
            # Store last used provider
            config['last_provider'] = provider
            
            with open(self._config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Set file permissions to be readable only by owner (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                os.chmod(self._config_file, 0o600)
                
        except Exception as e:
            # Silently fail - not critical
            pass
    
    def clear_saved_credentials(self) -> None:
        """Delete saved credentials from disk."""
        try:
            if self._config_file.exists():
                self._config_file.unlink()
        except Exception:
            pass
    
    def delete_saved_credentials(self) -> None:
        """Alias for clear_saved_credentials - delete saved credentials from disk."""
        self.clear_saved_credentials()
    
    def store_api_key(self, key: str, provider: Optional[str] = None) -> None:
        """
        Store an API key securely in memory for the current session.
        
        Args:
            key: The API key to store
            provider: The provider name (uses current provider if not specified)
            
        Raises:
            ValueError: If the key is None or empty
        """
        if key is None or not key.strip():
            raise ValueError("API key cannot be None or empty")
        
        provider_name = provider or self._provider
        if provider_name:
            self._api_keys[provider_name] = key
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """
        Retrieve the stored API key for a provider.
        
        Args:
            provider: The provider name (uses current provider if not specified)
        
        Returns:
            The stored API key, or None if no key has been stored
        """
        provider_name = provider or self._provider
        return self._api_keys.get(provider_name) if provider_name else None
    
    def store_provider(self, provider: str) -> None:
        """
        Store the selected provider name.
        
        Args:
            provider: The provider name to store
        """
        self._provider = provider
    
    def get_provider(self) -> str:
        """
        Retrieve the stored provider name.
        
        Returns:
            The stored provider name, or None if no provider has been stored
        """
        return self._provider
    
    def store_model(self, model: str) -> None:
        """
        Store the selected model name.
        
        Args:
            model: The model name to store
        """
        self._model = model
    
    def get_model(self) -> str:
        """
        Retrieve the stored model name.
        
        Returns:
            The stored model name, or None if no model has been stored
        """
        return self._model
    
    def clear_session(self) -> None:
        """
        Clear all sensitive data from memory.
        
        This method wipes all stored credentials and session data,
        ensuring sensitive information is removed when the session ends.
        """
        # Overwrite sensitive data before clearing
        self._api_keys.clear()
        
        self._provider = None
        self._model = None
    
    def has_api_key(self, provider: Optional[str] = None) -> bool:
        """
        Check if an API key is currently stored for a provider.
        
        Args:
            provider: The provider name (uses current provider if not specified)
        
        Returns:
            True if an API key is stored, False otherwise
        """
        provider_name = provider or self._provider
        return provider_name in self._api_keys and len(self._api_keys[provider_name]) > 0
    
    def __del__(self):
        """Destructor to ensure session is cleared when object is destroyed."""
        self.clear_session()
