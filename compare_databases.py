#!/usr/bin/env python3
"""
Compare Notion databases in detail to see which has better content.
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"

def notion_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def get_all_pages(db_id: str) -> List[Dict[str, Any]]:
    """Get all pages from a database."""
    url = f"{NOTION_BASE}/databases/{db_id}/query"
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        response = requests.post(url, headers=notion_headers(), json=payload)
        if response.status_code == 200:
            data = response.json()
            all_pages.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        else:
            print(f"❌ Failed to query database: {response.status_code}")
            break
    
    return all_pages

def extract_text_from_property(prop: Dict[str, Any]) -> str:
    """Extract text content from various Notion property types."""
    prop_type = prop.get("type", "")
    
    if prop_type == "title":
        items = prop.get("title", [])
        return "".join([item.get("plain_text", "") for item in items])
    elif prop_type == "rich_text":
        items = prop.get("rich_text", [])
        return "".join([item.get("plain_text", "") for item in items])
    elif prop_type == "select":
        select_obj = prop.get("select")
        return select_obj.get("name", "") if select_obj else ""
    elif prop_type == "number":
        return str(prop.get("number", "")) if prop.get("number") is not None else ""
    elif prop_type == "url":
        return prop.get("url", "") or ""
    else:
        return f"[{prop_type}]"

def compare_databases():
    """Compare the three databases in detail."""
    databases = [
        ("Database 1 (Latest)", "2600693c-0443-81e9-ac47-e287876d151f"),
        ("Database 2 (Enhanced)", "2600693c-0443-81cc-ac0e-e94f2fa52616"), 
        ("Database 3 (Original)", "2600693c-0443-81f6-b1f3-d813609556d8")
    ]
    
    for name, db_id in databases:
        print(f"\n{'='*60}")
        print(f"🔍 {name}")
        print(f"ID: {db_id}")
        print('='*60)
        
        # Get database info
        db_url = f"{NOTION_BASE}/databases/{db_id}"
        db_response = requests.get(db_url, headers=notion_headers())
        
        if db_response.status_code != 200:
            print(f"❌ Could not access database: {db_response.status_code}")
            continue
            
        db_info = db_response.json()
        properties = db_info.get("properties", {})
        
        print(f"📋 Properties ({len(properties)}):")
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type", "unknown")
            print(f"   • {prop_name}: {prop_type}")
        
        # Get all pages
        pages = get_all_pages(db_id)
        print(f"\n📄 Total Pages: {len(pages)}")
        
        if pages:
            print(f"\n📝 Sample Content (First 3 rows):")
            for i, page in enumerate(pages[:3]):
                print(f"\n   Row {i+1}:")
                page_props = page.get("properties", {})
                
                for prop_name, prop_data in page_props.items():
                    content = extract_text_from_property(prop_data)
                    if content:  # Only show non-empty content
                        # Truncate long content
                        if len(content) > 100:
                            content = content[:100] + "..."
                        print(f"     {prop_name}: {content}")
        
        print(f"\n🔗 Direct Link: https://www.notion.so/{db_id.replace('-', '')}")

if __name__ == "__main__":
    compare_databases()