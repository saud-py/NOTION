#!/usr/bin/env python3
"""
Enhance the best database (Database 2) with our detailed content
while preserving its visual enhancements.
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from models import RoadmapData

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

def add_details_property_to_database():
    """Add a Details property to the enhanced database."""
    url = f"{NOTION_BASE}/databases/{ENHANCED_DB_ID}"
    
    # First get current database structure
    response = requests.get(url, headers=notion_headers())
    if response.status_code != 200:
        print(f"❌ Could not get database: {response.status_code}")
        return False
    
    db_info = response.json()
    current_properties = db_info.get("properties", {})
    
    # Check if Details property already exists
    if "Details" in current_properties:
        print("✅ Details property already exists!")
        return True
    
    # Add Details property
    new_properties = current_properties.copy()
    new_properties["Details"] = {"rich_text": {}}
    
    payload = {"properties": new_properties}
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        print("✅ Added Details property to database!")
        return True
    else:
        print(f"❌ Failed to add Details property: {response.status_code} - {response.text}")
        return False

def update_pages_with_enhanced_content():
    """Update existing pages with our enhanced content."""
    print("🔄 Getting enhanced roadmap data...")
    weeks = RoadmapData.build_weeks()
    
    # Create a mapping of week number to enhanced data
    week_data = {w.week: w for w in weeks}
    
    print("📄 Getting existing pages...")
    pages = get_all_pages(ENHANCED_DB_ID)
    
    if not pages:
        print("❌ No pages found in database")
        return False
    
    print(f"📝 Updating {len(pages)} pages with enhanced content...")
    
    success_count = 0
    for page in pages:
        page_id = page["id"]
        properties = page.get("properties", {})
        
        # Get the week number from this page
        week_num = None
        if "Week" in properties and properties["Week"].get("number"):
            week_num = properties["Week"]["number"]
        
        if not week_num or week_num not in week_data:
            print(f"   ⚠️  Skipping page - could not determine week number")
            continue
        
        enhanced_week = week_data[week_num]
        
        # Prepare updates
        updates = {}
        
        # Update Learning Topic with clean title (preserve existing format if it's good)
        current_topic = ""
        if "Learning Topic" in properties:
            title_items = properties["Learning Topic"].get("title", [])
            current_topic = "".join([item.get("plain_text", "") for item in title_items])
        
        # Only update if current topic is different from our clean version
        if enhanced_week.topic not in current_topic:
            updates["Learning Topic"] = {
                "title": [{"type": "text", "text": {"content": enhanced_week.topic}}]
            }
        
        # Add Details field with bullet points
        if enhanced_week.details:
            updates["Details"] = {
                "rich_text": [{"type": "text", "text": {"content": enhanced_week.details}}]
            }
        
        # Update Project Phase with clean format
        updates["Project Phase"] = {
            "rich_text": [{"type": "text", "text": {"content": enhanced_week.project}}]
        }
        
        # Update Dataset/Resource if available
        if enhanced_week.dataset_url and "Dataset/Resource" in properties:
            updates["Dataset/Resource"] = {"url": enhanced_week.dataset_url}
        
        # Apply updates
        if updates:
            url = f"{NOTION_BASE}/pages/{page_id}"
            payload = {"properties": updates}
            
            response = requests.patch(url, headers=notion_headers(), json=payload)
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Updated Week {week_num}")
            else:
                print(f"   ❌ Failed Week {week_num}: {response.status_code}")
        else:
            print(f"   ℹ️  Week {week_num} - no updates needed")
    
    print(f"\n🎉 Successfully updated {success_count} pages!")
    return success_count > 0

def main():
    """Main function to enhance the best database."""
    print("🚀 Enhancing the best database with detailed content...")
    print(f"🎯 Target database: {ENHANCED_DB_ID}")
    print(f"🔗 URL: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
    
    # Step 1: Add Details property if needed
    print("\n📋 Step 1: Adding Details property...")
    if not add_details_property_to_database():
        print("❌ Failed to add Details property. Aborting.")
        return
    
    # Step 2: Update pages with enhanced content
    print("\n📝 Step 2: Updating pages with enhanced content...")
    if update_pages_with_enhanced_content():
        print("\n🎉 Database enhancement complete!")
        print(f"🔗 Check your enhanced database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
        print("\n✨ Your database now has:")
        print("   • Clean, concise Learning Topic titles")
        print("   • Detailed bullet points in Details field")
        print("   • Visual emoji enhancements (📋 📝)")
        print("   • Proper project phase organization")
        print("   • All 24 weeks of structured content")
    else:
        print("❌ Failed to update pages.")

if __name__ == "__main__":
    main()