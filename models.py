"""Data models for the roadmap structure."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WeekItem:
    """Represents a single week in the learning roadmap."""
    week: int
    month: int
    topic: str
    project: str
    dataset_url: Optional[str]
    repo_hint: Optional[str]
    due_label: str
    details: Optional[str] = None


class RoadmapData:
    """Factory class for creating the 24-week roadmap structure."""
    
    @staticmethod
    def build_weeks() -> List[WeekItem]:
        """Build the complete 24-week roadmap data structure."""
        weeks: List[WeekItem] = []
        
        # Month 1 – ETL Foundations
        weeks.extend(RoadmapData._month_1_etl_foundations())
        
        # Month 2 – Data Modeling + Warehousing
        weeks.extend(RoadmapData._month_2_data_warehousing())
        
        # Month 3 – DataOps
        weeks.extend(RoadmapData._month_3_dataops())
        
        # Month 4 – Big Data with Spark
        weeks.extend(RoadmapData._month_4_spark())
        
        # Month 5 – Streaming Data Pipeline
        weeks.extend(RoadmapData._month_5_streaming())
        
        # Month 6 – Capstone & Resume
        weeks.extend(RoadmapData._month_6_capstone())
        
        return weeks
    
    @staticmethod
    def _month_1_etl_foundations() -> List[WeekItem]:
        """Month 1: SQL, ETL Basics, and AWS Fundamentals - Get comfortable with SQL, data cleaning, and AWS basics."""
        superstore_url = "https://www.kaggle.com/datasets/vivek468/superstore-dataset-final"
        return [
            WeekItem(1, 1, "SQL basics + practice (50 problems)", 
                    "Month 1: SQL, ETL Basics & AWS Fundamentals", superstore_url, "retail-sales-etl", "Week 1",
                    "• Learn SELECT, WHERE, GROUP BY, JOINs, aggregate functions\n• Resources: LeetCode Database problems, SQLZoo, Mode Analytics SQL tutorials\n• Deliverable: Solve 50 SQL problems"),
            WeekItem(2, 1, "Python Pandas + boto3, Upload to S3", 
                    "Month 1: SQL, ETL Basics & AWS Fundamentals", superstore_url, "retail-sales-etl", "Week 2",
                    "• Learn dataframes, cleaning, joins in Pandas\n• Learn boto3 basics (upload, download, list S3 objects)\n• Deliverable: Python script to clean CSV data and upload to S3 bucket"),
            WeekItem(3, 1, "Glue basics + Athena querying", 
                    "Month 1: SQL, ETL Basics & AWS Fundamentals", superstore_url, "retail-sales-etl", "Week 3",
                    "• Learn AWS Glue (crawlers, jobs)\n• Learn Athena (querying S3 data with SQL)\n• Deliverable: Create a Glue crawler + query S3 dataset with Athena"),
            WeekItem(4, 1, "Build ETL end-to-end", 
                    "Month 1: SQL, ETL Basics & AWS Fundamentals", superstore_url, "retail-sales-etl", "Week 4",
                    "• Combine S3 + Glue + Athena\n• Deliverable: Ingest CSV → S3 → Glue → Athena query"),
        ]
    
    @staticmethod
    def _month_2_data_warehousing() -> List[WeekItem]:
        """Month 2: Data Warehousing - Learn how to model data and use Redshift."""
        superstore_url = "https://www.kaggle.com/datasets/vivek468/superstore-dataset-final"
        return [
            WeekItem(5, 2, "Design star schema (fact/dims)", 
                    "Month 2: Data Warehousing", superstore_url, "sales-data-warehouse", "Week 5",
                    "• Learn dimensional modeling (Kimball's approach)\n• Deliverable: Create ERD for Sales dataset (fact_sales, dim_customer, dim_product)"),
            WeekItem(6, 2, "Load to Redshift with COPY", 
                    "Month 2: Data Warehousing", superstore_url, "sales-data-warehouse", "Week 6",
                    "• Learn Redshift basics + COPY command from S3\n• Deliverable: Load Sales data into Redshift fact/dim tables"),
            WeekItem(7, 2, "Complex SQL (window functions, CTEs, performance tuning)", 
                    "Month 2: Data Warehousing", superstore_url, "sales-data-warehouse", "Week 7",
                    "• Learn ROW_NUMBER, RANK, LEAD/LAG, recursive queries\n• Deliverable: Write 10 analytical queries"),
            WeekItem(8, 2, "QuickSight dashboard", 
                    "Month 2: Data Warehousing", superstore_url, "sales-data-warehouse", "Week 8",
                    "• Learn Amazon QuickSight basics\n• Deliverable: Build sales performance dashboard"),
        ]
    
    @staticmethod
    def _month_3_dataops() -> List[WeekItem]:
        """Month 3: Data Pipelines & Automation - Automate data pipelines with Airflow + CI/CD."""
        covid_url = "https://github.com/CSSEGISandData/COVID-19"
        return [
            WeekItem(9, 3, "Airflow DAG (daily COVID data → S3)", 
                    "Month 3: Data Pipelines & Automation", covid_url, "covid-dataops-pipeline", "Week 9",
                    "• Learn Airflow basics (DAGs, operators, scheduling)\n• Deliverable: DAG that fetches daily COVID API → stores in S3"),
            WeekItem(10, 3, "Add Glue transform + Redshift load", 
                    "Month 3: Data Pipelines & Automation", covid_url, "covid-dataops-pipeline", "Week 10",
                    "• Extend DAG: ingest → transform with Glue → load into Redshift\n• Deliverable: Complete ETL pipeline with monitoring"),
            WeekItem(11, 3, "CI/CD (Bitbucket + CodePipeline)", 
                    "Month 3: Data Pipelines & Automation", covid_url, "covid-dataops-pipeline", "Week 11",
                    "• Learn version control for Airflow DAGs\n• Deliverable: Set up Git → CodePipeline for Airflow project"),
            WeekItem(12, 3, "Monitoring with CloudWatch alerts", 
                    "Month 3: Data Pipelines & Automation", covid_url, "covid-dataops-pipeline", "Week 12",
                    "• Set up CloudWatch metrics for S3/Glue/Redshift\n• Deliverable: Trigger alert when job fails"),
        ]
    
    @staticmethod
    def _month_4_spark() -> List[WeekItem]:
        """Month 4: Big Data Processing - Work with Spark + EMR."""
        nasa_logs_url = "https://www.kaggle.com/datasets/loganalyst/nasa-access-log"
        return [
            WeekItem(13, 4, "PySpark basics (DataFrames/RDDs)", 
                    "Month 4: Big Data Processing", nasa_logs_url, "log-analytics-spark", "Week 13",
                    "• Learn Spark DataFrame ops, transformations, actions\n• Deliverable: Clean & aggregate logs dataset with PySpark"),
            WeekItem(14, 4, "Run job on EMR/Databricks", 
                    "Month 4: Big Data Processing", nasa_logs_url, "log-analytics-spark", "Week 14",
                    "• Learn how to run PySpark jobs on EMR\n• Deliverable: Submit PySpark job to EMR"),
            WeekItem(15, 4, "Aggregations: top URLs, errors, traffic/hour", 
                    "Month 4: Big Data Processing", nasa_logs_url, "log-analytics-spark", "Week 15",
                    "• Advanced Spark analytics\n• Deliverable: Spark job that produces log analytics summary"),
            WeekItem(16, 4, "Store to S3 + query in Athena (compare performance)", 
                    "Month 4: Big Data Processing", nasa_logs_url, "log-analytics-spark", "Week 16",
                    "• Performance optimization techniques\n• Deliverable: Output aggregated logs to S3, query with Athena"),
        ]
    
    @staticmethod
    def _month_5_streaming() -> List[WeekItem]:
        """Month 5: Real-Time Streaming - Learn real-time analytics with Kinesis + Lambda + Spark."""
        return [
            WeekItem(17, 5, "Kinesis basics + event producer", 
                    "Month 5: Real-Time Streaming", None, "clickstream-realtime-analytics", "Week 17",
                    "• Learn Kinesis Data Streams fundamentals\n• Deliverable: Push dummy event data into Kinesis stream"),
            WeekItem(18, 5, "Lambda → S3 (raw events)", 
                    "Month 5: Real-Time Streaming", None, "clickstream-realtime-analytics", "Week 18",
                    "• Build serverless data ingestion\n• Deliverable: Lambda function that consumes Kinesis → stores to S3"),
            WeekItem(19, 5, "Spark Structured Streaming aggregations", 
                    "Month 5: Real-Time Streaming", None, "clickstream-realtime-analytics", "Week 19",
                    "• Real-time data processing with Spark\n• Deliverable: Real-time aggregation of streaming events"),
            WeekItem(20, 5, "QuickSight live dashboard", 
                    "Month 5: Real-Time Streaming", None, "clickstream-realtime-analytics", "Week 20",
                    "• Real-time visualization and monitoring\n• Deliverable: Real-time dashboard on clickstream data"),
        ]
    
    @staticmethod
    def _month_6_capstone() -> List[WeekItem]:
        """Month 6: Capstone Projects - Build end-to-end production projects."""
        return [
            WeekItem(21, 6, "E-commerce Data Platform: Define architecture (batch + streaming)", 
                    "Month 6: Capstone Projects", None, "ecommerce-data-platform", "Week 21",
                    "• Design complete data platform architecture\n• Architecture: Batch ETL (Glue → Redshift + Airflow DAG)\n• Streaming (Kinesis → Lambda → S3 + Spark Streaming)\n• Reporting (QuickSight dashboard)\n• Deliverable: Architecture diagram + GitHub repo + Resume bullets"),
            WeekItem(22, 6, "E-commerce Data Platform: Build batch ETL (S3→Glue→Redshift) + DAG", 
                    "Month 6: Capstone Projects", None, "ecommerce-data-platform", "Week 22",
                    "• Implement batch processing pipeline\n• Deliverable: Complete batch ETL with Airflow orchestration and data quality checks"),
            WeekItem(23, 6, "E-commerce Data Platform: Add streaming (Kinesis→Spark→Redshift)", 
                    "Month 6: Capstone Projects", None, "ecommerce-data-platform", "Week 23",
                    "• Implement real-time processing\n• Deliverable: Real-time streaming pipeline with monitoring and alerting"),
            WeekItem(24, 6, "E-commerce Data Platform: Docs + Repo polish + Resume bullets", 
                    "Month 6: Capstone Projects", None, "ecommerce-data-platform", "Week 24",
                    "• Finalize project documentation and portfolio\n• Deliverable: Complete documentation, polished GitHub repo, QuickSight reporting dashboard, and resume bullets highlighting your data engineering skills"),
        ]