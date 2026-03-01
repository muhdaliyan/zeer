"""
Chat session management module for zeer CLI.

This module provides the ChatSession class for managing conversation history
and coordinating message transmission with AI providers.

Requirements: 6.2, 6.4, 6.5
"""

from typing import List, Optional
from datetime import datetime
from src.provider_base import AIProvider, Message, ChatContext, Response, Model
from src.tools import ToolRegistry, ToolCall
import re


class ChatSession:
    """
    Manages a chat session with an AI provider.
    
    This class maintains conversation history, formats context for API calls,
    and coordinates message transmission with the selected provider.
    """
    
    def __init__(self, provider: AIProvider, model: str, context_window: Optional[int] = None, tool_registry: Optional[ToolRegistry] = None, skills_manager=None):
        """
        Initialize a new chat session.
        
        Args:
            provider: The AIProvider instance to use for communication
            model: The model ID to use for this session
            context_window: Optional context window size in tokens
            tool_registry: Optional tool registry for tool calling
            skills_manager: Optional skills manager for agent skills
        """
        self.provider = provider
        self.model = model
        self.context_window = context_window
        self.tool_registry = tool_registry
        self.skills_manager = skills_manager
        self._messages: List[Message] = []
        self._activated_skills = set()  # Track which skills have been loaded
        
        # Add system message for autonomous operation
        system_prompt = """You are an autonomous AI assistant with access to tools and skills. CRITICAL INSTRUCTIONS:

AUTONOMY & EXECUTION:
1. START IMMEDIATELY - Don't overthink, begin calling tools right away
2. When given a task, you MUST call ALL necessary tools to complete it in ONE GO
3. DO NOT stop after calling one or two tools - call ALL files/tools needed
4. DO NOT ask "should I continue?" or wait for user confirmation
5. DO NOT ask "which file?" when you can list and figure it out yourself
6. DO NOT say "I'll create the files" and then stop - CREATE THEM ALL IMMEDIATELY
7. DO NOT explain what you're going to do - JUST DO IT
8. Complete the ENTIRE task before responding with text
9. Tools are executed sequentially with progress shown to the user
10. SPEED MATTERS - Start with the first tool call within seconds, not minutes
11. When user says "fix it" or "run and fix" - DO IT ALL: read files, fix issues, update files, run commands

SMART FILE HANDLING:
- When user says "add to existing file" or "list it" - immediately call list_directory, identify the relevant file, read it, and update it
- When user says "list it" or "show files" - call list_directory AND display the results in your response
- Use context clues to identify which file they mean (e.g., if discussing palindrome code, look for palindrome.py)
- If there are multiple candidates, pick the most relevant one based on context
- DO NOT ask "which file?" - make an intelligent choice and proceed

WHEN TO USE vs NOT USE FILE TOOLS:
- Use create_file/write_to_file when user explicitly asks to "create", "make", "write", "save", "add to" a file
- DO NOT use file tools when user asks to "show", "display", "convert", "translate", "what would this look like"
- For "show me X in Y language" - just display the converted code in your response, don't create files
- For "convert this to X" - display the conversion, don't save it unless explicitly asked
- Exception: "add this to file" or "save this" means use file tools

FIXING ISSUES:
- When user reports an error, immediately read the relevant files, identify the issue, fix ALL related files, and test
- DO NOT explain the problem and ask if they want you to fix it - JUST FIX IT
- DO NOT provide step-by-step instructions for the user - DO THE STEPS YOURSELF
- If something needs to be restarted, use run_shell_command to do it
- Fix everything in one complete action, don't make the user ask multiple times

QUALITY STANDARDS (IMPORTANT):
- Create professional, production-quality outputs
- Use modern design patterns, advanced styling, and polished aesthetics
- Think like an expert professional, not a beginner
- Each file should be well-structured, properly commented, and follow best practices
- Pay attention to visual details, spacing, and user experience
- When skills are activated, follow their specific quality guidelines carefully
- Balance quality with speed - don't spend 10+ minutes planning

FILE CREATION APPROACH:
- When creating multiple files, start immediately with the first one
- Consider how files interact and depend on each other
- Add proper imports, error handling, and edge cases
- Include helpful comments explaining complex logic
- Make sure styling is modern and visually appealing

WEB PROJECTS:
- For React/Vite projects: Use run_shell_command("npm create vite@latest project-name -- --template react")
- The tool automatically handles prompts - just use the standard npm create command
- After project creation, use run_shell_command("npm install") in the project directory
- Use run_shell_command for any npm/git/shell commands
- DO NOT use run_code for shell commands - it only works for Python
- When fixing web projects, update ALL necessary files (package.json, config files, CSS, components) in one go

SHELL COMMANDS:
- Use run_shell_command tool for: npm, git, mkdir, and all terminal commands
- Use run_code tool ONLY for Python scripts
- Examples: run_shell_command("npm install react"), run_shell_command("git init")

PACKAGE INSTALLATION:
- For Python packages: Use install_package tool when you encounter "ModuleNotFoundError"
- For npm/JavaScript packages: Use run_shell_command with "npm install package-name"
- After installation succeeds, retry the operation

You have the ability to call multiple tools in one response. USE IT. Start immediately and work efficiently. Be autonomous - don't ask permission, just execute."""

        self.add_message("user", system_prompt)
        self.add_message("assistant", "Understood. I will work autonomously and complete tasks fully without asking for permission. When you say 'fix it', I'll read the files, identify issues, update everything needed, and test - all in one go. I'll create professional, high-quality outputs efficiently.")
        
        # Add system message with skills metadata if available
        if self.skills_manager:
            skills = self.skills_manager.list_skills()
            if skills:
                skills_content = self._build_skills_prompt(skills)
                self.add_message("user", skills_content)
                self.add_message("assistant", "I understand. I will activate skills as needed when working on tasks.")
    
    def _build_skills_prompt(self, skills) -> str:
        """Build a system prompt with available skills (metadata only for progressive disclosure)."""
        prompt = "You have access to the following skills. When you need detailed instructions for a skill, mention it in your response:\n\n"
        
        for skill in skills:
            prompt += f"- **{skill.name}**: {skill.description}\n"
            if skill.allowed_tools:
                prompt += f"  Tools: {', '.join(skill.allowed_tools)}\n"
        
        prompt += "\n\nWhen you decide to use a skill, mention it naturally in your response (e.g., 'I'll use the pdf skill to help with this'). The full skill instructions will be provided automatically."
        
        return prompt
    
    def _find_skill_for_tool(self, tool_name: str) -> Optional[str]:
        """Find which skill a tool belongs to based on allowed-tools."""
        if not self.skills_manager:
            return None
        
        # Check activated skills first (most likely to be relevant)
        activated_matches = []
        for skill_name in self._activated_skills:
            skill = self.skills_manager.get_skill(skill_name)
            if skill and skill.allowed_tools and tool_name in skill.allowed_tools:
                activated_matches.append(skill_name)
        
        # If we have exactly one activated skill that uses this tool, return it
        if len(activated_matches) == 1:
            return activated_matches[0]
        
        # If multiple activated skills use this tool, prefer the most recently activated
        if len(activated_matches) > 1:
            # Return the last activated skill (most recent)
            for skill_name in reversed(list(self._activated_skills)):
                if skill_name in activated_matches:
                    return skill_name
        
        # Don't show skill name for common tools used by many skills
        # This prevents confusion when multiple skills could use the same tool
        common_tools = ['run_code', 'create_file', 'read_file', 'write_to_file', 
                       'list_directory', 'make_directory', 'install_package']
        if tool_name in common_tools:
            return None
        
        return None
    
    def _check_and_activate_skills(self, message: str) -> Optional[str]:
        """Check if message mentions any skills and activate them if needed."""
        if not self.skills_manager:
            return None
        
        skills = self.skills_manager.list_skills()
        activated_content = []
        message_lower = message.lower()
        
        for skill in skills:
            # Check if skill should be activated
            should_activate = False
            
            # Check if skill name is mentioned
            if skill.name in message_lower and skill.name not in self._activated_skills:
                should_activate = True
            
            # Check if description keywords match (for better activation)
            # For example, "pdf" skill should activate on "create pdf", "generate pdf", etc.
            if not should_activate and skill.name not in self._activated_skills:
                # Extract key terms from description
                desc_lower = skill.description.lower()
                # Check if message contains skill-related keywords
                if skill.name == "pdf" and ("pdf" in message_lower or "document" in message_lower):
                    should_activate = True
                elif skill.name == "code-helper" and ("code" in message_lower or "project" in message_lower):
                    should_activate = True
                elif skill.name == "frontend-designer" and ("frontend" in message_lower or "website" in message_lower or "ui" in message_lower):
                    should_activate = True
            
            if should_activate:
                # Load full skill content
                full_content = f"\n\n--- Activating {skill.name} skill ---\n\n"
                full_content += skill.get_full_content()
                
                # Load scripts if available
                scripts = self.skills_manager.list_skill_scripts(skill.name)
                if scripts:
                    full_content += f"\n\nAvailable scripts:\n"
                    for script in scripts:
                        full_content += f"- {script}\n"
                
                activated_content.append(full_content)
                self._activated_skills.add(skill.name)
        
        return "\n".join(activated_content) if activated_content else None
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender ("user", "assistant", or "tool")
            content: The message content
            
        Raises:
            ValueError: If role is not valid
        """
        if role not in ["user", "assistant", "tool"]:
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'tool'")
        
        message = Message(role=role, content=content, timestamp=datetime.now())
        self._messages.append(message)
    
    def get_context(self) -> ChatContext:
        """
        Get the current conversation context.
        
        Returns:
            ChatContext object containing message history, model, and provider info
        """
        # Get tool schemas if tool registry is available
        tools = None
        if self.tool_registry:
            tools = self.tool_registry.get_tools_schema()
        
        return ChatContext(
            messages=self._messages.copy(),
            model=self.model,
            provider=self.provider.get_name(),
            tools=tools
        )
    
    async def send_message(self, message: str, indicator=None) -> Response:
        """
        Send a message to the AI provider and receive a response.
        
        This method adds the user message to history, sends it to the provider
        with full conversation context, receives the response, handles tool calls
        if any, and returns the final response.
        
        Args:
            message: The user's message to send
            indicator: Optional RunningIndicator to control during tool execution
            
        Returns:
            Response object containing the AI's reply
            
        Raises:
            Exception: If the API call fails
        """
        from colorama import Fore, Style
        import json
        from src.config import get_config
        
        # Load configuration
        config = get_config()
        
        # Add user message to history
        self.add_message("user", message)
        
        # Check if any skills should be activated based on the message
        skill_activation = self._check_and_activate_skills(message)
        if skill_activation:
            # Add skill content to context
            self.add_message("user", skill_activation)
        
        # Loop to handle multiple rounds of tool calls automatically
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        # Configuration for deliberate execution
        DELIBERATE_MODE = config.is_deliberate_mode()
        MAX_TOOLS_PER_BATCH = config.get_max_tools_per_batch()
        FILE_DELAY = config.get_file_creation_delay()
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get current context with tools
            context = self.get_context()
            
            # Send message to provider (empty string for continuation)
            response = await self.provider.send_message("" if iteration > 1 else message, context)
            
            # Check if model wants to call tools
            if response.tool_calls and self.tool_registry:
                # Stop the thinking indicator during tool execution
                if indicator:
                    indicator.stop()
                
                # Store tool calls for later reference
                tool_call_messages = []
                
                # DELIBERATE MODE: Execute tools in smaller batches
                if DELIBERATE_MODE:
                    # Execute tools one by one or in small batches
                    total_tools = len(response.tool_calls)
                    
                    for idx, tool_call in enumerate(response.tool_calls, 1):
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        tool_call_id = tool_call["id"]
                        
                        # Show tool with box style (no right border)
                        import shutil
                        term_width = shutil.get_terminal_size().columns
                        max_width = min(term_width - 2, 80)
                        
                        # Create tool header
                        tool_header = f"─ Tool: {tool_name} "
                        print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
                        
                        # Show key arguments or action description
                        has_content = False
                        if "path" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Path:{Style.RESET_ALL} {tool_args['path']}")
                            has_content = True
                        elif "directory" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Directory:{Style.RESET_ALL} {tool_args['directory']}")
                            has_content = True
                        elif "command" in tool_args:
                            cmd = tool_args['command']
                            if len(cmd) > 60:
                                cmd = cmd[:57] + "..."
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Command:{Style.RESET_ALL} {cmd}")
                            has_content = True
                        elif "name" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Name:{Style.RESET_ALL} {tool_args['name']}")
                            has_content = True
                        elif "process_id" in tool_args or "id" in tool_args:
                            pid = tool_args.get('process_id') or tool_args.get('id')
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Process ID:{Style.RESET_ALL} {pid}")
                            has_content = True
                        
                        # If no specific args, show action description
                        if not has_content:
                            action_desc = self._get_tool_action_description(tool_name)
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{action_desc}{Style.RESET_ALL}")
                        
                        # Execute the tool BEFORE closing the box
                        from src.tools import ToolCall
                        result = self.tool_registry.execute_tool(ToolCall(tool_name, tool_args))
                        
                        # Show error inside the box if failed
                        if not result.success:
                            error_msg = result.error
                            if "Traceback" in error_msg:
                                lines = error_msg.split('\n')
                                error_line = next((line for line in reversed(lines) if line.strip()), error_msg)
                            else:
                                error_line = error_msg
                            
                            # Display error inside box
                            print(f"{Fore.RED}│ ✗ {error_line}{Style.RESET_ALL}")
                        else:
                            # Show output for certain tools that users want to see
                            display_output_tools = ['list_directory', 'get_current_directory', 'read_file']
                            if tool_name in display_output_tools and result.output:
                                # Display the output in a readable format
                                output_lines = result.output.split('\n')
                                for line in output_lines[:20]:  # Limit to first 20 lines
                                    if line.strip():
                                        print(f"{Fore.CYAN}│{Style.RESET_ALL} {line}")
                                if len(output_lines) > 20:
                                    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}... ({len(output_lines) - 20} more lines){Style.RESET_ALL}")
                        
                        # Close the box
                        # No bottom border
                        print()
                        # Add to messages
                        if result.success:
                            tool_call_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": result.output
                            })
                        else:
                            tool_call_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": f"Error: {result.error}"
                            })
                        
                        # Add small delay between file creations for deliberation
                        import time
                        if tool_name in ["create_file", "write_to_file"]:
                            time.sleep(FILE_DELAY)  # Configurable pause between files
                        
                        # After batch, force AI to reflect before continuing
                        if idx % MAX_TOOLS_PER_BATCH == 0 and idx < total_tools:
                            print(f"\n{Fore.YELLOW}⏸  Pausing to review progress...{Style.RESET_ALL}\n")
                            time.sleep(0.5)
                    
                    print()  # Single line after all tools

                    
                else:
                    # FAST MODE: Execute all at once with clean display
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        tool_call_id = tool_call["id"]
                        
                        # Show tool with box style (no right border)
                        import shutil
                        term_width = shutil.get_terminal_size().columns
                        max_width = min(term_width - 2, 80)
                        
                        # Create tool header
                        tool_header = f"─ Tool: {tool_name} "
                        print(f"{Fore.CYAN}╭{tool_header}{'─' * (max_width - len(tool_header) - 1)}{Style.RESET_ALL}")
                        
                        # Show key arguments or action description
                        has_content = False
                        if "path" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Path:{Style.RESET_ALL} {tool_args['path']}")
                            has_content = True
                        elif "directory" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Directory:{Style.RESET_ALL} {tool_args['directory']}")
                            has_content = True
                        elif "command" in tool_args:
                            cmd = tool_args['command']
                            if len(cmd) > 60:
                                cmd = cmd[:57] + "..."
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Command:{Style.RESET_ALL} {cmd}")
                            has_content = True
                        elif "name" in tool_args:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Name:{Style.RESET_ALL} {tool_args['name']}")
                            has_content = True
                        elif "process_id" in tool_args or "id" in tool_args:
                            pid = tool_args.get('process_id') or tool_args.get('id')
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Process ID:{Style.RESET_ALL} {pid}")
                            has_content = True
                        
                        # If no specific args, show action description
                        if not has_content:
                            action_desc = self._get_tool_action_description(tool_name)
                            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{action_desc}{Style.RESET_ALL}")
                        
                        # Execute the tool BEFORE closing the box
                        from src.tools import ToolCall
                        result = self.tool_registry.execute_tool(ToolCall(tool_name, tool_args))
                        
                        # Show error inside the box if failed
                        if not result.success:
                            error_msg = result.error
                            if "Traceback" in error_msg:
                                lines = error_msg.split('\n')
                                error_line = next((line for line in reversed(lines) if line.strip()), error_msg)
                            else:
                                error_line = error_msg
                            
                            # Display error inside box
                            print(f"{Fore.RED}│ ✗ {error_line}{Style.RESET_ALL}")
                        else:
                            # Show output for certain tools that users want to see
                            display_output_tools = ['list_directory', 'get_current_directory', 'read_file']
                            if tool_name in display_output_tools and result.output:
                                # Display the output in a readable format
                                output_lines = result.output.split('\n')
                                for line in output_lines[:20]:  # Limit to first 20 lines
                                    if line.strip():
                                        print(f"{Fore.CYAN}│{Style.RESET_ALL} {line}")
                                if len(output_lines) > 20:
                                    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}... ({len(output_lines) - 20} more lines){Style.RESET_ALL}")
                        
                        # Close the box
                        # No bottom border
                        print()
                        # Add to messages
                        if result.success:
                            tool_call_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": result.output
                            })
                        else:
                            tool_call_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": f"Error: {result.error}"
                            })
                    
                    print()  # Single line after all tools
                
                # Add assistant's tool call message with actual tool_calls data
                # Store as JSON so we can reconstruct it
                tool_calls_json = json.dumps(response.tool_calls)
                self.add_message("assistant", f"__TOOL_CALLS__:{tool_calls_json}")
                
                # Add tool results to history
                for tool_msg in tool_call_messages:
                    # Store tool call ID in the message
                    self.add_message("tool", f"__TOOL_CALL_ID__:{tool_msg['tool_call_id']}:{tool_msg['content']}")
                
                # Restart the thinking indicator for next iteration
                if indicator:
                    indicator.start()
                
                # Continue the loop to get next response (might be more tool calls or final answer)
                continue
            
            # No more tool calls - this is the final response
            self.add_message("assistant", response.content)
            return response
        
        # If we hit max iterations, return the last response
        self.add_message("assistant", response.content)
        return response
    
    def get_message_history(self) -> List[Message]:
        """
        Get the complete message history.
        
        Returns:
            List of Message objects in chronological order
        """
        return self._messages.copy()
    
    def _get_tool_action_description(self, tool_name: str) -> str:
        """
        Get a descriptive action for tools without specific arguments.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Human-readable description of what the tool does
        """
        descriptions = {
            "list_directory": "Listing current directory contents",
            "get_current_directory": "Getting current working directory",
            "list_dev_servers": "Listing running development servers",
            "list_processes": "Listing background processes",
            "stop_dev_server": "Stopping development server",
            "get_system_info": "Getting system information",
            "check_dependencies": "Checking installed dependencies",
        }
        
        return descriptions.get(tool_name, "Executing action...")
    
    def clear_history(self) -> None:
        """
        Clear the conversation history.
        
        This removes all messages from the session but keeps the
        provider and model configuration intact.
        """
        self._messages.clear()
    
    def get_message_count(self) -> int:
        """
        Get the number of messages in the conversation history.
        
        Returns:
            The total number of messages (user + assistant)
        """
        return len(self._messages)
