"""Smoke test v2: clean up PaySim-style field names, send, read back."""
import json
from kafka import KafkaProducer, KafkaConsumer

# What the "application" (PaySim) hands us — its names, not ours.
raw = {
    "type": "PAYMENT",
    "amount": 250.75,
    "nameOrig": "C1231006815",
    "nameDest": "M1979787155",
    "isFraud": 0,
}


def to_clean_event(raw):
    """Rename PaySim fields into our event contract."""
    return {
        "transaction_type": raw["type"],
        "amount": raw["amount"],
        "origin_account": raw["nameOrig"],
        "destination_account": raw["nameDest"],
        "is_fraud": bool(raw["isFraud"]),
    }


event = to_clean_event(raw)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
producer.send("transactions", event)
producer.flush()
print("Sent:", event)

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    consumer_timeout_ms=5000,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)
for msg in consumer:
    print("Received:", msg.value)
    break
consumer.close()

