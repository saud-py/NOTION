#!/usr/bin/env python3
"""
Add a detailed status property to the Notion database with 
"Not started", "In progress", and "Done" options.
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

def get_database_info():
    """Get current database structure."""
    url = f"{NOTION_BASE}/databases/{ENHANCED_DB_ID}"
    response = requests.get(url, headers=notion_headers())
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get database: {response.status_code}")
        return None

def add_detailed_status_property():
    """Add a detailed status property with proper options."""
    print("📋 Adding detailed status property...")
    
    # Get current database structure
    db_info = get_database_info()
    if not db_info:
        return False
    
    current_properties = db_info.get("properties", {})
    
    # Check if Status 1 property already exists
    if "Status 1" in current_properties:
        print("✅ Status 1 property already exists!")
        return True
    
    # Add Status 1 property with proper status options
    new_properties = current_properties.copy()
    new_properties["Status 1"] = {
        "status": {
            "options": [
                {
                    "name": "Not started",
                    "color": "gray"
                },
                {
                    "name": "In progress", 
                    "color": "blue"
                },
                {
                    "name": "Done",
                    "color": "green"
                }
            ]
        }
    }
    
    # Update database
    url = f"{NOTION_BASE}/databases/{ENHANCED_DB_ID}"
    payload = {"properties": new_properties}
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        print("✅ Added Status 1 property with status options!")
        return True
    else:
        print(f"❌ Failed to add Status 1 property: {response.status_code} - {response.text}")
        return False

def get_all_pages():
    """Get all pages from the database."""
    url = f"{NOTION_BASE}/databases/{ENHANCED_DB_ID}/query"
    payload = {"page_size": 100}
    
    response = requests.post(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Failed to query database: {response.status_code}")
        return []

def set_default_status_for_all_pages():
    """Set default status to 'Not started' for all pages."""
    print("📄 Setting default status for all pages...")
    
    pages = get_all_pages()
    if not pages:
        print("❌ No pages found")
        return False
    
    print(f"📊 Found {len(pages)} pages to update")
    
    success_count = 0
    for page in pages:
        page_id = page["id"]
        properties = page.get("properties", {})
        
        # Get week number for display
        week_num = "?"
        if "Week" in properties and properties["Week"].get("number"):
            week_num = properties["Week"]["number"]
        
        # Update page with default status
        url = f"{NOTION_BASE}/pages/{page_id}"
        payload = {
            "properties": {
                "Status 1": {
                    "status": {"name": "Not started"}
                }
            }
        }
        
        response = requests.patch(url, headers=notion_headers(), json=payload)
        if response.status_code == 200:
            success_count += 1
            print(f"   ✅ Set Week {week_num} to 'Not started'")
        else:
            print(f"   ❌ Failed Week {week_num}: {response.status_code}")
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"\n🎉 Successfully updated {success_count}/{len(pages)} pages!")
    return success_count > 0

def main():
    """Main function to add detailed status property."""
    print("📊 Adding Detailed Status Property to Notion Database")
    print("=" * 60)
    print("This will add a 'Status 1' property with:")
    print("   🔘 Not started (gray)")
    print("   🔵 In progress (blue)")  
    print("   🟢 Done (green)")
    print(f"\nTarget database: {ENHANCED_DB_ID}")
    print()
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not found")
        return
    
    # Step 1: Add the Status 1 property
    print("📋 Step 1: Adding Status 1 property...")
    if not add_detailed_status_property():
        print("❌ Failed to add Status 1 property. Aborting.")
        return
    
    # Step 2: Set default status for all pages
    print("\n📝 Step 2: Setting default status for all pages...")
    confirm = input("❓ Set all weeks to 'Not started' status? (y/N): ").lower().strip()
    
    if confirm == 'y':
        if set_default_status_for_all_pages():
            print(f"\n🎉 Status property setup complete!")
            print(f"🔗 Check your database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
            print("\n✨ You can now track progress with:")
            print("   🔘 Not started - Tasks you haven't begun")
            print("   🔵 In progress - Tasks you're currently working on")
            print("   🟢 Done - Completed tasks")
        else:
            print("❌ Failed to set default status.")
    else:
        print("👋 Skipped setting default status. Property added successfully!")

if __name__ == "__main__":
    main()