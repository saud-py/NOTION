"""Configuration module for the Data Engineering Roadmap Bootstrapper."""

import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Configuration class to manage environment variables and settings."""
    
    # API Endpoints
    NOTION_BASE = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    GITHUB_API = "https://api.github.com"
    
    # Environment Variables
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_BUDGET_EMAIL = os.getenv("AWS_BUDGET_EMAIL")
    
    # Feature Toggles
    CREATE_LOCAL_FOLDERS = True
    CREATE_AWS_BUDGET = False
    REPOS_PRIVATE = True
    
    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Validate required configuration."""
        validation = {
            "notion": bool(cls.NOTION_TOKEN and cls.NOTION_PARENT_PAGE_ID),
            "github": bool(cls.GITHUB_TOKEN and cls.GITHUB_USERNAME),
            "aws": bool(cls.AWS_BUDGET_EMAIL) if cls.CREATE_AWS_BUDGET else True
        }
        return validation
    
    @classmethod
    def get_headers(cls, service: str) -> Dict[str, str]:
        """Get API headers for different services."""
        headers = {
            "notion": {
                "Authorization": f"Bearer {cls.NOTION_TOKEN}",
                "Notion-Version": cls.NOTION_VERSION,
                "Content-Type": "application/json",
            },
            "github": {
                "Authorization": f"Bearer {cls.GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            }
        }
        return headers.get(service, {})