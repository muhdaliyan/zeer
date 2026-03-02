# /setup Command Guide

The `/setup` command allows you to configure messaging platforms directly from the zeer CLI.

## Quick Start

1. Start zeer: `zeer`
2. Type `/setup` in the chat
3. Select a platform (Telegram, WhatsApp, Slack, Discord)
4. Enter your credentials
5. Start the bot!

## Telegram Setup via /setup

### Step 1: Run /setup
```
> /setup
```

### Step 2: Select Telegram
You'll see a table of available platforms:

```
┌─────────────────────────────────────────────────────────┐
│           Messaging Platforms Setup                     │
├─────────────────────────────────────────────────────────┤
│ Platform    │ Status     │ Configured │ Description     │
├─────────────────────────────────────────────────────────┤
│ Telegram    │ Available  │ ✗ No       │ Chat via bot    │
│ WhatsApp    │ Coming Soon│ ✗ No       │ Chat via bot    │
│ Slack       │ Coming Soon│ ✗ No       │ Chat via bot    │
│ Discord     │ Coming Soon│ ✗ No       │ Chat via bot    │
└─────────────────────────────────────────────────────────┘
```

Select: `Telegram - Setup`

### Step 3: Get Bot Token

The CLI will show you instructions:

```
┌─────────────────────────────────────────────────────────┐
│              Telegram Bot Setup                         │
├─────────────────────────────────────────────────────────┤
│ To create a Telegram bot:                              │
│ 1. Open Telegram and search for @BotFather             │
│ 2. Send /newbot command                                │
│ 3. Follow the prompts to create your bot               │
│ 4. Copy the bot token (looks like: 123456789:ABCdef...)│
│ 5. Paste it below                                      │
└─────────────────────────────────────────────────────────┘

Enter your Telegram bot token:
Bot Token: _
```

### Step 4: Enter Token

Paste your token from @BotFather:
```
Bot Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Step 5: Start Bot

After configuration, select `Start Bot (if configured)` from the menu.

The bot will start using your current AI provider and model!

```
┌─────────────────────────────────────────────────────────┐
│              Starting Telegram Bot                      │
├─────────────────────────────────────────────────────────┤
│ Provider: gemini                                        │
│ Model: gemini-1.5-flash                                 │
│ Token: 123456789:...xyz                                 │
│                                                         │
│ Bot will start in a new window...                      │
│ Press Ctrl+C in that window to stop the bot.          │
└─────────────────────────────────────────────────────────┘

✓ Bot module loaded
Starting bot... Press Ctrl+C to stop

Bot is now running...
```

### Step 6: Chat on Telegram

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Start chatting!

## Features

### Automatic Configuration
- Uses your current AI provider (Gemini, OpenAI, Claude, etc.)
- Uses your current model selection
- Saves bot token securely in `~/.zeer/messaging_platforms.json`

### Easy Management
- Reconfigure anytime with `/setup`
- Switch providers/models and restart bot
- View configured platforms

### Multiple Platforms (Coming Soon)
- WhatsApp
- Slack
- Discord

## Configuration Storage

Bot configurations are saved in:
```
~/.zeer/messaging_platforms.json
```

Example:
```json
{
  "telegram": {
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
  }
}
```

## Commands in /setup Menu

- **Platform - Setup**: Configure a new platform
- **Platform - Reconfigure**: Update existing configuration
- **Start Bot**: Launch the bot with current settings
- **Back to Chat**: Return to normal chat

## Troubleshooting

### "python-telegram-bot not installed"

The CLI will offer to install it automatically:
```
Would you like to install it now?
> Yes
```

Or install manually:
```bash
pip install python-telegram-bot
```

### "Please configure an AI provider first"

You need to setup an AI provider before starting the bot:
```
> /providers
```

Select a provider and enter your API key.

### "Please select a model first"

You need to select a model:
```
> /models
```

Choose a model from the list.

### Bot doesn't respond

1. Check the bot is running (you should see "Bot is now running...")
2. Make sure you sent `/start` in Telegram first
3. Check your AI provider API key is valid

## Comparison: /setup vs Manual Setup

### Using /setup (Recommended)
```
1. zeer
2. /setup
3. Select Telegram
4. Enter token
5. Start bot
```

**Pros:**
- Quick and easy
- Guided setup
- Automatic configuration
- Uses current provider/model
- Integrated into CLI

### Manual Setup
```
1. Create .env file
2. Add tokens manually
3. Run python start_telegram_bot.py
```

**Pros:**
- More control
- Can run independently
- Good for production deployment

## Tips

1. **Configure AI provider first**: Setup your AI provider before configuring messaging platforms
2. **Test in CLI first**: Make sure your AI provider works in the CLI before starting the bot
3. **Use /setup for quick testing**: Great for trying out the bot quickly
4. **Use manual setup for production**: For production, use the manual setup with systemd/Docker

## Example Workflow

```bash
# Start zeer
$ zeer

# Configure AI provider
> /providers
Select: Gemini
Enter API key: AIzaSy...

# Select model
> /models
Select: gemini-1.5-flash

# Setup Telegram
> /setup
Select: Telegram - Setup
Enter token: 123456789:ABC...

# Start bot
Select: Start Bot (if configured)

# Bot is now running!
# Open Telegram and chat with your bot
```

## Next Steps

After setup:
1. Open Telegram and find your bot
2. Send `/start` to begin
3. Chat with your AI assistant
4. Use `/clear` in Telegram to reset conversation
5. Stop bot with Ctrl+C when done

## Advanced

### Reconfigure Platform
```
> /setup
Select: Telegram - Reconfigure
Enter new token: ...
```

### Switch AI Provider
```
> /providers
Select new provider
> /setup
Select: Start Bot
```

The bot will restart with the new provider!

### Multiple Bots
You can run multiple bots by:
1. Configure in CLI with `/setup`
2. Start first bot
3. Open new terminal
4. Run `python start_telegram_bot.py` with different config

## See Also

- [TELEGRAM_QUICKSTART.md](TELEGRAM_QUICKSTART.md) - Manual setup guide
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Detailed setup instructions
- [TELEGRAM_TROUBLESHOOTING.md](TELEGRAM_TROUBLESHOOTING.md) - Common issues
- [README.md](README.md) - Main documentation
