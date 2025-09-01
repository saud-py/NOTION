#!/usr/bin/env python3
"""
Parse CSV file and add daily subtasks to each week in Notion database.
Ignores Week, Topic, Resources columns as requested.
Uses Day, Learning, Deliverable, Task columns to create subtasks.
"""

import csv
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

def parse_csv_file(filename: str) -> Dict[int, List[Dict[str, str]]]:
    """Parse CSV file and group by week number."""
    week_data = {}
    
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            week_num = int(row['Week'])
            day_num = int(row['Day'])
            
            # Extract the columns we want (ignoring Week, Topic, Resources)
            subtask = {
                'day': day_num,
                'learning': row['Learning'].strip(),
                'deliverable': row['Deliverable'].strip(),
                'task': row['Task'].strip()
            }
            
            if week_num not in week_data:
                week_data[week_num] = []
            
            week_data[week_num].append(subtask)
    
    return week_data

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

def add_subtasks_property_to_database():
    """Add a Subtasks property to the database if it doesn't exist."""
    url = f"{NOTION_BASE}/databases/{ENHANCED_DB_ID}"
    
    # Get current database structure
    response = requests.get(url, headers=notion_headers())
    if response.status_code != 200:
        print(f"❌ Could not get database: {response.status_code}")
        return False
    
    db_info = response.json()
    current_properties = db_info.get("properties", {})
    
    # Check if Subtasks property already exists
    if "Subtasks" in current_properties:
        print("✅ Subtasks property already exists!")
        return True
    
    # Add Subtasks property as rich_text
    new_properties = current_properties.copy()
    new_properties["Subtasks"] = {"rich_text": {}}
    
    payload = {"properties": new_properties}
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        print("✅ Added Subtasks property to database!")
        return True
    else:
        print(f"❌ Failed to add Subtasks property: {response.status_code} - {response.text}")
        return False

def format_subtasks_content(subtasks: List[Dict[str, str]]) -> str:
    """Format subtasks into a readable text format."""
    content_lines = []
    
    for subtask in sorted(subtasks, key=lambda x: x['day']):
        day_num = subtask['day']
        learning = subtask['learning']
        deliverable = subtask['deliverable']
        task = subtask['task']
        
        # Format each day's content
        day_content = f"📅 Day {day_num}: {task}\n"
        day_content += f"   🎯 Learning: {learning}\n"
        day_content += f"   📋 Deliverable: {deliverable}\n"
        
        content_lines.append(day_content)
    
    return "\n".join(content_lines)

def update_page_with_subtasks(page_id: str, subtasks_content: str) -> bool:
    """Update a page with subtasks content."""
    url = f"{NOTION_BASE}/pages/{page_id}"
    payload = {
        "properties": {
            "Subtasks": {
                "rich_text": [{"type": "text", "text": {"content": subtasks_content}}]
            }
        }
    }
    
    response = requests.patch(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to update page: {response.status_code} - {response.text}")
        return False

def add_subtasks_to_notion(csv_filename: str):
    """Main function to add subtasks from CSV to Notion pages."""
    print("📊 Parsing CSV file...")
    week_data = parse_csv_file(csv_filename)
    
    print(f"📄 Found data for {len(week_data)} weeks")
    for week_num in sorted(week_data.keys())[:5]:  # Show first 5 weeks
        print(f"   Week {week_num}: {len(week_data[week_num])} days")
    
    print("\n🔍 Getting Notion pages...")
    pages = get_all_pages(ENHANCED_DB_ID)
    
    if not pages:
        print("❌ No pages found in database")
        return False
    
    # Create mapping of week number to page ID
    week_to_page = {}
    for page in pages:
        properties = page.get("properties", {})
        if "Week" in properties and properties["Week"].get("number"):
            week_num = properties["Week"]["number"]
            week_to_page[week_num] = page["id"]
    
    print(f"📋 Found {len(week_to_page)} weeks in Notion database")
    
    # Show preview of what will be added
    print("\n📝 Preview of subtasks to be added:")
    for week_num in sorted(list(week_data.keys())[:3]):  # Show first 3 weeks
        if week_num in week_to_page:
            subtasks = week_data[week_num]
            print(f"\n   Week {week_num} ({len(subtasks)} days):")
            for i, subtask in enumerate(subtasks[:2]):  # Show first 2 days
                print(f"     Day {subtask['day']}: {subtask['task'][:50]}...")
            if len(subtasks) > 2:
                print(f"     ... and {len(subtasks) - 2} more days")
    
    # Ask for confirmation
    total_weeks = len([w for w in week_data.keys() if w in week_to_page])
    confirm = input(f"\n❓ Add subtasks to {total_weeks} weeks? (y/N): ").lower().strip()
    if confirm != 'y':
        print("👋 Cancelled.")
        return False
    
    print("\n🚀 Adding subtasks to Notion pages...")
    success_count = 0
    
    for week_num in sorted(week_data.keys()):
        if week_num not in week_to_page:
            print(f"   ⚠️  Week {week_num} not found in Notion database")
            continue
        
        page_id = week_to_page[week_num]
        subtasks = week_data[week_num]
        
        # Format subtasks content
        subtasks_content = format_subtasks_content(subtasks)
        
        print(f"   📝 Adding subtasks to Week {week_num} ({len(subtasks)} days)...")
        if update_page_with_subtasks(page_id, subtasks_content):
            success_count += 1
            print(f"   ✅ Updated Week {week_num}")
        else:
            print(f"   ❌ Failed Week {week_num}")
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"\n🎉 Successfully added subtasks to {success_count} weeks!")
    print(f"🔗 Check your database: https://www.notion.so/{ENHANCED_DB_ID.replace('-', '')}")
    
    return success_count > 0

def main():
    """Main function."""
    print("📋 CSV Subtasks Importer for Notion")
    print("=" * 50)
    print("This will add daily subtasks from CSV to your Notion database")
    print(f"Target database: {ENHANCED_DB_ID}")
    print("Ignoring columns: Week, Topic, Resources")
    print("Using columns: Day, Learning, Deliverable, Task")
    print()
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not found")
        return
    
    csv_filename = "data_engineering_6_month_plan_detailed.csv"
    
    if not os.path.exists(csv_filename):
        print(f"❌ CSV file not found: {csv_filename}")
        return
    
    # Step 1: Add Subtasks property if needed
    print("📋 Step 1: Adding Subtasks property to database...")
    if not add_subtasks_property_to_database():
        print("❌ Failed to add Subtasks property. Aborting.")
        return
    
    # Step 2: Add subtasks from CSV
    print("\n📝 Step 2: Adding subtasks from CSV...")
    add_subtasks_to_notion(csv_filename)

if __name__ == "__main__":
    main()