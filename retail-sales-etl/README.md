# Retail Sales ETL (CSV → S3 → Glue → Athena)

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
