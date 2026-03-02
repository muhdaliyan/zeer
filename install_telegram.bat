@echo off
REM Installation script for zeer Telegram bot (Windows)

echo ==================================
echo zeer Telegram Bot Installer
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed
    echo Please install Python 3.8 or higher first
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install python-telegram-bot python-dotenv

if errorlevel 1 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [OK] Created .env file from .env.example
        echo.
        echo WARNING: Edit .env file and add your tokens:
        echo    1. TELEGRAM_BOT_TOKEN (from @BotFather)
        echo    2. AI_API_KEY (from your AI provider)
        echo.
    ) else (
        echo WARNING: .env.example not found, creating basic .env
        (
            echo # Telegram Bot Configuration
            echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
            echo.
            echo # AI Provider Configuration
            echo AI_PROVIDER=gemini
            echo AI_API_KEY=your_api_key_here
            echo AI_MODEL=gemini-1.5-flash
        ) > .env
        echo [OK] Created .env file
        echo.
        echo WARNING: Edit .env file and add your tokens
        echo.
    )
) else (
    echo [OK] .env file already exists
    echo.
)

echo ==================================
echo Installation Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Get Telegram bot token from @BotFather
echo 2. Edit .env file with your tokens
echo 3. Run: python start_telegram_bot.py
echo.
echo See TELEGRAM_QUICKSTART.md for detailed guide
echo.
pause
