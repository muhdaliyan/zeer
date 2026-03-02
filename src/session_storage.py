"""
Session storage module for zeer CLI.

This module handles saving and loading chat sessions with unique IDs,
allowing users to continue conversations later.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import hashlib


class SessionStorage:
    """Manages persistent storage of chat sessions."""
    
    def __init__(self, storage_dir: str = ".zeer_sessions"):
        """
        Initialize session storage.
        
        Args:
            storage_dir: Directory to store session files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            8-character session ID
        """
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.sha256(timestamp.encode())
        return hash_obj.hexdigest()[:8]
    
    def save_session(self, session_id: str, messages: List[Dict], provider: str, model: str) -> bool:
        """
        Save a chat session to disk.
        
        Args:
            session_id: Unique session identifier
            messages: List of message dictionaries
            provider: Provider name
            model: Model name
            
        Returns:
            True if saved successfully
        """
        try:
            session_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "messages": messages
            }
            
            file_path = self.storage_dir / f"{session_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """
        Load a chat session from disk.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict]:
        """
        List all saved sessions.
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        try:
            for file_path in self.storage_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Find the last user message (excluding system messages)
                    last_user_message = None
                    for msg in reversed(data["messages"]):
                        if msg["role"] == "user" and not msg["content"].startswith("You are an autonomous"):
                            last_user_message = msg["content"]
                            break
                    
                    sessions.append({
                        "session_id": data["session_id"],
                        "created_at": data["created_at"],
                        "provider": data["provider"],
                        "model": data["model"],
                        "message_count": len(data["messages"]),
                        "last_user_message": last_user_message
                    })
        except Exception as e:
            print(f"Error listing sessions: {e}")
        
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
