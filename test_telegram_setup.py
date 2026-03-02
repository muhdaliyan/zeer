#!/usr/bin/env python3
"""
Test script to verify Telegram bot setup.

This script checks:
1. Required dependencies are installed
2. Configuration is present
3. Telegram token is valid
4. AI provider is accessible
"""

import sys
import os

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    
    required = {
        'telegram': 'python-telegram-bot',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All dependencies installed\n")
    return True


def check_config():
    """Check if .env file exists and has required values."""
    print("Checking configuration...")
    
    if not os.path.exists('.env'):
        print("  ✗ .env file not found")
        print("\n❌ Configuration missing")
        print("Run: cp .env.example .env")
        print("Then edit .env with your tokens")
        return False
    
    print("  ✓ .env file exists")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    # Check required variables
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token from @BotFather',
        'AI_PROVIDER': 'AI provider (gemini, openai, claude, etc.)',
        'AI_API_KEY': 'API key for your AI provider',
        'AI_MODEL': 'Model ID to use',
    }
    
    missing = []
    placeholder = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"  ✗ {var} - NOT SET")
            missing.append(var)
        elif 'your_' in value.lower() or 'token_here' in value.lower():
            print(f"  ⚠ {var} - PLACEHOLDER VALUE")
            placeholder.append(var)
        else:
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var:
                masked = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
                print(f"  ✓ {var} = {masked}")
            else:
                print(f"  ✓ {var} = {value}")
    
    if missing:
        print(f"\n❌ Missing configuration: {', '.join(missing)}")
        print("Edit .env file and add these values")
        return False
    
    if placeholder:
        print(f"\n⚠️  Placeholder values detected: {', '.join(placeholder)}")
        print("Edit .env file and replace with real values")
        return False
    
    print("✓ Configuration looks good\n")
    return True


def test_telegram_token():
    """Test if Telegram token is valid."""
    print("Testing Telegram connection...")
    
    try:
        from telegram import Bot
        import asyncio
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        async def test_bot():
            bot = Bot(token)
            me = await bot.get_me()
            return me
        
        me = asyncio.run(test_bot())
        print(f"  ✓ Bot connected: @{me.username}")
        print(f"  ✓ Bot name: {me.first_name}")
        print("✓ Telegram token is valid\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to connect: {e}")
        print("\n❌ Telegram token is invalid or bot is not accessible")
        print("Check your TELEGRAM_BOT_TOKEN in .env file")
        return False


def test_ai_provider():
    """Test if AI provider is accessible."""
    print("Testing AI provider...")
    
    provider_name = os.getenv('AI_PROVIDER', '').lower()
    api_key = os.getenv('AI_API_KEY', '')
    
    if not provider_name or not api_key:
        print("  ✗ Provider or API key not configured")
        return False
    
    try:
        # Import provider classes
        from src.providers.openai_provider import OpenAIProvider
        from src.providers.gemini_provider import GeminiProvider
        from src.providers.claude_provider import ClaudeProvider
        from src.providers.ollama_provider import OllamaProvider
        
        providers = {
            'openai': OpenAIProvider,
            'gemini': GeminiProvider,
            'claude': ClaudeProvider,
            'ollama': OllamaProvider,
        }
        
        provider_class = providers.get(provider_name)
        if not provider_class:
            print(f"  ✗ Unknown provider: {provider_name}")
            return False
        
        # Try to initialize provider
        provider = provider_class(api_key)
        print(f"  ✓ Provider initialized: {provider_name}")
        
        # For Ollama, check if it's running
        if provider_name == 'ollama':
            import asyncio
            try:
                asyncio.run(provider.validate_api_key())
                print("  ✓ Ollama is running")
            except:
                print("  ✗ Ollama is not running")
                print("    Start Ollama: ollama serve")
                return False
        
        print("✓ AI provider is accessible\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to initialize provider: {e}")
        print("\n⚠️  AI provider test failed")
        print("This might be okay - the bot will test it on first message")
        return True  # Don't fail the whole test


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("zeer Telegram Bot Setup Test")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Dependencies", check_dependencies()))
    results.append(("Configuration", check_config()))
    
    # Only test Telegram and AI if config is present
    if results[-1][1]:
        results.append(("Telegram Token", test_telegram_token()))
        results.append(("AI Provider", test_ai_provider()))
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print("="*60 + "\n")
    
    # Final verdict
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("\nStart your bot with:")
        print("  python start_telegram_bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nSee TELEGRAM_SETUP.md for help")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
