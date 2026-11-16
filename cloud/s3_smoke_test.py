"""S3 smoke test: upload, list, read back, and confirm delete is denied."""
import boto3
from botocore.exceptions import ClientError

BUCKET = "drift-monitor-nav2399-2026"
KEY = "smoke-test/hello.txt"


def main():
    session = boto3.Session(profile_name="drift-monitor")
    s3 = session.client("s3")

    s3.put_object(Bucket=BUCKET, Key=KEY, Body=b"hello from drift monitor")
    print("Upload:  OK")

    listing = s3.list_objects_v2(Bucket=BUCKET, Prefix="smoke-test/")
    print("List:   ", [obj["Key"] for obj in listing.get("Contents", [])])

    body = s3.get_object(Bucket=BUCKET, Key=KEY)["Body"].read()
    print("Read:   ", body.decode("utf-8"))

    try:
        s3.delete_object(Bucket=BUCKET, Key=KEY)
        print("Delete:  ALLOWED, so the policy is too broad!")
    except ClientError as e:
        print("Delete:  denied, as designed:", e.response["Error"]["Code"])


if __name__ == "__main__":
    main()
