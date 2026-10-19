# Drift Monitor — Real-Time Data Drift Detection for Transaction Streams

A reproducible streaming evaluation harness that detects distribution drift in
financial transaction streams and compares drift-detection methods on a
benchmark with known ground truth.

## The problem (research angle)

Detecting concept drift in data streams is well studied in theory, but
evaluating detectors reliably under realistic streaming conditions remains an
open challenge. Wares, Isaacs and Elyan (2019) identify four shortcomings in
the literature: outdated drift-detection methods, a lack of benchmark
datasets, flawed evaluation metrics that over-rely on classifier accuracy,
and detectors' inability to cope with temporal dependence. Bifet (2017)
showed that classifier accuracy can mislead drift-detector evaluation — a
non-change detector can outperform real change detectors — and Komorniczak
(2026) confirmed that accuracy is not a reliable proxy for detection
quality, while Lukats et al. (2024) found problems with common detection
metrics such as Mean Time Ratio and lift-per-drift. To our knowledge, no
universally adopted evaluation standard has emerged.

> **Citations verified Oct 2026** — authors, years, venues and quoted claims
> checked against the papers. Full details in `docs/research-notes.md`.
> The Cerqueira et al. (2026) framework is an arXiv preprint; its venue is
> unconfirmed, so no venue is claimed.

**What this project claims:** a small, reproducible, *live* answer to the
benchmark gap — controlled drift injected into real transaction data,
streamed through Kafka → Flink, scored against known drift points, with
compute cost measured. It does not claim to solve drift detection.

## Architecture

```
┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   ┌──────────┐
│  Generator   │──▶│    Kafka     │──▶│      PyFlink         │──▶│   S3     │
│ Python/NumPy │   │ transactions │   │ windows, watermarks, │   │ Delta /  │
│ Pandas       │   │ topic (kind) │   │ PSI / KS / ADWIN     │   │ Parquet  │
│ PaySim +     │   └──────────────┘   └──────────┬───────────┘   └────┬─────┘
│ drift inject │                                 │ alerts topic       │
└──────────────┘                                 ▼                    ▼
                                         ┌──────────────┐   ┌──────────────────┐
                                         │  Databricks  │◀──│  Bronze/Silver/  │
                                         │  Free Ed.    │   │  Gold (PySpark)  │
                                         │  SQL report  │   │  star schema     │
                                         └──────────────┘   └──────────────────┘
```

- **Generator** (`generator/`): replays PaySim, injects labeled drift —
  sudden, gradual (varying drift length), and feature-level. Produces
  time-ordered, autocorrelated streams (not shuffled rows). Ground truth is
  known, so detectors are scored against drift points, never via
  classifier accuracy.
- **Kafka** (`streaming/`): transaction topic + alerts topic. Runs on local
  Kubernetes (kind) — free forever, zero cloud cost.
- **Flink** (`streaming/`): PyFlink job with event-time windows, watermarks
  for late data, and three detectors (PSI, Kolmogorov–Smirnov, ADWIN).
  Emits drift alerts; measures throughput and latency per detector.
- **Sink**: raw events + alerts land as Delta/Parquet on AWS S3.
- **Databricks** (`databricks/`): bronze → silver → gold medallion pipeline
  in PySpark; analytics layer in SQL — star schema, window functions, CTEs;
  detector comparison report: false-alarm rate, missed detections,
  detection delay, precision/recall, compute cost.

## Metrics

False-alarm rate · missed detections · detection delay · precision/recall ·
Flink throughput and latency per detector (compute cost).

## 4-week plan

| Week | Dates | Focus | Deliverable |
|------|-------|-------|-------------|
| 1 | Oct 19–25 | Repo, scope, architecture, local k8s + Kafka, PaySim | This README + running local stack |
| 2 | Oct 26–Nov 1 | Generator + drift injection, Flink windows + detectors | Alerts flowing end to end |
| 3 | Nov 2–8 | S3 sink, Databricks medallion (PySpark + SQL) | Detector comparison report |
| 4 | Nov 9–15 | CI/CD, dashboard, write-up, demo video | Published portfolio piece |

## Free-tier rules (non-negotiable)

1. Kafka, Flink, Kubernetes run **locally on kind** — never on paid cloud.
2. AWS free tier only. **Set the AWS Budgets alert FIRST**, before creating
   anything. Least-privilege IAM user for the pipeline.
3. Databricks: try **Free Edition first**. If it blocks access to your S3
   bucket, fall back to the Azure/AWS Databricks trial — and watch the
   compute costs it generates. Check current free-tier credits and expiry
   dates in your AWS console before Week 3; terms change.

## Quick start

```bash
make setup        # python venv + pip install -r requirements.txt
make kind-up      # local Kubernetes cluster
make kafka-up     # Kafka on kind (Redpanda or Strimzi)
make test         # pytest
```

See `docs/architecture.md` for component details and `docs/research-notes.md`
for the citation verification checklist.
