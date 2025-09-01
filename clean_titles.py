#!/usr/bin/env python3
"""
Clean up Learning Topic titles by removing content after hyphen (-) 
since that information is already in the Details section.
"""

import json
import os
import requests
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"

# The enhanced database ID
ENHANCED_DB_ID = "2600693c-0443-81cc-ac0e-e94f2fa52616"

def notion_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def get_all_pages(db_id: str) -> List[Dict[str, Any]]:
    """Get all pages from a database."""
    url = f"{NOTION_BASE}/databases/{db_id}/query"
    payload = {"page_size": 100}
    
    response = requests.post(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Failed to query database: {response.status_code}")
        return []

def clean_title(title: str) -> str:
    """Remove content after hyphen (-) from title."""
    if " - " in title:
        return title.split(" - ")[0].strip()
    elif " -" in title:
        return title.split(" -")[0].strip()
    elif "- " in title:
        return title.split("- ")[0].strip()
    else:
        return title.strip()

def update_page_title(page_id: str, new_title: str) -> bool:
    """Update a page's Learning Topic title."""
    url = f"{NOTION_BASE}/pages/{page_id}"
    payload = {
        "properties": {
            "Learning Topic": {
                "title": [{"type": "text", "text": {"content": new_title}}]
            }
        }
    }
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to update page: {response.status_code} - {response.text}")
        return False

def clean_all_titles():
    """Clean up all Learning Topic titles in the database."""
    print("🔍 Getting all pages from database...")
    pages = get_all_pages(ENHANCED_DB_ID)
    
    if not pages:
        print("❌ No pages found")
        return False
    
    print(f"📄 Found {len(pages)} pages")
    
    # Analyze and clean titles
    updates_needed = []
    
    for page in pages:
        page_id = page["id"]
        properties = page.get("properties", {})
        
        # Get current title
        current_title = ""
        week_num = "?"
        
        if "Learning Topic" in properties:
            title_items = properties["Learning Topic"].get("title", [])
            current_title = "".join([item.get("plain_text", "") for item in title_items])
        
        if "Week" in properties and properties["Week"].get("number"):
            week_num = properties["Week"]["number"]
        
        # Clean the title
        cleaned_title = clean_title(current_title)
        
        if cleaned_title != current_title:
            updates_needed.append({
                "page_id": page_id,
                "week": week_num,
                "old_title": current_title,
                "new_title": cleaned_title
            })
    
    if not updates_needed:
        print("✅ All titles are already clean! No updates needed.")
        return True
    
    print(f"\n📝 Found {len(updates_needed)} titles that need cleaning:")
    print("\nPreview of changes:")
    for i, update in enumerate(updates_needed[:5]):  # Show first 5
        print(f"\n   Week {update['week']}:")
        print(f"   OLD: {update['old_title']}")
        print(f"   NEW: {update['new_title']}")
        if i == 4 and len(updates_needed) > 5:
            print(f"   ... and {len(updates_needed) - 5} more")
    
    # Ask for confirmation
    confirm = input(f"\n❓ Update {len(updates_needed)} titles? (y/N): ").lower().strip()
    if confirm != 'y':
        print("👋 Cancelled.")
        return False
    
    print("\n🚀 Updating titles...")
    success_count = 0
    
    for update in updates_needed:
        week = update["week"]
        page_id = update["page_id"]
        new_title = update["new_title"]
        
        print(f"   📝 Updating Week {week}...")
        if update_page_title(page_id, new_title):
            success_count += 1
            print(f"   ✅ Updated Week {week}: {new_title}")
        else:
            print(f"   ❌ Failed Week {week}")
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"\n🎉 Successfully updated {success_count}/{len(updates_needed)} titles!")
    print(f"🔗 Check your database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
    
    return success_count > 0

def main():
    """Main function to clean up titles."""
    print("🧹 Notion Title Cleaner")
    print("=" * 50)
    print("This will remove redundant content after hyphens (-) from Learning Topic titles")
    print(f"Target database: {ENHANCED_DB_ID}")
    print()
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not found")
        return
    
    clean_all_titles()

if __name__ == "__main__":
    main()