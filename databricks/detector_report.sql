-- Detector comparison report (Week 3).
-- Star schema: fact_alerts(detector_id, alert_ts, ...), dim_detector, dim_time.
-- Metrics: false-alarm rate, missed detections, detection delay,
--          precision/recall, compute cost (avg latency, throughput).

-- Example skeleton: detection delay per detector vs. ground truth.
-- WITH ground_truth AS (
--     SELECT drift_start_ts, drift_end_ts, drift_kind FROM gold.dim_drift
-- ),
-- alerts AS (
--     SELECT detector_id, alert_ts,
--            LAG(alert_ts) OVER (PARTITION BY detector_id ORDER BY alert_ts) AS prev_alert
--     FROM gold.fact_alerts
-- )
-- SELECT * FROM alerts LIMIT 10;
SELECT 'skeleton — Week 3' AS status;
