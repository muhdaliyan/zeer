"""
Tool calling system for zeer CLI.

This module provides the infrastructure for AI agents to call tools/functions
to perform actions like file operations, system commands, etc.
"""

import os
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Tool:
    """Represents a callable tool that agents can use."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


@dataclass
class ToolCall:
    """Represents a tool call request from the agent."""
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a new tool."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self.tools.values())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get tool schemas for API requests (OpenAI/Anthropic format)."""
        schemas = []
        for tool in self.tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas
    
    def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call."""
        tool = self.get_tool(tool_call.tool_name)
        
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{tool_call.tool_name}' not found"
            )
        
        try:
            result = tool.function(**tool_call.arguments)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error executing tool: {str(e)}"
            )


# File operation tools
def create_file(path: str, content: str = "") -> str:
    """Create a new file with optional content."""
    try:
        # Use current working directory for relative paths
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = Path.cwd() / path
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Use UTF-8 encoding explicitly to handle all Unicode characters
        file_path.write_text(content, encoding='utf-8')
        return f"File created: {file_path}"
    except Exception as e:
        raise Exception(f"Failed to create file: {str(e)}")


def read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        # Use current working directory for relative paths
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = Path.cwd() / path
        
        if not file_path.exists():
            raise Exception(f"File not found: {path}")
        # Use UTF-8 encoding explicitly
        return file_path.read_text(encoding='utf-8')
    except Exception as e:
        raise Exception(f"Failed to read file: {str(e)}")


def list_directory(path: str = ".") -> str:
    """List contents of a directory."""
    try:
        # Use current working directory for relative paths
        dir_path = Path(path)
        if not dir_path.is_absolute():
            dir_path = Path.cwd() / path
        
        if not dir_path.exists():
            raise Exception(f"Directory not found: {path}")
        
        items = []
        for item in sorted(dir_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type:5} {item.name}")
        
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        raise Exception(f"Failed to list directory: {str(e)}")


def make_directory(path: str) -> str:
    """Create a new directory."""
    try:
        # Use current working directory for relative paths
        dir_path = Path(path)
        if not dir_path.is_absolute():
            dir_path = Path.cwd() / path
        
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Directory created: {dir_path}"
    except Exception as e:
        raise Exception(f"Failed to create directory: {str(e)}")


def get_current_directory() -> str:
    """Get the current working directory."""
    cwd = str(Path.cwd())
    home = str(Path.home())
    return f"Current working directory: {cwd}\nUser home directory: {home}\n(Note: Files/folders are created in home directory by default)"


def change_directory(path: str) -> str:
    """Change the current working directory."""
    try:
        os.chdir(path)
        return f"Changed directory to: {path}"
    except Exception as e:
        raise Exception(f"Failed to change directory: {str(e)}")


def delete_file(path: str) -> str:
    """Delete a file."""
    try:
        # Use current working directory for relative paths
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = Path.cwd() / path
        
        if not file_path.exists():
            raise Exception(f"File not found: {path}")
        file_path.unlink()
        return f"File deleted: {file_path}"
    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")


def write_to_file(path: str, content: str, append: bool = False) -> str:
    """Write content to a file (overwrite or append)."""
    try:
        # Use current working directory for relative paths
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = Path.cwd() / path
        
        if append:
            with open(file_path, 'a') as f:
                f.write(content)
            return f"Content appended to: {file_path}"
        else:
            file_path.write_text(content)
            return f"Content written to: {file_path}"
    except Exception as e:
        raise Exception(f"Failed to write to file: {str(e)}")


def find_file_or_folder(name: str) -> str:
    """Find a file or folder by name in common locations."""
    try:
        search_locations = [
            Path.home(),
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.cwd()
        ]
        
        found_items = []
        for location in search_locations:
            if not location.exists():
                continue
            
            # Search in this location
            for item in location.iterdir():
                if name.lower() in item.name.lower():
                    item_type = "DIR" if item.is_dir() else "FILE"
                    found_items.append(f"{item_type}: {item}")
        
        if found_items:
            return "Found:\n" + "\n".join(found_items)
        else:
            return f"No files or folders matching '{name}' found in common locations"
    except Exception as e:
        raise Exception(f"Failed to search: {str(e)}")


def run_code(code: str, language: str = "python") -> str:
    """Execute Python code in a subprocess and return the output.
    
    IMPORTANT: This tool ONLY executes Python code. Do NOT use this for:
    - Shell commands (npm, git, etc.) - use run_shell_command tool instead
    - System commands - use run_shell_command tool instead
    - Package installations - use install_package tool instead
    
    Only use this for actual Python scripts and code snippets.
    """
    import subprocess
    import tempfile
    import re
    
    try:
        # Only support Python for now
        if language.lower() != "python":
            raise Exception(f"Language '{language}' not supported. Only Python is supported.")
        
        # Create a temporary file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # Add UTF-8 encoding declaration at the top
            f.write("# -*- coding: utf-8 -*-\n")
            f.write(code)
            temp_file = f.name
        
        try:
            # Run the code with longer timeout for complex operations
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for complex data analysis/ML tasks
                encoding='utf-8'
            )
            
            output = result.stdout
            stderr = result.stderr
            
            # Check for ModuleNotFoundError and suggest installation
            if result.returncode != 0 and stderr:
                # Look for missing module errors
                module_match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", stderr)
                if module_match:
                    module_name = module_match.group(1)
                    raise Exception(f"Missing Python package '{module_name}'. Use install_package tool to install it.")
                
                output += f"\nErrors:\n{stderr}"
                raise Exception(f"Code execution failed with return code {result.returncode}:\n{output}")
            
            if stderr:
                output += f"\nWarnings:\n{stderr}"
            
            return output if output else "Code executed successfully (no output)"
        finally:
            # Clean up temp file
            Path(temp_file).unlink(missing_ok=True)
            
    except subprocess.TimeoutExpired:
        raise Exception("Code execution timed out after 5 minutes")
    except Exception as e:
        raise Exception(f"Failed to execute code: {str(e)}")


def run_shell_command(command: str, working_directory: str = ".") -> str:
    """Execute a shell command (npm, git, etc.) and return the output.
    
    Use this tool for:
    - npm commands: npm install, npm create, npm run, etc.
    - git commands: git clone, git commit, git push, etc.
    - System commands: mkdir, cd, ls, dir, etc.
    - Any other shell/terminal commands
    
    Args:
        command: The shell command to execute (e.g., "npm install react")
        working_directory: Directory to run the command in (default: current directory)
    
    Returns:
        Command output (stdout and stderr combined)
    """
    import subprocess
    import os
    import sys
    from colorama import Fore, Style
    
    try:
        # Resolve working directory
        work_dir = Path(working_directory)
        if not work_dir.is_absolute():
            work_dir = Path.cwd() / working_directory
        
        # Create directory if it doesn't exist
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert npm create to npx with -y flag to avoid prompts
        if command.startswith('npm create '):
            # npm create vite@latest -> npx -y create-vite@latest
            command = command.replace('npm create ', 'npx -y create-', 1)
        
        # For Windows, wrap commands that might prompt in echo y |
        if sys.platform == 'win32' and ('npm create' in command or 'npx create' in command):
            command = f'echo y | {command}'
        
        # Show what command is running
        print(f"\n{Fore.CYAN}Running: {command}{Style.RESET_ALL}")
        if str(work_dir) != ".":
            print(f"{Fore.LIGHTBLACK_EX}In: {work_dir}{Style.RESET_ALL}")
        
        # Set environment variables to skip all prompts
        env = os.environ.copy()
        env['npm_config_yes'] = 'true'
        env['CI'] = 'true'  # Many tools skip prompts in CI mode
        env['FORCE_COLOR'] = '0'  # Disable color codes that might interfere
        
        # Run the command with real-time output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,  # Provide stdin to send 'y' if needed
            text=True,
            cwd=str(work_dir),
            env=env,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Send 'y' to stdin immediately to handle any prompts
        try:
            process.stdin.write('y\n')
            process.stdin.flush()
            process.stdin.close()
        except:
            pass  # If stdin is already closed, that's fine
        
        output_lines = []
        
        # Read output in real-time
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    # Check if process finished
                    if process.poll() is not None:
                        break
                    continue
                
                line = line.rstrip()
                if line:
                    print(f"{Fore.LIGHTBLACK_EX}{line}{Style.RESET_ALL}")
                    output_lines.append(line)
        except KeyboardInterrupt:
            process.kill()
            raise
        
        # Wait for process to complete with timeout
        try:
            return_code = process.wait(timeout=600)
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("Command execution timed out after 10 minutes")
        
        combined_output = '\n'.join(output_lines)
        
        # Check for errors
        if return_code != 0:
            error_msg = f"Command failed with return code {return_code}"
            if combined_output:
                error_msg += f":\n{combined_output}"
            raise Exception(error_msg)
        
        print(f"{Fore.GREEN}✓ Command completed{Style.RESET_ALL}\n")
        return combined_output if combined_output else "Command executed successfully"
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception("Command execution timed out after 10 minutes")
    except Exception as e:
        raise Exception(f"Failed to execute command: {str(e)}")


def read_skill_reference(skill_name: str, reference_path: str) -> str:
    """Read a reference file from a skill's directory."""
    try:
        from src.skills_manager import SkillsManager
        skills_manager = SkillsManager("skills")
        
        content = skills_manager.resolve_file_reference(skill_name, reference_path)
        if content:
            return content
        else:
            raise Exception(f"Reference file not found: {reference_path}")
    except Exception as e:
        raise Exception(f"Failed to read reference: {str(e)}")


