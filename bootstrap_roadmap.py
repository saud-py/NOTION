#!/usr/bin/env python3
"""
All-in-One bootstrapper to programmatically set up:
1) A Notion Database with 24 weekly tasks covering a 6‑month Cloud Data Engineer/DataOps roadmap
2) 6 GitHub repositories scaffolded with starter files, READMEs, and folder structures for each project

Optional (toggleable):
- Create local folders mirroring each repo structure
- Create an AWS budget (to keep free-tier costs under control)

USAGE (one-time):
1) Install dependencies:
   pip install requests python-dotenv boto3

2) Export the required environment variables (or place them in a .env file):
   NOTION_TOKEN=<your_notion_internal_integration_token>
   NOTION_PARENT_PAGE_ID=<the Notion page_id under which to create the database>
   GITHUB_TOKEN=<a GitHub personal access token with repo scope>
   GITHUB_USERNAME=<your github username>
   
   Optional (for AWS budget feature):
   AWS_REGION=<e.g. us-east-1>
   AWS_BUDGET_EMAIL=<your-email@example.com>

3) Run the script:
   python bootstrap_roadmap.py

4) Output:
   - Notion: A database titled "6‑Month Data Engineering Career Plan" with 24 rows (weeks)
   - GitHub: Six repos created (private by default) with starter structure & README

Notes:
- This script uses only official REST APIs (Notion & GitHub). No 3rd-party SDKs for Notion are required.
- You can re-run safely; exists checks avoid duplication (idempotent-ish). Delete resources manually if you need a clean slate.
"""

from __future__ import annotations
import base64
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Import our updated models
from models import WeekItem, RoadmapData

# -----------------------------
# Environment & Constants
# -----------------------------
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
AWS_REGION = os.getenv("AWS_REGION") or "us-east-1"
AWS_BUDGET_EMAIL = os.getenv("AWS_BUDGET_EMAIL")

NOTION_VERSION = "2022-06-28"  # stable
NOTION_BASE = "https://api.notion.com/v1"
GITHUB_API = "https://api.github.com"

# Toggles
CREATE_LOCAL_FOLDERS = True
CREATE_AWS_BUDGET = False  # set True if you provided AWS creds + email
REPOS_PRIVATE = True

# Safety checks
if not NOTION_TOKEN or not NOTION_PARENT_PAGE_ID:
    print("[!] Missing NOTION env vars. Please set NOTION_TOKEN and NOTION_PARENT_PAGE_ID.")

if not GITHUB_TOKEN or not GITHUB_USERNAME:
    print("[!] Missing GitHub env vars. Please set GITHUB_TOKEN and GITHUB_USERNAME.")

# Use the updated models from models.py
def build_weeks() -> List[WeekItem]:
    """Build the 24-week roadmap data structure using the updated models."""
    return RoadmapData.build_weeks()

