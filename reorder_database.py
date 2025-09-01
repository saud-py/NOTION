#!/usr/bin/env python3
"""
Reorder the Notion database so Week 1 appears at the top (ascending order).
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

def extract_page_data(page: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all data from a page."""
    properties = page.get("properties", {})
    extracted = {}
    
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type", "")
        
        if prop_type == "title":
            items = prop_data.get("title", [])
            extracted[prop_name] = {"title": items}
        elif prop_type == "rich_text":
            items = prop_data.get("rich_text", [])
            extracted[prop_name] = {"rich_text": items}
        elif prop_type == "select":
            select_obj = prop_data.get("select")
            if select_obj:
                extracted[prop_name] = {"select": {"name": select_obj.get("name", "")}}
        elif prop_type == "number":
            number = prop_data.get("number")
            if number is not None:
                extracted[prop_name] = {"number": number}
        elif prop_type == "url":
            url = prop_data.get("url")
            if url:
                extracted[prop_name] = {"url": url}
    
    return extracted

def create_page_with_data(db_id: str, page_data: Dict[str, Any]) -> bool:
    """Create a new page with the given data."""
    url = f"{NOTION_BASE}/pages"
    payload = {
        "parent": {"database_id": db_id},
        "properties": page_data
    }
    
    response = requests.post(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to create page: {response.status_code} - {response.text}")
        return False

def archive_page(page_id: str) -> bool:
    """Archive a page."""
    url = f"{NOTION_BASE}/pages/{page_id}"
    payload = {"archived": True}
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    return response.status_code == 200

def reorder_database():
    """Reorder the database so Week 1 is at the top."""
    print("🔄 Getting all pages from database...")
    pages = get_all_pages(ENHANCED_DB_ID)
    
    if not pages:
        print("❌ No pages found")
        return False
    
    print(f"📄 Found {len(pages)} pages")
    
    # Extract page data and sort by week number
    page_data_list = []
    for page in pages:
        properties = page.get("properties", {})
        week_num = None
        
        if "Week" in properties and properties["Week"].get("number"):
            week_num = properties["Week"]["number"]
        
        if week_num:
            page_data = extract_page_data(page)
            page_data_list.append({
                "week": week_num,
                "page_id": page["id"],
                "data": page_data
            })
    
    # Sort by week number (ascending - Week 1 first)
    page_data_list.sort(key=lambda x: x["week"])
    
    print(f"📊 Sorted {len(page_data_list)} pages by week number")
    
    # Ask for confirmation
    print(f"\n🎯 This will recreate all pages in ascending order (Week 1 → Week 24)")
    print(f"📍 Database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
    
    confirm = input("\n❓ Continue with reordering? (y/N): ").lower().strip()
    if confirm != 'y':
        print("👋 Cancelled.")
        return False
    
    print("\n🚀 Starting reorder process...")
    
    # Create pages in the correct order (Week 1 first)
    success_count = 0
    for item in page_data_list:
        week_num = item["week"]
        page_data = item["data"]
        
        print(f"   📝 Creating Week {week_num}...")
        if create_page_with_data(ENHANCED_DB_ID, page_data):
            success_count += 1
            print(f"   ✅ Created Week {week_num}")
        else:
            print(f"   ❌ Failed Week {week_num}")
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"\n📊 Successfully created {success_count}/{len(page_data_list)} pages")
    
    if success_count == len(page_data_list):
        print("\n🗑️  Now archiving old pages...")
        archived_count = 0
        for item in page_data_list:
            page_id = item["page_id"]
            week_num = item["week"]
            
            if archive_page(page_id):
                archived_count += 1
                print(f"   🗑️  Archived old Week {week_num}")
            else:
                print(f"   ❌ Failed to archive Week {week_num}")
            
            time.sleep(0.2)
        
        print(f"\n🎉 Reordering complete!")
        print(f"✅ Created {success_count} new pages in correct order")
        print(f"🗑️  Archived {archived_count} old pages")
        print(f"🔗 Check your database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
        print("\n📈 Week 1 should now be at the top!")
        
    else:
        print("\n❌ Some pages failed to create. Please check manually.")
    
    return success_count > 0

def main():
    """Main function."""
    print("🔄 Notion Database Reorder Tool")
    print("=" * 50)
    print("This will reorder your database so Week 1 appears at the top")
    print(f"Target database: {ENHANCED_DB_ID}")
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not found in environment")
        return
    
    reorder_database()

if __name__ == "__main__":
    main()