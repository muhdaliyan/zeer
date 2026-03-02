# 🤖 zeer Telegram Bot

Chat with your zeer AI assistant through Telegram!

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Create Bot
Open Telegram → Search `@BotFather` → Send `/newbot` → Copy your token

### 2️⃣ Install
```bash
pip install python-telegram-bot python-dotenv
```

### 3️⃣ Configure
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

Get free Gemini API key: https://makersuite.google.com/app/apikey

### 4️⃣ Run
```bash
python start_telegram_bot.py
```

### 5️⃣ Chat
Open Telegram → Find your bot → Send `/start` → Start chatting!

---

## 📚 Documentation

- **Quick Start** (5 min): [TELEGRAM_QUICKSTART.md](TELEGRAM_QUICKSTART.md)
- **Full Setup Guide**: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
- **Troubleshooting**: [TELEGRAM_TROUBLESHOOTING.md](TELEGRAM_TROUBLESHOOTING.md)
- **Complete Summary**: [TELEGRAM_INTEGRATION_SUMMARY.md](TELEGRAM_INTEGRATION_SUMMARY.md)

---

## ✨ Features

- 💬 Natural conversations with AI
- 🛠️ Full tool calling support
- 🎯 All zeer skills available
- 👥 Multi-user support
- 🖼️ Image generation & handling
- 📝 Long message support
- 🔄 Persistent conversations
- 🚀 Production ready

---

## 🎮 Commands

- `/start` - Start the bot
- `/help` - Show help
- `/clear` - Clear conversation history

---

## 🔧 Supported AI Providers

- **Gemini** (Google) - Free tier available ⭐
- **OpenAI** (GPT-4, GPT-3.5)
- **Claude** (Anthropic)
- **Ollama** (Local, no API key needed)
- **OpenRouter** (Multiple models)

---

## 🐳 Deployment Options

### Development
```bash
python start_telegram_bot.py
```

### Docker
```bash
docker-compose -f docker-compose.telegram.yml up -d
```

### Linux Service
```bash
sudo systemctl start zeer-telegram
```

See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for details.

---

## 🧪 Test Your Setup

```bash
python test_telegram_setup.py
```

---

## 🆘 Need Help?

1. Run test: `python test_telegram_setup.py`
2. Check [TELEGRAM_TROUBLESHOOTING.md](TELEGRAM_TROUBLESHOOTING.md)
3. Open issue: https://github.com/muhdaliyan/zeer/issues

---

## 🔒 Security

- ✅ Never commit `.env` file
- ✅ Keep API keys secure
- ✅ Monitor usage regularly
- ✅ Use process manager in production

---

## 📊 What It Costs

- **Telegram Bot**: Free
- **Gemini**: Free tier + pay-per-use
- **OpenAI**: Pay-per-token
- **Claude**: Pay-per-token
- **Ollama**: Free (local)

**Tip**: Start with Gemini free tier or local Ollama!

---

## 🎯 Example Conversations

```
You: Create a PDF report about Python
Bot: [Creates PDF using pdf-builder skill]

You: List all Python files in this directory
Bot: [Uses file-operations skill]

You: Generate an image of a sunset
Bot: [Generates and sends image]

You: Explain how async/await works
Bot: [Provides detailed explanation]
```

---

## 🚀 Next Steps

1. ✅ Get bot running
2. ✅ Test with friends
3. ✅ Deploy to production
4. ✅ Monitor usage
5. ✅ Customize features

---

## 📖 Full Documentation

Main README: [README.md](README.md)

---

**Made with ❤️ by the zeer community**

⭐ Star us on GitHub: https://github.com/muhdaliyan/zeer
