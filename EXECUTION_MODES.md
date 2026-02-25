# Execution Modes

Zeer CLI supports two execution modes for file generation and tool execution:

## Deliberate Mode (Default) ⭐

**Recommended for quality work**

In deliberate mode, the AI:
- Creates files one-by-one with progress indicators
- Adds small pauses between file creations (300ms by default)
- Shows detailed progress: `[1/10] ● create_file`
- Pauses every 3 files to "reflect" on progress
- Encourages the AI to think more carefully about each file
- Results in higher quality, more thoughtful code

**Best for:**
- Building websites and applications
- Creating complex projects
- When you want professional, polished output
- Learning and understanding the generation process

## Fast Mode

**Maximum speed execution**

In fast mode, the AI:
- Creates all files simultaneously
- No delays between operations
- Grouped display by tool type
- Optimized for speed over deliberation

**Best for:**
- Simple file operations
- Quick prototypes
- When you know exactly what you want
- Batch operations

## Switching Modes

Use the `/mode` command in the CLI:

```
> /mode
```

Or edit the config file directly at `~/.zeer/config.json`:

```json
{
  "execution_mode": "deliberate",
  "max_tools_per_batch": 3,
  "file_creation_delay": 0.3,
  "show_progress": true
}
```

## Configuration Options

- `execution_mode`: `"deliberate"` or `"fast"`
- `max_tools_per_batch`: Number of tools to execute before pausing (deliberate mode only)
- `file_creation_delay`: Seconds to pause between file creations (deliberate mode only)
- `show_progress`: Show detailed progress indicators

## Why Deliberate Mode?

When the AI creates files too quickly, it tends to:
- Use generic templates without customization
- Skip important details and edge cases
- Create basic/ugly styling
- Not think through file interactions

Deliberate mode forces the AI to slow down, resulting in:
- More thoughtful implementations
- Better code quality and structure
- Modern, polished designs
- Proper error handling and comments
- Professional-grade output

## Example Output

### Deliberate Mode
```
[1/8] ● create_file
     src/App.jsx
     ✓ Done

[2/8] ● create_file
     src/components/Header.jsx
     ✓ Done

[3/8] ● create_file
     src/styles/App.css
     ✓ Done

⏸  Pausing to review progress...

[4/8] ● create_file
     ...
```

### Fast Mode
```
● create_file
  └─ 8 calls
     src/App.jsx
     src/components/Header.jsx
     src/styles/App.css
     ...
```

## Tips

1. Start with deliberate mode for new projects
2. Switch to fast mode for simple edits or known patterns
3. Adjust `file_creation_delay` if you want faster/slower execution
4. Use `max_tools_per_batch` to control pause frequency