# -----------------------------
# Notion helpers
# -----------------------------
def notion_headers() -> Dict[str, str]:
    """Return headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def ensure_notion_database(title: str = "6‑Month Data Engineering Career Plan") -> Optional[str]:
    """Create a Notion database with the roadmap structure."""
    if not NOTION_TOKEN or not NOTION_PARENT_PAGE_ID:
        print("[Notion] Skipping (missing env vars)")
        return None
    
    # Create database under a parent page
    url = f"{NOTION_BASE}/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": NOTION_PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": {
            "Week": {"number": {}},
            "Month": {"select": {"options": [
                {"name": "1"}, {"name": "2"}, {"name": "3"}, 
                {"name": "4"}, {"name": "5"}, {"name": "6"}
            ]}},
            "Learning Topic": {"title": {}},
            "Details": {"rich_text": {}},
            "Project Phase": {"rich_text": {}},
            "Status": {"select": {"options": [
                {"name": "To Do", "color": "red"},
                {"name": "In Progress", "color": "yellow"},
                {"name": "Done", "color": "green"}
            ]}},
            "Priority": {"select": {"options": [
                {"name": "High", "color": "red"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "gray"}
            ]}},
            "GitHub": {"url": {}},
            "Dataset": {"url": {}},
        }
    }
    
    # Notion has no simple "find by title" for databases; we attempt create and fall back on conflict messages
    resp = requests.post(url, headers=notion_headers(), data=json.dumps(payload))
    if resp.status_code == 200:
        db_id = resp.json()["id"]
        print(f"[Notion] Database created: {db_id}")
        return db_id
    else:
        # If you accidentally try to create duplicate, you may get 400/409. We'll print details.
        print(f"[Notion] Create DB response: {resp.status_code} {resp.text}")
        return None

def add_weeks_to_notion(db_id: str, weeks: List[WeekItem], repo_urls: Dict[str, str]):
    """Add all 24 weeks as pages in the Notion database."""
    if not db_id:
        return
    
    url = f"{NOTION_BASE}/pages"
    headers = notion_headers()
    
    for w in weeks:
        github_url = repo_urls.get(w.repo_hint or "", "")
        
        # Determine priority based on month
        priority = "High" if w.month <= 2 else "Medium" if w.month <= 4 else "Low"
        
        page = {
            "parent": {"database_id": db_id},
            "properties": {
                "Week": {"number": w.week},
                "Month": {"select": {"name": str(w.month)}},
                "Learning Topic": {"title": [{"type": "text", "text": {"content": w.topic}}]},
                "Details": {"rich_text": [{"type": "text", "text": {"content": w.details or ""}}]},
                "Project Phase": {"rich_text": [{"type": "text", "text": {"content": w.project}}]},

                "Status": {"select": {"name": "To Do"}},
                "Priority": {"select": {"name": priority}},
                "GitHub": {"url": github_url or None},
                "Dataset": {"url": w.dataset_url or None},
            }
        }
        
        r = requests.post(url, headers=headers, data=json.dumps(page))
        if r.status_code != 200:
            print(f"[Notion] Failed to add Week {w.week}: {r.status_code} {r.text}")
        else:
            print(f"[Notion] Added Week {w.week}")
        time.sleep(0.2)

# -----------------------------
# GitHub helpers
# -----------------------------
PROJECTS = [
    ("retail-sales-etl", "Retail Sales ETL (CSV→S3→Glue→Athena)"),
    ("sales-data-warehouse", "Sales Data Warehouse on Redshift + QuickSight"),
    ("covid-dataops-pipeline", "COVID Data Lake with Airflow + CodePipeline"),
    ("log-analytics-spark", "Log Analytics with PySpark on EMR/Databricks"),
    ("clickstream-realtime-analytics", "Real-Time Clickstream Analytics (Kinesis→Spark→Redshift)"),
    ("ecommerce-data-platform", "Capstone: End-to-End E-commerce Data Platform (Batch + Streaming)"),
]

REPO_SCAFFOLDS: Dict[str, List[str]] = {
    "retail-sales-etl": [
        "data_samples/.gitkeep",
        "glue_jobs/transform_sales.py",
        "notebooks/exploration.ipynb",
        "scripts/data_ingestion.py",
        "architecture/diagram.png",
    ],
    "sales-data-warehouse": [
        "schema/star_schema.sql",
        "etl_scripts/load_to_redshift.sql",
        "dashboards/sales_dashboard.png",
    ],
    "covid-dataops-pipeline": [
        "dags/covid_pipeline_dag.py",
        "glue_jobs/covid_transform.py",
        "ci-cd/buildspec.yml",
        "architecture/diagram.png",
    ],
    "log-analytics-spark": [
        "spark_jobs/parse_logs.py",
        "notebooks/log_analysis.ipynb",
        "architecture/diagram.png",
    ],
    "clickstream-realtime-analytics": [
        "event_producer/generate_events.py",
        "lambda/process_stream.py",
        "spark_jobs/streaming_agg.py",
        "dashboards/realtime_dashboard.png",
        "architecture/diagram.png",
    ],
    "ecommerce-data-platform": [
        "dags/README.md",
        "glue_jobs/README.md",
        "spark_jobs/README.md",
        "lambda/README.md",
        "dashboards/overview.png",
        "architecture/diagram.png",
    ],
}

README_TEMPLATES: Dict[str, str] = {
    "retail-sales-etl": """# Retail Sales ETL (CSV → S3 → Glue → Athena)

**Goal**: Build an end-to-end batch ETL using the Superstore dataset.

## Stack
- AWS S3 (data lake)
- AWS Glue (PySpark) for transforms
- AWS Athena for querying
- Python (Pandas, boto3)

## Steps
1. Upload raw CSV to `s3://<bucket>/raw/`
2. Glue job `transform_sales.py` writes to `processed/`
3. Query in Athena (external table on processed)

## Dataset
- Superstore Sales: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

## Diagram
See `architecture/diagram.png`.
""",
    "sales-data-warehouse": """# Sales Data Warehouse (Redshift + QuickSight)

**Goal**: Design a star schema, load from S3 into Redshift, and build BI dashboards.

## Stack
- Amazon Redshift (warehouse)
- S3 as stage + COPY
- QuickSight (BI)

## Deliverables
- `schema/star_schema.sql`
- `etl_scripts/load_to_redshift.sql`
- Dashboard screenshot(s) in `dashboards/`
""",
    "covid-dataops-pipeline": """# COVID Data Lake (Airflow + CI/CD)

