"""Count events on a topic and show the first and last one."""
import json

from kafka import KafkaConsumer


def main():
    consumer = KafkaConsumer(
        "transactions",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=5000,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    count = 0
    first = None
    last = None
    for msg in consumer:
        if first is None:
            first = msg.value
        last = msg.value
        count += 1
    consumer.close()

    print("Count:", count)
    print("First:", first)
    print("Last :", last)


if __name__ == "__main__":
    main()
