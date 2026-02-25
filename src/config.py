"""
Configuration module for zeer CLI.

This module manages application settings and preferences.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages zeer CLI configuration."""
    
    DEFAULT_CONFIG = {
        "execution_mode": "deliberate",  # "deliberate" or "fast"
        "max_tools_per_batch": 3,  # For deliberate mode
        "file_creation_delay": 0.3,  # Seconds between file creations
        "show_progress": True,  # Show detailed progress during execution
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager."""
        if config_path is None:
            config_path = Path.home() / ".zeer" / "config.json"
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception:
                # If loading fails, use defaults
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config
            return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
        self.save()
    
    def is_deliberate_mode(self) -> bool:
        """Check if deliberate execution mode is enabled."""
        return self.get("execution_mode") == "deliberate"
    
    def get_max_tools_per_batch(self) -> int:
        """Get maximum tools per batch for deliberate mode."""
        return self.get("max_tools_per_batch", 3)
    
    def get_file_creation_delay(self) -> float:
        """Get delay between file creations in seconds."""
        return self.get("file_creation_delay", 0.3)


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
