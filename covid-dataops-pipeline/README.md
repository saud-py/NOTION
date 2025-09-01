# COVID Data Lake (Airflow + CI/CD)

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
