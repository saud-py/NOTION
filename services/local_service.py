"""Local file system service for creating project folders."""

import os
from typing import List, Tuple

from config import Config
from data.project_templates import ProjectTemplates


class LocalService:
    """Service class for local file system operations."""
    
    def __init__(self):
        self.config = Config()
        self.templates = ProjectTemplates()
    
    def create_local_scaffolds(self):
        """Create local project folders if enabled."""
        if not self.config.CREATE_LOCAL_FOLDERS:
            print("[Local] Local folder creation disabled")
            return
        
        projects = self.templates.get_projects()
        
        for repo_name, _ in projects:
            self._create_project_scaffold(repo_name)
        
        print("[Local] Created local project folders.")
    
    def _create_project_scaffold(self, repo_name: str):
        """Create local project folder structure for a single repository."""
        try:
            # Create root directory
            root_dir = os.path.join(os.getcwd(), repo_name)
            os.makedirs(root_dir, exist_ok=True)
            
            # Create README
            readme_path = os.path.join(root_dir, "README.md")
            readme_content = self.templates.get_readme(repo_name)
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            # Create scaffold files
            scaffold_files = self.templates.get_scaffold_files(repo_name)
            for file_path in scaffold_files:
                self._create_local_file(root_dir, file_path)
                
        except Exception as e:
            print(f"[Local] Error creating scaffold for {repo_name}: {e}")
    
    def _create_local_file(self, root_dir: str, file_path: str):
        """Create a single file in the local project structure."""
        full_path = os.path.join(root_dir, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Determine file mode (binary for images, text for others)
        mode = "wb" if file_path.endswith(".png") else "w"
        
        with open(full_path, mode) as f:
            if mode == "w":
                content = self.templates.get_starter_content(file_path)
                f.write(content)
            else:
                f.write(b"")  # Empty binary file for images