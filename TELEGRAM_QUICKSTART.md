# Telegram Bot - Quick Start (5 Minutes)

Get your zeer assistant running on Telegram in 5 minutes!

## 1. Create Bot (2 minutes)

Open Telegram → Search `@BotFather` → Send:
```
/newbot
```

Follow prompts and **copy your token** (looks like `123456789:ABCdef...`)

## 2. Install (1 minute)

```bash
pip install python-telegram-bot python-dotenv
```

## 3. Configure (1 minute)

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key
AI_MODEL=gemini-1.5-flash
```

**Get Gemini API key**: https://makersuite.google.com/app/apikey (free)

## 4. Run (1 minute)

```bash
python start_telegram_bot.py
```

## 5. Chat!

Open Telegram → Search your bot → Send `/start` → Start chatting!

---

## Need Help?

See full guide: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

## Other Providers

**OpenAI:**
```env
AI_PROVIDER=openai
AI_API_KEY=sk-...
AI_MODEL=gpt-4
```

**Claude:**
```env
AI_PROVIDER=claude
AI_API_KEY=sk-ant-...
AI_MODEL=claude-3-sonnet-20240229
```

**Ollama (Local):**
```env
AI_PROVIDER=ollama
AI_API_KEY=
AI_MODEL=llama3.2
```

Make sure Ollama is running: `ollama serve`
