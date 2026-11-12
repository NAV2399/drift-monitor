"""Drift injection: create streams with known, labelled drift."""
import numpy as np
import pandas as pd


def inject_sudden(
    df: pd.DataFrame,
    start: int,
    column: str = "amount",
    factor: float = 2.0,
) -> pd.DataFrame:
    """From row `start` onward, multiply `column` by `factor`, and label those rows."""
    out = df.copy()
    out["is_drifted"] = False
    out.loc[start:, column] = out.loc[start:, column] * factor
    out.loc[start:, "is_drifted"] = True
    return out


def inject_gradual(
    df: pd.DataFrame,
    start: int,
    width: int,
    column: str = "amount",
    factor: float = 2.0,
    seed: int = 42,
) -> pd.DataFrame:
    """Fade drift in over `width` rows starting at `start`, and label the drifted rows."""
    out = df.copy()
    rng = np.random.default_rng(seed)
    positions = np.arange(len(out))
    chance = np.clip((positions - start) / width, 0, 1)
    drifted = rng.random(len(out)) < chance
    out["is_drifted"] = drifted
    out.loc[drifted, column] = out.loc[drifted, column] * factor
    return out
