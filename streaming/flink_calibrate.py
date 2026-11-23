"""Calibrate the Flink rule: read window-stats and compare two reference choices."""
import json

import pandas as pd
from kafka import KafkaConsumer

AMOUNT_JUMP = 0.5
TRANSFER_JUMP = 0.05


def load_windows() -> pd.DataFrame:
    consumer = KafkaConsumer(
        "window-stats",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=5000,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    rows = [msg.value for msg in consumer]
    consumer.close()
    return pd.DataFrame(rows).sort_values("window_start").reset_index(drop=True)


def score(w: pd.DataFrame, lag: int, label: str, min_txns: int = 0) -> None:
    amount = (w["avg_amount"] / w["avg_amount"].shift(lag) - 1).abs()
    transfer = (w["transfer_share"] - w["transfer_share"].shift(lag)).abs()
    big_enough = (w["txns"] >= min_txns) & (w["txns"].shift(lag) >= min_txns)
    alerts = ((amount > AMOUNT_JUMP) | (transfer > TRANSFER_JUMP)) & big_enough
    compared = (amount.notna() & big_enough).sum()
    print(f"{label:<20} lag {lag}  min {min_txns:>6}: {int(alerts.sum()):>2} alerts / "
          f"{compared:>3} judged ({100 * alerts.sum() / max(compared, 1):.1f}%)")


def main():
    w = load_windows()
    print(f"Loaded {len(w)} windows")
    print(w["txns"].describe(percentiles=[0.1, 0.25, 0.5]).round(0))
    for min_txns in [0, 1_000, 10_000, 30_000]:
        score(w, 1, "Previous window", min_txns)
        score(w, 4, "Same time yesterday", min_txns)




if __name__ == "__main__":
    main()

