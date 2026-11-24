"""Stream PaySim rows to Kafka in file (step) order, optionally with injected sudden drift."""
import argparse
import json
import time

import pandas as pd
from kafka import KafkaProducer

from generator.contract import to_clean_event
from generator.drift import inject_sudden

CSV_PATH = "data/paysim.csv"
TOPIC = "transactions"
CHUNK_SIZE = 50_000
PROGRESS_EVERY = 500_000


def read_rows(path, chunk_size=CHUNK_SIZE, drift_start=None, factor=2.0):
    """Yield raw rows in file order; from row `drift_start` on, multiply amounts by `factor`."""
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        if drift_start is not None:
            chunk = inject_sudden(chunk, start=drift_start, factor=factor)
        yield from chunk.to_dict("records")


def main(max_rows=None, csv_path=CSV_PATH, drift_start=None, factor=2.0):
    if drift_start is not None:
        print(f"Injecting sudden drift: amount x{factor} from row {drift_start:,}")
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=20,
        batch_size=256 * 1024,
    )
    start = time.time()
    sent = 0
    for raw in read_rows(csv_path, drift_start=drift_start, factor=factor):
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
    parser.add_argument("--csv", default=CSV_PATH, help="Path to the PaySim CSV.")
    parser.add_argument("--drift-start", type=int, default=None,
                        help="Inject sudden amount drift from this row (default: no drift).")
    parser.add_argument("--factor", type=float, default=2.0,
                        help="Amount multiplier for the injected drift.")
    args = parser.parse_args()
    main(max_rows=args.max_rows, csv_path=args.csv,
         drift_start=args.drift_start, factor=args.factor)
