

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
