# Image Generation Skill

Generate high-quality images using Google's Imagen 4 models for websites, applications, and creative projects.

## Setup

### 1. Install Google GenAI Library

```bash
pip install google-genai
```

### 2. Get API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Permanent (add to your shell profile):**
```bash
# Add to ~/.bashrc or ~/.zshrc
export GEMINI_API_KEY="your-api-key-here"
```

## Usage

### Basic Image Generation

```
> generate an image of a modern coffee shop interior
```

### For Website Projects

```
> create a landing page for a tech startup

AI: Would you like me to generate custom images using Imagen AI?

> yes

[AI generates hero image, logo, and other assets automatically]
```

### Custom Parameters

The AI will automatically choose appropriate settings, but you can be specific:

```
> generate a 16:9 hero image of a mountain landscape for my website
> create a square logo for my fitness app
> generate 4 variations of a product mockup
```

## Features

- **High Quality**: Imagen 4 generates photorealistic, professional images
- **Multiple Formats**: Supports various aspect ratios (1:1, 4:3, 16:9, etc.)
- **Batch Generation**: Generate up to 4 images at once
- **Auto-Integration**: Images are automatically saved to project directories
- **SynthID Watermark**: All images include invisible watermark for authenticity

## Supported Styles

- Photography (portraits, landscapes, products)
- Illustrations (digital art, sketches)
- Logos and branding
- UI elements and backgrounds
- Historical art styles

## Pricing

Check [Google AI Pricing](https://ai.google.dev/pricing) for current rates. Imagen 4 typically charges per image generated.

## Limitations

- English prompts only
- Text in images limited to 25 characters
- Requires active internet connection
- API rate limits apply

## Examples

### Hero Image for Website
```
Prompt: "Professional photograph of modern office space, natural lighting, 
minimalist design, plants, large windows, 16:9 aspect ratio, high quality"
```

### Logo Generation
```
Prompt: "A modern minimalist logo for a tech startup on solid blue background. 
Include the text TechFlow. Geometric shapes, clean lines, professional"
```

### Background Pattern
```
Prompt: "Abstract geometric pattern background, muted blue and gray tones, 
modern, subtle, professional, 16:9"
```

## Troubleshooting

### "No API key found"
- Make sure you've set the `GEMINI_API_KEY` environment variable
- Restart your terminal after setting the variable

### "google-genai not installed"
- Run: `pip install google-genai`

### "API key invalid"
- Verify your API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Make sure you copied the entire key

### Rate Limit Errors
- Wait a few moments and try again
- Consider upgrading your API tier if you need higher limits

## Learn More

- [Imagen Documentation](https://ai.google.dev/gemini-api/docs/imagen)
- [Prompt Writing Guide](https://ai.google.dev/gemini-api/docs/imagen#prompt-writing-basics)
- [Google AI Studio](https://aistudio.google.com/)
