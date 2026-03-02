# 📱 Telegram Bot Visual Setup Guide

Step-by-step visual guide to set up your zeer Telegram bot.

---

## 🎯 Overview

```
┌─────────────┐
│   Telegram  │
│    User     │
└──────┬──────┘
       │
       │ Messages
       ↓
┌─────────────┐
│  Telegram   │
│  Bot API    │
└──────┬──────┘
       │
       │ Webhook/Polling
       ↓
┌─────────────┐
│    zeer     │
│ Telegram Bot│
└──────┬──────┘
       │
       │ API Calls
       ↓
┌─────────────┐
│ AI Provider │
│ (Gemini/etc)│
└─────────────┘
```

---

## 📋 Step 1: Create Bot with BotFather

### 1.1 Open Telegram
```
┌──────────────────────────┐
│  Telegram App            │
│                          │
│  🔍 Search: @BotFather   │
│                          │
│  ┌────────────────────┐  │
│  │  @BotFather        │  │
│  │  ✓ Verified        │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

### 1.2 Start Chat
```
┌──────────────────────────┐
│  @BotFather              │
├──────────────────────────┤
│  You:                    │
│  /newbot                 │
│                          │
│  BotFather:              │
│  Alright, a new bot.     │
│  How are we going to     │
│  call it?                │
└──────────────────────────┘
```

### 1.3 Name Your Bot
```
┌──────────────────────────┐
│  @BotFather              │
├──────────────────────────┤
│  You:                    │
│  My Zeer Assistant       │
│                          │
│  BotFather:              │
│  Good. Now let's choose  │
│  a username for your bot.│
│  It must end in 'bot'.   │
└──────────────────────────┘
```

### 1.4 Choose Username
```
┌──────────────────────────┐
│  @BotFather              │
├──────────────────────────┤
│  You:                    │
│  my_zeer_bot             │
│                          │
│  BotFather:              │
│  Done! Your token is:    │
│  123456789:ABCdef...     │
│                          │
│  ⚠️ SAVE THIS TOKEN!     │
└──────────────────────────┘
```

---

## 💻 Step 2: Install Dependencies

### 2.1 Terminal Commands
```bash
┌─────────────────────────────────────┐
│ $ pip install python-telegram-bot  │
│ Collecting python-telegram-bot...   │
│ Successfully installed ✓            │
│                                     │
│ $ pip install python-dotenv         │
│ Collecting python-dotenv...         │
│ Successfully installed ✓            │
└─────────────────────────────────────┘
```

### 2.2 Or Use Installer
```bash
┌─────────────────────────────────────┐
│ Linux/Mac:                          │
│ $ bash install_telegram.sh          │
│                                     │
│ Windows:                            │
│ > install_telegram.bat              │
└─────────────────────────────────────┘
```

---

## ⚙️ Step 3: Configure

### 3.1 Create .env File
```bash
┌─────────────────────────────────────┐
│ $ cp .env.example .env              │
│ ✓ Created .env file                 │
└─────────────────────────────────────┘
```

### 3.2 Edit .env File
```
┌─────────────────────────────────────┐
│ File: .env                          │
├─────────────────────────────────────┤
│ # Telegram Bot Token                │
│ TELEGRAM_BOT_TOKEN=123456789:ABC... │
│                                     │
│ # AI Provider                       │
│ AI_PROVIDER=gemini                  │
│                                     │
│ # API Key                           │
│ AI_API_KEY=AIzaSy...                │
│                                     │
│ # Model                             │
│ AI_MODEL=gemini-1.5-flash           │
└─────────────────────────────────────┘
```

### 3.3 Get Gemini API Key
```
┌─────────────────────────────────────┐
│ 1. Visit:                           │
│    makersuite.google.com/app/apikey │
│                                     │
│ 2. Click "Create API Key"           │
│                                     │
│ 3. Copy key: AIzaSy...              │
│                                     │
│ 4. Paste in .env file               │
└─────────────────────────────────────┘
```

---

## 🚀 Step 4: Run Bot

### 4.1 Start Command
```bash
┌─────────────────────────────────────┐
│ $ python start_telegram_bot.py      │
│                                     │
│ ✓ Loaded configuration from .env    │
│                                     │
│ ============...=============        │
│ zeer Telegram Bot                   │
│ ============...=============        │
│                                     │
│ Configuration:                      │
│   Provider: gemini                  │
│   Model: gemini-1.5-flash           │
│   Token: 123456789:...xyz           │
│                                     │
│ ✓ Bot initialized successfully      │
│                                     │
│ 🤖 Bot is now running...            │
│ Press Ctrl+C to stop                │
└─────────────────────────────────────┘
```

---

## 💬 Step 5: Chat with Bot

### 5.1 Find Your Bot
```
┌──────────────────────────┐
│  Telegram App            │
│                          │
│  🔍 Search: @my_zeer_bot │
│                          │
│  ┌────────────────────┐  │
│  │  @my_zeer_bot      │  │
│  │  My Zeer Assistant │  │
│  └────────────────────┘  │
└──────────────────────────┘
```

### 5.2 Start Conversation
```
┌──────────────────────────┐
│  @my_zeer_bot            │
├──────────────────────────┤
│  You:                    │
│  /start                  │
│                          │
│  Bot:                    │
│  👋 Hello!               │
│  I'm your zeer AI        │
│  assistant powered by    │
│  Gemini.                 │
│                          │
│  Commands:               │
│  /start - Show this      │
│  /clear - Clear history  │
│  /help - Show help       │
│                          │
│  Just send me a message  │
│  to start chatting!      │
└──────────────────────────┘
```

### 5.3 Chat Example
```
┌──────────────────────────┐
│  @my_zeer_bot            │
├──────────────────────────┤
│  You:                    │
│  What is Python?         │
│                          │
│  Bot: 💭 typing...       │
│                          │
│  Bot:                    │
│  Python is a high-level  │
│  programming language... │
│  [detailed response]     │
└──────────────────────────┘
```

---

## 🧪 Step 6: Test Setup

### 6.1 Run Test Script
```bash
┌─────────────────────────────────────┐
│ $ python test_telegram_setup.py     │
│                                     │
│ ============...=============        │
│ zeer Telegram Bot Setup Test        │
│ ============...=============        │
│                                     │
│ Checking dependencies...            │
│   ✓ python-telegram-bot             │
│   ✓ python-dotenv                   │
│ ✓ All dependencies installed        │
│                                     │
│ Checking configuration...           │
│   ✓ .env file exists                │
│   ✓ TELEGRAM_BOT_TOKEN = 123...    │
│   ✓ AI_PROVIDER = gemini            │
│   ✓ AI_API_KEY = AIz...             │
│   ✓ AI_MODEL = gemini-1.5-flash     │
│ ✓ Configuration looks good          │
│                                     │
│ Testing Telegram connection...      │
│   ✓ Bot connected: @my_zeer_bot     │
│   ✓ Bot name: My Zeer Assistant     │
│ ✓ Telegram token is valid           │
│                                     │
│ Testing AI provider...              │
│   ✓ Provider initialized: gemini    │
│ ✓ AI provider is accessible         │
│                                     │
│ ============...=============        │
│ Test Summary                        │
│ ============...=============        │
│ ✓ PASS   Dependencies               │
│ ✓ PASS   Configuration              │
│ ✓ PASS   Telegram Token             │
│ ✓ PASS   AI Provider                │
│ ============...=============        │
│                                     │
│ 🎉 All tests passed!                │
│ Your bot is ready to run.           │
│                                     │
│ Start your bot with:                │
│   python start_telegram_bot.py      │
└─────────────────────────────────────┘
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    Telegram Users                    │
│  👤 User 1    👤 User 2    👤 User 3    👤 User N   │
└────────┬──────────┬──────────┬──────────┬───────────┘
         │          │          │          │
         └──────────┴──────────┴──────────┘
                     │
                     ↓
         ┌───────────────────────┐
         │   Telegram Bot API    │
         │   (api.telegram.org)  │
         └───────────┬───────────┘
                     │
                     ↓
         ┌───────────────────────┐
         │  zeer Telegram Bot    │
         │  (start_telegram_bot) │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ↓                       ↓
