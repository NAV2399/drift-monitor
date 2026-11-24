"""Alert relay: read drift-alerts and email each one (printing only, unless email is configured)."""
import json
import os
import smtplib
from email.message import EmailMessage

from kafka import KafkaConsumer

EMAIL_FROM = os.environ.get("ALERT_EMAIL_FROM")
EMAIL_TO = os.environ.get("ALERT_EMAIL_TO")
APP_PASSWORD = os.environ.get("ALERT_EMAIL_APP_PASSWORD")
MAX_EMAILS = int(os.environ.get("ALERT_MAX_EMAILS", "5"))
EMAIL_ON = all([EMAIL_FROM, EMAIL_TO, APP_PASSWORD])


def format_alert(a: dict) -> tuple[str, str]:
    change = (a["avg_amount"] / a["prev_avg_amount"] - 1) * 100
    subject = f"[Drift Monitor] Drift detected in window {a['window_start']}"
    body = (
        f"Window: {a['window_start']} -> {a['window_end']}\n"
        f"Average amount: {a['avg_amount']:,.0f} (same time yesterday {a['prev_avg_amount']:,.0f}, {change:+.0f}%)\n"
        f"Transfer share: {a['transfer_share']:.3f} (same time yesterday {a['prev_transfer_share']:.3f})\n"
        f"Transactions in window: {a['txns']:,}\n"
    )
    return subject, body


def send_email(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.starttls()
        server.login(EMAIL_FROM, APP_PASSWORD)
        server.send_message(msg)


def main():
    print(f"Email {'ON' if EMAIL_ON else 'OFF (printing only)'}; max emails: {MAX_EMAILS}", flush=True)
    consumer = KafkaConsumer(
        "drift-alerts",
        bootstrap_servers="localhost:9092",
        group_id="alert-relay",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    sent = 0
    for msg in consumer:
        subject, body = format_alert(msg.value)
        print(f"{subject}\n{body}", flush=True)
        if EMAIL_ON and sent < MAX_EMAILS:
            send_email(subject, body)
            sent += 1
            print(f"  -> emailed ({sent}/{MAX_EMAILS})", flush=True)


if __name__ == "__main__":
    main()
