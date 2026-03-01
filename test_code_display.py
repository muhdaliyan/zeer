"""
Test script to demonstrate code block display with line numbers, background, and syntax highlighting.
"""

from colorama import Fore, Style, Back, init
import re

# Initialize colorama
init()

def highlight_python(line):
    """Apply Python syntax highlighting."""
    # Keywords
    line = re.sub(r'\b(def|class|if|else|elif|for|while|return|import|from|try|except|with|as|in|is|not|and|or)\b', 
                 f'{Fore.MAGENTA}\\1{Fore.WHITE}', line)
    # Strings
    line = re.sub(r'(["\'])([^"\']*)\1', f'{Fore.GREEN}\\1\\2\\1{Fore.WHITE}', line)
    # Comments
    line = re.sub(r'(#.*$)', f'{Fore.LIGHTBLACK_EX}\\1{Fore.WHITE}', line)
    # Functions
    line = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', f'{Fore.YELLOW}\\1{Fore.WHITE}(', line)
    # Numbers
    line = re.sub(r'\b(\d+)\b', f'{Fore.CYAN}\\1{Fore.WHITE}', line)
    return line

def highlight_javascript(line):
    """Apply JavaScript syntax highlighting."""
    # Keywords
    line = re.sub(r'\b(function|const|let|var|if|else|for|while|return|import|export|class|async|await)\b', 
                 f'{Fore.MAGENTA}\\1{Fore.WHITE}', line)
    # Strings
    line = re.sub(r'(["\'])([^"\']*)\1', f'{Fore.GREEN}\\1\\2\\1{Fore.WHITE}', line)
    line = re.sub(r'(`[^`]*`)', f'{Fore.GREEN}\\1{Fore.WHITE}', line)
    # Comments
    line = re.sub(r'(//.*$)', f'{Fore.LIGHTBLACK_EX}\\1{Fore.WHITE}', line)
    # Functions
    line = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', f'{Fore.YELLOW}\\1{Fore.WHITE}(', line)
    # Numbers
    line = re.sub(r'\b(\d+)\b', f'{Fore.CYAN}\\1{Fore.WHITE}', line)
    return line

def display_code_example():
    """Show how code blocks will look."""
    print("\n" + "=" * 80)
    print("🎨 Code Block Display with Syntax Highlighting")
    print("=" * 80 + "\n")
    
    print("Example 1: Python Code")
    print("-" * 80)
    
    # Simulate code block display
    lang = "python"
    code_lines = [
        'def is_palindrome(text):',
        '    """Check if text is a palindrome."""',
        '    processed = "".join(char.lower() for char in text if char.isalnum())',
        '    return processed == processed[::-1]',
        '',
        'if __name__ == "__main__":',
        '    word = input("Enter a word: ")',
        '    if is_palindrome(word):',
        '        print(f"{word} is a palindrome.")  # Success!',
        '    else:',
        '        print(f"{word} is not a palindrome.")'
    ]
    
    print(f"\n{Fore.BLACK}{Back.LIGHTWHITE_EX} {lang} {Style.RESET_ALL}")
    for idx, line in enumerate(code_lines, 1):
        if line.strip():
            highlighted = highlight_python(line)
            line_num = f"{idx:3d}"
            print(f"{Fore.WHITE}{Back.LIGHTBLACK_EX}{line_num}{Style.RESET_ALL}{Back.BLACK} {Fore.WHITE}{highlighted}{Style.RESET_ALL}")
        else:
            print(f"{Back.BLACK} {Style.RESET_ALL}")
    print()
    
    print("\n" + "-" * 80)
    print("Example 2: JavaScript Code")
    print("-" * 80)
    
    lang = "javascript"
    code_lines = [
        'function greet(name) {',
        '  const message = `Hello, ${name}!`;',
        '  console.log(message);  // Print greeting',
        '  return message;',
        '}',
        '',
        'const result = greet("World");',
        'if (result) {',
        '  console.log("Success!");',
        '}'
    ]
    
    print(f"\n{Fore.BLACK}{Back.LIGHTWHITE_EX} {lang} {Style.RESET_ALL}")
    for idx, line in enumerate(code_lines, 1):
        if line.strip():
            highlighted = highlight_javascript(line)
            line_num = f"{idx:3d}"
            print(f"{Fore.WHITE}{Back.LIGHTBLACK_EX}{line_num}{Style.RESET_ALL}{Back.BLACK} {Fore.WHITE}{highlighted}{Style.RESET_ALL}")
        else:
            print(f"{Back.BLACK} {Style.RESET_ALL}")
    print()
    
    print("\n" + "=" * 80)
    print("✨ Code blocks now have:")
    print("  • Line numbers with gray background")
    print("  • Black background for code (distinct from terminal)")
    print("  • Syntax highlighting:")
    print(f"    - {Fore.MAGENTA}Keywords{Style.RESET_ALL} in magenta")
    print(f"    - {Fore.GREEN}Strings{Style.RESET_ALL} in green")
    print(f"    - {Fore.YELLOW}Functions{Style.RESET_ALL} in yellow")
    print(f"    - {Fore.CYAN}Numbers{Style.RESET_ALL} in cyan")
    print(f"    - {Fore.LIGHTBLACK_EX}Comments{Style.RESET_ALL} in gray")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    display_code_example()
