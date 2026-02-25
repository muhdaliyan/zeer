# Agent Skills

This directory contains agent skills following the [agentskills.io](https://agentskills.io) specification.

## Quality Standards

All skills follow the universal quality standards defined in [QUALITY_STANDARDS.md](./QUALITY_STANDARDS.md). Each skill also has its own specific quality guidelines in its SKILL.md file.

## What are Agent Skills?

Agent Skills are modular packages of instructions, scripts, and resources that AI agents can discover and use to perform specific tasks more accurately and efficiently.

## Available Skills

### file-operations
Perform file system operations like creating, reading, listing, and managing files and directories.

**Tools:** create_file, read_file, list_directory, make_directory, get_current_directory, change_directory, delete_file, write_to_file

**Use cases:**
- List files (ls command)
- Navigate directories (cd command)
- Create files and folders
- Read and write files

### code-helper
Help with code-related tasks like creating project files, reading source code, and organizing code structure.

**Tools:** create_file, read_file, list_directory, make_directory, write_to_file

**Use cases:**
- Project setup
- Code organization
- File management for development

## Creating New Skills

To create a new skill:

1. Create a new directory in `skills/` with a lowercase, hyphenated name
2. Create a `SKILL.md` file with the following structure:

```markdown
---
name: your-skill-name
description: What your skill does and when to use it
license: MIT
compatibility: Any requirements
allowed-tools: tool1 tool2 tool3
---

## Goal

What this skill helps accomplish

## Procedure

1. Step-by-step instructions
2. For the agent to follow

## Examples

Example usage scenarios
```

3. Optionally add:
   - `scripts/` - Executable scripts
   - `references/` - Additional documentation
   - `assets/` - Static resources

## Skill Format

Skills follow the [Agent Skills specification](https://agentskills.io/specification):

- **name**: Lowercase, hyphenated identifier (max 64 chars)
- **description**: Clear description of what the skill does (max 1024 chars)
- **license**: License information (optional)
- **compatibility**: Environment requirements (optional)
- **allowed-tools**: Space-delimited list of tools the skill can use (optional)

## Using Skills

Skills are automatically loaded when zeer CLI starts. Use the `/skills` command in chat to see all available skills.

The AI agent will automatically select and use appropriate skills based on your requests.

## Learn More

- [Agent Skills Documentation](https://agentskills.io)
- [Specification](https://agentskills.io/specification)
- [Example Skills](https://github.com/anthropics/agent-skills)