def run_dev_server(directory: str, install_command: str = "npm install", dev_command: str = "npm run dev") -> str:
    """Install dependencies and start a development server in background."""
    import subprocess
    import time
    from colorama import Fore, Style
    from src.process_manager import get_process_manager
    from src.tool_display import get_tool_display
    
    try:
        # Convert to absolute path
        dir_path = Path(directory)
        if not dir_path.is_absolute():
            dir_path = Path.cwd() / directory
        
        if not dir_path.exists():
            raise Exception(f"Directory not found: {directory}")
        
        display = get_tool_display()
        
        # Step 1: Install dependencies
        display.console.print(f"\n[cyan]Installing dependencies in {dir_path.name}...[/cyan]")
        
        install_result = subprocess.run(
            install_command,
            cwd=str(dir_path),
            capture_output=True,
            text=True,
            timeout=300,
            shell=True
        )
        
        if install_result.returncode != 0:
            error_output = install_result.stderr or install_result.stdout
            raise Exception(f"Installation failed:\n{error_output}")
        
        display.console.print(f"[green]✓ Dependencies installed[/green]\n")
        
        # Step 2: Start dev server in background
        display.console.print(f"[cyan]Starting development server...[/cyan]\n")
        
        manager = get_process_manager()
        bg_process = manager.start_process(
            name=dir_path.name,
            command=dev_command,
            directory=str(dir_path)
        )
        
        # Wait a bit for server to start and detect URL
        time.sleep(3)
        
        # Show server running message
        if bg_process.url:
            display.show_server_running(dir_path.name, bg_process.url)
        else:
            display.console.print(f"\n[green]● Server started in background[/green]")
            display.console.print(f"[dim]Process ID: {bg_process.id}[/dim]\n")
        
        return f"Development server for {directory} is running in background (ID: {bg_process.id})"
        
    except subprocess.TimeoutExpired:
        raise Exception("Installation timed out after 5 minutes")
    except Exception as e:
        raise Exception(str(e))
        raise Exception(f"Failed to run dev server: {str(e)}")


