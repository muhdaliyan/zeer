"""
Messaging Platforms Manager for zeer CLI

This module manages configuration for messaging platforms like Telegram, WhatsApp, Slack, Discord.
"""

import os
import json
from typing import Optional, Dict, List
from pathlib import Path


class MessagingPlatformsManager:
    """Manages messaging platform configurations."""
    
    CONFIG_DIR = Path.home() / ".zeer"
    CONFIG_FILE = CONFIG_DIR / "messaging_platforms.json"
    
    PLATFORMS = {
        "telegram": {
            "name": "Telegram",
            "description": "Chat with your assistant via Telegram bot",
            "fields": {
                "bot_token": {
                    "label": "Bot Token (from @BotFather)",
                    "secret": True,
                    "required": True
                }
            },
            "status": "available"
        },
        "whatsapp": {
            "name": "WhatsApp",
            "description": "Chat with your assistant via WhatsApp",
            "fields": {
                "phone_number": {
                    "label": "Phone Number",
                    "secret": False,
                    "required": True
                },
                "api_key": {
                    "label": "WhatsApp Business API Key",
                    "secret": True,
                    "required": True
                }
            },
            "status": "coming_soon"
        },
        "slack": {
            "name": "Slack",
            "description": "Chat with your assistant via Slack bot",
            "fields": {
                "bot_token": {
                    "label": "Bot Token",
                    "secret": True,
                    "required": True
                },
                "app_token": {
                    "label": "App Token",
                    "secret": True,
                    "required": True
                }
            },
            "status": "coming_soon"
        },
        "discord": {
            "name": "Discord",
            "description": "Chat with your assistant via Discord bot",
            "fields": {
                "bot_token": {
                    "label": "Bot Token",
                    "secret": True,
                    "required": True
                }
            },
            "status": "coming_soon"
        }
    }
    
    def __init__(self):
        """Initialize the messaging platforms manager."""
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict:
        """Load the messaging platforms configuration."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_config(self, config: Dict) -> bool:
        """Save the messaging platforms configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_platform_config(self, platform: str) -> Optional[Dict]:
        """Get configuration for a specific platform."""
        config = self.load_config()
        return config.get(platform)
    
    def set_platform_config(self, platform: str, platform_config: Dict) -> bool:
        """Set configuration for a specific platform."""
        config = self.load_config()
        config[platform] = platform_config
        return self.save_config(config)
    
    def is_platform_configured(self, platform: str) -> bool:
        """Check if a platform is configured."""
        platform_config = self.get_platform_config(platform)
        if not platform_config:
            return False
        
        # Check if all required fields are present
        platform_def = self.PLATFORMS.get(platform, {})
        fields = platform_def.get("fields", {})
        
        for field_name, field_def in fields.items():
            if field_def.get("required") and not platform_config.get(field_name):
                return False
        
        return True
    
    def list_platforms(self) -> List[Dict]:
        """List all available platforms with their status."""
        platforms = []
        config = self.load_config()
        
        for platform_id, platform_def in self.PLATFORMS.items():
            is_configured = self.is_platform_configured(platform_id)
            platforms.append({
                "id": platform_id,
                "name": platform_def["name"],
                "description": platform_def["description"],
                "status": platform_def["status"],
                "configured": is_configured
            })
        
        return platforms
    
    def remove_platform_config(self, platform: str) -> bool:
        """Remove configuration for a specific platform."""
        config = self.load_config()
        if platform in config:
            del config[platform]
            return self.save_config(config)
        return False
