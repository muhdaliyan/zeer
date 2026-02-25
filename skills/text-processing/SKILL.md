---
name: text-processing
description: Process and manipulate text files, including reading, writing, searching, and transforming text content. Use for text editing, file content manipulation, search and replace, text analysis.
license: MIT
compatibility: Requires file system access
allowed-tools: read_file write_to_file create_file list_directory
---

## Goal

Enable text processing operations on files, including reading, writing, searching, and transforming text content.

## Capabilities

### Read Text Files
- Read entire file contents
- Display file content to user
- Extract specific information from files

### Write Text Files
- Create new text files
- Overwrite existing files
- Append to existing files

### Text Analysis
- Count lines, words, characters
- Search for patterns
- Extract specific sections

### Text Transformation
- Format text content
- Replace text patterns
- Combine multiple files

## Procedure

1. **Reading Files**
   - Use `read_file` to get file contents
   - Present content to user or analyze it

2. **Writing Files**
   - Use `create_file` for new files
   - Use `write_to_file` with append=false to overwrite
   - Use `write_to_file` with append=true to add content

3. **Processing Text**
   - Read file content
   - Process/transform in memory
   - Write results back to file

4. **Batch Operations**
   - Use `list_directory` to find files
   - Process each file individually
   - Report results

## Examples

User: "Read the contents of README.md"
→ Use `read_file` with path="README.md"

User: "Create a file called notes.txt with 'Meeting notes'"
→ Use `create_file` with path="notes.txt" and content="Meeting notes"

User: "Append 'New line' to notes.txt"
→ Use `write_to_file` with path="notes.txt", content="New line", append=true

User: "Show me all text files in the docs folder"
→ Use `list_directory` with path="docs"
→ Filter results for .txt files

## Best Practices

- Always check if file exists before reading
- Confirm before overwriting files
- Use appropriate line endings for the platform
- Handle encoding properly (UTF-8 default)
- Provide clear feedback on operations performed
