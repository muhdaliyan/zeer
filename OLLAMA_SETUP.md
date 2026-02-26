# Ollama Setup Guide

## Prerequisites

1. **Install Ollama** on your machine:
   - Visit [ollama.ai](https://ollama.ai) and download for your OS
   - Or use package managers:
     - macOS: `brew install ollama`
     - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
     - Windows: Download from website

2. **Start Ollama server**:
   ```bash
   ollama serve
   ```
   The server runs on `http://localhost:11434` by default

3. **Pull a model** (required before using):
   ```bash
   # Popular models
   ollama pull llama3.2
   ollama pull mistral
   ollama pull codellama
   ollama pull deepseek-coder
   ```

## Using Ollama with Zeer

### Local Models (Recommended - No API Key Required)

1. Make sure Ollama is running: `ollama serve`
2. Start zeer: `zeer`
3. Select "Ollama" as provider
4. **Press Enter** when asked for API key (leave blank for local)
5. Select from your downloaded models

That's it! No API key needed for local usage.

### Cloud Models (Optional - Requires Login)

If you want to use Ollama cloud models:

1. Login to Ollama:
   ```bash
   ollama login
   ```

2. Get your API key from [ollama.ai/account](https://ollama.ai/account)

3. Start zeer and enter your API key when prompted

## Available Models

Check available models:
```bash
ollama list
```

Browse all models at [ollama.ai/library](https://ollama.ai/library)

## Tips

- **Local models run entirely on your machine** (no internet needed, no API key)
- Model performance depends on your hardware (GPU recommended)
- First run of a model may be slower (loading into memory)
- Use smaller models (7B) for faster responses on limited hardware
- Use larger models (70B+) for better quality if you have the resources

## Troubleshooting

**"Connection refused"**: Make sure Ollama server is running (`ollama serve`)

**"Model not found"**: Pull the model first (`ollama pull <model-name>`)

**Slow responses**: Try a smaller model or check your system resources

**API key prompt**: Just press Enter to skip - API key is only needed for cloud models
