"""
CLI Interface module for zeer.

This module handles all user interaction, input collection, and output formatting.
"""

from typing import List, Optional
import sys
import inquirer
from colorama import Fore, Style, Back, init
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
            "/servers": "Show running servers",
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
    commands = ["/models", "/providers", "/clear", "/reset", "/skills", "/tools", "/servers", "/mode", "/exit", "/help"]
    
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
        subtitle_text = "OpenSource"
        version_text = f"v{__version__}"
    else:
        subtitle_text = "OpenSource"
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
    
    # Top border with title
    title = " Agentic AI CLI "
    title_len = len(title)
    # Calculate how many dashes on each side
    total_border_width = left_width + right_width + 1  # +1 for the middle divider
    left_dashes = 4  # Fixed number of dashes before title
    right_dashes = total_border_width - left_dashes - title_len
    
    lines.append(f"{Fore.RED}┌{'─' * left_dashes}{Fore.CYAN}{title}{Fore.RED}{'─' * right_dashes}┐{Style.RESET_ALL}")
    
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
    """Display error message with box style."""
    import shutil
    
    # Get terminal width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Create header
    header = "─ Error "
    print(f"\n{Fore.RED}╭{header}{'─' * (max_width - len(header) - 1)}{Style.RESET_ALL}", file=sys.stderr)
    
    # Split error into lines if it's long
    error_lines = error.split('\n')
    for line in error_lines:
        if line.strip():
            # Wrap long lines
            if len(line) > max_width - 4:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_width - 4:
                        current_line += word + " "
                    else:
                        if current_line:
                            print(f"{Fore.RED}│{Style.RESET_ALL} {current_line.strip()}", file=sys.stderr)
                        current_line = word + " "
                if current_line:
                    print(f"{Fore.RED}│{Style.RESET_ALL} {current_line.strip()}", file=sys.stderr)
            else:
                print(f"{Fore.RED}│{Style.RESET_ALL} {line}", file=sys.stderr)
    
    print(file=sys.stderr)


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
            elif key == b'\xe0' or key == b'\x00':  # Arrow keys prefix (both \xe0 and \x00)
                arrow = msvcrt.getch()
                if arrow == b'H':  # Up
                    return 'up'
                elif arrow == b'P':  # Down
                    return 'down'
                elif arrow == b'K':  # Left
                    return None
                elif arrow == b'M':  # Right
                    return None
                else:
                    # Consume unknown special key
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
        "/resume - Resume saved session",
        "/sessions - List saved sessions",
        "/skills - List agent skills",
        "/tools - List available tools",
        "/servers - Show running servers",
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
            elif key == b'\xe0' or key == b'\x00':  # Arrow keys prefix (both \xe0 and \x00)
                arrow = msvcrt.getch()
                if arrow == b'H':  # Up
                    return 'up'
                elif arrow == b'P':  # Down
                    return 'down'
                elif arrow == b'K':  # Left
                    return None
                elif arrow == b'M':  # Right
                    return None
                else:
                    # Consume unknown special key
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
        
        # Show attached files if any with removal option
        if files_attached:
            for idx, filepath in enumerate(files_attached, 1):
                print(f"{Fore.CYAN}File {idx}:{Style.RESET_ALL} {filepath} {Fore.LIGHTBLACK_EX}(Press Ctrl+{idx} to remove){Style.RESET_ALL}")
        
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
            else:
                # Insert / normally if not at start
                event.app.current_buffer.insert_text('/')
        
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
        
        # Add key bindings to remove attached files (Ctrl+1, Ctrl+2, etc)
        for i in range(1, 10):
            @kb.add(f'c-{i}')
            def _(event, file_idx=i):
                """Remove attached file."""
                if file_idx <= len(files_attached):
                    saved_text = event.app.current_buffer.text
                    event.app.exit(result=f'__REMOVE_FILE__|||{file_idx}|||{saved_text}')
        
        # Build toolbar text
        toolbar_parts = ['Press / for commands', '@ for files']
        if files_attached:
            toolbar_parts.append(f'{len(files_attached)} file(s) attached')
            toolbar_parts.append('Ctrl+# to remove')
        toolbar_text = ' • '.join(toolbar_parts)
        
        # Create bottom toolbar with separator and minimal spacing
        from prompt_toolkit.formatted_text import HTML as PTK_HTML
        separator_line = '─' * WIDTH
        
        def get_bottom_toolbar():
            # Add just 2 empty lines for minimal spacing
            return PTK_HTML(f'<ansibrightblack>{separator_line}</ansibrightblack>\n<ansibrightblack>{toolbar_text}</ansibrightblack>\n\n\n\n\n\n')
        
        # Custom style to remove white background
        custom_prompt_style = PromptStyle.from_dict({
            'prompt': 'cyan',
            'placeholder': 'ansibrightblack',
            'bottom-toolbar': 'noreverse',  # Remove reverse video (white background)
        })
        
        try:
            # Get input with default text
            user_input = prompt(
                '> ',
                completer=CommandCompleter(),
                complete_while_typing=True,
                style=custom_prompt_style,
                placeholder=HTML('<style color="#808080">Type your message here...</style>'),
                bottom_toolbar=get_bottom_toolbar,
                key_bindings=kb,
                default=default_text,
                reserve_space_for_menu=0  # Don't reserve extra space
            )
            
            # Print separator AFTER input (right below it)
            console.print(f"[dim]{'─' * WIDTH}[/dim]")
            
            # Don't strip yet - return as is
            return user_input
            
        except (KeyboardInterrupt, EOFError):
            # Print separator even on cancel
            console.print(f"[dim]{'─' * WIDTH}[/dim]")
            return None
    
    # Main loop to handle input
    while True:
        user_input = show_input_prompt(current_text, attached_files)
        
        if user_input is None:
            # Ctrl+C or EOF pressed - raise KeyboardInterrupt to let caller handle it
            raise KeyboardInterrupt
        
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
        
        # Check if user wants to remove a file
        if user_input.startswith('__REMOVE_FILE__|||'):
            parts = user_input.split('|||')
            file_idx = int(parts[1])
            current_text = parts[2] if len(parts) > 2 else ""
            
            # Remove the file
            if 1 <= file_idx <= len(attached_files):
                removed_file = attached_files.pop(file_idx - 1)
                
                # Clear the input area
                import sys
                lines_to_clear = 2 + file_idx  # separator + input + files
                
                for _ in range(lines_to_clear):
                    sys.stdout.write('\033[F')  # Move up
                    sys.stdout.write('\033[K')  # Clear line
                sys.stdout.flush()
                
                print(f"{Fore.YELLOW}✓ Removed: {removed_file}{Style.RESET_ALL}")
            
            # Continue to show input
            continue
        
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
        if user_input.startswith('/') and user_input not in ["/models", "/providers", "/clear", "/reset", "/skills", "/tools", "/servers", "/exit", "/help", "/mode"]:
            match = get_command_match(user_input)
            if match:
                user_input = match
        
        # Separator already printed by show_input_prompt
        print()  # Just add a newline for spacing
        
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
                # Clear attached files after sending
                attached_files.clear()
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
    """Display assistant message with typewriter effect and markdown rendering."""
    import shutil
    import sys
    import re
    
    # Get terminal width and set console width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 100)
    
    # Create a console with the appropriate width
    from rich.console import Console
    display_console = Console(width=max_width)
    
    # STEP 1: Strip Gemini's fake ANSI codes (format: [35m not \x1b[35m)
    message = re.sub(r'\[(\d+)m', '', message)
    
    # STEP 2: Detect and convert Gemini's line-numbered code to markdown
    def detect_and_wrap_code(text):
        """Detect code blocks with line numbers and wrap them in proper markdown."""
        lines = text.split('\n')
        result = []
        in_code = False
        code_lines = []
        lang = ''
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line is a language name (python, javascript, etc.)
            lang_match = re.match(r'^(python|javascript|java|cpp|c|ruby|go|rust|typescript|php|swift|kotlin|scala|r|sql|bash|shell|html|css|json|yaml|xml|jsx|tsx)\s*$', line.lower())
            
            if lang_match and not in_code:
                # Check if next line starts with a number (line number)
                if i + 1 < len(lines) and re.match(r'^\d+\s+', lines[i + 1]):
                    # This is the start of a code block
                    lang = lang_match.group(1)
                    in_code = True
                    code_lines = []
                    i += 1
                    continue
                else:
                    # Just a regular line that happens to be a language name
                    result.append(line)
                    i += 1
                    continue
            
            if in_code:
                # Check if line has line number (no leading spaces before number)
                # Match: line_number + single_space + rest_of_line (preserving indentation)
                num_match = re.match(r'^(\d+) (.*)$', line)
                if num_match:
                    # Extract code part, preserving ALL spacing in the code
                    code_part = num_match.group(2)
                    code_lines.append(code_part)
                    i += 1
                    continue
                elif not line.strip():
                    # Empty line in code
                    code_lines.append('')
                    i += 1
                    continue
                else:
                    # End of code block - no more line numbers
                    result.append(f'```{lang}')
                    result.extend(code_lines)
                    result.append('```')
                    code_lines = []
                    in_code = False
                    lang = ''
                    result.append(line)
                    i += 1
                    continue
            else:
                result.append(line)
                i += 1
        
        # Close any remaining code block
        if in_code and code_lines:
            result.append(f'```{lang}')
            result.extend(code_lines)
            result.append('```')
        
        return '\n'.join(result)
    
    message = detect_and_wrap_code(message)
    clean_message = message
    
    # Parse markdown formatting and apply colors
    def format_text_with_colors(text):
        """Convert markdown to colored terminal output with smart styling."""
        import re
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.formatters import Terminal256Formatter
        from pygments.util import ClassNotFound
        from pygments.style import Style as PygmentsStyle
        from pygments.token import Token
        
        # Define a custom color scheme for terminal with COMPLETE coverage
        class CustomStyle(PygmentsStyle):
            default_style = ""
            styles = {
                # Keywords - magenta/purple
                Token.Keyword: '#af00ff',
                Token.Keyword.Constant: '#af00ff',
                Token.Keyword.Declaration: '#af00ff',
                Token.Keyword.Namespace: '#af00ff',
                Token.Keyword.Pseudo: '#af00ff',
                Token.Keyword.Reserved: '#af00ff',
                Token.Keyword.Type: '#af00ff',
                
                # Names - yellow for functions/classes
                Token.Name.Function: '#ffff00',
                Token.Name.Class: '#ffff00',
                Token.Name.Builtin: '#ffff00',
                Token.Name.Builtin.Pseudo: '#ffff00',
                Token.Name.Decorator: '#ffff00',
                Token.Name.Exception: '#ffff00',
                
                # Strings - green
                Token.String: '#00ff00',
                Token.String.Doc: '#00ff00',
                Token.String.Double: '#00ff00',
                Token.String.Single: '#00ff00',
                Token.String.Backtick: '#00ff00',
                Token.String.Char: '#00ff00',
                Token.String.Escape: '#00ff00',
                Token.String.Interpol: '#00ff00',
                
                # Numbers - cyan
                Token.Number: '#00ffff',
                Token.Number.Float: '#00ffff',
                Token.Number.Hex: '#00ffff',
                Token.Number.Integer: '#00ffff',
                Token.Number.Oct: '#00ffff',
                Token.Number.Bin: '#00ffff',
                
                # Comments - gray
                Token.Comment: '#808080',
                Token.Comment.Single: '#808080',
                Token.Comment.Multiline: '#808080',
                Token.Comment.Preproc: '#808080',
                Token.Comment.PreprocFile: '#808080',
                Token.Comment.Special: '#808080',
                
                # Operators - red
                Token.Operator: '#ff5555',
                Token.Operator.Word: '#ff5555',
                
                # Punctuation - white
                Token.Punctuation: '#ffffff',
                
                # Variables and names - white
                Token.Name: '#ffffff',
                Token.Name.Attribute: '#ffffff',
                Token.Name.Variable: '#ffffff',
                Token.Name.Variable.Class: '#ffffff',
                Token.Name.Variable.Global: '#ffffff',
                Token.Name.Variable.Instance: '#ffffff',
                
                # Generic/other - white
                Token.Text: '#ffffff',
                Token.Text.Whitespace: '',
                Token.Literal: '#ffffff',
                Token.Error: '#ff0000',
            }
        
        # Split text into code blocks and non-code parts
        parts = re.split(r'(```[\s\S]*?```)', text)
        formatted_parts = []
        
        for part in parts:
            if part.startswith('```') and part.endswith('```'):
                # This is a code block - format it
                lines = part[3:-3].split('\n')
                lang = lines[0].strip() if lines and lines[0].strip() else ''
                code = '\n'.join(lines[1:]) if len(lines) > 1 else ''
                
                if not code.strip():
                    continue
                
                # Use Pygments for syntax highlighting
                try:
                    if lang:
                        lexer = get_lexer_by_name(lang, stripall=True)
                    else:
                        lexer = guess_lexer(code)
                except ClassNotFound:
                    from pygments.lexers import TextLexer
                    lexer = TextLexer()
                
                # Format with terminal colors using our custom style
                formatter = Terminal256Formatter(style=CustomStyle)
                highlighted = highlight(code, lexer, formatter)
                
                # Build code block with header and line numbers
                result = []
                result.append(f"\n{Fore.BLACK}{Back.LIGHTWHITE_EX} {lang or 'code'} {Style.RESET_ALL}")
                
                for idx, line in enumerate(highlighted.rstrip().split('\n'), 1):
                    line_num = f"{idx:3d}"
                    result.append(f"{Fore.WHITE}{Back.LIGHTBLACK_EX}{line_num}{Style.RESET_ALL}{Back.BLACK} {line}{Style.RESET_ALL}")
                
                result.append("")
                # Mark this as a code block so we don't apply typewriter effect
                formatted_parts.append(('CODE_BLOCK', '\n'.join(result)))
            else:
                # Regular text - apply markdown formatting
                # Replace **bold** with cyan color
                part = re.sub(r'\*\*([^*]+)\*\*', f'{Fore.CYAN}\\1{Style.RESET_ALL}', part)
                
                # Replace `code` with yellow
                part = re.sub(r'`([^`]+)`', f'{Fore.YELLOW}\\1{Style.RESET_ALL}', part)
                
                # Handle bullet points - make them cyan
                part = re.sub(r'^\*\s+', f'{Fore.CYAN}• {Style.RESET_ALL}', part, flags=re.MULTILINE)
                part = re.sub(r'^\-\s+', f'{Fore.CYAN}• {Style.RESET_ALL}', part, flags=re.MULTILINE)
                
                # Color numbered lists
                part = re.sub(r'^(\d+)\.\s+', f'{Fore.CYAN}\\1.{Style.RESET_ALL} ', part, flags=re.MULTILINE)
                
                # Color section headers
                part = re.sub(r'^([A-Z][^:]+:)$', f'{Fore.MAGENTA}\\1{Style.RESET_ALL}', part, flags=re.MULTILINE)
                
                # Color file extensions
                part = re.sub(r'(\.[a-z]{2,4})\b', f'{Fore.YELLOW}\\1{Style.RESET_ALL}', part)
                
                # Color paths
                part = re.sub(r'(/[a-zA-Z0-9_/.-]+)', f'{Fore.YELLOW}\\1{Style.RESET_ALL}', part)
                
                # Color common directory/file names
                part = re.sub(r'\b(__pycache__|node_modules|\.git|dist|build)\b', 
                             f'{Fore.MAGENTA}\\1{Style.RESET_ALL}', part)
                
                formatted_parts.append(('TEXT', part))
        
        return formatted_parts
    
    # Format the message
    formatted_parts = format_text_with_colors(clean_message)
    
    # Calculate delay for text parts only
    text_length = sum(len(part[1]) for part in formatted_parts if part[0] == 'TEXT')
    max_duration = 5.0
    
    if text_length > 0:
        delay_per_char = max_duration / text_length
        delay_per_char = max(0.001, min(delay_per_char, 0.01))
    else:
        delay_per_char = 0.005
    
    # Display with typewriter effect for text, instant for code blocks
    start_time = time.time()
    
    for part_type, content in formatted_parts:
        if part_type == 'CODE_BLOCK':
            # Print code blocks instantly (no typewriter effect)
            print(content)
        else:
            # Apply typewriter effect to text
            i = 0
            while i < len(content):
                # Check if we've exceeded 5 seconds
                if time.time() - start_time > max_duration:
                    sys.stdout.write(content[i:])
                    sys.stdout.flush()
                    break
                
                char = content[i]
                
                # Check if this is the start of an ANSI escape sequence
                if char == '\x1b' and i + 1 < len(content) and content[i + 1] == '[':
                    # Find the end of the ANSI sequence
                    end = i + 2
                    while end < len(content) and content[end] != 'm':
                        end += 1
                    # Print the entire ANSI sequence at once
                    sys.stdout.write(content[i:end + 1])
                    sys.stdout.flush()
                    i = end + 1
                else:
                    # Regular character
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(delay_per_char)
                    i += 1
    
    print("\n")  # New line after message
    
    # Build metadata line
    metadata_parts = []
    metadata_parts.append(f"{model}")
    metadata_parts.append(f"{elapsed_time:.1f}s")
    
    if tokens:
        completion_tokens = tokens.get('completionTokens', 0)
        if completion_tokens > 0:
            metadata_parts.append(f"{completion_tokens:,} tokens")
        
        prompt_tokens = tokens.get('promptTokens', 0)
        if context_window and context_window > 0:
            context_pct = (prompt_tokens / context_window) * 100
            metadata_parts.append(f"{context_pct:.1f}% context")
        elif prompt_tokens > 0:
            metadata_parts.append(f"{prompt_tokens:,} context tokens")
    
    display_console.print(f"[dim]{' • '.join(metadata_parts)}[/dim]\n")



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
        self.cancelled = False

    def start(self):
        self.running = True
        self.cancelled = False
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._display)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> float:
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)

        elapsed = time.time() - self.start_time
        # Clear the thinking line completely
        print("\r" + " " * 100 + "\r", end="", flush=True)
        return elapsed
    
    def is_cancelled(self) -> bool:
        """Check if user pressed ESC to cancel."""
        return self.cancelled

    def _display(self):
        import msvcrt
        import sys
        import _thread
        
        while self.running:
            # Check for ESC or Ctrl+C key press (non-blocking)
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':  # ESC key
                    self.cancelled = True
                    self.running = False
                    print(f"\r{' ' * 80}\r{Fore.YELLOW}✗ Cancelled{Style.RESET_ALL}\n", flush=True)
                    # Interrupt the main thread to stop the API call
                    _thread.interrupt_main()
                    return
                elif key == b'\x03':  # Ctrl+C
                    self.cancelled = True
                    self.running = False
                    print(f"\r{' ' * 80}\r{Fore.YELLOW}✗ Cancelled{Style.RESET_ALL}\n", flush=True)
                    # Raise KeyboardInterrupt to be caught by app_controller
                    _thread.interrupt_main()
                    return
                    raise KeyboardInterrupt()
            
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
            
            # Build the message with purple "Thinking"
            message = f"{Fore.CYAN}{spinner}{Style.RESET_ALL} {Fore.MAGENTA}Thinking... {time_str}{Style.RESET_ALL}"
            
            # Clear the entire line and print the message
            print(f"\r{' ' * 80}\r{message}", end="", flush=True)
            time.sleep(0.1)
