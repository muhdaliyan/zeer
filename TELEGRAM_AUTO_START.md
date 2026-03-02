# Telegram Bot Auto-Start Feature

## Overview

The Telegram bot now automatically starts in the background when you launch zeer CLI, and stops when you exit. This allows you to chat with your AI assistant both through Telegram and the CLI simultaneously.

## How It Works

### Auto-Start
When you run `zeer`, the application:
1. Checks if Telegram is configured (bot token exists)
2. Checks if AI provider and model are configured
3. Checks if `python-telegram-bot` is installed
4. If all conditions are met, starts the bot in the background
5. Shows a confirmation message: "✓ Telegram bot started in background"

### Auto-Stop
When you exit zeer (Ctrl+C or `/exit`):
1. The Telegram bot process is automatically terminated
2. Shows a confirmation: "Telegram bot stopped"
3. All resources are cleaned up

## Usage

### Normal Flow
```bash
# Start zeer
zeer

# You'll see:
# ✓ Telegram bot started in background
#   Bot will stop when you exit zeer

# Now you can:
# - Chat in the CLI
# - Chat on Telegram simultaneously
# - Both use the same AI provider and model

# When you exit:
# Ctrl+C or /exit

# You'll see:
# Telegram bot stopped
# Exiting zeer. Goodbye!
```

### Check Bot Status
```bash
# In zeer CLI, type:
/status

# You'll see:
# ● Telegram bot is running
#   Token: 123456789:...xyz
#   Provider: gemini
#   Model: gemini-1.5-flash
#
#   Bot will stop when you exit zeer
```

## Commands

### New Commands
- `/status` - Show Telegram bot status (running/stopped)
- `/setup` - Configure Telegram bot (if not already configured)

### Existing Commands Still Work
- `/models` - Switch model (affects both CLI and Telegram)
- `/providers` - Switch provider (affects both CLI and Telegram)
- `/clear` - Clear CLI conversation (Telegram conversations are per-user)
- `/exit` - Exit zeer and stop Telegram bot

## Requirements

For auto-start to work, you need:
1. ✅ Telegram bot configured (via `/setup`)
2. ✅ AI provider selected
3. ✅ Model selected
4. ✅ `python-telegram-bot` installed

If any requirement is missing, the bot won't auto-start (no error shown).

## Configuration

### First Time Setup
```bash
# 1. Start zeer
zeer

# 2. Select provider and model
# (follow prompts)

# 3. Setup Telegram
/setup

# 4. Select "Telegram"
# 5. Enter bot token from @BotFather
# 6. Exit and restart zeer

# 7. Bot will now auto-start!
zeer
# ✓ Telegram bot started in background
```

### Manual Start (If Auto-Start Fails)
```bash
# If auto-start doesn't work, you can start manually:
python start_telegram_bot.py

# Or use the CLI:
zeer
/setup
# Select "Start Bot"
```

## Benefits

### 1. Seamless Experience
- No need to run bot in separate terminal
- Bot starts automatically when you need it
- Bot stops automatically when you're done

### 2. Shared Configuration
- CLI and Telegram use same provider/model
- Change model in CLI → affects Telegram too
- One configuration for both interfaces

### 3. Resource Management
- Bot only runs when zeer is running
- No orphaned processes
- Clean shutdown on exit

### 4. Multi-Interface Access
- Chat in CLI for development
- Chat on Telegram for mobile access
- Both work simultaneously
- Each has independent conversation history

## Technical Details

### Process Management
- Bot runs as subprocess of zeer
- Output is suppressed (runs silently)
- Process ID tracked for clean shutdown
- Graceful termination with 2-second timeout
- Force kill if graceful shutdown fails

### Environment Variables
The bot receives:
- `TELEGRAM_BOT_TOKEN` - From configuration
- `AI_PROVIDER` - From current session
- `AI_API_KEY` - From current session
- `AI_MODEL` - From current session

### Background Execution
```python
# Bot runs with:
subprocess.Popen(
    [sys.executable, "-m", "src.telegram_bot"],
    stdout=DEVNULL,  # No output
    stderr=DEVNULL,  # No errors shown
    stdin=DEVNULL    # No input needed
)
```

## Troubleshooting

### Bot Doesn't Auto-Start

**Check requirements:**
```bash
zeer
/status

# If shows "not running", check:
# 1. Is Telegram configured?
/setup
# Look for "Telegram" with checkmark

# 2. Is python-telegram-bot installed?
pip list | grep telegram

# 3. Is provider/model selected?
/providers
/models
```

**Install missing dependency:**
```bash
pip install python-telegram-bot
```

**Reconfigure Telegram:**
```bash
zeer
/setup
# Select Telegram
# Re-enter bot token
```

### Bot Doesn't Stop on Exit

**Check if process is still running:**
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep telegram_bot
```

**Kill manually if needed:**
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f telegram_bot
```

### Bot Stops Unexpectedly

**Possible causes:**
1. zeer CLI crashed
2. Bot encountered error
3. Invalid configuration

**Check logs:**
```bash
# Run bot manually to see errors:
python start_telegram_bot.py
```

### Multiple Bots Running

**If you accidentally started multiple bots:**
```bash
# Stop all Python processes
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f python

# Then restart zeer
zeer
```

## Comparison: Auto vs Manual

### Auto-Start (Default)
✅ Starts automatically
✅ Stops automatically
✅ No separate terminal needed
✅ Integrated with CLI
✅ Shared configuration
❌ Runs only when zeer is running

### Manual Start
✅ Runs independently
✅ Can run 24/7
✅ Survives CLI restarts
❌ Requires separate terminal
❌ Manual configuration
❌ Need to stop manually

## Best Practices

### Development
- Use auto-start for testing
- Quick iterations
- Easy debugging

### Production
- Use manual start or systemd
- See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
- 24/7 availability

### Hybrid Approach
```bash
# Development: Auto-start
zeer  # Bot starts automatically

# Production: Systemd
sudo systemctl start zeer-telegram

# Or Docker
docker-compose -f docker-compose.telegram.yml up -d
```

## FAQ

**Q: Can I disable auto-start?**
A: Not currently, but the bot only starts if configured. To prevent auto-start, remove the Telegram configuration.

**Q: Does the bot share conversation history with CLI?**
A: No. Each Telegram user has their own conversation. CLI has its own conversation. They're independent.

**Q: Can I run multiple bots?**
A: Not with auto-start. For multiple bots, use manual start with different configurations.

**Q: What happens if I change the model in CLI?**
A: The Telegram bot will use the new model for new conversations. Existing Telegram conversations continue with their current model until bot restarts.

**Q: Can I use different models for CLI and Telegram?**
A: Not with auto-start. They share the same configuration. For different models, use manual start.

**Q: Does auto-start work on all platforms?**
A: Yes! Works on Windows, Linux, and Mac.

## See Also

- [TELEGRAM_QUICKSTART.md](TELEGRAM_QUICKSTART.md) - 5-minute setup
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Full setup guide
- [TELEGRAM_TROUBLESHOOTING.md](TELEGRAM_TROUBLESHOOTING.md) - Common issues
- [README_TELEGRAM.md](README_TELEGRAM.md) - Overview

---

**Enjoy seamless AI assistance across CLI and Telegram!** 🚀
