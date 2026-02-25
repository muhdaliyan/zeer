---
name: code-helper
description: Help with code-related tasks like creating project files, reading source code, and organizing code structure. Use for programming, coding, development, project setup, code review.
license: MIT
compatibility: Requires file system access
allowed-tools: create_file read_file list_directory make_directory write_to_file
---

## Goal

Assist developers with common coding tasks including project setup, file organization, and code management.

## Capabilities

### Project Setup
- Create project directory structures
- Generate boilerplate files
- Set up configuration files

### Code Management
- Read and analyze source files
- Create new code files with templates
- Organize code into proper directory structures

### File Organization
- List project files
- Navigate project structure
- Create organized folder hierarchies

## Procedure

1. When setting up a new project:
   - Create root directory with `make_directory`
   - Create subdirectories (src, tests, docs, etc.)
   - Generate initial files (README, config files)

2. When working with existing code:
   - Use `list_directory` to explore structure
   - Use `read_file` to examine source files
   - Use `write_to_file` to update code

3. When creating new code:
   - Use `create_file` with appropriate templates
   - Follow language-specific conventions
   - Include proper comments and documentation

## Best Practices

- Always check if files exist before creating
- Use consistent naming conventions
- Organize code into logical directories
- Include README files for documentation
- Add comments to explain complex logic

## Examples

User: "Set up a Python project"
→ Create directories: src/, tests/, docs/
→ Create files: README.md, requirements.txt, setup.py

User: "Show me the project structure"
→ Use `list_directory` recursively

User: "Create a new Python module for database operations"
→ Use `create_file` with path="src/database.py" and appropriate template