def install_npm_package(package_name: str, directory: str = ".") -> str:
    """Install an npm package in a project directory."""
    import subprocess
    from colorama import Fore, Style
    
    try:
        # Convert to absolute path
        dir_path = Path(directory)
        if not dir_path.is_absolute():
            dir_path = Path.cwd() / directory
        
        if not dir_path.exists():
            raise Exception(f"Directory not found: {directory}")
        
        # Auto-install without prompting
        print(f"\n{Fore.CYAN}Installing {package_name}...{Style.RESET_ALL}")
        
        result = subprocess.run(
            f"npm install {package_name}",
            cwd=str(dir_path),
            capture_output=True,
            text=True,
            timeout=300,
            shell=True
        )
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✓ Installed {package_name}{Style.RESET_ALL}")
            return f"Successfully installed '{package_name}'. The package is now available in your project."
        else:
            raise Exception(f"Installation failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Installation timed out after 5 minutes")
    except Exception as e:
        raise Exception(f"Failed to install npm package: {str(e)}")


def install_package(package_name: str) -> str:
    """Install a Python package using pip with user confirmation."""
    import subprocess
    from colorama import Fore, Style
    
    try:
        # Handle common package name aliases
        package_aliases = {
            'sklearn': 'scikit-learn',
            'cv2': 'opencv-python',
            'PIL': 'Pillow'
        }
        
        actual_package = package_aliases.get(package_name, package_name)
        
        # Auto-install without prompting
        if actual_package != package_name:
            print(f"\n{Fore.CYAN}Installing {package_name} (as {actual_package})...{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.CYAN}Installing {actual_package}...{Style.RESET_ALL}")
        
        result = subprocess.run(
            ['pip', 'install', actual_package],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes for large packages like tensorflow
        )
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✓ Installed {actual_package}{Style.RESET_ALL}")
            return f"Successfully installed '{actual_package}'. You can now use it in your code."
        else:
            raise Exception(f"Installation failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Installation timed out after 10 minutes")
    except Exception as e:
        raise Exception(f"Failed to install package: {str(e)}")


