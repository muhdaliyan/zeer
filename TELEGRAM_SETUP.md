# Telegram Bot Integration Guide

This guide will help you set up and run your zeer AI assistant as a Telegram bot.

## Prerequisites

- Python 3.8 or higher
- A Telegram account
- An API key for your chosen AI provider (OpenAI, Gemini, Claude, etc.)

## Step 1: Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "My zeer Assistant")
   - Choose a username (must end in 'bot', e.g., "my_zeer_bot")
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. **Save this token** - you'll need it in the next step

## Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install python-telegram-bot python-dotenv
```

Or install all dependencies from the project:

```bash
pip install -e .
```

## Step 3: Configure Your Bot

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   # Your Telegram bot token from BotFather
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   
   # Choose your AI provider: openai, gemini, claude, openrouter, ollama
   AI_PROVIDER=gemini
   
   # Your AI provider API key
   AI_API_KEY=your_api_key_here
   
   # Model to use
   AI_MODEL=gemini-1.5-flash
   ```

### Provider-Specific Configuration

#### Gemini (Google)
```env
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key
AI_MODEL=gemini-1.5-flash
```
Get your API key: https://makersuite.google.com/app/apikey

#### OpenAI
```env
AI_PROVIDER=openai
AI_API_KEY=your_openai_api_key
AI_MODEL=gpt-4
```
Get your API key: https://platform.openai.com/api-keys

#### Claude (Anthropic)
```env
AI_PROVIDER=claude
AI_API_KEY=your_claude_api_key
AI_MODEL=claude-3-sonnet-20240229
```
Get your API key: https://console.anthropic.com/

#### Ollama (Local)
```env
AI_PROVIDER=ollama
AI_API_KEY=
AI_MODEL=llama3.2
```
Make sure Ollama is running locally: https://ollama.ai

## Step 4: Start Your Bot

Run the startup script:

```bash
python start_telegram_bot.py
```

You should see:
```
✓ Loaded configuration from .env file

============================================================
zeer Telegram Bot
============================================================

Configuration:
  Provider: gemini
  Model: gemini-1.5-flash
  Token: 123456789:...xyz

✓ Bot initialized successfully

🤖 Bot is now running...
Press Ctrl+C to stop
```

## Step 5: Chat with Your Bot

1. Open Telegram
2. Search for your bot by username (e.g., `@my_zeer_bot`)
3. Start a chat and send `/start`
4. Start chatting!

## Available Commands

- `/start` - Show welcome message
- `/help` - Show help and available commands
- `/clear` - Clear your conversation history

## Features

- **Persistent Conversations**: Each user has their own conversation history
- **Tool Calling**: The bot can use tools and skills just like the CLI version
- **Multi-User Support**: Multiple users can chat with the bot simultaneously
- **Long Message Support**: Automatically splits long responses
- **Error Handling**: Graceful error messages if something goes wrong

## Troubleshooting

### Bot doesn't respond
- Check that the bot is running (you should see "Bot is now running..." in the terminal)
- Verify your Telegram token is correct
- Make sure your AI provider API key is valid

### "AI provider is not available" error
- Check your AI_API_KEY is correct
- Verify you have internet connection
- For Ollama: make sure Ollama is running locally

### Import errors
- Make sure you installed all dependencies: `pip install -e .`
- Install telegram library: `pip install python-telegram-bot`

### Rate limiting
- Some AI providers have rate limits
- Consider using a different model or provider
- Add delays between requests if needed

## Running in Production

### Using systemd (Linux)

Create a service file `/etc/systemd/system/zeer-telegram.service`:

```ini
[Unit]
Description=zeer Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/zeer
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python start_telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable zeer-telegram
sudo systemctl start zeer-telegram
sudo systemctl status zeer-telegram
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .
RUN pip install python-telegram-bot python-dotenv

CMD ["python", "start_telegram_bot.py"]
```

Build and run:
```bash
docker build -t zeer-telegram .
docker run -d --env-file .env zeer-telegram
```

### Using screen (Simple)

```bash
screen -S zeer-bot
python start_telegram_bot.py
# Press Ctrl+A then D to detach
```

To reattach:
```bash
screen -r zeer-bot
```

## Security Notes

- **Never commit your .env file** - it contains sensitive tokens
- Keep your API keys secure
- Consider using environment variables in production
- Regularly rotate your API keys
- Monitor your bot's usage and costs

## Advanced Configuration

### Custom Skills

The bot automatically uses all skills from the `skills/` directory. To add custom skills:

1. Create a new skill in `skills/your-skill/`
2. Follow the skill structure from existing skills
3. Restart the bot

### Multiple Bots

You can run multiple bots with different configurations:

```bash
# Bot 1 with Gemini
TELEGRAM_BOT_TOKEN=token1 AI_PROVIDER=gemini python start_telegram_bot.py

# Bot 2 with OpenAI
TELEGRAM_BOT_TOKEN=token2 AI_PROVIDER=openai python start_telegram_bot.py
```

## Support

If you encounter issues:

1. Check the logs in your terminal
2. Verify your configuration in `.env`
3. Test your AI provider API key separately
4. Open an issue on GitHub: https://github.com/muhdaliyan/zeer/issues

## License

MIT License - see LICENSE file for details
