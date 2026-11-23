"""Flink streaming job: 6-hour event-time windows over transactions, flag big jumps."""
from pyflink.table import EnvironmentSettings, TableEnvironment

BROKERS = "redpanda:29092"
AMOUNT_JUMP = 0.5        # alert if the window's average amount changes by more than 50%
TRANSFER_JUMP = 0.05     # alert if the TRANSFER share changes by more than 5 points
MIN_TXNS = 1000          # never judge a window (or its reference) smaller than this


SOURCE = f"""
CREATE TABLE transactions (
    step INT,
    transaction_type STRING,
    amount DOUBLE,
    is_fraud BOOLEAN,
    event_time AS TO_TIMESTAMP_LTZ(CAST(step AS BIGINT) * 3600 * 1000, 3),
    WATERMARK FOR event_time AS event_time - INTERVAL '1' HOUR
) WITH (
    'connector' = 'kafka',
    'topic' = 'transactions',
    'properties.bootstrap.servers' = '{BROKERS}',
    'properties.group.id' = 'flink-drift',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
"""

WINDOW_STATS = """
CREATE VIEW window_stats AS
SELECT
    window_start,
    window_end,
    window_time,
    COUNT(*) AS txns,
    AVG(amount) AS avg_amount,
    AVG(CASE WHEN transaction_type = 'TRANSFER' THEN 1.0 ELSE 0.0 END) AS transfer_share
FROM TABLE(TUMBLE(TABLE transactions, DESCRIPTOR(event_time), INTERVAL '6' HOUR))
GROUP BY window_start, window_end, window_time
"""

SCORED = """
CREATE VIEW scored AS
SELECT
    window_start, window_end, txns, avg_amount, transfer_share,
    LAG(avg_amount, 4)     OVER (ORDER BY window_time) AS prev_avg_amount,
    LAG(transfer_share, 4) OVER (ORDER BY window_time) AS prev_transfer_share,
    LAG(txns, 4)           OVER (ORDER BY window_time) AS prev_txns
FROM window_stats
"""

STATS_SINK = f"""
CREATE TABLE window_stats_out (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    txns BIGINT,
    avg_amount DOUBLE,
    transfer_share DOUBLE,
    prev_avg_amount DOUBLE,
    prev_transfer_share DOUBLE
) WITH (
    'connector' = 'kafka',
    'topic' = 'window-stats',
    'properties.bootstrap.servers' = '{BROKERS}',
    'format' = 'json'
)
"""

ALERTS_SINK = f"""
CREATE TABLE drift_alerts_out (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    txns BIGINT,
    avg_amount DOUBLE,
    prev_avg_amount DOUBLE,
    transfer_share DOUBLE,
    prev_transfer_share DOUBLE
) WITH (
    'connector' = 'kafka',
    'topic' = 'drift-alerts',
    'properties.bootstrap.servers' = '{BROKERS}',
    'format' = 'json'
)
"""

INSERT_STATS = """
INSERT INTO window_stats_out
SELECT window_start, window_end, txns, avg_amount, transfer_share,
       prev_avg_amount, prev_transfer_share
FROM scored
"""

INSERT_ALERTS = f"""
INSERT INTO drift_alerts_out
SELECT window_start, window_end, txns, avg_amount, prev_avg_amount,
       transfer_share, prev_transfer_share
FROM scored
WHERE prev_avg_amount IS NOT NULL
  AND txns >= {MIN_TXNS} AND prev_txns >= {MIN_TXNS}
  AND (ABS(avg_amount / prev_avg_amount - 1) > {AMOUNT_JUMP}
       OR ABS(transfer_share - prev_transfer_share) > {TRANSFER_JUMP})
"""


def main():
    t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
    for ddl in (SOURCE, WINDOW_STATS, SCORED, STATS_SINK, ALERTS_SINK):
        t_env.execute_sql(ddl)

    statements = t_env.create_statement_set()
    statements.add_insert_sql(INSERT_STATS)
    statements.add_insert_sql(INSERT_ALERTS)
    statements.execute()


if __name__ == "__main__":
    main()
