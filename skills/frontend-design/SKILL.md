---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
license: MIT
compatibility: Web (HTML, CSS, JS, React, Next.js, Vue)
allowed-tools: create_file read_file list_directory make_directory write_to_file run_dev_server install_npm_package generate_image
---

## Goal

Design and implement distinctive, production-grade frontend interfaces with exceptional aesthetic quality, strong conceptual direction, and meticulous attention to detail. Avoid generic “AI slop” UI patterns and produce interfaces that feel intentionally designed, memorable, and emotionally engaging.

## Design Philosophy

Each frontend artifact must commit to a **bold, coherent aesthetic direction**. Every decision — typography, layout, color, motion, and spacing — must reinforce that direction.

Core principles:
- Intentional design > default patterns
- Strong visual identity > generic SaaS layouts
- Concept-driven UI > component libraries
- Craftsmanship > speed

## Capabilities

### UI & Frontend Development
- Build full web pages and applications (HTML, CSS, JS, React, Next.js, Vue)
- Create landing pages, dashboards, portfolios, product pages, and experimental interfaces
- Develop reusable UI components with strong aesthetic identity

### Visual Design & Aesthetics
- Advanced typography systems (distinctive font pairings, rhythm, hierarchy)
- Cohesive color systems using CSS variables
- Bold spatial composition (asymmetry, overlap, grid-breaking layouts)
- Atmospheric backgrounds (gradient meshes, noise textures, layered effects)
- Custom UI details (borders, shadows, patterns, textures)

### Motion & Interaction
- Page-load animations with staggered reveals
- High-impact hover and scroll-based interactions
- Subtle micro-interactions for tactile feedback
- Smooth transitions and visual continuity

### Production Quality
- Clean, maintainable, and modular code
- Responsive layouts for all screen sizes
- Accessibility-aware color contrast and typography
- Performance-conscious animations and layouts

## Procedure

1. **Understand Context**
   - Identify purpose, audience, and usage scenario
   - Extract constraints (tech stack, performance, accessibility)

2. **Commit to an Aesthetic Direction**
   - Choose a strong visual and emotional tone (e.g., brutalist, editorial, luxury, industrial, playful, minimal)
   - Define typography strategy, color system, layout logic, and motion language

3. **Design the Interface**
   - Construct layout with intentional composition
   - Select distinctive fonts
   - Establish spacing, rhythm, and visual hierarchy

4. **Implement Code**
   - Write clean, production-grade HTML/CSS/JS or React code
   - Use CSS variables and modular structure
   - Implement motion using CSS or animation libraries when appropriate

5. **Refine Details**
   - Polish transitions, hover states, typography spacing, and alignment
   - Ensure visual coherence and uniqueness

## Aesthetic Guidelines

- **Typography**: Avoid Inter, Roboto, Arial, system fonts. Use distinctive display + refined body font pairings.
- **Color**: Commit to dominant palettes with intentional accent usage. Avoid cliché purple gradients.
- **Layout**: Prefer asymmetry, layered depth, and bold composition.
- **Motion**: One strong animation sequence > many weak micro-effects.
- **Atmosphere**: Use textures, noise, gradients, shadows, and layering for depth.

## Best Practices

- Never use default UI layouts or component-library aesthetics
- Avoid predictable hero → features → pricing → CTA patterns
- Maintain a consistent visual language throughout
- Prioritize emotional impact and memorability
- Write maintainable, scalable frontend code

## Examples

User: "Design a landing page for a CLI developer tool"
→ Commit to brutalist + terminal-inspired aesthetic  
→ Implement asymmetric grid, mono display font, raw textures, dramatic contrast

User: "Build a SaaS dashboard UI"
→ Choose editorial + data-centric design  
→ Create modular card system, layered typography, subtle motion

User: "Make a personal portfolio"
→ Select expressive typography, bold layouts, animated page reveals  
→ Build a visually distinctive, non-template interface


## Image Generation Integration

When building websites or applications, you can generate custom images using the `generate_image` tool:

### When to Offer Image Generation

- **Always ask first**: "Would you like me to generate custom images using Google's Imagen AI for this project?"
- Offer for: hero images, backgrounds, logos, illustrations, product mockups
- Don't generate without permission

### Best Practices

1. **Ask Permission**: Always confirm before generating images
2. **Context-Aware Prompts**: Match the website's aesthetic and purpose
3. **Appropriate Ratios**: 
   - Hero images: 16:9
   - Logos: 1:1
   - Mobile designs: 9:16
   - General content: 4:3
4. **Save to Project**: Use `project-name/images/` directory
5. **Descriptive Names**: `hero-background.png`, `logo.png`, not `image1.png`

### Example Workflow

```
User: "Create a landing page for a coffee shop"

AI: "I'll create a landing page for your coffee shop. Would you like me to generate 
a custom hero image using Google's Imagen AI? (This will create a professional 
photograph of a cozy coffee shop interior)"

User: "Yes please"

AI: [Calls generate_image]
prompt: "Professional photograph of cozy coffee shop interior, warm lighting, 
wooden tables, espresso machine in background, inviting atmosphere, natural light, 
high quality, 16:9 aspect ratio"
output_dir: "coffee-shop/images"
filename: "hero-background.jpg"

[Then creates HTML with the generated image]
```

### Prompt Guidelines for Web Design

- **Hero Images**: "Professional photograph of [subject], [lighting], [atmosphere], 16:9 aspect ratio, high quality"
- **Backgrounds**: "Abstract [style] background, [colors], subtle, modern, 16:9"
- **Logos**: "A [style] logo for a [industry] company on solid color background. Include text [name]."
- **Illustrations**: "Modern [style] illustration of [subject], clean lines, [colors], professional"

### Quality Modifiers

Always include these for professional results:
- "professional"
- "high quality"
- "modern"
- "clean"
- "polished"
