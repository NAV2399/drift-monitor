"""Download bronze Parquet files from S3 into data/bronze/ for upload to a Databricks Volume."""
from pathlib import Path

import boto3

BUCKET = "drift-monitor-nav2399-2026"
PREFIX = "bronze/transactions/"
LOCAL_DIR = Path("data/bronze/transactions")


def main():
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    s3 = boto3.Session(profile_name="drift-monitor").client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    count = 0
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            name = obj["Key"].split("/")[-1]
            s3.download_file(BUCKET, obj["Key"], str(LOCAL_DIR / name))
            count += 1
    print(f"Downloaded {count} files to {LOCAL_DIR}")


if __name__ == "__main__":
    main()
