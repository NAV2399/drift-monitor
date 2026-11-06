"""Stream PaySim rows to Kafka in file (step) order."""
import json
import time

import pandas as pd
from kafka import KafkaProducer

from generator.contract import to_clean_event

CSV_PATH = "data/paysim.csv"
TOPIC = "transactions"
CHUNK_SIZE = 50_000


def read_rows(path, chunk_size=CHUNK_SIZE):
    """Yield raw rows one at a time, in file order, without loading the whole file."""
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        for _, row in chunk.iterrows():
            yield row


def main(max_rows=1000):
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    start = time.time()
    sent = 0
    for raw in read_rows(CSV_PATH):
        if sent >= max_rows:
            break
        producer.send(TOPIC, to_clean_event(raw))
        sent += 1
    producer.flush()
    producer.close()
    elapsed = time.time() - start
    print(f"Sent {sent} events in {elapsed:.2f}s ({sent / elapsed:.0f} events/s)")


if __name__ == "__main__":
    main()
