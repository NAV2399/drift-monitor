"""Drift detectors. Each implements: update(value) -> bool (drift or not).

Detectors run inside the PyFlink job over windowed features (Week 2).
These pure-Python versions are unit-testable without Flink.
"""
import numpy as np


class PSIDetector:
    """Population Stability Index vs. a reference window."""

    def __init__(self, bins: int = 10, threshold: float = 0.25):
        self.bins = bins
        self.threshold = threshold
        self.reference = None

    def update(self, window: np.ndarray) -> bool:
        raise NotImplementedError  # Week 2


class KSDetector:
    """Kolmogorov–Smirnov two-sample test vs. a reference window."""

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.reference = None

    def update(self, window: np.ndarray) -> bool:
        raise NotImplementedError  # Week 2


class ADWINDetector:
    """Adaptive windowing detector over the feature stream."""

    def __init__(self, delta: float = 0.002):
        self.delta = delta

    def update(self, value: float) -> bool:
        raise NotImplementedError  # Week 2
