#!/usr/bin/env python3
"""
Quick fix script to help set up Notion integration properly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔧 Notion Integration Setup Helper")
    print("=" * 40)
    
    notion_token = os.getenv("NOTION_TOKEN")
    page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    
    print(f"Current NOTION_TOKEN: {notion_token[:20]}..." if notion_token else "❌ NOTION_TOKEN not set")
    print(f"Current PAGE_ID: {page_id}" if page_id else "❌ NOTION_PARENT_PAGE_ID not set")
    
    print("\n🎯 To fix the Notion 404 error:")
    print("1. Go to your Notion page in the browser")
    print("2. Click 'Share' in the top right")
    print("3. Click 'Invite' and search for your integration name")
    print("4. Give it 'Can edit' permissions")
    print("5. Make sure the page ID in .env matches the URL")
    
    print("\n📋 Page ID Format:")
    print("From URL: https://notion.so/workspace/2600693c0443805e8f17cf79815091fe")
    print("Use: 2600693c0443805e8f17cf79815091fe (without dashes)")
    print("Or: 2600693c-0443-805e-8f17-cf79815091fe (with dashes - both work)")
    
    print("\n🔗 Helpful Links:")
    print("• Create Integration: https://www.notion.so/my-integrations")
    print("• API Documentation: https://developers.notion.com/docs/getting-started")
    
    # Test the current setup
    if notion_token and page_id:
        print("\n🧪 Testing current setup...")
        try:
            import requests
            import json
            
            headers = {
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }
            
            # Try to get the page
            url = f"https://api.notion.com/v1/pages/{page_id}"
            resp = requests.get(url, headers=headers)
            
            if resp.status_code == 200:
                print("✅ Page access successful!")
                page_data = resp.json()
                print(f"   Page title: {page_data.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')}")
            elif resp.status_code == 404:
                print("❌ Page not found or integration not shared")
                print("   Make sure to share the page with your integration!")
            else:
                print(f"❌ API Error: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n🚀 After fixing, run: python3 main.py")

if __name__ == "__main__":
    main()