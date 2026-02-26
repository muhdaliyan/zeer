"""
Tool execution display module with collapsible sections like Claude.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from colorama import Fore, Style


class ToolDisplay:
    """Handles clean display of tool execution with collapsible sections."""
    
    def __init__(self):
        self.console = Console()
        self.current_section = None
        self.tool_count = 0
    
    def start_section(self, title: str, collapsible=True):
        """Start a new collapsible section."""
        self.current_section = title
        self.tool_count = 0
        
        # Display section header
        text = Text()
        text.append("● ", style="dim")
        text.append(title, style="bold")
        if collapsible:
            text.append(" (Ctrl+o to expand)", style="dim")
        
        self.console.print(text)
    
    def show_tool(self, tool_name: str, args: dict, success: bool = True):
        """Show a single tool execution."""
        self.tool_count += 1
        
        # Create tool line with green dot
        text = Text()
        text.append("● ", style="green")
        text.append(tool_name, style="cyan")
        
        # Show key argument
        if "path" in args:
            text.append(f" {args['path']}", style="dim")
        elif "directory" in args:
            text.append(f" {args['directory']}", style="dim")
        elif "command" in args:
            text.append(f" {args['command']}", style="dim")
        
        # No tick at the end - just clean line
        
        self.console.print(text)
    
    def show_bash_command(self, command: str, cwd: str = None):
        """Show a bash command being executed."""
        text = Text()
        text.append("● ", style="green bold")
        text.append("Bash", style="green bold")
        
        if cwd:
            text.append(f"(cd {cwd} && {command})", style="dim")
        else:
            text.append(f"({command})", style="dim")
        
        self.console.print(text)
        self.console.print(f"  Running in the background (! to manage)", style="dim")
    
    def show_task_output(self, task_id: str, preview: str = None):
        """Show task output section."""
        text = Text()
        text.append("● ", style="green bold")
        text.append("Task Output", style="green bold")
        text.append(f"(non-blocking) {task_id}", style="dim")
        
        self.console.print(text)
        
        if preview:
            # Show preview of output
            lines = preview.split('\n')[:3]
            for line in lines:
                self.console.print(f"  > {line}", style="dim")
            if len(preview.split('\n')) > 3:
                self.console.print(f"  ... +{len(preview.split('\n')) - 3} lines (Ctrl+o to expand)", style="dim")
    
    def show_server_running(self, name: str, url: str):
        """Show that a server is running."""
        text = Text()
        text.append("● ", style="green bold")
        text.append(f"The development server for ", style="")
        text.append(name, style="bold")
        text.append(" is now running. You can access it at:", style="")
        
        self.console.print()
        self.console.print(text)
        self.console.print()
        self.console.print(f"  {url}", style="bold cyan")
        self.console.print()
        self.console.print("  The server is running in the background. If you need to stop it or see more logs, let me know!", style="dim")
        self.console.print()
    
    def end_section(self):
        """End the current section."""
        if self.tool_count > 0:
            self.console.print()  # Add spacing after tools


# Global instance
_display = ToolDisplay()


def get_tool_display() -> ToolDisplay:
    """Get the global tool display instance."""
    return _display
