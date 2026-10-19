# Architecture

## Data flow

1. **Generator** reads PaySim transactions, injects labeled drift at known
   timestamps, and produces a time-ordered event stream. Output: JSON events
   on the Kafka `transactions` topic. Ground-truth drift points are written
   to a separate manifest file (never sent to detectors).
2. **Kafka** (local, on kind): two topics — `transactions` (raw events),
   `drift-alerts` (detector output).
3. **Flink (PyFlink)**: consumes `transactions`, applies event-time
   windowing with watermarks (late-data policy: allowed lateness 5 min),
   computes windowed features (amount distribution, type mix, velocity),
   and runs three detectors in parallel:
   - PSI (Population Stability Index) vs. a reference window
   - Kolmogorov–Smirnov two-sample test on amount distributions
   - ADWIN (adaptive windowing) on the feature stream
   Emits alerts to `drift-alerts`; records per-detector processing latency
   and throughput.
4. **Sink**: a connector (or batch job in Week 3) writes raw events and
   alerts to S3 as Delta/Parquet.
5. **Databricks**: bronze (raw), silver (cleaned, typed, deduped), gold
   (star schema: fact_alerts, dim_detector, dim_time). SQL report compares
   detectors on false-alarm rate, missed detections, detection delay,
   precision/recall, and compute cost.

## Drift types injected

- **Sudden**: distribution changes at a single timestamp.
- **Gradual**: distribution shifts linearly over a configurable window;
  vary the length to show how detection delay grows with slower drift.
- **Feature-level**: a single feature's distribution changes while the
  label distribution stays fixed (the "neglected" drift type).

## Key design decisions

- Streams are **time-ordered and autocorrelated**, not shuffled — this is
  what the temporal-dependence argument in the literature depends on.
- Detectors are scored against **known drift points**, never by retraining
  a classifier — this avoids the classifier-accuracy flaw the project
  itself critiques.
- Late data is handled with **watermarks**, and the README's talking
  points explain why they matter.

## Assumptions (to revisit)

- PaySim fits in memory for the generator (sample if not).
- kind on a laptop handles Kafka + Flink for dev volumes (~1k events/s).
- Databricks Free Edition storage-link limits are checked before Week 3.

## Laptop-friendly mode (recommended — the default path)

Running kind (3 nodes) + Kafka + Flink at once needs ~6–8 GB RAM just for
infra. Instead we phase it so the laptop only ever runs what's needed:

**Phase A — Weeks 1–3: Docker Compose + Python (light).**
- `infra/docker-compose.yml` runs **Redpanda**: a single ~1 GB container
  with a Kafka-compatible API. Your `kafka-python` code works unchanged —
  in interviews you say "Redpanda, wire-compatible with Kafka" and nobody
  blinks.
- The streaming consumer is **plain Python + pandas** (tumbling windows
  over the Kafka topic). No JVM, no Flink cluster, no Kubernetes.
- Databricks and S3 are in the cloud: zero laptop cost.
- Typical footprint: ~1.5 GB. Fine on an 8 GB laptop.

**Phase B — late Week 3 / Week 4: add Flink.**
- Swap the Python consumer for a **PyFlink** job in Docker (same topics,
  same detectors). This is the "production-grade" upgrade and a great
  interview story: *why* watermarks and exactly-once matter.
- Flink needs Java (~1–2 GB). Run it only when you're working on it.

**Phase C — Week 4: Kubernetes deployment story.**
- Single-node kind cluster (`infra/kind-config.yaml` — one node on
  purpose). Deploy Redpanda + jobs with manifests. Tear it down after the
  demo video. Kubernetes is the packaging chapter, not the daily driver.

Nothing is ever "skipped" — every topic in the original plan (Kafka, Flink,
Kubernetes) still ships. They just don't all run at the same time.