**Goal**: Automated daily ingestion → S3 → Glue → Redshift with CI/CD and monitoring.

## Stack
- Apache Airflow (DAGs)
- AWS Glue (transforms)
- Redshift (load)
- Bitbucket + CodePipeline (CI/CD)
- CloudWatch (alerts)

## Files
- `dags/covid_pipeline_dag.py`
- `glue_jobs/covid_transform.py`
- `ci-cd/buildspec.yml`
""",
    "log-analytics-spark": """# Log Analytics with PySpark (EMR/Databricks)

**Goal**: Parse NASA HTTP logs, compute KPIs, store results to S3, and query with Athena.

## Stack
- PySpark (DataFrames)
- EMR or Databricks Community Edition
- S3 + Athena

## Files
- `spark_jobs/parse_logs.py`
- `notebooks/log_analysis.ipynb`
""",
    "clickstream-realtime-analytics": """# Real-Time Clickstream Analytics (Kinesis → Spark → Redshift)

**Goal**: Stream synthetic click events, process with Spark Structured Streaming, and visualize in QuickSight.

## Stack
- Kinesis Data Streams
- AWS Lambda (ingest → S3)
- Spark Structured Streaming
- Redshift + QuickSight

## Files
- `event_producer/generate_events.py`
- `lambda/process_stream.py`
- `spark_jobs/streaming_agg.py`
""",
    "ecommerce-data-platform": """# Capstone: E-commerce Data Platform (Batch + Streaming)

**Goal**: Combine batch ETL and streaming analytics into a single platform with orchestration and BI.

## Modules
- `dags/` (Airflow)
- `glue_jobs/` (ETL)
- `spark_jobs/` (Spark)
- `lambda/` (serverless)
- `dashboards/` (BI)
- `architecture/diagram.png`
""",
}

STARTER_FILE_CONTENT: Dict[str, str] = {
    # Minimal starter code snippets
    "glue_jobs/transform_sales.py": """# PySpark Glue job skeleton
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# TODO: add transforms
""",
    "scripts/data_ingestion.py": """# Upload files to S3 using boto3
# python scripts/data_ingestion.py --bucket <name> --path data_samples/
""",
    "dags/covid_pipeline_dag.py": """# Airflow DAG skeleton
from airflow import DAG
from datetime import datetime
# TODO: define tasks/operators
""",
    "glue_jobs/covid_transform.py": """# Glue transform for COVID data
""",
    "ci-cd/buildspec.yml": """version: 0.2
phases:
  build:
    commands:
      - echo Deploy DAGs / Glue jobs
""",
    "spark_jobs/parse_logs.py": """# PySpark job to parse logs
from pyspark.sql import SparkSession
# TODO: parse NASA logs
""",
    "event_producer/generate_events.py": """# Synthetic clickstream generator
# TODO: implement event generation to Kinesis
""",
    "lambda/process_stream.py": """# AWS Lambda handler for Kinesis records
# TODO: implement processing
""",
    "spark_jobs/streaming_agg.py": """# Spark Structured Streaming aggregation
