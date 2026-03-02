---
name: image-generation
description: Generate high-quality images using Google's Imagen models for websites, applications, and creative projects. Use this skill when building websites, landing pages, or any project that needs custom images, logos, illustrations, or visual assets.
license: MIT
compatibility: All platforms (generates PNG/JPEG images)
allowed-tools: create_file read_file list_directory make_directory write_to_file generate_image
---

## Goal

Generate professional, high-quality images using Google's Imagen 4 models and integrate them seamlessly into web projects, applications, or creative workflows. Automatically save generated images to the appropriate project directory.

## Capabilities

### Image Generation
- Generate photorealistic images from text descriptions
- Create logos, illustrations, and graphics for websites
- Generate hero images, backgrounds, and visual assets
- Support for multiple aspect ratios (1:1, 4:3, 16:9, 9:16)
- Generate 1-4 images per request
- High-resolution output with SynthID watermark

### Integration
- Automatically save images to project directories
- Generate appropriate filenames based on content
- Create image assets for web projects (HTML, React, etc.)
- Organize images in logical folder structures

### Supported Styles
- Photography (portraits, landscapes, product shots)
- Illustrations (digital art, sketches, paintings)
- Logos and branding materials
- UI elements and backgrounds
- Historical art styles (impressionism, art deco, etc.)

## Procedure

### When User Requests Website/Project with Images

1. **Identify Image Needs**
   - Analyze the project requirements
   - Determine what images are needed (hero, logo, icons, backgrounds)
   - Ask user if they want AI-generated images using Imagen

2. **Confirm Image Generation**
   - Present the option: "Would you like me to generate custom images using Google's Imagen AI model?"
   - If user agrees, proceed with generation
   - If user declines, use placeholder images or skip

3. **Generate Images**
   - Create detailed, specific prompts based on project context
   - Use appropriate aspect ratios for each use case
   - Generate images using the generate_image tool

4. **Save and Integrate**
   - Save images to project directory (e.g., `website-name/images/`)
   - Use descriptive filenames (e.g., `hero-background.png`, `logo.png`)
   - Update HTML/CSS/React code to reference the generated images
   - Provide image paths in the code

### Direct Image Generation Requests

When user directly asks to generate an image:

1. **Understand Requirements**
   - Extract subject, style, and context from user request
   - Determine appropriate aspect ratio
   - Clarify any ambiguous details

2. **Create Detailed Prompt**
   - Build a comprehensive prompt following Imagen best practices
   - Include subject, context, style, and quality modifiers
   - Keep prompts clear and descriptive

3. **Generate and Save**
   - Use generate_image tool with the crafted prompt
   - Save to appropriate directory
   - Display the saved image path to user

## Imagen Prompt Guidelines

### Prompt Structure
```
[Style] of [Subject] [Context/Background] [Additional Details]
```

### Photography Prompts
- Start with "A photo of..." or "A photograph of..."
- Add camera details: "35mm portrait", "wide angle 10mm", "macro lens 60mm"
- Include lighting: "golden hour", "dramatic lighting", "natural light"
- Add film types: "black and white film", "film noir", "polaroid"

### Illustration Prompts
- Specify art style: "digital art", "watercolor painting", "pencil sketch"
- Reference art movements: "impressionist style", "art deco", "minimalist"
- Add quality modifiers: "highly detailed", "professional", "award-winning"

### Logo Prompts
- Use format: "A [style] logo for a [industry] company on a solid color background. Include the text [name]."
- Styles: minimalist, modern, traditional, geometric, abstract
- Keep text under 25 characters

### Quality Modifiers
Add these for better results:
- "highly detailed"
- "professional"
- "award-winning"
- "high resolution"
- "photorealistic"
- "4K quality"

## Aspect Ratios

Choose based on use case:
- **1:1 (Square)** - Social media, profile images, icons
- **4:3 (Fullscreen)** - General photography, product shots
- **3:4 (Portrait)** - Vertical layouts, mobile screens
- **16:9 (Widescreen)** - Hero images, banners, landscapes
- **9:16 (Portrait)** - Mobile-first designs, stories

## Tool: generate_image

**IMPORTANT**: This is a SIMULATED tool for demonstration. The actual implementation requires:
1. Google Cloud API key with Imagen access
2. Integration with `google.genai` Python library
3. Proper API configuration

### Usage
```python
generate_image(
    prompt="A modern minimalist logo for a tech startup on a solid blue background",
    aspect_ratio="1:1",
    number_of_images=1,
    output_dir="website/images",
    filename="logo.png"
)
```

### Parameters
- `prompt` (required): Detailed text description of the image
- `aspect_ratio` (optional): "1:1", "4:3", "3:4", "16:9", "9:16" (default: "1:1")
- `number_of_images` (optional): 1-4 (default: 1)
- `output_dir` (optional): Directory to save images (default: "generated_images")
- `filename` (optional): Custom filename (default: auto-generated)

## Examples

### Example 1: Website Hero Image
```
User: "Create a landing page for a coffee shop"

AI: "I'll create a landing page for your coffee shop. Would you like me to generate a custom hero image using Google's Imagen AI?"

User: "Yes please"

AI: [Generates image with prompt]
"A professional photograph of a cozy coffee shop interior, warm lighting, wooden tables, espresso machine in background, inviting atmosphere, 16:9 aspect ratio"

[Saves to coffee-shop/images/hero-background.jpg]
[Updates HTML to use the image]
```

### Example 2: Logo Generation
```
User: "Generate a logo for my fitness app called FitTrack"

AI: [Generates with prompt]
"A modern minimalist logo for a fitness company on a solid color background. Include the text FitTrack. Geometric shapes, energetic, professional"

[Saves to generated_images/fittrack-logo.png]
```

### Example 3: Multiple Assets
```
User: "Build a portfolio website and generate images for it"

AI: "I'll create your portfolio website. Would you like me to generate custom images (hero background, profile photo placeholder, project thumbnails) using Imagen AI?"

User: "Yes, generate them"

AI: [Generates multiple images]
1. Hero background: "Abstract geometric pattern, modern, professional, muted colors, 16:9"
2. Project thumbnail 1: "Minimalist tech illustration, clean lines, blue and white, 4:3"
3. Project thumbnail 2: "Creative design mockup, modern interface, professional, 4:3"

[Saves all to portfolio/images/]
[Updates HTML/CSS with image references]
```

## Best Practices

1. **Always Ask Permission** - Before generating images, ask if user wants AI-generated images
2. **Context-Aware Prompts** - Tailor prompts to match the project's style and purpose
3. **Appropriate Aspect Ratios** - Choose ratios that fit the use case
4. **Descriptive Filenames** - Use clear, semantic filenames (hero-bg.png, not image1.png)
5. **Organized Structure** - Save images in logical directories (images/, assets/, etc.)
6. **Quality First** - Use quality modifiers for professional results
7. **Iterate if Needed** - If user isn't satisfied, refine the prompt and regenerate

## Integration with Frontend Projects

When building websites with this skill:

1. Create images directory first
2. Generate images before writing HTML/CSS
3. Use relative paths in code: `<img src="images/hero.jpg">`
4. Add alt text describing the generated image
5. Consider responsive images with multiple sizes

## Limitations

- Imagen supports English prompts only
- Text in images limited to 25 characters
- Generated images include SynthID watermark
- Requires Google Cloud API access
- Rate limits apply based on API tier

## Notes

This skill works best when combined with:
- `frontend-design` skill for complete website creation
- `code-helper` skill for project setup
- `file-operations` skill for organizing assets
