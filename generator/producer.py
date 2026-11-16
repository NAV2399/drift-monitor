
import argparse
import json
import time

import pandas as pd
from kafka import KafkaProducer

from generator.contract import to_clean_event

CSV_PATH = "data/paysim.csv"
TOPIC = "transactions"
CHUNK_SIZE = 50_000
PROGRESS_EVERY = 500_000


def read_rows(path, chunk_size=CHUNK_SIZE):
    """Yield raw rows one at a time, in file order, without loading the whole file."""
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        yield from chunk.to_dict("records")


def main(max_rows=None):
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=20,
        batch_size=256 * 1024,
    )
    start = time.time()
    sent = 0
    for raw in read_rows(CSV_PATH):
        if max_rows is not None and sent >= max_rows:
            break
        producer.send(TOPIC, to_clean_event(raw))
        sent += 1
        if sent % PROGRESS_EVERY == 0:
            print(f"  {sent:,} events sent ({time.time() - start:.0f}s)")
    producer.flush()
    producer.close()
    elapsed = time.time() - start
    print(f"Sent {sent:,} events in {elapsed:.1f}s ({sent / elapsed:,.0f} events/s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream PaySim to Kafka.")
    parser.add_argument("--max-rows", type=int, default=None,
                        help="Stop after this many rows (default: all rows).")
    args = parser.parse_args()
    main(max_rows=args.max_rows)