# Initialize default tool registry
def create_default_registry() -> ToolRegistry:
    """Create a registry with default file operation tools."""
    registry = ToolRegistry()
    
    # Register file operation tools
    registry.register(Tool(
        name="create_file",
        description="Create a new file with optional content",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to create"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file (optional)",
                    "default": ""
                }
            },
            "required": ["path"]
        },
        function=create_file
    ))
    
    registry.register(Tool(
        name="read_file",
        description="Read the contents of a file",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        },
        function=read_file
    ))
    
    registry.register(Tool(
        name="list_directory",
        description="List contents of a directory (like ls command)",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list (default: current directory)",
                    "default": "."
                }
            },
            "required": []
        },
        function=list_directory
    ))
    
    registry.register(Tool(
        name="make_directory",
        description="Create a new directory (like mkdir command)",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to create"
                }
            },
            "required": ["path"]
        },
        function=make_directory
    ))
    
    registry.register(Tool(
        name="get_current_directory",
        description="Get the current working directory (like pwd command)",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        function=get_current_directory
    ))
    
    registry.register(Tool(
        name="change_directory",
        description="Change the current working directory (like cd command)",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to change to"
                }
            },
            "required": ["path"]
        },
        function=change_directory
    ))
    
    registry.register(Tool(
        name="delete_file",
        description="Delete a file",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to delete"
                }
            },
            "required": ["path"]
        },
        function=delete_file
    ))
    
    registry.register(Tool(
        name="write_to_file",
        description="Write or append content to a file",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                },
                "append": {
                    "type": "boolean",
                    "description": "Whether to append (true) or overwrite (false)",
                    "default": False
                }
            },
            "required": ["path", "content"]
        },
        function=write_to_file
    ))
    
    registry.register(Tool(
        name="find_file_or_folder",
        description="Search for a file or folder by name in common locations (home, desktop, documents, downloads)",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name or part of name to search for"
                }
            },
            "required": ["name"]
        },
        function=find_file_or_folder
    ))
    
    registry.register(Tool(
        name="run_code",
        description="Execute Python code and return the output. ONLY for Python scripts. For shell commands (npm, git, etc.), use run_shell_command instead.",
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language (only 'python' supported)",
                    "default": "python"
                }
            },
            "required": ["code"]
        },
        function=run_code
    ))
    
    registry.register(Tool(
        name="run_shell_command",
        description="Execute shell commands like npm, git, mkdir, etc. Use this for any terminal/command-line operations. Examples: 'npm install react', 'git clone <url>', 'npm create vite@latest my-app -- --template react'",
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute (e.g., 'npm install', 'git status')"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Directory to run the command in (default: current directory)",
                    "default": "."
                }
            },
            "required": ["command"]
        },
        function=run_shell_command
    ))
    
    registry.register(Tool(
        name="read_skill_reference",
        description="Read a reference file from a skill's directory (e.g., references/api_docs.md). Use this to access additional documentation or examples.",
        parameters={
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill (e.g., 'pdf', 'code-helper')"
                },
                "reference_path": {
                    "type": "string",
                    "description": "Path to reference file relative to skill directory (e.g., 'references/examples.md')"
                }
            },
            "required": ["skill_name", "reference_path"]
        },
        function=read_skill_reference
    ))
    
    registry.register(Tool(
        name="install_package",
        description="Install a Python package using pip automatically. Use this when you encounter 'ModuleNotFoundError' or need a specific Python library. Installs immediately without prompting.",
        parameters={
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "Name of the Python package to install (e.g., 'python-pptx', 'requests', 'pandas')"
                }
            },
            "required": ["package_name"]
        },
        function=install_package
    ))
    
    registry.register(Tool(
        name="install_npm_package",
        description="Install an npm package in a Node.js/React project automatically. Use this when you encounter missing npm packages or need JavaScript libraries. Installs immediately without prompting.",
        parameters={
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "Name of the npm package to install (e.g., 'react-router-dom', 'axios', 'bootstrap')"
                },
                "directory": {
                    "type": "string",
                    "description": "Path to the project directory (default: current directory)",
                    "default": "."
                }
            },
            "required": ["package_name"]
        },
        function=install_npm_package
    ))
    
    registry.register(Tool(
        name="run_dev_server",
        description="Install dependencies and start a development server. Use this after creating a web project to run it. The server will run until the user presses Ctrl+C. Automatically runs npm install first. IMPORTANT: Use 'npm run dev' for Vite projects, 'npm start' for Create React App projects. Check package.json scripts to determine the correct command.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Path to the project directory (e.g., 'my-react-app')"
                },
                "install_command": {
                    "type": "string",
                    "description": "Command to install dependencies (default: 'npm install')",
                    "default": "npm install"
                },
                "dev_command": {
                    "type": "string",
                    "description": "Command to start dev server. Use 'npm run dev' for Vite, 'npm start' for Create React App (default: 'npm run dev')",
                    "default": "npm run dev"
                }
            },
            "required": ["directory"]
        },
        function=run_dev_server
    ))
    
    registry.register(Tool(
        name="stop_dev_server",
        description="Stop a running development server. Can stop by process ID, by name, or stop all servers if no parameters provided.",
        parameters={
            "type": "object",
            "properties": {
                "process_id": {
                    "type": "string",
                    "description": "Process ID of the server to stop (optional)"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the server to stop (optional)"
                }
            },
            "required": []
        },
        function=stop_dev_server
    ))
    
    registry.register(Tool(
        name="list_dev_servers",
        description="List all currently running development servers with their status, URLs, and process IDs.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        function=list_dev_servers
    ))
    
    return registry


