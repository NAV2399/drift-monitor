import numpy as np

from streaming.detectors import adwin_detections, ks_numeric, psi_categorical, psi_numeric
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


def test_ks_same_data_has_small_gap():
    rng = np.random.default_rng(0)
    a = rng.normal(100, 10, 5000)
    b = rng.normal(100, 10, 5000)
    d, _ = ks_numeric(a, b)
    assert d < 0.05


def test_ks_shifted_data_has_large_gap():
    rng = np.random.default_rng(0)
    a = rng.normal(100, 10, 5000)
    b = rng.normal(130, 10, 5000)
    d, p = ks_numeric(a, b)
    assert d > 0.5
    assert p < 0.001

def test_adwin_quiet_on_stable_data():
    rng = np.random.default_rng(0)
    values = rng.normal(0, 1, 2000)
    assert adwin_detections(values) == []


def test_adwin_catches_mean_jump():
    rng = np.random.default_rng(0)
    values = np.concatenate([rng.normal(0, 1, 1000), rng.normal(3, 1, 1000)])
    positions = adwin_detections(values)
    assert any(1000 <= p < 1200 for p in positions)
