# Decisions

## Drift detection

- **Windows:** count-based, 50,000 rows. Hourly volume ranges from 2 to 51,352 transactions, so time-based windows would be statistically meaningless.
- **Reference:** the previous window. A fixed reference would fire constantly, because average amounts swing 5× across the month naturally.
- **Last partial window:** excluded (12,620 rows is too small for a reliable comparison).
- **PSI threshold:** 0.25 (industry standard). Baseline false alarms: amount 0.8%, type 0%.
- **KS threshold:** D > 0.15, not p < 0.05. With 50k-row windows, p-values flag even natural noise. 0.15 gives about 4% baseline false alarms. We chose sensitivity over silence because the data represents customers' money.
- **Labels:** `is_drifted` never enters Kafka, to prevent label leakage.
