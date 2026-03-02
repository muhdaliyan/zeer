#!/usr/bin/env python3
"""
Telegram Bot Integration for zeer CLI

This module provides a Telegram bot interface to interact with the zeer AI assistant.
Users can chat with the assistant through Telegram messages.
"""

import asyncio
import logging
import os
from typing import Optional, Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.chat_session import ChatSession
from src.provider_base import AIProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.claude_provider import ClaudeProvider
from src.providers.openrouter_provider import OpenRouterProvider
from src.providers.ollama_provider import OllamaProvider
from src.tools import create_default_registry
from src.skills_manager import SkillsManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot that interfaces with zeer AI assistant."""
    
    PROVIDERS = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider
    }
    
    def __init__(self, telegram_token: str, provider_name: str, api_key: str, model_id: str):
        """
        Initialize the Telegram bot.
        
        Args:
            telegram_token: Telegram bot token from BotFather
            provider_name: AI provider name (openai, gemini, claude, etc.)
            api_key: API key for the AI provider
            model_id: Model ID to use
        """
        self.telegram_token = telegram_token
        self.provider_name = provider_name
        self.api_key = api_key
        self.model_id = model_id
        
        # Initialize AI components
        self.tool_registry = create_default_registry()
        self.skills_manager = SkillsManager("skills")
        
        # User sessions: {user_id: ChatSession}
        self.user_sessions: Dict[int, ChatSession] = {}
        
        # Initialize provider
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> Optional[AIProvider]:
        """Initialize the AI provider."""
        try:
            provider_class = self.PROVIDERS.get(self.provider_name.lower())
            if not provider_class:
                logger.error(f"Unknown provider: {self.provider_name}")
                return None
            
            provider = provider_class(self.api_key)
            logger.info(f"Initialized provider: {self.provider_name}")
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            return None
    
    def _get_or_create_session(self, user_id: int) -> Optional[ChatSession]:
        """Get or create a chat session for a user."""
        if user_id not in self.user_sessions:
            if not self.provider:
                return None
            
            # Create new session for this user
            self.user_sessions[user_id] = ChatSession(
                self.provider,
                self.model_id,
                context_window=None,
                tool_registry=self.tool_registry,
                skills_manager=self.skills_manager
            )
            logger.info(f"Created new session for user {user_id}")
        
        return self.user_sessions[user_id]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_message = (
            f"👋 Hello {user.first_name}!\n\n"
            f"I'm your zeer AI assistant powered by {self.provider_name.title()}.\n\n"
            f"Commands:\n"
            f"/start - Show this message\n"
            f"/clear - Clear conversation history\n"
            f"/help - Show help\n\n"
            f"Just send me a message to start chatting!"
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "🤖 zeer AI Assistant\n\n"
            "Available commands:\n"
            "/start - Start the bot\n"
            "/clear - Clear your conversation history\n"
            "/help - Show this help message\n\n"
            "Features:\n"
            "• Natural language conversations\n"
            "• Tool calling capabilities\n"
            "• Extensible skills system\n"
            "• Context-aware responses\n\n"
            "Just send me any message and I'll help you!"
        )
        await update.message.reply_text(help_message)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command."""
        user_id = update.effective_user.id
        
        if user_id in self.user_sessions:
            # Clear the session
            self.user_sessions[user_id] = ChatSession(
                self.provider,
                self.model_id,
                context_window=None,
                tool_registry=self.tool_registry,
                skills_manager=self.skills_manager
            )
            await update.message.reply_text("✅ Conversation history cleared!")
        else:
            await update.message.reply_text("No conversation history to clear.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Get or create session
        session = self._get_or_create_session(user_id)
        if not session:
            await update.message.reply_text(
                "❌ Sorry, the AI provider is not available. Please check the configuration."
            )
            return
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Send message to AI and get response
            response = await session.send_message(user_message)
            
            # Extract text from Response object
            if hasattr(response, 'content'):
                text = response.content
            elif isinstance(response, dict):
                text = response.get('text', '') or response.get('content', '')
            else:
                text = str(response)
            
            # Handle images if present
            images = []
            if hasattr(response, 'images') and response.images:
                images = response.images
            elif isinstance(response, dict) and 'images' in response:
                images = response.get('images', [])
            
            # Send text response if we have content
            if text and text.strip():
                # Split long messages (Telegram has 4096 char limit)
                if len(text) > 4000:
                    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                    for chunk in chunks:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(text)
            elif not images:
                # No text and no images - send a default message
                await update.message.reply_text("✓ Done")
            
            # Send images if any
            for image_data in images:
                if isinstance(image_data, bytes):
                    await update.message.reply_photo(photo=image_data)
                elif isinstance(image_data, str):
                    # If it's a file path, read and send
                    try:
                        with open(image_data, 'rb') as f:
                            await update.message.reply_photo(photo=f)
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                f"❌ Sorry, I encountered an error: {str(e)}\n\n"
                "Please try again or use /clear to start a new conversation."
            )
    
    def run(self):
        """Start the Telegram bot."""
        logger.info("Starting Telegram bot...")
        
        # Create application
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start the bot
        logger.info("Bot is running. Press Ctrl+C to stop.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point for the Telegram bot."""
    import sys
    
    # Get configuration from environment variables or command line
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    provider_name = os.getenv("AI_PROVIDER", "gemini")
    api_key = os.getenv("AI_API_KEY")
    model_id = os.getenv("AI_MODEL", "gemini-1.5-flash")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        telegram_token = sys.argv[1]
    if len(sys.argv) > 2:
        provider_name = sys.argv[2]
    if len(sys.argv) > 3:
        api_key = sys.argv[3]
    if len(sys.argv) > 4:
        model_id = sys.argv[4]
    
    # Validate required parameters
    if not telegram_token:
        print("Error: TELEGRAM_BOT_TOKEN is required")
        print("\nUsage:")
        print("  python -m src.telegram_bot <telegram_token> [provider] [api_key] [model]")
        print("\nOr set environment variables:")
        print("  TELEGRAM_BOT_TOKEN=your_token")
        print("  AI_PROVIDER=gemini")
        print("  AI_API_KEY=your_api_key")
        print("  AI_MODEL=gemini-1.5-flash")
        sys.exit(1)
    
    if not api_key:
        print("Error: AI_API_KEY is required")
        sys.exit(1)
    
    # Create and run bot
    bot = TelegramBot(telegram_token, provider_name, api_key, model_id)
    bot.run()


if __name__ == "__main__":
    main()
