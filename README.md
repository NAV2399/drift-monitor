# Drift Monitor — Real-Time Data Drift Detection for Transaction Streams
[![tests](https://github.com/NAV2399/drift-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/NAV2399/drift-monitor/actions/workflows/tests.yml)


A reproducible streaming evaluation harness that detects distribution drift in financial transaction streams and compares drift-detection methods against known, injected ground truth.

It replays 6,362,620 PaySim transactions through Kafka, lands them in an S3/Databricks medallion lakehouse, scores three drift detectors offline, and runs a live Flink detector that sends email alerts.

---

## Results at a glance

Drift is injected at a known point, and each detector is graded on **detection delay** (in 50,000-transaction windows), **misses** and **false alarms**. Classifier accuracy is never used.

| Scenario | PSI (amount) | PSI (type) | KS (amount) | ADWIN (amount) |
|---|---|---|---|---|
| No drift (false alarms) | 1 | 0 | 1 | **0** |
| Sudden, amount × 2 | **caught (0)** | not watched | **caught (0)** | caught (3) |
| Gradual over 200k rows | **caught (4)** | not watched | missed | caught (7) |
| Gradual over 1M rows | missed | not watched | missed | **caught (16)** |
| Type shift, 30% of payments | not watched | missed | not watched | not watched |

*"Not watched" means the drift was in a feature that detector does not monitor; it is neither a success nor a miss.*

**Key findings**

- **PSI is fastest on sudden and short drift**, but blind to slow drift.
- **ADWIN is the only detector that catches slow drift**, and the only one with zero false alarms, at the cost of a slower reaction to sudden drift.
- **KS adds nothing PSI doesn't already catch.**
- **A 30% shift in transaction type sits inside PaySim's natural noise** (PSI ≈ 0.12 against a baseline maximum of 0.117).
- **Recommendation:** run PSI and ADWIN together — PSI for fast jumps, ADWIN for slow creep.

Results are reproducible: a rerun days later produced identical numbers, and grading uses a no-drift control so that natural noise is never credited as a detection.

---

## The problem (research angle)

Detecting concept drift in data streams is well studied in theory, but evaluating detectors reliably under realistic streaming conditions remains an open challenge. Wares, Isaacs and Elyan (2019) identify four shortcomings in the literature: outdated drift-detection methods, a lack of benchmark datasets, flawed evaluation metrics that over-rely on classifier accuracy, and detectors' inability to cope with temporal dependence. Bifet (2017) showed that classifier accuracy can mislead drift-detector evaluation — a non-change detector can outperform real change detectors — and Komorniczak (2026) confirmed that accuracy is not a reliable proxy for detection quality, while Lukats et al. (2024) found problems with common detection metrics such as Mean Time Ratio and lift-per-drift. To our knowledge, no universally adopted evaluation standard has emerged.

Citations verified October 2026 — authors, years, venues and quoted claims checked against the papers. Full details in [`docs/research-notes.md`](docs/research-notes.md). The Cerqueira et al. (2026) framework is an arXiv preprint; its venue is unconfirmed, so no venue is claimed.

**What this project claims:** a small, reproducible answer to the benchmark gap — controlled drift injected into transaction data, streamed through Kafka, scored against known drift points. It does not claim to solve drift detection.

---

## Architecture

One Kafka topic feeds two halves: a **batch path** that is the source of truth for evaluation, and a **streaming path** that raises live alerts (a Lambda-style design).

```
PaySim CSV ──▶ Producer ──▶ Redpanda (Kafka) — topic "transactions"
 6.36M rows    clean event                 │
               contract       ┌────────────┴─────────────┐
                              ▼                          ▼
                       S3 sink (bronze)            Flink (PyFlink)
                       Parquet on AWS S3           6-hour event-time windows,
                              │                    watermarks, LAG
                              ▼                          │
                       Databricks medallion        topic "drift-alerts"
                       bronze → silver → gold            │
                              │                          ▼
                              ▼                    Alert relay ──▶ email
                       Detector comparison report
```

| Component | Folder | What it does |
|---|---|---|
| Event contract | `generator/contract.py` | Renames raw PaySim fields once, at the source, into a clean schema |
| Producer | `generator/producer.py` | Streams PaySim in time order to Kafka (≈ 6,400–8,600 events/s on a laptop) |
| Drift injection | `generator/drift.py` | Sudden, gradual and transaction-type drift, each with exact labels |
| Broker | `infra/docker-compose.yml` | Redpanda (Kafka-compatible), with internal and external listeners |
| S3 sink | `cloud/s3_sink.py` | Writes 50,000-event Parquet files to S3; commits offsets only after a successful write |
| Detectors | `streaming/detectors.py` | PSI (numeric and categorical), KS, ADWIN |
| Scoring harness | `streaming/score.py` | Injects drift, runs every detector, grades delay, misses and false alarms against a no-drift control |
| Lakehouse | `databricks/` | Bronze checks, silver and gold tables, and the detector comparison report |
| Live detector | `streaming/flink_job.py` | Flink SQL inside PyFlink: event-time windows and a calibrated alert rule |
| Alert relay | `streaming/alert_relay.py` | Reads `drift-alerts`, prints and emails each alert, with a safety cap |

---

## How the evaluation works

1. **Data:** 6,362,620 PaySim transactions over 743 hourly steps, replayed in time order (never shuffled).
2. **Windows:** count-based windows of 50,000 transactions, each compared with the previous window. Hourly volume ranges from 2 to 51,352 transactions, so time-based windows would often be too small to judge.
3. **Drift:** injected exactly at window 60 (row 3,000,000) of 126 full windows.
4. **Calibration:** every detector is first run on undrifted data to set thresholds — PSI 0.25 (industry standard), KS D > 0.15, ADWIN `delta` 0.002.
5. **Grading:**
   - **False alarms:** alerts before window 60.
   - **Detection delay:** windows from drift start to the first alert.
   - **Missed:** no alert within 30 windows (longer than the slowest drift).
   - **No-drift control:** any alert that also fires on clean data is not credited as a detection.

### Live detector calibration

The Flink job's first rule (compare each 6-hour window with the previous one) raised **31 false alarms out of 122 comparisons (25%)** on a clean replay. Two causes were measured and fixed:

- **Daily seasonality:** windows are now compared with **the same time yesterday** (4 windows back).
- **Tiny windows:** windows, and their references, with fewer than **1,000 transactions** are not judged. With p ≈ 0.084, the standard error of a 170-transaction window's transfer share is about 0.021, so a 0.05 threshold sits inside the noise.

Result on the same clean replay: **4 false alarms out of 93 judged windows (4.3%)**.

---

## Data findings

Profiling with DuckDB and Spark surfaced facts that shaped the design:

- **743 hourly steps, not 744;** no gaps, and the file is already in time order.
- **Fraud occurs only in TRANSFER (0.769%) and CASH_OUT (0.184%)**, as transfer-then-cash-out pairs. Overall fraud is 0.1291% — not the 0.0735% seen in the first 200,000 rows, because the first N rows are not a random sample.
- **The natural fraud rate swings about 540× across windows,** so detectors must be calibrated on clean data first.
- **74% of outgoing rows don't balance** (and merchant balances are always 0), so balance columns are flagged in silver and never used by detectors.
- **Day 31 is 100% fraud,** so the final window is unrepresentative and excluded.
- **Day 3's 29% fraud rate comes from collapsing volume** (1,070 transactions), not more fraud (310, a normal count): check the numerator and the denominator before alerting on a ratio.

**Reconciliation:** DuckDB on the raw CSV and Spark on bronze, silver and gold all return 6,362,620 rows and 8,213 fraud transactions, with identical counts per type.

---

## Key design decisions

Full reasoning in [`docs/decisions.md`](docs/decisions.md).

| Decision | Why | Trade-off |
|---|---|---|
| Single Kafka partition | Guarantees global time order | No parallelism |
| Labels never enter Kafka | Prevents label leakage | Scoring needs a separate join |
| Commit after write + offset-named files | At-least-once delivery with idempotent writes: no loss, no duplicates | Reprocessing after a restart |
| KS uses D > 0.15, not p < 0.05 | At 50,000 rows, p-values flag natural noise | About 4% baseline false alarms |
| Lambda design | Batch is the source of truth; streaming gives live alerts | Two code paths that can disagree |
| Flink in Docker | PyFlink does not support the laptop's Python 3.14 | A 2.5 GB image |
| Least-privilege IAM | The pipeline can list, read and write one bucket only; delete is denied | — |

---

## Tech stack

**Python** (pandas, NumPy, SciPy, river, kafka-python, boto3, pytest) · **SQL** (DuckDB, Spark SQL, Flink SQL) · **PySpark** and **Delta Lake** on Databricks Free Edition · **Apache Flink 1.20** (PyFlink) · **Redpanda** (Kafka API) · **Docker Compose** · **AWS** (S3, IAM, Budgets)

---

## Repository layout

```
generator/   event contract, producer, drift injection
streaming/   detectors, scoring harness, Flink job, alert relay
cloud/       S3 smoke test, S3 sink, bronze checks and download
sql/         DuckDB profiling queries
databricks/  bronze, silver, gold and detector-report notebooks
infra/       docker-compose.yml, Flink Dockerfile
tests/       pytest suite for drift injection and detectors
docs/        architecture, research notes, decisions log
```

---

## Running it locally

**Prerequisites:** Docker Desktop, Python 3.10+, and the [PaySim dataset](https://www.kaggle.com/datasets/ealaxi/paysim1) saved as `data/paysim.csv`. The `data/` folder is git-ignored.

```bash
# 1. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Tests
python -m pytest tests/ -v

# 3. Offline evaluation (DuckDB copy of PaySim, then the scoring harness)
python sql/02_load.py
python -m streaming.score

# 4. Streaming stack: Redpanda + Flink
docker compose -f infra/docker-compose.yml up -d --build
docker exec redpanda rpk topic create transactions window-stats drift-alerts -p 1 -r 1

# 5. Live detector and alerts
docker exec flink-jobmanager ./bin/flink run -d -py /opt/flink/jobs/flink_job.py
python -m streaming.alert_relay        # terminal 1: prints alerts (email optional)
python -m generator.producer           # terminal 2: replays all transactions
```

The Flink dashboard is at `http://localhost:8081`.

**Optional — S3 sink:** requires an AWS profile named `drift-monitor` and your own bucket name in `cloud/s3_sink.py`. Run `python -m cloud.s3_sink` alongside the producer.

**Optional — email alerts:** set `ALERT_EMAIL_FROM`, `ALERT_EMAIL_TO` and `ALERT_EMAIL_APP_PASSWORD` (a Gmail App Password) as environment variables before starting the relay. Never put credentials in code.

---

## Cost and security

- **$0 cloud spend target:** AWS free plan, a budget alert set before anything was created, and Databricks Free Edition.
- **No secrets in the repo:** AWS keys live in a local profile, and email credentials in environment variables.
- **Least privilege:** the pipeline's IAM user can reach one bucket only; Databricks access is read-only.

---

## Known limitations

- **Synthetic data:** PaySim's balance columns are unreliable and its final day is artificial.
- **Two windowing schemes:** offline evaluation uses count-based windows; the live Flink job uses 6-hour time windows. Their alerts are not yet reconciled with each other.
- **Simpler live rule:** Flink uses a relative-change rule on average amount and transfer share, not PSI or ADWIN.
- **No Flink checkpoints yet:** a restarted job rereads the topic from the start.
- **Databricks Free Edition:** a Unity Catalog external location to S3 failed at the IAM role step, so bronze is copied into a Databricks Volume. On paid Databricks, the external location is the correct design.
- **One test design:** drift always starts at window 60 with fixed magnitudes.

## Next steps

- Local Kubernetes (kind) deployment of the streaming stack
- CI with GitHub Actions running the test suite on every push
- Flink checkpointing, and retry with backoff in the alert relay
- Reconcile Flink's live alerts with the offline scores on the same replay
