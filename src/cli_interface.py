"""
CLI Interface module for zeer.

This module handles all user interaction, input collection, and output formatting.
"""

from typing import List, Optional
import sys
import inquirer
from colorama import Fore, Style, init
import time
import threading
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style as PromptStyle
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

init(autoreset=True)

console = Console()
WIDTH = 100  # Maximum width for better readability


class CommandCompleter(Completer):
    """Autocomplete completer for slash commands."""
    
    def __init__(self):
        self.commands = {
            "/models": "Switch model",
            "/providers": "Switch provider",
            "/clear": "Clear conversation",
            "/reset": "Reset everything",
            "/skills": "List agent skills",
            "/tools": "List available tools",
            "/mode": "Toggle execution mode",
            "/exit": "Exit application",
            "/help": "Show help"
        }
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # Only show completions if text starts with /
        if text.startswith('/'):
            for cmd, desc in self.commands.items():
                if cmd.startswith(text.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=f"{cmd}",
                        display_meta=desc
                    )


def get_command_match(text: str) -> Optional[str]:
    """Get the first matching command for auto-completion."""
    commands = ["/models", "/providers", "/clear", "/reset", "/skills", "/tools", "/mode", "/exit", "/help"]
    
    if text.startswith('/') and len(text) > 1:
        for cmd in commands:
            if cmd.startswith(text.lower()):
                return cmd
    return None


def separator():
    return f"{Fore.CYAN}{'─' * WIDTH}{Style.RESET_ALL}"


