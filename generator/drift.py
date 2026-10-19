"""Drift injection functions. Each returns a transformed DataFrame chunk
plus the (start_event, end_event) ground-truth interval."""
import numpy as np
import pandas as pd


def inject_sudden(df: pd.DataFrame, feature: str, magnitude: float,
                  rng: np.random.Generator) -> pd.DataFrame:
    """Shift a feature's distribution abruptly from this chunk on."""
    raise NotImplementedError  # Week 2


def inject_gradual(df: pd.DataFrame, feature: str, magnitude: float,
                   progress: float, rng: np.random.Generator) -> pd.DataFrame:
    """Shift a feature's distribution linearly; progress in [0, 1]."""
    raise NotImplementedError  # Week 2


def inject_feature_drift(df: pd.DataFrame, feature: str, magnitude: float,
                         rng: np.random.Generator) -> pd.DataFrame:
    """Change one feature's distribution while keeping the label fixed."""
    raise NotImplementedError  # Week 2
