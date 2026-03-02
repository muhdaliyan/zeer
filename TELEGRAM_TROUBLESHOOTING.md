# Telegram Bot Troubleshooting Guide

Common issues and solutions for zeer Telegram bot.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Connection Issues](#connection-issues)
- [Runtime Issues](#runtime-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### "ModuleNotFoundError: No module named 'telegram'"

**Problem:** python-telegram-bot not installed

**Solution:**
```bash
pip install python-telegram-bot
```

### "ModuleNotFoundError: No module named 'dotenv'"

**Problem:** python-dotenv not installed

**Solution:**
```bash
pip install python-dotenv
```

### "ModuleNotFoundError: No module named 'src'"

**Problem:** zeer package not installed

**Solution:**
```bash
# Install in editable mode
pip install -e .
```

---

## Configuration Issues

### "TELEGRAM_BOT_TOKEN not found"

**Problem:** .env file missing or not configured

**Solution:**
1. Copy example file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your token from @BotFather
3. Make sure the file is in the same directory as `start_telegram_bot.py`

### "AI_API_KEY not found"

**Problem:** API key not configured

**Solution:**
1. Get API key from your provider:
   - Gemini: https://makersuite.google.com/app/apikey
   - OpenAI: https://platform.openai.com/api-keys
   - Claude: https://console.anthropic.com/
2. Add to `.env` file:
   ```env
   AI_API_KEY=your_actual_api_key_here
   ```

### Bot token format error

**Problem:** Invalid token format

**Solution:**
- Token should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- No spaces or quotes around it in .env file
- Get new token from @BotFather if needed

---

## Connection Issues

### "Unauthorized" or "Invalid token"

**Problem:** Telegram token is wrong or revoked

**Solution:**
1. Go to @BotFather on Telegram
2. Send `/mybots`
3. Select your bot
4. Click "API Token" to see current token
5. Update `.env` with correct token
6. If token was revoked, generate new one with `/newbot`

### "AI provider is not available"

**Problem:** AI provider can't be reached

**Solution:**

For Gemini:
```bash
# Test your API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY"
```

For OpenAI:
```bash
# Test your API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

For Ollama:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### "Connection timeout" or "Network error"

**Problem:** Network connectivity issues

**Solution:**
1. Check internet connection
2. Check if firewall is blocking Python
3. Try different network
4. Check if API endpoint is accessible:
   ```bash
   ping api.telegram.org
   ```

---

## Runtime Issues

### Bot doesn't respond to messages

**Checklist:**
1. Is the bot running? Check terminal for "Bot is now running..."
2. Did you send `/start` first?
3. Is the bot added to the chat?
4. Check logs for errors

**Debug:**
```bash
# Run with verbose logging
python start_telegram_bot.py
# Watch for errors in terminal
```

### "Sorry, I encountered an error"

**Problem:** AI provider error

**Common causes:**
1. **Rate limit exceeded** - Wait a few minutes
2. **Invalid API key** - Check key in .env
3. **Model not available** - Try different model
4. **Quota exceeded** - Check your provider dashboard

**Solution:**
```bash
# Test your setup
python test_telegram_setup.py
```

### Bot stops after a while

**Problem:** Process crashed or killed

**Solution:**
1. Check logs for errors
2. Use process manager:
   ```bash
   # Using screen
   screen -S zeer-bot
   python start_telegram_bot.py
   # Ctrl+A then D to detach
   
   # Using systemd (Linux)
   sudo systemctl start zeer-telegram
   
   # Using Docker
   docker-compose -f docker-compose.telegram.yml up -d
   ```

### "Context length exceeded"

**Problem:** Conversation too long

**Solution:**
- User should send `/clear` to reset conversation
- Or restart the bot to clear all sessions

---

## Performance Issues

### Slow responses

**Causes:**
1. Large conversation history
2. Slow AI model
3. Network latency
4. Server overload

**Solutions:**
1. Use faster model (e.g., gemini-1.5-flash instead of pro)
2. Clear conversation with `/clear`
3. Check network speed
4. Use local Ollama for faster responses

### High memory usage

**Problem:** Bot using too much RAM

**Solutions:**
1. Restart bot periodically
2. Limit conversation history
3. Use lighter model
4. Deploy with memory limits:
   ```bash
   # Docker with memory limit
   docker run -m 512m zeer-telegram
   ```

### Multiple users causing issues

**Problem:** Bot slow with many users

**Solutions:**
1. Each user has separate session (this is normal)
2. Consider rate limiting
3. Use faster model
4. Deploy on better server
5. Consider multiple bot instances with load balancer

---

## Testing & Debugging

### Test your setup

```bash
# Run comprehensive test
python test_telegram_setup.py
```

### Check bot status

```bash
# If using systemd
sudo systemctl status zeer-telegram

# If using Docker
docker-compose -f docker-compose.telegram.yml ps
docker-compose -f docker-compose.telegram.yml logs -f

# If using screen
screen -r zeer-bot
```

### Enable debug logging

Edit `src/telegram_bot.py` and change:
```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed from INFO to DEBUG
)
```

### Test AI provider separately

```python
# test_provider.py
import asyncio
from src.providers.gemini_provider import GeminiProvider

async def test():
    provider = GeminiProvider("your_api_key")
    response = await provider.send_message("Hello", None)
    print(response)

asyncio.run(test())
```

---

## Common Error Messages

### "telegram.error.NetworkError"
- Check internet connection
- Verify Telegram API is accessible
- Try again in a few minutes

### "telegram.error.Unauthorized"
- Invalid bot token
- Token was revoked
- Get new token from @BotFather

### "telegram.error.BadRequest"
- Invalid message format
- Message too long (>4096 chars)
- Bot tries to edit message that doesn't exist

### "Provider validation failed"
- Invalid API key
- API key doesn't have required permissions
- Provider service is down

### "No models available"
- For Ollama: No models pulled
- For cloud: API key doesn't have access
- Solution: Pull model or check permissions

---

## Getting Help

If you're still stuck:

1. **Check logs** - Most errors are explained in the terminal output
2. **Run test script** - `python test_telegram_setup.py`
3. **Search issues** - https://github.com/muhdaliyan/zeer/issues
4. **Ask for help** - Open a new issue with:
   - Error message
   - Steps to reproduce
   - Your configuration (without sensitive tokens)
   - Output of test script

---

## Useful Commands

```bash
# Test setup
python test_telegram_setup.py

# Start bot
python start_telegram_bot.py

# Start with Docker
docker-compose -f docker-compose.telegram.yml up -d

# View logs (Docker)
docker-compose -f docker-compose.telegram.yml logs -f

# Stop bot (Docker)
docker-compose -f docker-compose.telegram.yml down

# Restart bot (systemd)
sudo systemctl restart zeer-telegram

# View logs (systemd)
sudo journalctl -u zeer-telegram -f
```

---

## Prevention Tips

1. **Keep tokens secure** - Never commit .env to git
2. **Monitor usage** - Check your AI provider dashboard
3. **Set up alerts** - Get notified if bot goes down
4. **Regular updates** - Keep dependencies updated
5. **Backup config** - Save your .env file securely
6. **Test changes** - Use test script before deploying
7. **Use process manager** - Don't run bot directly in production

---

## Still Need Help?

- Documentation: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
- Quick Start: [TELEGRAM_QUICKSTART.md](TELEGRAM_QUICKSTART.md)
- GitHub Issues: https://github.com/muhdaliyan/zeer/issues
- Main README: [README.md](README.md)
