import numpy as np

from streaming.detectors import psi_categorical, psi_numeric


def test_psi_numeric_same_data_is_near_zero():
    rng = np.random.default_rng(0)
    a = rng.normal(100, 10, 5000)
    b = rng.normal(100, 10, 5000)
    assert psi_numeric(a, b) < 0.10


def test_psi_numeric_shifted_data_is_drift():
    rng = np.random.default_rng(0)
    a = rng.normal(100, 10, 5000)
    b = rng.normal(130, 10, 5000)
    assert psi_numeric(a, b) > 0.25


def test_psi_categorical_same_mix_is_zero():
    mix = ["PAYMENT"] * 60 + ["TRANSFER"] * 40
    assert psi_categorical(mix, mix) < 1e-9


def test_psi_categorical_shifted_mix_is_drift():
    before = ["PAYMENT"] * 60 + ["TRANSFER"] * 40
    after = ["PAYMENT"] * 20 + ["TRANSFER"] * 80
    assert psi_categorical(before, after) > 0.25
