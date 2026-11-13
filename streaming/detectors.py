"""Drift detectors: compare a reference window with a current window."""
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

EPS = 1e-6  # tiny number to avoid dividing by zero or log(0)


def psi_from_shares(ref_shares, cur_shares) -> float:
    """PSI between two lists of bucket shares (each list sums to 1)."""
    ref = np.clip(ref_shares, EPS, None)
    cur = np.clip(cur_shares, EPS, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))


def psi_numeric(reference, current, bins: int = 10) -> float:
    """PSI for a numeric column, e.g. amount."""
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    return psi_from_shares(ref_counts / len(reference), cur_counts / len(current))


def psi_categorical(reference, current) -> float:
    """PSI for a category column, e.g. transaction type."""
    categories = sorted(set(reference) | set(current))
    ref = pd.Series(reference).value_counts(normalize=True)
    cur = pd.Series(current).value_counts(normalize=True)
    ref_shares = np.array([ref.get(c, 0.0) for c in categories])
    cur_shares = np.array([cur.get(c, 0.0) for c in categories])
    return psi_from_shares(ref_shares, cur_shares)


def ks_numeric(reference, current) -> tuple[float, float]:
    """KS test: returns (D statistic, p-value)."""
    result = ks_2samp(reference, current)
    return float(result.statistic), float(result.pvalue)
