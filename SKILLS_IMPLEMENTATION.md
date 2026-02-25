# Agent Skills Implementation

## Overview
Fully implemented Agent Skills following the [agentskills.io](https://agentskills.io) specification.

## Features Implemented

### 1. Progressive Disclosure ✅
- **Metadata Loading**: Only skill names and descriptions are loaded at startup
- **On-Demand Activation**: Full skill content is loaded only when the AI mentions the skill
- **Context Efficiency**: Saves tokens by not loading all skills upfront

### 2. Scripts Directory Support ✅
- Skills can include a `scripts/` directory with executable code
- Scripts are listed when a skill is activated
- AI can reference and use these scripts

### 3. File References ✅
- Skills can reference files within their directory
- Supports `scripts/`, `references/`, and `assets/` directories
- Use relative paths from skill root (e.g., `scripts/setup.py`)

### 4. Validation ✅
- Validates skill format on load
- Checks:
  - Name: max 64 chars, lowercase, numbers, hyphens only
  - Description: required, max 1024 chars
  - Compatibility: max 500 chars
- Displays warnings for invalid skills

## Directory Structure

```
skills/
├── skill-name/
│   ├── SKILL.md          # Required: skill definition
│   ├── scripts/          # Optional: executable code
│   │   └── script.py
│   ├── references/       # Optional: additional docs
│   │   └── api.md
│   └── assets/           # Optional: static resources
│       └── image.png
```

## SKILL.md Format

```markdown
---
name: skill-name
description: What this skill does and when to use it
license: MIT
compatibility: Requirements (optional)
allowed-tools: tool1 tool2 tool3
---

## Skill Content

Instructions, procedures, and best practices...
```

## How It Works

1. **Startup**: AI receives list of available skills (names + descriptions only)
2. **User Request**: User asks for something (e.g., "create a PDF")
3. **Skill Activation**: AI mentions the skill (e.g., "I'll use the pdf skill")
4. **Auto-Load**: System detects skill mention and loads full content + scripts
5. **Execution**: AI follows skill instructions and uses available tools/scripts

## Example: PDF Skill

```
skills/pdf/
├── SKILL.md              # PDF creation instructions
└── scripts/
    └── generate_pdf.py   # Python script for PDF generation
```

When activated, AI receives:
- Full SKILL.md content
- List of available scripts
- Can reference the script in responses

## Creating a New Skill

1. Create folder: `skills/your-skill-name/`
2. Create `SKILL.md` with frontmatter and content
3. (Optional) Add `scripts/` directory with executable code
4. (Optional) Add `references/` for additional docs
5. Skill is automatically discovered and validated

## Validation Rules

- **Name**: lowercase, numbers, hyphens, max 64 chars
- **Description**: required, max 1024 chars
- **Compatibility**: optional, max 500 chars
- Invalid skills show warnings but don't break the system

## Benefits

- **Token Efficient**: Progressive disclosure saves context
- **Modular**: Skills are self-contained and portable
- **Extensible**: Easy to add new capabilities
- **Standard**: Follows open agentskills.io specification
- **Validated**: Automatic format checking
