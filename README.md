# Zeer

**Zeer** is an OpenSource agentic AI CLI that connects to multiple providers (OpenAI, Gemini, Claude) with **tool-calling capabilities** and an **extensible skills system**.  

Think of it as **Claude Code for the terminal**, provider-agnostic and developer-friendly.

<img src="https://i.ibb.co/7NpbpPhw/image.png" alt="image" border="0">

---

## 🎯 Why Zeer?

Tools like Claude Code, Kiro, and Cursor are powerful but come with limitations:

* **Subscription Required** – Monthly fees for access
* **Fixed Models** – Locked into specific AI providers
* **Closed Source** – Limited customization options

**Zeer is different:**

* ✅ **Use Your Own API Keys** – Pay only for what you use, no subscriptions
* ✅ **Multi-Provider Support** – Switch between OpenAI, Gemini, Claude, or add your own
* ✅ **100% Open Source** – Customize, extend, and contribute freely
* ✅ **Extensible Skills System** – Create custom agent behaviors without code changes
* ✅ **Terminal-First** – Lightweight, fast, and integrates with your workflow

> **Note:** Zeer is currently in beta. We appreciate your contributions and feedback as we continue to improve. This project will always remain open source.

---

## 🚀 Get Started

Start using Zeer quickly with the following installation options.

### **For Users (PyPI)**

```bash
pip install zeer
```

### **For Developers (Local / Editable)**

```bash
# Clone the repository
git clone https://github.com/muhdaliyan/zeer.git
cd zeer

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# Run Zeer
zeer
```

> Any code changes will reflect immediately without reinstalling.

---

## 🎯 Quick Start

```bash
zeer
```

1. Select your AI provider
2. Enter your API key
3. Choose a model
4. Start chatting and using AI tools

---

## 💻 Usage Examples

```bash
# AI automatically executes tasks
> create a PDF report about machine learning
> list all Python files in this directory
> set up a new React project structure
> read and summarize config.json

# Commands
/skills    # View available skills
/tools     # View available tools
/clear     # Clear conversation
/providers # Switch provider
/models    # Switch model
```

---

## 🔧 Built-in Skills

* **pdf-builder** – Generate PDF documents with reportlab
* **code-helper** – Project setup & code organization
* **file-operations** – File system operations
* **text-processing** – Text manipulation & analysis
* **frontend-designer** – Frontend development assistance

---

## ✨ Creating Custom Skills

1. Create `skills/your-skill/SKILL.md`:

```markdown
---
name: your-skill
description: What this skill does and when to use it
allowed-tools: create_file read_file run_code
---

## Goal
Your skill's purpose

## Procedure
Step-by-step instructions for the AI

## Examples
Usage examples
```

2. Restart Zeer – skills are auto-discovered.

See [SKILLS_IMPLEMENTATION.md](SKILLS_IMPLEMENTATION.md) for advanced details.

---

## 🏗️ Architecture

```
zeer/
├── src/
│   ├── providers/          # AI provider implementations
│   ├── tools.py            # Tool registry & execution
│   ├── skills_manager.py   # Skills loading & validation
│   └── chat_session.py     # Context management
└── skills/                 # Modular agent skills
    ├── backend-developer/
    │   ├── SKILL.md        # Skill definition
    │   ├── scripts/        # Executable Python scripts
    |   |   └── script.py
    │   └── references/     # Additional documentation
    ├── code-helper/
    │   └── SKILL.md
    ├── file-operations/
    │   └── SKILL.md
    └── ...
```

---

## 🔄 Tool Calling Flow

1. User sends a message
2. AI decides to use tools
3. Tools execute (file ops, code, etc.)
4. Results fed back to AI
5. AI responds with final answer

---

## 📜 Skills System

* **Metadata Loading**: Only names/descriptions loaded initially
* **On-Demand Activation**: Full skill content loaded when referenced
* **Scripts Support**: Skills can include executable Python scripts
* **References**: Additional documentation files
* **Validation**: Automatic format checking on load

---

## ⚙️ Requirements

* Python 3.8+
* API key for at least one provider (OpenAI, Gemini, or Claude)

---

## 🤝 Contributing

Contributions are welcome! Follow these steps:

### Development Setup

```bash
git clone https://github.com/muhdaliyan/zeer.git
cd zeer
pip install -r requirements.txt
pip install -e .
```

### Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test locally with `zeer`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Adding Custom Tools

Edit `src/tools.py` and add to the registry in `create_default_registry()`.

### Adding Custom Skills

Create a new folder in `skills/` with a `SKILL.md` following the [agentskills.io](https://agentskills.io) specification.

---

## 📜 License

MIT

---

## 🔗 Links

* [GitHub Repository](https://github.com/muhdaliyan/zeer)
* [PyPI Package](https://pypi.org/project/zeer/)
* [Agent Skills Specification](https://agentskills.io)