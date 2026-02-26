"""
Background process manager for dev servers and long-running commands.
"""

import subprocess
import threading
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BackgroundProcess:
    """Represents a background process."""
    id: str
    name: str
    command: str
    directory: str
    process: subprocess.Popen
    started_at: datetime
    output_lines: list
    url: Optional[str] = None


class ProcessManager:
    """Manages background processes."""
    
    def __init__(self):
        self.processes: Dict[str, BackgroundProcess] = {}
        self._next_id = 1
    
    def start_process(self, name: str, command: str, directory: str, shell=True) -> BackgroundProcess:
        """Start a new background process."""
        import hashlib
        
        # Generate unique ID
        process_id = hashlib.md5(f"{name}{command}{datetime.now()}".encode()).hexdigest()[:8]
        
        # Start the process with stdin detached
        process = subprocess.Popen(
            command,
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,  # Detach from stdin so it doesn't interfere with terminal
            text=True,
            bufsize=1,
            shell=shell,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
        )
        
        # Create background process object
        bg_process = BackgroundProcess(
            id=process_id,
            name=name,
            command=command,
            directory=directory,
            process=process,
            started_at=datetime.now(),
            output_lines=[]
        )
        
        # Start output monitoring thread
        def monitor_output():
            import re
            # Regex to strip ANSI escape codes
            ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\[0m|\[[0-9]+m')
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    bg_process.output_lines.append(line.rstrip())
                    
                    # Detect URL - strip ANSI codes first
                    clean_line = ansi_escape.sub('', line)
                    
                    if 'localhost' in clean_line.lower() or 'local:' in clean_line.lower():
                        # Extract URL from cleaned line
                        url_match = re.search(r'https?://[^\s]+', clean_line)
                        if url_match:
                            bg_process.url = url_match.group(0)
                        elif 'localhost:' in clean_line:
                            port_match = re.search(r'localhost:(\d+)', clean_line)
                            if port_match:
                                bg_process.url = f"http://localhost:{port_match.group(1)}/"
        
        thread = threading.Thread(target=monitor_output, daemon=True)
        thread.start()
        
        # Store process
        self.processes[process_id] = bg_process
        
        return bg_process
    
    def stop_process(self, process_id: str) -> bool:
        """Stop a background process."""
        import sys
        import signal
        
        if process_id not in self.processes:
            return False
        
        bg_process = self.processes[process_id]
        
        try:
            # On Windows, we need to kill the entire process tree
            if sys.platform == 'win32':
                import subprocess
                # Use taskkill to kill the process tree
                subprocess.run(
                    ['taskkill', '/F', '/T', '/PID', str(bg_process.process.pid)],
                    capture_output=True,
                    timeout=5
                )
            else:
                # On Unix, send SIGTERM first
                bg_process.process.terminate()
                try:
                    bg_process.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # If it doesn't terminate, kill it
                    bg_process.process.kill()
                    bg_process.process.wait()
        except Exception as e:
            # If all else fails, try to kill it
            try:
                bg_process.process.kill()
                bg_process.process.wait(timeout=2)
            except:
                pass  # Process might already be dead
        
        del self.processes[process_id]
        return True
    
    def get_process(self, process_id: str) -> Optional[BackgroundProcess]:
        """Get a background process by ID."""
        return self.processes.get(process_id)
    
    def list_processes(self) -> list:
        """List all running processes."""
        return list(self.processes.values())
    
    def stop_all(self):
        """Stop all background processes."""
        for process_id in list(self.processes.keys()):
            self.stop_process(process_id)


# Global instance
_manager = ProcessManager()


def get_process_manager() -> ProcessManager:
    """Get the global process manager instance."""
    return _manager
