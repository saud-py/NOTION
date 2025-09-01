"""Notion API service for managing databases and pages."""

import json
import time
from typing import Dict, List, Optional
import requests

from config import Config
from models import WeekItem


class NotionService:
    """Service class for Notion API operations."""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.NOTION_BASE
        self.headers = self.config.get_headers("notion")
    
    def create_database(self, title: str = "6‑Month Data Engineering Career Plan") -> Optional[str]:
        """Create a Notion database with the roadmap structure."""
        if not self.config.NOTION_TOKEN or not self.config.NOTION_PARENT_PAGE_ID:
            print("[Notion] Skipping (missing env vars)")
            return None
        
        url = f"{self.base_url}/databases"
        payload = self._build_database_payload(title)
        
        try:
            resp = requests.post(url, headers=self.headers, data=json.dumps(payload))
            if resp.status_code == 200:
                db_id = resp.json()["id"]
                print(f"[Notion] Database created: {db_id}")
                return db_id
            else:
                print(f"[Notion] Create DB response: {resp.status_code} {resp.text}")
                return None
        except Exception as e:
            print(f"[Notion] Error creating database: {e}")
            return None
    
    def add_weeks_to_database(self, db_id: str, weeks: List[WeekItem], repo_urls: Dict[str, str]):
        """Add all 24 weeks as pages in the Notion database."""
        if not db_id:
            return
        
        url = f"{self.base_url}/pages"
        
        for week in weeks:
            try:
                page_payload = self._build_page_payload(db_id, week, repo_urls)
                resp = requests.post(url, headers=self.headers, data=json.dumps(page_payload))
                
                if resp.status_code != 200:
                    print(f"[Notion] Failed to add Week {week.week}: {resp.status_code} {resp.text}")
                else:
                    print(f"[Notion] Added Week {week.week}")
                
                time.sleep(0.2)  # Rate limiting
            except Exception as e:
                print(f"[Notion] Error adding Week {week.week}: {e}")
    
    def _build_database_payload(self, title: str) -> Dict:
        """Build the payload for creating a Notion database."""
        return {
            "parent": {"type": "page_id", "page_id": self.config.NOTION_PARENT_PAGE_ID},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": {
                "Week": {"number": {}},
                "Month": {"select": {"options": [
                    {"name": "Month 1: SQL & ETL Basics", "color": "blue"},
                    {"name": "Month 2: Data Warehousing", "color": "green"},
                    {"name": "Month 3: DataOps & Automation", "color": "orange"},
                    {"name": "Month 4: Big Data Processing", "color": "purple"},
                    {"name": "Month 5: Real-Time Streaming", "color": "pink"},
                    {"name": "Month 6: Capstone Projects", "color": "red"}
                ]}},
                "Learning Topic": {"title": {}},
                "Project Phase": {"rich_text": {}},
                "Details": {"rich_text": {}},
                "Status": {"select": {"options": [
                    {"name": "📋 To Do", "color": "red"},
                    {"name": "🔄 In Progress", "color": "yellow"},
                    {"name": "✅ Done", "color": "green"},
                    {"name": "🔍 Review", "color": "blue"}
                ]}},
                "GitHub Repo": {"url": {}},
                "Dataset/Resource": {"url": {}},
                "Priority": {"select": {"options": [
                    {"name": "🔥 High", "color": "red"},
                    {"name": "⚡ Medium", "color": "yellow"},
                    {"name": "📝 Low", "color": "gray"}
                ]}},
                "Week Timeline": {"rich_text": {}},
            }
        }
    
    def _build_page_payload(self, db_id: str, week: WeekItem, repo_urls: Dict[str, str]) -> Dict:
        """Build the payload for creating a page in the database."""
        github_url = repo_urls.get(week.repo_hint or "", "")
        
        # Map month numbers to descriptive names
        month_names = {
            1: "Month 1: SQL & ETL Basics",
            2: "Month 2: Data Warehousing", 
            3: "Month 3: DataOps & Automation",
            4: "Month 4: Big Data Processing",
            5: "Month 5: Real-Time Streaming",
            6: "Month 6: Capstone Projects"
        }
        
        # Set priority based on week number
        if week.week <= 8:
            priority = "🔥 High"
        elif week.week <= 16:
            priority = "⚡ Medium"
        else:
            priority = "📝 Low"
        
        return {
            "parent": {"database_id": db_id},
            "properties": {
                "Week": {"number": week.week},
                "Month": {"select": {"name": month_names.get(week.month, f"Month {week.month}")}},
                "Learning Topic": {"title": [{"type": "text", "text": {"content": week.topic}}]},
                "Project Phase": {"rich_text": [{"type": "text", "text": {"content": week.project}}]},
                "Details": {"rich_text": [{"type": "text", "text": {"content": week.details or ""}}]},
                "Status": {"select": {"name": "📋 To Do"}},
                "GitHub Repo": {"url": github_url or None},
                "Dataset/Resource": {"url": week.dataset_url or None},
                "Priority": {"select": {"name": priority}},
                "Week Timeline": {"rich_text": [{"type": "text", "text": {"content": week.due_label}}]},
            }
        }