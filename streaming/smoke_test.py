"""Smoke test v2: clean up PaySim-style field names, send, read back."""
from kafka import KafkaProducer, KafkaConsumer
from generator.contract import to_clean_event
import json

# What the "application" (PaySim) hands us — its names, not ours.
raw = {
    "type": "PAYMENT",
    "amount": 250.75,
    "nameOrig": "C1231006815",
    "nameDest": "M1979787155",
    "isFraud": 0,
    "step": 1,
    "oldbalanceOrg": 1000.0,
    "newbalanceOrig": 749.25,
    "oldbalanceDest": 0.0,
    "newbalanceDest": 0.0,
}



event = to_clean_event(raw)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
producer.send("smoke-test", event)
producer.flush()
print("Sent:", event)

consumer = KafkaConsumer(
    "smoke-test",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    consumer_timeout_ms=5000,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)
for msg in consumer:
    print("Received:", msg.value)
    break
consumer.close()

