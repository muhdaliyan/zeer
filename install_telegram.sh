#!/bin/bash
# Installation script for zeer Telegram bot

echo "=================================="
echo "zeer Telegram Bot Installer"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher first"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install python-telegram-bot python-dotenv

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env file from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file and add your tokens:"
        echo "   1. TELEGRAM_BOT_TOKEN (from @BotFather)"
        echo "   2. AI_API_KEY (from your AI provider)"
        echo ""
    else
        echo "⚠️  .env.example not found, creating basic .env"
        cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI Provider Configuration
AI_PROVIDER=gemini
AI_API_KEY=your_api_key_here
AI_MODEL=gemini-1.5-flash
EOF
        echo "✓ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file and add your tokens"
        echo ""
    fi
else
    echo "✓ .env file already exists"
    echo ""
fi

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Get Telegram bot token from @BotFather"
echo "2. Edit .env file with your tokens"
echo "3. Run: python start_telegram_bot.py"
echo ""
echo "See TELEGRAM_QUICKSTART.md for detailed guide"
