# Tool Display Improvements

## Goal
Make tool execution display clean and professional like Claude Code, with:
- Collapsible sections for tool groups
- Clean bullet points with status indicators
- Background server management
- No "Thinking..." spinner during tool execution

## Implementation Status

### ✅ Completed
1. Created `src/tool_display.py` with:
   - `ToolDisplay` class for clean formatting
   - Collapsible section support
   - Tool execution display with status
   - Bash command display
   - Server running notifications

### 🔄 In Progress
1. Update `src/chat_session.py`:
   - Replace current tool display with `ToolDisplay`
   - Remove "Thinking..." spinner during tool execution
   - Group tools into collapsible sections

2. Update `src/tools.py`:
   - Modify `run_dev_server()` to run in true background
   - Return immediately with server info
   - Store process handle for management

### 📋 TODO
1. Add process management commands:
   - `!list` - Show running processes
   - `!stop <id>` - Stop a process
   - `!logs <id>` - Show process logs

2. Update `run_bash_command()`:
   - Detect long-running commands (servers, watchers)
   - Run them in background automatically
   - Show clean status message

## Usage Example

```
> run my zeer landing page project

● Read 2 files (Ctrl+o to expand)

● I'll start the development server for your zeer-landing-page project.

● Bash(cd zeer-landing-page && npm run dev)
  Running in the background (! to manage)

● Task Output(non-blocking) b26c0b0
  > zeer-landing-page@0.0.0 dev
  > vite
  ... +6 lines (Ctrl+o to expand)

● The development server for zeer-landing-page is now running. You can access it at:

  http://localhost:5173/

  The server is running in the background. If you need to stop it or see more logs, let me know!
```

## Files to Modify

1. `src/chat_session.py` - Lines 300-420 (tool execution loop)
2. `src/tools.py` - `run_dev_server()` and `run_bash_command()`
3. `src/app_controller.py` - Add process management commands

## Next Steps

1. Update chat_session.py to use ToolDisplay
2. Modify run_dev_server to return immediately
3. Add background process tracking
4. Implement process management commands
