"""
Test script to demonstrate the new box-style UI.
Run this to see how tools and images are displayed.
"""

from colorama import Fore, Style, init
import shutil

# Initialize colorama
init()


def display_tool(tool_name: str, arg_label: str, arg_value: str):
    """Display a tool execution with box style (no right border)."""
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Create tool header
    tool_header = f"─ Tool: {tool_name} "
    print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{arg_label}:{Style.RESET_ALL} {arg_value}")
    print(f"{Fore.CYAN}╰{'─' * max_width}{Style.RESET_ALL}")


def display_image(filepath: str, size_kb: float):
    """Display an image generation with box style (no right border)."""
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Create header
    header = "─ Image Generated "
    print(f"{Fore.CYAN}╭{header}{'─' * (max_width - len(header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Path:{Style.RESET_ALL} {Fore.YELLOW}{filepath}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Size:{Style.RESET_ALL} {size_kb:.1f} KB")
    print(f"{Fore.CYAN}╰{'─' * max_width}{Style.RESET_ALL}")


def display_server(project: str, url: str):
    """Display a server running message with box style (no right border)."""
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Create header
    header = "─ Server Running "
    print(f"{Fore.GREEN}╭{header}{'─' * (max_width - len(header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Project:{Style.RESET_ALL} {project}")
    print(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}URL:{Style.RESET_ALL} {Fore.CYAN}{url}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Status:{Style.RESET_ALL} Running in background")
    print(f"{Fore.GREEN}╰{'─' * max_width}{Style.RESET_ALL}")


def display_error_box(error: str):
    """Display an error message with box style (no right border)."""
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Create header
    header = "─ Error "
    print(f"{Fore.RED}╭{header}{'─' * (max_width - len(header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.RED}│{Style.RESET_ALL} {error}")
    print(f"{Fore.RED}╰{'─' * max_width}{Style.RESET_ALL}")


def main():
    """Demonstrate the new UI."""
    print("\n" + "=" * 80)
    print("🎨 New Box-Style UI Demonstration")
    print("=" * 80 + "\n")
    
    print("Example 1: Tools with Arguments")
    print("-" * 80 + "\n")
    
    display_tool("list_directory", "Directory", "src/")
    print()
    display_tool("read_file", "Path", "config.json")
    print()
    display_tool("create_file", "Path", "test.py")
    print()
    
    print("\n" + "-" * 80)
    print("Example 2: Tools without Arguments (with action description)")
    print("-" * 80 + "\n")
    
    # Simulate tools without arguments
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    tool_header = "─ Tool: list_directory "
    print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Listing current directory contents{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╰{'─' * max_width}{Style.RESET_ALL}")
    print()
    
    tool_header = "─ Tool: stop_dev_server "
    print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Stopping development server{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╰{'─' * max_width}{Style.RESET_ALL}")
    print()
    
    print("\n" + "-" * 80)
    print("Example 3: Tool with Error")
    print("-" * 80 + "\n")
    
    tool_header = "─ Tool: read_file "
    print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Path:{Style.RESET_ALL} non_existent_file.txt")
    print(f"{Fore.RED}│ ✗ Failed to read file: File not found: non_existent_file.txt{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╰{'─' * max_width}{Style.RESET_ALL}")
    print()
    
    print("\n" + "-" * 80)
    print("Example 4: Image Generation")
    print("-" * 80 + "\n")
    
    display_image("generated_images/image_20260301_143022_1.png", 245.3)
    print()
    
    print("\n" + "-" * 80)
    print("Example 5: Server Running")
    print("-" * 80 + "\n")
    
    print(f"{Fore.CYAN}╭─ Installing Dependencies ───────────────────────────────────────────────────{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Project:{Style.RESET_ALL} zeer_website")
    print(f"{Fore.CYAN}╰{'─' * 80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}✓ Dependencies installed{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}╭─ Starting Development Server ───────────────────────────────────────────────{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Project:{Style.RESET_ALL} zeer_website")
    print(f"{Fore.CYAN}╰{'─' * 80}{Style.RESET_ALL}\n")
    
    display_server("zeer_website", "http://localhost:5173/")
    print()
    
    print("\n" + "-" * 80)
    print("Example 6: Error Display")
    print("-" * 80 + "\n")
    
    display_error_box("Failed to connect to API. Please check your internet connection.")
    print()
    
    display_error_box("Model 'invalid-model' not found. Use /models to see available models.")
    print()
    
    print("\n" + "=" * 80)
    print("✨ Clean, consistent, and informative!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
