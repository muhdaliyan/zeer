#!/usr/bin/env python3
"""
Startup script for zeer Telegram bot.

This script loads configuration from .env file and starts the Telegram bot.
"""

import os
import sys
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded configuration from .env file")
except ImportError:
    print("Note: python-dotenv not installed. Using environment variables only.")
    print("Install with: pip install python-dotenv")

# Import the bot
from src.telegram_bot import TelegramBot


def main():
    """Start the Telegram bot with configuration."""
    
    print("\n" + "="*60)
    print("zeer Telegram Bot")
    print("="*60 + "\n")
    
    # Get configuration
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    provider_name = os.getenv("AI_PROVIDER", "gemini")
    api_key = os.getenv("AI_API_KEY")
    model_id = os.getenv("AI_MODEL", "gemini-1.5-flash")
    
    # Validate configuration
    if not telegram_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found")
        print("\nPlease set up your configuration:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your tokens")
        print("3. Run this script again")
        print("\nOr set environment variables:")
        print("  export TELEGRAM_BOT_TOKEN=your_token")
        print("  export AI_PROVIDER=gemini")
        print("  export AI_API_KEY=your_api_key")
        print("  export AI_MODEL=gemini-1.5-flash")
        sys.exit(1)
    
    if not api_key:
        print("❌ Error: AI_API_KEY not found")
        print("\nPlease add your AI provider API key to .env file")
        sys.exit(1)
    
    # Display configuration
    print("Configuration:")
    print(f"  Provider: {provider_name}")
    print(f"  Model: {model_id}")
    print(f"  Token: {telegram_token[:10]}...{telegram_token[-4:]}")
    print()
    
    # Create and run bot
    try:
        bot = TelegramBot(telegram_token, provider_name, api_key, model_id)
        print("✓ Bot initialized successfully")
        print("\n🤖 Bot is now running...")
        print("Press Ctrl+C to stop\n")
        bot.run()
    except KeyboardInterrupt:
        print("\n\n✓ Bot stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
