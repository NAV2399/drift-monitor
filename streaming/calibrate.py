"""Calibration: run detectors on the undrifted baseline to see how often they fire."""
import duckdb
import pandas as pd

from streaming.detectors import ks_numeric, psi_categorical, psi_numeric

WINDOW_SIZE = 50_000


def load_baseline() -> pd.DataFrame:
    """Load type and amount for all rows, in file order."""
    con = duckdb.connect("data/paysim.duckdb", read_only=True)
    df = con.sql("SELECT type, amount FROM paysim ORDER BY rowid").df()
    con.close()
    return df


def compare_adjacent_windows(df: pd.DataFrame, window_size: int = WINDOW_SIZE) -> pd.DataFrame:
    """Score each full window against the window just before it."""
    n_full = len(df) // window_size
    rows = []
    for i in range(1, n_full):
        ref = df.iloc[(i - 1) * window_size : i * window_size]
        cur = df.iloc[i * window_size : (i + 1) * window_size]
        ks_d, _ = ks_numeric(ref["amount"], cur["amount"])
        rows.append({
            "window": i,
            "psi_amount": psi_numeric(ref["amount"], cur["amount"]),
            "psi_type": psi_categorical(ref["type"], cur["type"]),
            "ks_d_amount": ks_d,
        })
    return pd.DataFrame(rows)


def main():
    df = load_baseline()
    results = compare_adjacent_windows(df)
    print(results.describe(percentiles=[0.5, 0.95]).round(3))
    print("Windows over PSI 0.25 (amount):", int((results["psi_amount"] > 0.25).sum()))
    print("Windows over PSI 0.25 (type):  ", int((results["psi_type"] > 0.25).sum()))
    results.to_csv("data/baseline_scores.csv", index=False)


if __name__ == "__main__":
    main()
