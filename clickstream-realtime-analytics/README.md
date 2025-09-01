# Real-Time Clickstream Analytics (Kinesis → Spark → Redshift)

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
