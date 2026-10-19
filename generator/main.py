"""Entry point: stream PaySim rows to Kafka with injected drift.

Usage:
    python -m generator.main --config configs/dev.yaml
"""
import argparse
import json

from generator.config import GeneratorConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Drift-injecting transaction generator")
    parser.add_argument("--config", default="configs/dev.yaml")
    args = parser.parse_args()
    cfg = GeneratorConfig()
    print(f"config={args.config} seed={cfg.seed} rate={cfg.events_per_second}/s")
    # Week 2: load PaySim, apply drifts in event order, emit to Kafka,
    # write ground-truth manifest to cfg.manifest_path
    raise NotImplementedError("Week 2")


if __name__ == "__main__":
    main()