┌────────────────┐      ┌────────────────┐
│  User Session  │      │  User Session  │
│   (User 1)     │      │   (User 2)     │
│                │      │                │
│  ChatSession   │      │  ChatSession   │
│  ToolRegistry  │      │  ToolRegistry  │
│  SkillsManager │      │  SkillsManager │
└────────┬───────┘      └────────┬───────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ↓
         ┌───────────────────────┐
         │    AI Provider        │
         │  (Gemini/OpenAI/etc)  │
         └───────────┬───────────┘
                     │
                     ↓
         ┌───────────────────────┐
         │     AI Model          │
         │  (gemini-1.5-flash)   │
         └───────────────────────┘
```

---

## 🔄 Message Flow

```
1. User sends message
   ↓
2. Telegram forwards to bot
   ↓
3. Bot receives update
   ↓
4. Get/create user session
   ↓
5. Send to ChatSession
   ↓
6. ChatSession processes with tools/skills
   ↓
7. Send to AI provider
   ↓
8. AI generates response
   ↓
9. Process response (split if long)
   ↓
10. Send back to user via Telegram
```

---

## 📁 File Structure

```
zeer/
├── src/
│   ├── telegram_bot.py          ← Main bot code
│   ├── chat_session.py          ← Session management
│   ├── providers/               ← AI providers
│   │   ├── gemini_provider.py
│   │   ├── openai_provider.py
│   │   └── ...
│   └── ...
│
├── skills/                      ← Agent skills
│   ├── pdf/
│   ├── code-helper/
│   └── ...
│
├── start_telegram_bot.py        ← Startup script
├── test_telegram_setup.py       ← Test script
├── .env                         ← Your config (SECRET!)
├── .env.example                 ← Config template
│
├── TELEGRAM_QUICKSTART.md       ← 5-min guide
├── TELEGRAM_SETUP.md            ← Full guide
├── TELEGRAM_TROUBLESHOOTING.md  ← Help
└── README_TELEGRAM.md           ← Overview
```

---

## 🎯 Common Use Cases

### Use Case 1: Code Help
```
You: How do I read a CSV file in Python?
Bot: [Provides code example with explanation]
```

### Use Case 2: File Operations
```
You: List all Python files in the current directory
Bot: [Uses file-operations skill to list files]
```

### Use Case 3: PDF Generation
```
You: Create a PDF report about machine learning
Bot: [Uses pdf-builder skill to generate PDF]
```

### Use Case 4: Image Generation
```
You: Generate an image of a futuristic city
Bot: [Generates and sends image]
```

---

## 🛠️ Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Bot doesn't respond | Check if script is running |
| "Unauthorized" error | Check TELEGRAM_BOT_TOKEN |
| "AI provider error" | Check AI_API_KEY |
| Slow responses | Use faster model (flash vs pro) |
| Bot crashes | Use process manager (systemd/docker) |

See [TELEGRAM_TROUBLESHOOTING.md](TELEGRAM_TROUBLESHOOTING.md) for details.

---

## 🎉 Success!

Your zeer AI assistant is now on Telegram!

```
┌──────────────────────────┐
│  ✅ Bot Created          │
│  ✅ Dependencies OK      │
│  ✅ Configuration Done   │
│  ✅ Bot Running          │
│  ✅ Tests Passed         │
│                          │
│  🎊 Ready to Chat! 🎊   │
└──────────────────────────┘
```

---

**Need help?** Check the documentation files or open an issue on GitHub!
