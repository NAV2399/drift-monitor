"""Scoring harness: inject known drift into the real stream and grade each detector."""
import pandas as pd

from generator.drift import inject_gradual, inject_sudden, inject_type_shift
from streaming.calibrate import WINDOW_SIZE, compare_adjacent_windows, load_baseline

THRESHOLDS = {"psi_amount": 0.25, "psi_type": 0.25, "ks_d_amount": 0.15}
DRIFT_WINDOW = 60
DRIFT_START = DRIFT_WINDOW * WINDOW_SIZE
HORIZON = 10

SCENARIOS = [
    ("no_drift",         lambda df: df),
    ("sudden_x2",        lambda df: inject_sudden(df, DRIFT_START, factor=2.0)),
    ("gradual_200k",     lambda df: inject_gradual(df, DRIFT_START, width=200_000)),
    ("gradual_1m",       lambda df: inject_gradual(df, DRIFT_START, width=1_000_000)),
    ("type_shift_30pct", lambda df: inject_type_shift(df, DRIFT_START, fraction=0.3)),
]


def alert_windows(scores: pd.DataFrame) -> dict:
    """For each detector, the set of windows where it fired."""
    return {d: set(scores.loc[scores[d] > t, "window"]) for d, t in THRESHOLDS.items()}


def grade(scores: pd.DataFrame, scenario: str, control: dict) -> list[dict]:
    """Grade alerts against the drift window, ignoring windows where the control also fired."""
    rows = []
    for detector, threshold in THRESHOLDS.items():
        alerts = scores.loc[scores[detector] > threshold, "window"]
        false_alarms = int((alerts < DRIFT_WINDOW).sum())
        hits = [
            w for w in alerts
            if DRIFT_WINDOW <= w < DRIFT_WINDOW + HORIZON and w not in control[detector]
        ]
        delay = int(min(hits) - DRIFT_WINDOW) if hits else None
        rows.append({
            "scenario": scenario,
            "detector": detector,
            "false_alarms": false_alarms,
            "delay_windows": delay,
            "missed": delay is None,
        })
    return rows


def main():
    base = load_baseline()
    control = alert_windows(compare_adjacent_windows(base))
    results = []
    for name, make_drift in SCENARIOS:
        print(f"Running {name} ...")
        scores = compare_adjacent_windows(make_drift(base))
        results.extend(grade(scores, name, control))
    table = pd.DataFrame(results)
    print(table.to_string(index=False))
    table.to_csv("data/score_results.csv", index=False)


if __name__ == "__main__":
    main()
