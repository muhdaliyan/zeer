"""
Skills management system following agentskills.io specification.

This module handles loading, parsing, and managing agent skills.
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class Skill:
    """Represents an agent skill following agentskills.io format."""
    name: str
    description: str
    path: Path
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    allowed_tools: Optional[List[str]] = None
    body: str = ""
    
    def get_full_content(self) -> str:
        """Get the full skill content including frontmatter."""
        frontmatter = f"""---
name: {self.name}
description: {self.description}"""
        
        if self.license:
            frontmatter += f"\nlicense: {self.license}"
        if self.compatibility:
            frontmatter += f"\ncompatibility: {self.compatibility}"
        if self.metadata:
            frontmatter += f"\nmetadata: {yaml.dump(self.metadata, default_flow_style=False)}"
        if self.allowed_tools:
            frontmatter += f"\nallowed-tools: {' '.join(self.allowed_tools)}"
        
        frontmatter += "\n---\n\n"
        return frontmatter + self.body
    
    def validate(self) -> List[str]:
        """Validate skill format and return list of errors."""
        errors = []
        
        # Validate name
        if not self.name:
            errors.append("Name is required")
        elif len(self.name) > 64:
            errors.append("Name must be max 64 characters")
        elif not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', self.name):
            errors.append("Name must be lowercase letters, numbers, and hyphens only. Must not start or end with hyphen")
        
        # Validate description
        if not self.description:
            errors.append("Description is required")
        elif len(self.description) > 1024:
            errors.append("Description must be max 1024 characters")
        
        # Validate compatibility
        if self.compatibility and len(self.compatibility) > 500:
            errors.append("Compatibility must be max 500 characters")
        
        return errors


class SkillsManager:
    """Manager for loading and accessing agent skills."""
    
    def __init__(self, skills_dir: str = "skills"):
        """
        Initialize the skills manager.
        
        Args:
            skills_dir: Directory containing skill folders
        """
        # Handle both absolute and relative paths
        skills_path = Path(skills_dir)
        
        if not skills_path.is_absolute():
            # Try to find skills directory in multiple locations
            # 1. Current working directory (for running from project root)
            cwd_skills = Path.cwd() / skills_dir
            
            # 2. Relative to this file (for development and installed package)
            current_file = Path(__file__)
            package_skills = current_file.parent.parent / skills_dir
            
            # 3. Try using importlib.resources for installed packages (Python 3.9+)
            try:
                import sys
                if sys.version_info >= (3, 9):
                    from importlib.resources import files
                    try:
                        # Try to get skills from package data
                        pkg_skills = files('skills')
                        if pkg_skills.is_dir():
                            skills_path = Path(str(pkg_skills))
                    except (TypeError, ModuleNotFoundError, AttributeError):
                        pass
            except ImportError:
                pass
            
            # Choose the first existing path
            if cwd_skills.exists() and cwd_skills.is_dir():
                skills_path = cwd_skills
            elif package_skills.exists() and package_skills.is_dir():
                skills_path = package_skills
            # else: keep the original skills_path
        
        self.skills_dir = skills_path
        self.skills: Dict[str, Skill] = {}
        self._load_skills()
    
    def _load_skills(self) -> None:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            # Try to provide helpful debug info
            import sys
            print(f"Warning: Skills directory not found at: {self.skills_dir.absolute()}", file=sys.stderr)
            print(f"Current working directory: {Path.cwd()}", file=sys.stderr)
            return
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            
            try:
                skill = self._parse_skill(skill_file, skill_dir)
                if skill:
                    # Validate skill
                    errors = skill.validate()
                    if errors:
                        print(f"Warning: Skill '{skill.name}' has validation errors: {', '.join(errors)}")
                    else:
                        self.skills[skill.name] = skill
            except Exception as e:
                print(f"Warning: Failed to load skill from {skill_dir}: {e}")
    
    def _parse_skill(self, skill_file: Path, skill_dir: Path) -> Optional[Skill]:
        """
        Parse a SKILL.md file.
        
        Args:
            skill_file: Path to SKILL.md
            skill_dir: Path to skill directory
            
        Returns:
            Parsed Skill object or None if invalid
        """
        content = skill_file.read_text(encoding='utf-8')
        
        # Split frontmatter and body
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        # Parse frontmatter
        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None
        
        # Validate required fields
        if 'name' not in frontmatter or 'description' not in frontmatter:
            return None
        
        # Extract body
        body = parts[2].strip()
        
        # Parse allowed-tools if present
        allowed_tools = None
        if 'allowed-tools' in frontmatter:
            allowed_tools = frontmatter['allowed-tools'].split()
        
        return Skill(
            name=frontmatter['name'],
            description=frontmatter['description'],
            path=skill_dir,
            license=frontmatter.get('license'),
            compatibility=frontmatter.get('compatibility'),
            metadata=frontmatter.get('metadata'),
            allowed_tools=allowed_tools,
            body=body
        )
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Skill]:
        """List all available skills."""
        return list(self.skills.values())
    
    def get_skill_content(self, name: str) -> Optional[str]:
        """Get the full content of a skill."""
        skill = self.get_skill(name)
        return skill.get_full_content() if skill else None
    
    def read_skill_file(self, skill_name: str, file_path: str) -> Optional[str]:
        """
        Read a file from a skill's directory.
        
        Args:
            skill_name: Name of the skill
            file_path: Relative path within the skill directory
            
        Returns:
            File content or None if not found
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return None
        
        full_path = skill.path / file_path
        if not full_path.exists() or not full_path.is_file():
            return None
        
        try:
            return full_path.read_text(encoding='utf-8')
        except Exception:
            return None
    
    def list_skill_scripts(self, skill_name: str) -> List[str]:
        """
        List all scripts in a skill's scripts/ directory.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            List of script filenames
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return []
        
        scripts_dir = skill.path / "scripts"
        if not scripts_dir.exists() or not scripts_dir.is_dir():
            return []
        
        scripts = []
        for script_file in scripts_dir.iterdir():
            if script_file.is_file():
                scripts.append(script_file.name)
        
        return scripts
    
    def get_script_path(self, skill_name: str, script_name: str) -> Optional[Path]:
        """
        Get the full path to a script file.
        
        Args:
            skill_name: Name of the skill
            script_name: Name of the script file
            
        Returns:
            Path to script or None if not found
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return None
        
        script_path = skill.path / "scripts" / script_name
        if script_path.exists() and script_path.is_file():
            return script_path
        
        return None
    
    def resolve_file_reference(self, skill_name: str, reference: str) -> Optional[str]:
        """
        Resolve a file reference in skill content.
        
        Args:
            skill_name: Name of the skill
            reference: File reference (e.g., "scripts/setup.py" or "references/api.md")
            
        Returns:
            File content or None if not found
        """
        return self.read_skill_file(skill_name, reference)
