# Decisions

## Drift detection

- **Windows:** count-based, 50,000 rows. Hourly volume ranges from 2 to 51,352 transactions, so time-based windows would be statistically meaningless.
- **Reference:** the previous window. A fixed reference would fire constantly, because average amounts swing 5× across the month naturally.
- **Last partial window:** excluded (12,620 rows is too small for a reliable comparison).
- **PSI threshold:** 0.25 (industry standard). Baseline false alarms: amount 0.8%, type 0%.
- **KS threshold:** D > 0.15, not p < 0.05. With 50k-row windows, p-values flag even natural noise. 0.15 gives about 4% baseline false alarms. We chose sensitivity over silence because the data represents customers' money.
- **Labels:** `is_drifted` never enters Kafka, to prevent label leakage.
## First results (previous-window reference)

- Sudden ×2: caught at delay 0 by PSI and KS on amount.
- Gradual over 200k rows: caught by PSI at delay 4; KS missed.
- Gradual over 1M rows: missed by all detectors. Neighbouring windows differ too little.
- Type shift 30%: missed. A PSI of about 0.12 is within natural noise (baseline max 0.117).
- Grading uses a no-drift control: alerts that also fire on undrifted data are not credited.

## Known limitation

- Count-based windows fill slowly in quiet hours, so overnight drift may be detected hours late. Production fix: close a window at 50k rows OR 1 hour, whichever comes first.

## Results with ADWIN (horizon 30 windows)

- Sudden ×2: PSI 0, KS 0, ADWIN 3 windows.
- Gradual 200k: PSI 4, KS missed, ADWIN 7.
- Gradual 1M: PSI and KS missed; ADWIN caught at 16 — the only detector that catches slow drift.
- False alarms before drift: PSI 1, KS 1, ADWIN 0.
- Horizon 30 vs 50 gave identical results, so the results are robust to the horizon choice.
- Conclusion: run PSI and ADWIN together: PSI for fast jumps, ADWIN for slow creep.