def display_branding() -> None:
    from src import __version__
    import os
    import shutil
    from src.config import get_config

    # Get terminal width and current working directory
    term_width = shutil.get_terminal_size().columns
    cwd = os.getcwd()
    
    # Get execution mode
    config = get_config()
    execution_mode = config.get("execution_mode", "deliberate")
    mode_display = execution_mode.capitalize()
    
    # Always show banner, but adapt size to terminal
    # Minimum 60 chars, maximum 100 chars
    total_width = max(60, min(term_width - 2, 100))
    
    divider_pos = total_width // 2
    
    # Left and right section widths (excluding borders)
    left_width = divider_pos - 1
    right_width = total_width - divider_pos - 1
    
    # Compact logo for small terminals
    if total_width < 80:
        logo_lines = [
            "███████╗███████╗███████╗██████╗",
            "╚══███╔╝██╔════╝██╔════╝██╔══██╗",
            "  ███╔╝ █████╗  █████╗  ██████╔╝",
            " ███╔╝  ██╔══╝  ██╔══╝  ██╔══██╗",
            "███████╗███████╗███████╗██║  ██║",
            "╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝"
        ]
    else:
        logo_lines = [
            "███████╗███████╗███████╗██████╗ ",
            "╚══███╔╝██╔════╝██╔════╝██╔══██╗",
            "  ███╔╝ █████╗  █████╗  ██████╔╝",
            " ███╔╝  ██╔══╝  ██╔══╝  ██╔══██╗",
            "███████╗███████╗███████╗██║  ██║",
            "╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝"
        ]
    
    # Compact text for small terminals
    if total_width < 70:
        subtitle_text = "AI CLI"
        version_text = f"v{__version__}"
    else:
        subtitle_text = "Agentic AI CLI • OpenSource"
        version_text = f"v{__version__}"
    
    # Right section content - adapt text length based on width
    dir_label = "Dir:" if total_width < 80 else "Directory:"
    max_dir_len = right_width - len(dir_label) - 3
    if len(cwd) > max_dir_len:
        dir_text = "..." + cwd[-(max_dir_len - 3):]
    else:
        dir_text = cwd
    
    # Helper functions
    def center_text(text, width):
        """Center text within given width."""
        text_len = len(text)
        if text_len >= width:
            return text[:width]
        padding_left = (width - text_len) // 2
        padding_right = width - text_len - padding_left
        return ' ' * padding_left + text + ' ' * padding_right
    
    def left_align_text(text, width, indent=1):
        """Left align text with indent."""
        text_len = len(text)
        if text_len >= width - indent:
            return ' ' * indent + text[:width - indent]
        return ' ' * indent + text + ' ' * (width - text_len - indent)
    
    # Build content for both sides
    left_content_lines = []
    right_content_lines = []
    
    # Left side content - add empty line at top for centering
    left_content_lines.append(('', 'empty'))
    for logo_line in logo_lines:
        left_content_lines.append((logo_line, 'logo'))
    left_content_lines.append(('', 'empty'))
    left_content_lines.append((subtitle_text, 'subtitle'))
    left_content_lines.append((version_text, 'version'))
    left_content_lines.append(('', 'empty'))
    
    # Right side content - show mode instead of recent activity
    if total_width < 80:
        # Compact text for small terminals
        right_content_lines.append(('Getting started', 'title'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append(('/ for commands', 'item'))
        right_content_lines.append(('@ for file path', 'item'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append((f"Mode: {mode_display}", 'mode'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append((f"{dir_label} {dir_text}", 'dir'))
    else:
        # Full text for larger terminals
        right_content_lines.append(('Tips for getting started', 'title'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append(('Run / for commands', 'item'))
        right_content_lines.append(('Use @ for file path', 'item'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append(('Execution mode', 'title'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append((mode_display, 'mode'))
        right_content_lines.append(('', 'empty'))
        right_content_lines.append((f"{dir_label} {dir_text}", 'dir'))
    
    # Make sure both sides have same number of lines
    max_lines = max(len(left_content_lines), len(right_content_lines))
    
    while len(left_content_lines) < max_lines:
        left_content_lines.append(('', 'empty'))
    while len(right_content_lines) < max_lines:
        right_content_lines.append(('', 'empty'))
    
    # Build banner lines - stick together with no extra spacing
    lines = []
    
    # Top border
    lines.append(f"{Fore.RED}┌{'─' * left_width}┬{'─' * right_width}┐{Style.RESET_ALL}")
    
    # Build all content rows
    for i in range(max_lines):
        left_text, left_type = left_content_lines[i]
        right_text, right_type = right_content_lines[i]
        
        # Format left side
        if left_type == 'logo':
            left_formatted = center_text(left_text, left_width)
            left_colored = f"{Fore.MAGENTA}{left_formatted}{Fore.RED}"
        elif left_type == 'subtitle':
            left_formatted = center_text(left_text, left_width)
            left_colored = f"{Fore.GREEN}{left_formatted}{Fore.RED}"
        elif left_type == 'version':
            left_formatted = center_text(left_text, left_width)
            left_colored = f"{Fore.CYAN}{left_formatted}{Fore.RED}"
        else:
            left_formatted = ' ' * left_width
            left_colored = left_formatted
        
        # Format right side
        if right_type == 'title':
            right_formatted = left_align_text(right_text, right_width, 1)
            right_colored = f"{Fore.MAGENTA}{right_formatted}{Fore.RED}"
        elif right_type == 'item':
            right_formatted = left_align_text(right_text, right_width, 1)
            right_colored = f"{Fore.LIGHTBLACK_EX}{right_formatted}{Fore.RED}"
        elif right_type == 'mode':
            right_formatted = left_align_text(right_text, right_width, 1)
            right_colored = f"{Fore.CYAN}{right_formatted}{Fore.RED}"
        elif right_type == 'dir':
            right_formatted = left_align_text(right_text, right_width, 1)
            right_colored = f"{Fore.LIGHTBLACK_EX}{right_formatted}{Fore.RED}"
        else:
            right_formatted = ' ' * right_width
            right_colored = right_formatted
        
        lines.append(f"{Fore.RED}│{left_colored}│{right_colored}│{Style.RESET_ALL}")
    
    # Bottom border
    lines.append(f"{Fore.RED}└{'─' * left_width}┴{'─' * right_width}┘{Style.RESET_ALL}")
    
    # Print banner with no extra newlines - stick together
    print('\n' + '\n'.join(lines) + '\n')


def display_error(error: str) -> None:
    print(f"\n{Fore.RED}✗ Error:{Style.RESET_ALL} {error}\n", file=sys.stderr)


def prompt_choice(prompt: str, options: List[str]) -> str:
    questions = [
        inquirer.List(
            "choice",
            message=prompt,
            choices=options,
            carousel=True,
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        raise KeyboardInterrupt

    return answers["choice"]


def prompt_searchable_choice(prompt_text: str, options: List[str], placeholder: str = "Type to filter...") -> str:
    """
    Display a searchable list with real-time filtering as you type.
    Exact UI like Claude's command palette - search at top, results below with descriptions.
    
    Args:
        prompt_text: The prompt message to display
        options: List of options to choose from
        placeholder: Not used, kept for compatibility
        
    Returns:
        The selected option
    """
    import sys
    import os
    import shutil
    from colorama import Fore, Style
    
    # Detect platform
    is_windows = os.name == 'nt'
    
    if is_windows:
        import msvcrt
    else:
        import tty
        import termios
    
    # Get terminal width dynamically
    term_width = shutil.get_terminal_size().columns
    display_width = min(term_width - 2, 80)  # Max 80, but adapt to smaller terminals
    
    # State
    search_query = ""
    selected_index = 0
    filtered_options = options.copy()
    last_display_lines = 0
    
    def filter_options(query):
        if not query:
            return options
        query_lower = query.lower()
        return [opt for opt in options if query_lower in opt.lower()]
    
    def clear_previous_display():
        """Clear the previous display by moving up and clearing lines."""
        nonlocal last_display_lines
        if last_display_lines > 0:
            for _ in range(last_display_lines):
                sys.stdout.write('\033[F')  # Move up one line
                sys.stdout.write('\033[K')  # Clear line
            sys.stdout.flush()
    
    def truncate_text(text, max_length):
        """Truncate text with ellipsis if too long."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def display_list():
        nonlocal last_display_lines
        
        # Clear previous display
        clear_previous_display()
        
        lines = []
        
        # Top border line
        lines.append(f"{Fore.LIGHTBLACK_EX}{'─' * display_width}{Style.RESET_ALL}")
        
        # Search input with cursor
        search_display = search_query if search_query else ""
        cursor = "█" if len(search_display) == 0 else ""
        search_line = f"{Fore.CYAN}> {Style.RESET_ALL}{search_display}{cursor}"
        lines.append(search_line)
        
        # Bottom border line
        lines.append(f"{Fore.LIGHTBLACK_EX}{'─' * display_width}{Style.RESET_ALL}")
        
        # Add "esc to cancel" hint in grey
        lines.append(f"{Fore.LIGHTBLACK_EX}esc to cancel{Style.RESET_ALL}")
        
        if not filtered_options:
            lines.append(f"{Fore.YELLOW}No matches found{Style.RESET_ALL}")
        else:
            # Show filtered options (max 8 visible for cleaner look)
            visible_start = max(0, selected_index - 4)
            visible_end = min(len(filtered_options), visible_start + 8)
            
            # Calculate available width for name and description
            name_width = min(40, display_width // 2)
            desc_width = display_width - name_width - 1
            
            for i in range(visible_start, visible_end):
                option = filtered_options[i]
                
                # Split option into name and description if it has parentheses
                if '(' in option and ')' in option:
                    # Extract name and description
                    parts = option.split('(', 1)
                    name = parts[0].strip()
                    desc = '(' + parts[1]
                    
                    # Truncate to fit terminal
                    name_display = truncate_text(name, name_width - 2)  # Leave space for >
                    desc_display = truncate_text(desc, desc_width)
                    
                    if i == selected_index:
                        # Selected item - highlighted with >
                        lines.append(f"{Fore.CYAN}> {name_display}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{desc_display}{Style.RESET_ALL}")
                    else:
                        # Normal item with spacing
                        lines.append(f"  {name_display} {Fore.LIGHTBLACK_EX}{desc_display}{Style.RESET_ALL}")
                else:
                    # No description, just show the option
                    option_display = truncate_text(option, display_width - 2)  # Leave space for >
                    if i == selected_index:
                        lines.append(f"{Fore.CYAN}> {option_display}{Style.RESET_ALL}")
                    else:
                        lines.append(f"  {option_display}")
        
        # Print all lines
        for line in lines:
            print(line)
        
        # Remember how many lines we printed
        last_display_lines = len(lines)
        sys.stdout.flush()
    
    def read_key_windows():
        """Read a key on Windows."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            if key == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif key == b'\x1b':  # ESC
                raise KeyboardInterrupt
            elif key == b'\r':  # Enter
                return 'enter'
            elif key == b'\x08':  # Backspace
                return 'backspace'
            elif key == b'\xe0':  # Arrow keys prefix
                arrow = msvcrt.getch()
                if arrow == b'H':  # Up
                    return 'up'
                elif arrow == b'P':  # Down
                    return 'down'
            elif key == b'\x00':  # Function keys prefix
                msvcrt.getch()  # Consume next byte
                return None
            else:
                try:
                    return key.decode('utf-8')
                except:
                    return None
        return None
    
    def read_key_unix(fd):
        """Read a key on Unix."""
        char = sys.stdin.read(1)
        
        if char == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif char == '\x1b':  # ESC or escape sequence
            # Try to read more characters to see if it's an arrow key
            import select
            if select.select([sys.stdin], [], [], 0.1)[0]:
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    next2 = sys.stdin.read(1)
                    if next2 == 'A':
                        return 'up'
                    elif next2 == 'B':
                        return 'down'
            # If no more characters, it's just ESC
            raise KeyboardInterrupt
        elif char == '\r' or char == '\n':  # Enter
            return 'enter'
        elif char == '\x7f':  # Backspace
            return 'backspace'
        elif char.isprintable():
            return char
        return None
    
    # Save terminal settings (Unix only)
    if not is_windows:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
    
    try:
        # Set terminal to raw mode (Unix only)
        if not is_windows:
            tty.setraw(fd)
        
        # Initial display
        display_list()
        
        while True:
            # Read key based on platform
            if is_windows:
                import time
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                key = read_key_windows()
            else:
                key = read_key_unix(fd)
            
            if key is None:
                continue
            
            # Handle key
            if key == 'enter':
                # Clear the display
                clear_previous_display()
                
                if filtered_options:
                    return filtered_options[selected_index]
                else:
                    print(f"{Fore.RED}No options available{Style.RESET_ALL}")
                    raise KeyboardInterrupt
                    
            elif key == 'up':
                if selected_index > 0:
                    selected_index -= 1
                    
            elif key == 'down':
                if selected_index < len(filtered_options) - 1:
                    selected_index += 1
                    
            elif key == 'backspace':
                if search_query:
                    search_query = search_query[:-1]
                    filtered_options = filter_options(search_query)
                    selected_index = 0
                    
            elif isinstance(key, str) and len(key) == 1 and key.isprintable():
                search_query += key
                filtered_options = filter_options(search_query)
                selected_index = 0
            
            # Redraw
            display_list()
    
    except KeyboardInterrupt:
        # Clean up display when ESC is pressed
        clear_previous_display()
        raise
            
    finally:
        # Restore terminal settings (Unix only)
        if not is_windows:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def prompt_slash_command() -> str:
    commands = [
        "/models - Switch model",
        "/providers - Switch provider",
        "/clear - Clear conversation",
        "/reset - Reset everything",
        "/skills - List agent skills",
        "/tools - List available tools",
        "/mode - Toggle execution mode",
        "/exit - Exit application",
        "/help - Show help",
        "Cancel",  # Move Cancel to bottom
    ]

    try:
        # Use special searchable selection that only searches command names
        selected = prompt_searchable_choice_commands(
            "Select command",
            commands
        )

        if selected == "Cancel":
            return ""

        return selected.split(" - ")[0]

    except KeyboardInterrupt:
        return ""


def prompt_file_reference() -> str:
    """Show searchable file picker for @ file references with directory navigation."""
    import os
    
    current_dir = '.'
    
    while True:
        try:
            # Get all items (files and directories) in current directory
            items = []
            
            # Add parent directory option if not at root
            if current_dir != '.':
                items.append('../ (Go back)')
            
            # List directories first, then files
            dirs = []
            files = []
            
            try:
                for item in os.listdir(current_dir):
                    item_path = os.path.join(current_dir, item)
                    if os.path.isdir(item_path):
                        # Skip common excluded directories
                        if item not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.pytest_cache', '.egg-info'}:
                            dirs.append(f"📁 {item}/")
                    elif os.path.isfile(item_path):
                        files.append(f"📄 {item}")
            except PermissionError:
                display_error("Permission denied to access this directory")
                if current_dir == '.':
                    return ""
                current_dir = os.path.dirname(current_dir) if os.path.dirname(current_dir) else '.'
                continue
            
            # Combine: directories first, then files
            dirs.sort()
            files.sort()
            items.extend(dirs)
            items.extend(files)
            
            # Add cancel option at the end
            items.append("Cancel")
            
            if len(items) == 1:  # Only "Cancel" option
                items.insert(0, "(Empty directory)")
            
            # Show current directory in the prompt
            display_path = current_dir if current_dir != '.' else 'Current directory'
            
            # Show searchable picker
            selected = prompt_searchable_choice(
                f"Browse: {display_path}",
                items
            )
            
            if selected == "Cancel":
                return ""
            
            if selected == "(Empty directory)":
                continue
            
            # Handle parent directory
            if selected == '../ (Go back)':
                current_dir = os.path.dirname(current_dir) if os.path.dirname(current_dir) else '.'
                continue
            
            # Remove emoji prefix
            if selected.startswith('📁 '):
                # It's a directory - navigate into it
                dir_name = selected[2:].rstrip('/')
                current_dir = os.path.join(current_dir, dir_name)
                continue
            elif selected.startswith('📄 '):
                # It's a file - return the full path
                file_name = selected[2:]
                file_path = os.path.join(current_dir, file_name)
                # Normalize the path
                file_path = os.path.normpath(file_path)
                return file_path
            
        except KeyboardInterrupt:
            return ""
        except Exception as e:
            display_error(f"Error browsing files: {str(e)}")
            return ""


def prompt_searchable_choice_commands(prompt_text: str, options: List[str]) -> str:
    """
    Searchable list for commands - searches only the command name, not description.
    """
    import sys
    import os
    import shutil
    from colorama import Fore, Style
    
    # Detect platform
    is_windows = os.name == 'nt'
    
    if is_windows:
        import msvcrt
    else:
        import tty
        import termios
    
    # Get terminal width dynamically
    term_width = shutil.get_terminal_size().columns
    display_width = min(term_width - 2, 80)  # Max 80, but adapt to smaller terminals
    
    # State
    search_query = ""
    selected_index = 0
    filtered_options = options.copy()
    last_display_lines = 0
    
    def filter_options(query):
        if not query:
            return options
        query_lower = query.lower()
        # Only search in the command name (before " - ")
        filtered = []
        for opt in options:
            command_name = opt.split(" - ")[0] if " - " in opt else opt
            if query_lower in command_name.lower():
                filtered.append(opt)
        return filtered
    
    def clear_previous_display():
        """Clear the previous display by moving up and clearing lines."""
        nonlocal last_display_lines
        if last_display_lines > 0:
            for _ in range(last_display_lines):
                sys.stdout.write('\033[F')  # Move up one line
                sys.stdout.write('\033[K')  # Clear line
            sys.stdout.flush()
    
    def truncate_text(text, max_length):
        """Truncate text with ellipsis if too long."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def display_list():
        nonlocal last_display_lines
        
        # Clear previous display
        clear_previous_display()
        
        lines = []
        
        # Top border line
        lines.append(f"{Fore.LIGHTBLACK_EX}{'─' * display_width}{Style.RESET_ALL}")
        
        # Search input with cursor
        search_display = search_query if search_query else ""
        cursor = "█" if len(search_display) == 0 else ""
        search_line = f"{Fore.CYAN}> {Style.RESET_ALL}{search_display}{cursor}"
        lines.append(search_line)
        
        # Bottom border line
        lines.append(f"{Fore.LIGHTBLACK_EX}{'─' * display_width}{Style.RESET_ALL}")
        
        # Add "esc to cancel" hint in grey
        lines.append(f"{Fore.LIGHTBLACK_EX}esc to cancel{Style.RESET_ALL}")
        
        if not filtered_options:
            lines.append(f"{Fore.YELLOW}No matches found{Style.RESET_ALL}")
        else:
            # Show filtered options (max 8 visible for cleaner look)
            visible_start = max(0, selected_index - 4)
            visible_end = min(len(filtered_options), visible_start + 8)
            
            # Calculate available width for name and description
            name_width = min(40, display_width // 2)
            desc_width = display_width - name_width - 1
            
            for i in range(visible_start, visible_end):
                option = filtered_options[i]
                
                # Split option into name and description if it has " - "
                if ' - ' in option:
                    parts = option.split(' - ', 1)
                    name = parts[0].strip()
                    desc = parts[1].strip()
                    
                    # Truncate to fit terminal
                    name_display = truncate_text(name, name_width - 2)  # Leave space for >
                    desc_display = truncate_text(desc, desc_width)
                    
                    if i == selected_index:
                        # Selected item - highlighted with >
                        lines.append(f"{Fore.CYAN}> {name_display}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{desc_display}{Style.RESET_ALL}")
                    else:
                        # Normal item with spacing
                        lines.append(f"  {name_display} {Fore.LIGHTBLACK_EX}{desc_display}{Style.RESET_ALL}")
                else:
                    # No description, just show the option
                    option_display = truncate_text(option, display_width - 2)  # Leave space for >
                    if i == selected_index:
                        lines.append(f"{Fore.CYAN}> {option_display}{Style.RESET_ALL}")
                    else:
                        lines.append(f"  {option_display}")
        
        # Print all lines
        for line in lines:
            print(line)
        
        # Remember how many lines we printed
        last_display_lines = len(lines)
        sys.stdout.flush()
    
    def read_key_windows():
        """Read a key on Windows."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            if key == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif key == b'\x1b':  # ESC
                raise KeyboardInterrupt
            elif key == b'\r':  # Enter
                return 'enter'
            elif key == b'\x08':  # Backspace
                return 'backspace'
            elif key == b'\xe0':  # Arrow keys prefix
                arrow = msvcrt.getch()
                if arrow == b'H':  # Up
                    return 'up'
                elif arrow == b'P':  # Down
                    return 'down'
            elif key == b'\x00':  # Function keys prefix
                msvcrt.getch()  # Consume next byte
                return None
            else:
                try:
                    return key.decode('utf-8')
                except:
                    return None
        return None
    
    def read_key_unix(fd):
        """Read a key on Unix."""
        char = sys.stdin.read(1)
        
        if char == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif char == '\x1b':  # ESC or escape sequence
            # Try to read more characters to see if it's an arrow key
            import select
            if select.select([sys.stdin], [], [], 0.1)[0]:
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    next2 = sys.stdin.read(1)
                    if next2 == 'A':
                        return 'up'
                    elif next2 == 'B':
                        return 'down'
            # If no more characters, it's just ESC
            raise KeyboardInterrupt
        elif char == '\r' or char == '\n':  # Enter
            return 'enter'
        elif char == '\x7f':  # Backspace
            return 'backspace'
        elif char.isprintable():
            return char
        return None
    
    # Save terminal settings (Unix only)
    if not is_windows:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
    
    try:
        # Set terminal to raw mode (Unix only)
        if not is_windows:
            tty.setraw(fd)
        
        # Initial display
        display_list()
        
        while True:
            # Read key based on platform
            if is_windows:
                import time
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                key = read_key_windows()
            else:
                key = read_key_unix(fd)
            
            if key is None:
                continue
            
            # Handle key
            if key == 'enter':
                # Clear the display
                clear_previous_display()
                
                if filtered_options:
                    return filtered_options[selected_index]
                else:
                    print(f"{Fore.RED}No options available{Style.RESET_ALL}")
                    raise KeyboardInterrupt
                    
            elif key == 'up':
                if selected_index > 0:
                    selected_index -= 1
            elif key == 'down':
                if selected_index < len(filtered_options) - 1:
                    selected_index += 1
                    
            elif key == 'backspace':
                if search_query:
                    search_query = search_query[:-1]
                    filtered_options = filter_options(search_query)
                    selected_index = 0
                    
            elif isinstance(key, str) and len(key) == 1 and key.isprintable():
                search_query += key
                filtered_options = filter_options(search_query)
                selected_index = 0
            
            # Redraw
            display_list()
    
    except KeyboardInterrupt:
        # Clean up display when ESC is pressed
        clear_previous_display()
        raise
            
    finally:
        # Restore terminal settings (Unix only)
        if not is_windows:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def display_success(message: str) -> None:
    """Display success message with text wrapping."""
    import textwrap
    import shutil
    
    # Get terminal width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 4, 100)  # Leave some margin
    
    # Wrap text to fit terminal
    wrapped = textwrap.fill(message, width=max_width, subsequent_indent='  ')
    print(f"{Fore.GREEN}✓{Style.RESET_ALL} {wrapped}")


def display_info(message: str) -> None:
    """Display info message with text wrapping."""
    import textwrap
    import shutil
    
    # Get terminal width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 4, 100)  # Leave some margin
    
    # Wrap text to fit terminal
    wrapped = textwrap.fill(message, width=max_width, subsequent_indent='  ')
    print(f"{Fore.CYAN}ℹ{Style.RESET_ALL} {wrapped}")


def display_separator() -> None:
    print("\n" + separator() + "\n")


def clear_screen() -> None:
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def display_input_prompt_with_slash_detection() -> tuple:
    """
    Advanced input with fixed position and autocomplete.
    Shows searchable command palette when / is typed.
    Shows searchable file picker when @ is typed.
    """
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.application import get_app
    from prompt_toolkit.document import Document
    
    # Track attached files
    attached_files = []
    current_text = ""
    
    def show_input_prompt(default_text="", files_attached=None):
        """Show input prompt with optional default text and file attachments."""
        nonlocal current_text, attached_files
        
        if files_attached is None:
            files_attached = attached_files
        
        # Print separator BEFORE input (no extra spacing)
        console.print(f"[dim]{'─' * WIDTH}[/dim]")
        
        # Show attached files if any
        if files_attached:
            for idx, filepath in enumerate(files_attached, 1):
                print(f"{Fore.CYAN}File attached {idx}:{Style.RESET_ALL} {filepath}")
        
        # Custom style for prompt
        prompt_style = PromptStyle.from_dict({
            'prompt': 'cyan',
            'placeholder': 'ansibrightblack',
        })
        
        # Create custom key bindings
        kb = KeyBindings()
        
        @kb.add('/')
        def _(event):
            """When / is pressed at start, show searchable command palette."""
            # Only trigger if at start of line
            if event.app.current_buffer.cursor_position == 0:
                event.app.exit(result='__SHOW_COMMANDS__')
        
        @kb.add('@')
        def _(event):
            """When @ is pressed, show searchable file picker."""
            # Only trigger if @ is at start or preceded by a space
            # Don't trigger if it's part of an email (preceded by alphanumeric)
            buffer = event.app.current_buffer
            cursor_pos = buffer.cursor_position
            
            # Check if @ is at the start
            if cursor_pos == 0:
                saved_text = buffer.text
                event.app.exit(result=f'__SHOW_FILES__|||{saved_text}')
                return
            
            # Check the character before @
            text_before = buffer.text[:cursor_pos]
            if text_before:
                last_char = text_before[-1]
                # Only trigger if preceded by space or at start
                # Don't trigger if preceded by alphanumeric (part of email)
                if last_char.isspace():
                    saved_text = buffer.text
                    event.app.exit(result=f'__SHOW_FILES__|||{saved_text}')
                    return
            
            # If not triggered, insert @ normally
            buffer.insert_text('@')
        
        # Build toolbar text
        toolbar_parts = ['Press / for commands', '@ for files']
        if files_attached:
            toolbar_parts.append(f'{len(files_attached)} file(s) attached')
        toolbar_text = ' • '.join(toolbar_parts)
        
        try:
            # Get input with default text
            user_input = prompt(
                '> ',
                completer=CommandCompleter(),
                complete_while_typing=True,
                style=prompt_style,
                placeholder=HTML('<style color="#808080">Type your message here...</style>'),
                bottom_toolbar=toolbar_text,
                key_bindings=kb,
                default=default_text
            )
            
            # Don't strip yet - return as is
            return user_input
            
        except (KeyboardInterrupt, EOFError):
            return None
    
    # Main loop to handle input
    while True:
        user_input = show_input_prompt(current_text, attached_files)
        
        if user_input is None:
            print()
            return "", False
        
        # Check if user pressed /
        if user_input == '__SHOW_COMMANDS__':
            # Clear the input area
            import sys
            lines_to_clear = 2  # separator + input
            if attached_files:
                lines_to_clear += len(attached_files)
            
            for _ in range(lines_to_clear):
                sys.stdout.write('\033[F')  # Move up
                sys.stdout.write('\033[K')  # Clear line
            sys.stdout.flush()
            
            # Show searchable command palette
            command = prompt_slash_command()
            return command, True
        
        # Check if user pressed @
        if user_input.startswith('__SHOW_FILES__|||'):
            # Extract current text - everything after the marker
            current_text = user_input.replace('__SHOW_FILES__|||', '', 1)
            
            # Clear the input area
            import sys
            lines_to_clear = 2  # separator + input
            if attached_files:
                lines_to_clear += len(attached_files)
            
            for _ in range(lines_to_clear):
                sys.stdout.write('\033[F')  # Move up
                sys.stdout.write('\033[K')  # Clear line
            sys.stdout.flush()
            
            # Show searchable file picker
            filepath = prompt_file_reference()
            if filepath:
                # Add to attached files
                attached_files.append(filepath)
                # Continue to show input with file attached and preserved text
                continue
            else:
                # User cancelled, continue with current state
                continue
        
        # Now strip the input
        user_input = user_input.strip()
        
        # Auto-complete if it's a partial command match
        if user_input.startswith('/') and user_input not in ["/models", "/providers", "/clear", "/reset", "/skills", "/tools", "/exit", "/help", "/mode"]:
            match = get_command_match(user_input)
            if match:
                user_input = match
        
        # Print bottom separator after input
        console.print(f"[dim]{'─' * WIDTH}[/dim]\n")
        
        # If we have attached files, build the full message
        if attached_files:
            file_references = []
            for idx, filepath in enumerate(attached_files, 1):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    file_references.append(f"[File {idx}: {filepath}]\n```\n{file_content}\n```\n")
                except Exception as e:
                    display_error(f"Error reading file {filepath}: {str(e)}")
            
            # Combine file references with user message
            if file_references:
                full_message = '\n'.join(file_references) + '\n' + user_input
                return full_message, False
        
        return user_input, False


def display_input_prompt() -> str:
    sep = separator()

    print("\n" + sep)
    user_input = input(f"{Fore.YELLOW}>{Style.RESET_ALL} ").strip()
    print(sep + "\n")

    return user_input


def display_user_message(message: str) -> None:
    """Display user message - intentionally empty as we don't show user messages."""
    pass  # Don't display user messages


def display_assistant_message(
    message: str,
    model: str,
    tokens: Optional[dict] = None,
    elapsed_time: float = 0,
    context_window: Optional[int] = None,
) -> None:
    """Display assistant message with rich formatting and proper width."""
    import shutil
    
    # Get terminal width and set console width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 100)
    
    # Create a console with the appropriate width
    from rich.console import Console
    display_console = Console(width=max_width)
    
    # Use rich to render markdown
    md = Markdown(message)
    display_console.print(md)
    display_console.print()
    
    # Build metadata line - all grey
    metadata_parts = []
    metadata_parts.append(f"{model}")
    metadata_parts.append(f"{elapsed_time:.1f}s")
    
    if tokens:
        # Show output/completion tokens
        completion_tokens = tokens.get('completionTokens', 0)
        if completion_tokens > 0:
            metadata_parts.append(f"{completion_tokens:,} tokens")
        
        # Display context usage percentage
        prompt_tokens = tokens.get('promptTokens', 0)
        if context_window and context_window > 0:
            context_pct = (prompt_tokens / context_window) * 100
            metadata_parts.append(f"{context_pct:.1f}% context")
        elif prompt_tokens > 0:
            # Show token count if no context window available
            metadata_parts.append(f"{prompt_tokens:,} context tokens")
    
    display_console.print(f"[dim]{' • '.join(metadata_parts)}[/dim]")
    display_console.print(f"[dim]{'─' * max_width}[/dim]\n")


def format_message_with_code_blocks(message: str) -> str:
    """Format message with syntax highlighting for code blocks and bold text."""
    # First handle code blocks
    parts = re.split(r'(```[\s\S]*?```|`[^`]+`)', message)
    
    formatted_parts = []
    for part in parts:
        if part.startswith('```') and part.endswith('```'):
            # Multi-line code block
            lines = part[3:-3].split('\n')
            lang = lines[0].strip() if lines else ''
            code = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
            
            formatted_parts.append(f"\n{Fore.LIGHTBLACK_EX}┌─ {lang if lang else 'code'} ─{Style.RESET_ALL}")
            for line in code.split('\n'):
                formatted_parts.append(f"{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL} {Fore.WHITE}{line}{Style.RESET_ALL}")
            formatted_parts.append(f"{Fore.LIGHTBLACK_EX}└{'─' * (WIDTH - 2)}{Style.RESET_ALL}\n")
        elif part.startswith('`') and part.endswith('`'):
            # Inline code
            code = part[1:-1]
            formatted_parts.append(f"{Fore.YELLOW}{code}{Style.RESET_ALL}")
        else:
            # Handle bold text (**text**)
            part = re.sub(r'\*\*([^*]+)\*\*', f'{Style.BRIGHT}\\1{Style.NORMAL}', part)
            # Regular text
            formatted_parts.append(part)
    
    return ''.join(formatted_parts)


class RunningIndicator:
    """Display running indicator with animated spinner and elapsed time."""

    def __init__(self):
        self.running = False
        self.thread = None
        self.start_time = 0
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_idx = 0

    def start(self):
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._display)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> float:
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)

        elapsed = time.time() - self.start_time
        print("\r" + " " * WIDTH + "\r", end="", flush=True)
        return elapsed

    def _display(self):
        while self.running:
            elapsed = int(time.time() - self.start_time)
            spinner = self.spinner_chars[self.spinner_idx % len(self.spinner_chars)]
            self.spinner_idx += 1
            
            # Format time as minutes and seconds if over 60 seconds
            if elapsed >= 60:
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes}m {seconds}s"
            else:
                time_str = f"{elapsed}s"
            
            # Build the message
            message = f"{Fore.CYAN}{spinner}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Thinking... {time_str}{Style.RESET_ALL}"
            
            # Clear the entire line and print the message
            print(f"\r{' ' * 80}\r{message}", end="", flush=True)
            time.sleep(0.1)