def stop_dev_server(process_id: str = None, name: str = None) -> str:
    """Stop a running development server by ID or name."""
    from src.process_manager import get_process_manager
    from colorama import Fore, Style
    
    manager = get_process_manager()
    
    # If no ID or name provided, stop all
    if not process_id and not name:
        processes = manager.list_processes()
        if not processes:
            return "No servers are currently running."
        
        for proc in processes:
            manager.stop_process(proc.id)
        
        return f"Stopped {len(processes)} server(s)."
    
    # Find by ID
    if process_id:
        if manager.stop_process(process_id):
            return f"Stopped server {process_id}"
        else:
            return f"Server {process_id} not found"
    
    # Find by name
    if name:
        processes = manager.list_processes()
        for proc in processes:
            if proc.name == name:
                manager.stop_process(proc.id)
                return f"Stopped server '{name}'"
        
        return f"Server '{name}' not found"


def list_dev_servers() -> str:
    """List all running development servers."""
    from src.process_manager import get_process_manager
    
    manager = get_process_manager()
    processes = manager.list_processes()
    
    if not processes:
        return "No servers are currently running."
    
    result = "Running servers:\n\n"
    for proc in processes:
        status = "running" if proc.process.poll() is None else "stopped"
        result += f"● {proc.name}\n"
        result += f"  ID: {proc.id}\n"
        result += f"  Status: {status}\n"
        if proc.url:
            result += f"  URL: {proc.url}\n"
        result += f"  Started: {proc.started_at.strftime('%H:%M:%S')}\n\n"
    
    return result