# TODO: implement streaming aggregations
""",
}

def gh_headers() -> Dict[str, str]:
    """Return headers for GitHub API requests."""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

def github_repo_exists(name: str) -> bool:
    """Check if a GitHub repository already exists."""
    url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{name}"
    r = requests.get(url, headers=gh_headers())
    return r.status_code == 200

def create_github_repo(name: str, description: str) -> str:
    """Create a new GitHub repository."""
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print("[GitHub] Skipping (missing env vars)")
        return ""
    
    if github_repo_exists(name):
        print(f"[GitHub] Repo exists: {name}")
        return f"https://github.com/{GITHUB_USERNAME}/{name}"
    
    url = f"{GITHUB_API}/user/repos"
    payload = {
        "name": name,
        "description": description,
        "private": REPOS_PRIVATE,
        "auto_init": True,
    }
    
    r = requests.post(url, headers=gh_headers(), data=json.dumps(payload))
    if r.status_code not in (201, 202):
        print(f"[GitHub] Failed to create repo {name}: {r.status_code} {r.text}")
        return ""
    
    print(f"[GitHub] Created repo {name}")
    return f"https://github.com/{GITHUB_USERNAME}/{name}"

def put_github_file(repo: str, path: str, content: str, message: str = "add file") -> bool:
    """Add a file to a GitHub repository."""
    url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    
    r = requests.put(url, headers=gh_headers(), data=json.dumps(data))
    if r.status_code not in (201, 200):
        print(f"[GitHub] Failed to create {repo}:{path}: {r.status_code} {r.text}")
        return False
    return True

def scaffold_repo(name: str):
    """Create the folder structure and starter files for a repository."""
    # README
    readme = README_TEMPLATES.get(name, f"# {name}\n")
    put_github_file(name, "README.md", readme, message="chore: add README")
    
    # Files/folders
    for rel in REPO_SCAFFOLDS.get(name, []):
        # If endswith .png/.ipynb placeholder binary vs text; we push empty placeholder for binary
        if rel.endswith(".png"):
            content = ""  # empty placeholder (GitHub will store an empty file)
        else:
            content = STARTER_FILE_CONTENT.get(rel, "# TODO\n")
        put_github_file(name, rel, content, message=f"chore: scaffold {rel}")
        time.sleep(0.2)

def ensure_github_repos() -> Dict[str, str]:
    """Create all GitHub repositories and return their URLs."""
    repo_urls: Dict[str, str] = {}
    for repo, desc in PROJECTS:
        url = create_github_repo(repo, desc)
        if url:
            repo_urls[repo] = url
            scaffold_repo(repo)
    return repo_urls

# -----------------------------
# Local folder mirror (optional)
# -----------------------------
def create_local_scaffold(repo: str):
    """Create local project folder structure."""
    root = os.path.join(os.getcwd(), repo)
    os.makedirs(root, exist_ok=True)
    
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_TEMPLATES.get(repo, f"# {repo}\n"))
    
    for rel in REPO_SCAFFOLDS.get(repo, []):
        full = os.path.join(root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        mode = "wb" if rel.endswith(".png") else "w"
        with open(full, mode) as f:
            if mode == "w":
                f.write(STARTER_FILE_CONTENT.get(rel, "# TODO\n"))
            else:
                f.write(b"")

def ensure_local_scaffolds():
    """Create local project folders if enabled."""
    if not CREATE_LOCAL_FOLDERS:
        return
    for repo, _ in PROJECTS:
        create_local_scaffold(repo)
    print("[Local] Created local project folders.")

# -----------------------------
# AWS Budget (optional)
# -----------------------------
def create_aws_budget():
    """Create an AWS budget for cost control."""
    if not CREATE_AWS_BUDGET:
        return
    
    try:
        import boto3
        client = boto3.client("budgets", region_name=AWS_REGION)
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        
        budget_name = "LearningBudget-$5"
        budget = {
            "BudgetName": budget_name,
            "BudgetLimit": {"Amount": "5", "Unit": "USD"},
            "TimeUnit": "MONTHLY",
            "BudgetType": "COST",
        }
        
        notifications_with_subscribers = []
        if AWS_BUDGET_EMAIL:
            notifications_with_subscribers.append({
                "Notification": {
                    "NotificationType": "ACTUAL",
                    "ComparisonOperator": "GREATER_THAN",
                    "Threshold": 80.0,
                    "ThresholdType": "PERCENTAGE"
                },
                "Subscribers": [{"SubscriptionType": "EMAIL", "Address": AWS_BUDGET_EMAIL}]
            })
        
        client.create_budget(
            AccountId=account_id,
            Budget=budget,
            NotificationsWithSubscribers=notifications_with_subscribers,
        )
        print(f"[AWS] Created budget '{budget_name}' for $5/month with email alerts.")
    except Exception as e:
        print(f"[AWS] Skipping budget creation ({e})")

# -----------------------------
# Main Orchestration
# -----------------------------
def main():
    """Main function to orchestrate the entire setup process."""
    print("🚀 Starting Data Engineering Roadmap Bootstrap...")
    
    # 1) GitHub repos
    print("\n📁 Creating GitHub repositories...")
    repo_urls = ensure_github_repos()
    
    # 2) Notion database + rows
    print("\n📊 Setting up Notion database...")
    db_id = ensure_notion_database()
    weeks = build_weeks()
    add_weeks_to_notion(db_id, weeks, repo_urls)
    
    # 3) Local mirrors (optional)
    print("\n💻 Creating local project folders...")
    ensure_local_scaffolds()
    
    # 4) AWS Budget (optional)
    print("\n💰 Setting up AWS budget...")
    create_aws_budget()
    
    print("\n✅ Done! Summary:")
    print("GitHub repos:")
    for k, v in repo_urls.items():
        print(f"  - {k}: {v}")
    
    if db_id:
        print(f"Notion Database ID: {db_id}")
    else:
        print("Notion: database not created (check logs)")
    
    print("\n🎯 Next steps:")
    print("1. Check your Notion database for the 24-week roadmap")
    print("2. Clone the GitHub repos locally to start coding")
    print("3. Set up your AWS account for the projects")
    print("4. Start with Week 1 - SQL basics!")

if __name__ == "__main__":
    main()