#!/usr/bin/env python3
"""
Notion Database Scanner and Updater

This script will:
1. Scan for all databases in your Notion workspace
2. Identify databases that might be your roadmap (by title/content)
3. Show you the structure and sample content of each
4. Allow you to update the better database with enhanced content
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Import our enhanced models
from models import RoadmapData

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"

def notion_headers() -> Dict[str, str]:
    """Return headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def search_databases() -> List[Dict[str, Any]]:
    """Search for all databases in the workspace."""
    url = f"{NOTION_BASE}/search"
    payload = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    
    response = requests.post(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Search failed: {response.status_code} - {response.text}")
        return []

def get_database_info(db_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a database."""
    url = f"{NOTION_BASE}/databases/{db_id}"
    response = requests.get(url, headers=notion_headers())
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get database {db_id}: {response.status_code}")
        return None

def get_database_pages(db_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get sample pages from a database."""
    url = f"{NOTION_BASE}/databases/{db_id}/query"
    payload = {"page_size": limit}
    
    response = requests.post(url, headers=notion_headers(), json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Failed to query database {db_id}: {response.status_code}")
        return []

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
        return str(prop.get("number", ""))
    elif prop_type == "url":
        return prop.get("url", "")
    else:
        return f"[{prop_type}]"

def analyze_database(db_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a database and return summary information."""
    title = ""
    title_items = db_info.get("title", [])
    if title_items:
        title = "".join([item.get("plain_text", "") for item in title_items])
    
    properties = db_info.get("properties", {})
    
    # Get sample pages
    pages = get_database_pages(db_info["id"])
    
    analysis = {
        "id": db_info["id"],
        "title": title,
        "created_time": db_info.get("created_time", ""),
        "last_edited_time": db_info.get("last_edited_time", ""),
        "properties": list(properties.keys()),
        "page_count": len(pages),
        "sample_content": []
    }
    
    # Analyze sample pages
    for page in pages[:3]:  # Show first 3 pages
        page_content = {}
        for prop_name, prop_data in page.get("properties", {}).items():
            page_content[prop_name] = extract_text_from_property(prop_data)
        analysis["sample_content"].append(page_content)
    
    return analysis

def is_roadmap_database(analysis: Dict[str, Any]) -> bool:
    """Check if this looks like a roadmap database."""
    title = analysis["title"].lower()
    properties = [p.lower() for p in analysis["properties"]]
    
    # Check for roadmap-related keywords
    roadmap_keywords = ["roadmap", "learning", "data engineering", "career", "plan", "week"]
    title_match = any(keyword in title for keyword in roadmap_keywords)
    
    # Check for typical roadmap properties
    roadmap_props = ["week", "topic", "learning", "project", "month"]
    prop_match = any(any(rp in prop for rp in roadmap_props) for prop in properties)
    
    return title_match or prop_match

def update_database_with_enhanced_content(db_id: str) -> bool:
    """Update an existing database with our enhanced roadmap content."""
    print(f"\n🔄 Updating database {db_id} with enhanced content...")
    
    # Get enhanced weeks data
    weeks = RoadmapData.build_weeks()
    
    # First, clear existing pages (optional - ask user)
    clear_existing = input("❓ Do you want to clear existing pages first? (y/N): ").lower().strip()
    
    if clear_existing == 'y':
        print("🗑️  Clearing existing pages...")
        existing_pages = get_database_pages(db_id, limit=100)
        for page in existing_pages:
            # Archive the page
            url = f"{NOTION_BASE}/pages/{page['id']}"
            payload = {"archived": True}
            requests.patch(url, headers=notion_headers(), json=payload)
        print(f"   Archived {len(existing_pages)} existing pages")
    
    # Add enhanced content
    print("📝 Adding enhanced roadmap content...")
    url = f"{NOTION_BASE}/pages"
    
    success_count = 0
    for w in weeks:
        # Determine priority
        priority = "High" if w.month <= 2 else "Medium" if w.month <= 4 else "Low"
        
        # Create page payload - adapt to existing database structure
        page = {
            "parent": {"database_id": db_id},
            "properties": {}
        }
        
        # Try different property name variations
        property_mappings = {
            "week": ["Week", "week", "Week #", "Week Number"],
            "month": ["Month", "month", "Month #"],
            "topic": ["Learning Topic", "Topic", "Learning", "Title", "Name"],
            "details": ["Details", "Description", "Notes", "Content"],
            "project": ["Project Phase", "Project", "Phase"],
            "status": ["Status", "status"],
            "priority": ["Priority", "priority"],
            "github": ["GitHub", "Github", "Repo", "Repository"],
            "dataset": ["Dataset", "Data", "Source"]
        }
        
        # Get database structure to match properties
        db_info = get_database_info(db_id)
        if not db_info:
            print(f"❌ Could not get database info for {db_id}")
            return False
        
        existing_props = db_info.get("properties", {})
        
        # Map our data to existing properties
        for our_key, possible_names in property_mappings.items():
            for prop_name in existing_props.keys():
                if prop_name in possible_names:
                    prop_type = existing_props[prop_name]["type"]
                    
                    if our_key == "week" and prop_type == "number":
                        page["properties"][prop_name] = {"number": w.week}
                    elif our_key == "month" and prop_type in ["select", "number"]:
                        if prop_type == "select":
                            page["properties"][prop_name] = {"select": {"name": str(w.month)}}
                        else:
                            page["properties"][prop_name] = {"number": w.month}
                    elif our_key == "topic" and prop_type == "title":
                        page["properties"][prop_name] = {"title": [{"type": "text", "text": {"content": w.topic}}]}
                    elif our_key == "details" and prop_type == "rich_text":
                        page["properties"][prop_name] = {"rich_text": [{"type": "text", "text": {"content": w.details or ""}}]}
                    elif our_key == "project" and prop_type == "rich_text":
                        page["properties"][prop_name] = {"rich_text": [{"type": "text", "text": {"content": w.project}}]}
                    elif our_key == "status" and prop_type == "select":
                        page["properties"][prop_name] = {"select": {"name": "To Do"}}
                    elif our_key == "priority" and prop_type == "select":
                        page["properties"][prop_name] = {"select": {"name": priority}}
                    elif our_key == "github" and prop_type == "url":
                        # We'll leave this empty for now since we don't have the repo URLs in this context
                        pass
                    elif our_key == "dataset" and prop_type == "url":
                        if w.dataset_url:
                            page["properties"][prop_name] = {"url": w.dataset_url}
                    break
        
        # Create the page
        response = requests.post(url, headers=notion_headers(), json=page)
        if response.status_code == 200:
            success_count += 1
            print(f"   ✅ Added Week {w.week}")
        else:
            print(f"   ❌ Failed Week {w.week}: {response.status_code} - {response.text}")
    
    print(f"\n✅ Successfully added {success_count}/{len(weeks)} weeks to database!")
    return success_count > 0

def main():
    """Main function to scan and analyze Notion databases."""
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not found. Please set it in your .env file.")
        return
    
    print("🔍 Scanning for Notion databases...")
    databases = search_databases()
    
    if not databases:
        print("❌ No databases found or search failed.")
        return
    
    print(f"📊 Found {len(databases)} databases. Analyzing...")
    
    roadmap_databases = []
    
    for db in databases:
        print(f"\n📋 Analyzing: {db['id']}")
        analysis = analyze_database(db)
        
        print(f"   Title: '{analysis['title']}'")
        print(f"   Properties: {', '.join(analysis['properties'])}")
        print(f"   Pages: {analysis['page_count']}")
        print(f"   Created: {analysis['created_time'][:10]}")
        
        if analysis["sample_content"]:
            print("   Sample content:")
            for i, content in enumerate(analysis["sample_content"][:2]):
                print(f"     Row {i+1}: {dict(list(content.items())[:3])}")
        
        if is_roadmap_database(analysis):
            roadmap_databases.append(analysis)
            print("   🎯 This looks like a roadmap database!")
    
    if not roadmap_databases:
        print("\n❌ No roadmap databases found.")
        return
    
    print(f"\n🎯 Found {len(roadmap_databases)} potential roadmap database(s):")
    
    for i, db in enumerate(roadmap_databases):
        print(f"\n{i+1}. {db['title']} (ID: {db['id']})")
        print(f"   Properties: {', '.join(db['properties'])}")
        print(f"   Last edited: {db['last_edited_time'][:10]}")
        print(f"   Pages: {db['page_count']}")
    
    # Ask user which database to update
    if len(roadmap_databases) == 1:
        choice = input(f"\n❓ Update this database with enhanced content? (y/N): ").lower().strip()
        if choice == 'y':
            update_database_with_enhanced_content(roadmap_databases[0]['id'])
    else:
        choice = input(f"\n❓ Which database would you like to update? (1-{len(roadmap_databases)}, or 0 to skip): ")
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(roadmap_databases):
                selected_db = roadmap_databases[choice_num - 1]
                print(f"\n🎯 Selected: {selected_db['title']}")
                update_database_with_enhanced_content(selected_db['id'])
            elif choice_num == 0:
                print("👋 Skipping update.")
            else:
                print("❌ Invalid choice.")
        except ValueError:
            print("❌ Invalid input.")

if __name__ == "__main__":
    main()