<<<<<<< HEAD
# 6-Month Data Engineering Career Roadmap Bootstrapper

This script automatically sets up a comprehensive 6-month data engineering learning plan by creating:

1. **Notion Database**: 24 weekly tasks covering Cloud Data Engineer/DataOps roadmap
2. **GitHub Repositories**: 6 scaffolded repos with starter files and folder structures
3. **Local Project Structure** (optional): Mirror repos locally
4. **AWS Budget** (optional): $5/month budget with email alerts

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `NOTION_TOKEN`: Your Notion integration token
- `NOTION_PARENT_PAGE_ID`: Page ID where database will be created
- `GITHUB_TOKEN`: GitHub personal access token with repo scope
- `GITHUB_USERNAME`: Your GitHub username

Optional (for AWS budget):
- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_BUDGET_EMAIL`: Email for budget alerts

### 3. Run the Script
```bash
python bootstrap_roadmap.py
```

## What Gets Created

### Notion Database: "6‑Month Data Engineering Career Plan"
24 weekly tasks organized by month:

**Month 1 - ETL Foundations**
- SQL basics + practice (50 problems)
- Python Pandas + boto3, upload to S3
- Glue basics + Athena querying
- Build ETL v1 end-to-end

**Month 2 - Data Modeling + Warehousing**
- Design star schema (fact/dims)
- Load to Redshift via COPY
- Complex SQL (windows, perf)
- QuickSight dashboard

**Month 3 - DataOps (Automation + CI/CD)**
- Airflow DAG: pull daily COVID data → S3
- Add Glue transform + Redshift load
- CI/CD (Bitbucket + CodePipeline)
- Monitoring with CloudWatch alerts

**Month 4 - Big Data with Spark**
- PySpark basics (DataFrames/RDDs)
- Run job on EMR/Databricks
- Aggregations: top URLs, errors, traffic/hour
- Store to S3 + query in Athena (compare perf)

**Month 5 - Streaming Data Pipeline**
- Kinesis basics + event producer
- Lambda → S3 (raw events)
- Spark Structured Streaming aggregations
- QuickSight live dashboard

**Month 6 - Capstone & Resume**
- Define architecture (batch + streaming)
- Build batch ETL (S3→Glue→Redshift) + DAG
- Add streaming (Kinesis→Spark→Redshift)
- Docs + Repo polish + Resume bullets

### GitHub Repositories Created

1. **retail-sales-etl** - Retail Sales ETL (CSV→S3→Glue→Athena)
2. **sales-data-warehouse** - Sales Data Warehouse on Redshift + QuickSight
3. **covid-dataops-pipeline** - COVID Data Lake with Airflow + CodePipeline
4. **log-analytics-spark** - Log Analytics with PySpark on EMR/Databricks
5. **clickstream-realtime-analytics** - Real-Time Clickstream Analytics
6. **ecommerce-data-platform** - Capstone: End-to-End E-commerce Data Platform

Each repo includes:
- Comprehensive README with project goals and tech stack
- Scaffolded folder structure
- Starter code files with TODO comments
- Architecture diagram placeholders

## Configuration Options

Edit the toggles in `bootstrap_roadmap.py`:

```python
CREATE_LOCAL_FOLDERS = True    # Create local project folders
CREATE_AWS_BUDGET = False      # Create AWS budget (requires AWS creds)
REPOS_PRIVATE = True           # Make GitHub repos private
```

## Getting Your Tokens

### Notion Integration Token
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create new integration
3. Copy the "Internal Integration Token"
4. Share your target page with the integration

### GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy the token (starts with `ghp_`)

### Notion Page ID
1. Open your target Notion page
2. Copy the page ID from URL: `notion.so/workspace/PAGE_ID_HERE?v=...`

## Safety Features

- **Idempotent**: Safe to re-run; checks for existing resources
- **Error Handling**: Graceful failures with detailed error messages
- **Rate Limiting**: Built-in delays to respect API limits
- **Validation**: Checks for required environment variables

## Troubleshooting

**Notion Database Creation Failed**
- Verify your integration token and page ID
- Ensure the integration has access to the parent page
- Check that the parent page exists and is accessible

**GitHub Repo Creation Failed**
- Verify your GitHub token has `repo` scope
- Check that the username is correct
- Ensure you haven't hit GitHub's rate limits

**Missing Dependencies**
```bash
pip install requests python-dotenv boto3
```

## Next Steps

After running the script:

1. **Check Notion**: Review your new database and start tracking progress
2. **Clone Repos**: Clone the GitHub repos locally to start coding
3. **Set Up AWS**: Configure your AWS account for the projects
4. **Start Learning**: Begin with Week 1 - SQL basics!

The roadmap is designed to take you from beginner to job-ready in 6 months with hands-on projects that demonstrate real-world data engineering skills.
=======
# NOTION
>>>>>>> 990979740dd9e7ce291df77daaf1094a52b37dc7
