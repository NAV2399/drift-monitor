import pandas as pd

from generator.drift import inject_sudden


def test_sudden_changes_only_rows_from_start():
    df = pd.DataFrame({"amount": [10.0, 10.0, 10.0, 10.0]})
    out = inject_sudden(df, start=2, factor=3.0)
    assert out["amount"].tolist() == [10.0, 10.0, 30.0, 30.0]
    assert out["is_drifted"].tolist() == [False, False, True, True]


def test_sudden_does_not_modify_input():
    df = pd.DataFrame({"amount": [10.0, 10.0]})
    inject_sudden(df, start=0, factor=3.0)
    assert df["amount"].tolist() == [10.0, 10.0]




