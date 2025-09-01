"""GitHub API service for repository management."""

import base64
import json
import time
from typing import Dict, List, Tuple
import requests

from config import Config
from data.project_templates import ProjectTemplates


class GitHubService:
    """Service class for GitHub API operations."""
    
    def __init__(self):
        self.config = Config()
        self.api_url = self.config.GITHUB_API
        self.headers = self.config.get_headers("github")
        self.templates = ProjectTemplates()
    
    def create_all_repositories(self) -> Dict[str, str]:
        """Create all GitHub repositories and return their URLs."""
        if not self.config.GITHUB_TOKEN or not self.config.GITHUB_USERNAME:
            print("[GitHub] Skipping (missing env vars)")
            return {}
        
        repo_urls: Dict[str, str] = {}
        projects = self.templates.get_projects()
        
        for repo_name, description in projects:
            url = self._create_repository(repo_name, description)
            if url:
                repo_urls[repo_name] = url
                self._scaffold_repository(repo_name)
        
        return repo_urls
    
    def _create_repository(self, name: str, description: str) -> str:
        """Create a single GitHub repository."""
        if self._repository_exists(name):
            print(f"[GitHub] Repo exists: {name}")
            return f"https://github.com/{self.config.GITHUB_USERNAME}/{name}"
        
        url = f"{self.api_url}/user/repos"
        payload = {
            "name": name,
            "description": description,
            "private": self.config.REPOS_PRIVATE,
            "auto_init": True,
        }
        
        try:
            resp = requests.post(url, headers=self.headers, data=json.dumps(payload))
            if resp.status_code in (201, 202):
                print(f"[GitHub] Created repo {name}")
                return f"https://github.com/{self.config.GITHUB_USERNAME}/{name}"
            else:
                print(f"[GitHub] Failed to create repo {name}: {resp.status_code} {resp.text}")
                return ""
        except Exception as e:
            print(f"[GitHub] Error creating repo {name}: {e}")
            return ""
    
    def _repository_exists(self, name: str) -> bool:
        """Check if a GitHub repository already exists."""
        url = f"{self.api_url}/repos/{self.config.GITHUB_USERNAME}/{name}"
        try:
            resp = requests.get(url, headers=self.headers)
            return resp.status_code == 200
        except Exception:
            return False
    
    def _scaffold_repository(self, repo_name: str):
        """Create the folder structure and starter files for a repository."""
        # Add README
        readme_content = self.templates.get_readme(repo_name)
        self._add_file_to_repo(repo_name, "README.md", readme_content, "chore: add README")
        
        # Add scaffold files
        scaffold_files = self.templates.get_scaffold_files(repo_name)
        for file_path in scaffold_files:
            content = self.templates.get_starter_content(file_path)
            self._add_file_to_repo(repo_name, file_path, content, f"chore: scaffold {file_path}")
            time.sleep(0.2)  # Rate limiting
    
    def _add_file_to_repo(self, repo: str, path: str, content: str, message: str = "add file") -> bool:
        """Add a file to a GitHub repository."""
        url = f"{self.api_url}/repos/{self.config.GITHUB_USERNAME}/{repo}/contents/{path}"
        
        # Handle binary files (like .png) with empty content
        if path.endswith(".png"):
            content = ""
        
        # Check if file exists first (for README.md that's auto-created)
        existing_file = self._get_file_sha(repo, path)
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        }
        
        # If file exists, include SHA for update
        if existing_file:
            data["sha"] = existing_file
        
        try:
            resp = requests.put(url, headers=self.headers, data=json.dumps(data))
            if resp.status_code not in (201, 200):
                print(f"[GitHub] Failed to create {repo}:{path}: {resp.status_code} {resp.text}")
                return False
            return True
        except Exception as e:
            print(f"[GitHub] Error adding file {repo}:{path}: {e}")
            return False
    
    def _get_file_sha(self, repo: str, path: str) -> str:
        """Get the SHA of an existing file, or None if it doesn't exist."""
        url = f"{self.api_url}/repos/{self.config.GITHUB_USERNAME}/{repo}/contents/{path}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json().get("sha", "")
            return ""
        except Exception:
            return ""