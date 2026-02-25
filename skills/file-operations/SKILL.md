---
name: file-operations
description: Perform file system operations like creating, reading, listing, and managing files and directories. Use for file management, directory navigation, file creation, file reading, ls, cd, mkdir, pwd commands.
license: MIT
compatibility: Requires file system access
allowed-tools: create_file read_file list_directory make_directory get_current_directory change_directory delete_file write_to_file
---

## Goal

Enable the agent to perform common file system operations similar to Unix/Linux commands.

## Available Operations

### List Directory (ls)
Use `list_directory` tool to list contents of a directory.
- Default: lists current directory
- Specify path to list other directories

### Change Directory (cd)
Use `change_directory` tool to navigate to a different directory.
- Provide absolute or relative path

### Print Working Directory (pwd)
Use `get_current_directory` tool to show the current working directory.

### Make Directory (mkdir)
Use `make_directory` tool to create new directories.
- Creates parent directories automatically if needed

### Create File
Use `create_file` tool to create new files.
- Optionally provide initial content
- Creates parent directories if needed

### Read File
Use `read_file` tool to read file contents.
- Returns the full text content of the file

### Write to File
Use `write_to_file` tool to write or append content to files.
- Set `append: true` to add to existing content
- Set `append: false` to overwrite

### Delete File
Use `delete_file` tool to remove files.
- Be careful - this is permanent!

## Procedure

1. When user asks to list files, use `list_directory`
2. When user asks to navigate (cd), use `change_directory`
3. When user asks where they are (pwd), use `get_current_directory`
4. When user asks to create directories, use `make_directory`
5. When user asks to create files, use `create_file`
6. When user asks to read files, use `read_file`
7. When user asks to write to files, use `write_to_file`
8. When user asks to delete files, use `delete_file`

## Examples

User: "List files in the current directory"
→ Use `list_directory` with path="."

User: "Create a new file called test.txt"
→ Use `create_file` with path="test.txt"

User: "What's in the src folder?"
→ Use `list_directory` with path="src"

User: "Create a directory called output"
→ Use `make_directory` with path="output"
