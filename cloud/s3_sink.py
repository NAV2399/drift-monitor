"""S3 sink: consume clean events from Kafka and write them to S3 as Parquet (bronze)."""
import io
import json

import boto3
import pandas as pd
from kafka import KafkaConsumer

BUCKET = "drift-monitor-nav2399-2026"
TOPIC = "transactions"
PREFIX = "bronze/transactions"
BATCH_SIZE = 500


def write_batch(s3, events: list, first_offset: int) -> None:
    """Write one batch as a Parquet file named after its first Kafka offset."""
    buffer = io.BytesIO()
    pd.DataFrame(events).to_parquet(buffer, index=False)
    key = f"{PREFIX}/offset_{first_offset:010d}.parquet"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.getvalue())
    print(f"Wrote {len(events)} events to s3://{BUCKET}/{key}")


def main():
    s3 = boto3.Session(profile_name="drift-monitor").client("s3")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers="localhost:9092",
        group_id="s3-sink",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=5000,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    batch, first_offset = [], None
    for msg in consumer:
        if first_offset is None:
            first_offset = msg.offset
        batch.append(msg.value)
        if len(batch) >= BATCH_SIZE:
            write_batch(s3, batch, first_offset)
            consumer.commit()
            batch, first_offset = [], None

    if batch:
        write_batch(s3, batch, first_offset)
        consumer.commit()
    consumer.close()


if __name__ == "__main__":
    main()
