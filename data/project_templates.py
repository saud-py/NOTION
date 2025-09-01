"""Project templates and content for repository scaffolding."""

from typing import Dict, List, Tuple


class ProjectTemplates:
    """Class containing all project templates and content."""
    
    def __init__(self):
        self._projects = [
            ("retail-sales-etl", "Retail Sales ETL (CSV→S3→Glue→Athena)"),
            ("sales-data-warehouse", "Sales Data Warehouse on Redshift + QuickSight"),
            ("covid-dataops-pipeline", "COVID Data Lake with Airflow + CodePipeline"),
            ("log-analytics-spark", "Log Analytics with PySpark on EMR/Databricks"),
            ("clickstream-realtime-analytics", "Real-Time Clickstream Analytics (Kinesis→Spark→Redshift)"),
            ("ecommerce-data-platform", "Capstone: End-to-End E-commerce Data Platform (Batch + Streaming)"),
        ]
        
        self._repo_scaffolds = {
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
        
        self._readme_templates = {
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
        
        self._starter_content = {
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
    
    def get_projects(self) -> List[Tuple[str, str]]:
        """Get list of all projects."""
        return self._projects
    
    def get_scaffold_files(self, repo_name: str) -> List[str]:
        """Get scaffold files for a specific repository."""
        return self._repo_scaffolds.get(repo_name, [])
    
    def get_readme(self, repo_name: str) -> str:
        """Get README template for a specific repository."""
        return self._readme_templates.get(repo_name, f"# {repo_name}\n")
    
    def get_starter_content(self, file_path: str) -> str:
        """Get starter content for a specific file."""
        return self._starter_content.get(file_path, "# TODO\n")