"""Verify bronze: count files and total size in S3."""
import boto3

BUCKET = "drift-monitor-nav2399-2026"
PREFIX = "bronze/transactions/"


def main():
    s3 = boto3.Session(profile_name="drift-monitor").client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    files, total_bytes = 0, 0
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            files += 1
            total_bytes += obj["Size"]
    print(f"Files: {files}")
    print(f"Total size: {total_bytes / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
