import pandas as pd

from generator.drift import inject_gradual, inject_sudden


def test_sudden_changes_only_rows_from_start():
    df = pd.DataFrame({"amount": [10.0, 10.0, 10.0, 10.0]})
    out = inject_sudden(df, start=2, factor=3.0)
    assert out["amount"].tolist() == [10.0, 10.0, 30.0, 30.0]
    assert out["is_drifted"].tolist() == [False, False, True, True]


def test_sudden_does_not_modify_input():
    df = pd.DataFrame({"amount": [10.0, 10.0]})
    inject_sudden(df, start=0, factor=3.0)
    assert df["amount"].tolist() == [10.0, 10.0]


def test_gradual_fades_in():
    df = pd.DataFrame({"amount": [10.0] * 1000})
    out = inject_gradual(df, start=200, width=600)
    before = out.loc[:199, "is_drifted"].mean()
    middle = out.loc[400:599, "is_drifted"].mean()
    after = out.loc[800:, "is_drifted"].mean()
    assert before == 0.0
    assert 0.2 < middle < 0.8
    assert after == 1.0


def test_gradual_is_reproducible():
    df = pd.DataFrame({"amount": [10.0] * 1000})
    a = inject_gradual(df, start=200, width=600)
    b = inject_gradual(df, start=200, width=600)
    assert a["is_drifted"].tolist() == b["is_drifted"].tolist()
