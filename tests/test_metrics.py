"""Metric functions checked against independent implementations (scikit-learn) and hand-worked cases."""
import numpy as np
import pytest
from sklearn.metrics import cohen_kappa_score, f1_score, roc_auc_score

from drjev import calibrate
from drjev import metrics as M

rng = np.random.default_rng(0)


def test_qwk_matches_sklearn():
    for _ in range(20):
        y = rng.integers(0, 5, 400)
        yh = np.clip(y + rng.integers(-2, 3, 400), 0, 4)
        assert M.qwk(y, yh) == pytest.approx(cohen_kappa_score(y, yh, weights="quadratic"), abs=1e-12)


def test_auroc_matches_sklearn_including_ties():
    for _ in range(20):
        y = rng.random(300) < 0.3
        s = np.round(rng.random(300) + 0.4 * y, 1)          # heavy ties
        assert M.auroc(y, s) == pytest.approx(roc_auc_score(y, s), abs=1e-12)
    assert np.isnan(M.auroc(np.zeros(5, bool), rng.random(5)))


def test_macro_f1_matches_sklearn():
    y = rng.integers(0, 5, 500)
    yh = rng.integers(0, 5, 500)
    assert M.macro_f1(y, yh) == pytest.approx(f1_score(y, yh, average="macro"), abs=1e-12)


def test_ece_hand_example():
    # two bins: confidence 0.9 with 50% correct (gap 0.4), confidence 0.6 with 100% correct (gap 0.4)
    conf = np.array([0.9, 0.9, 0.6, 0.6])
    correct = np.array([1, 0, 1, 1])
    assert M.ece(conf, correct, bins=10) == pytest.approx(0.4)
    assert M.ece(np.array([0.8] * 5), np.array([1, 1, 1, 1, 0]), 10) == pytest.approx(0.0)


def test_brier():
    p = np.array([[1, 0, 0, 0, 0], [0.5, 0.5, 0, 0, 0]], float)
    assert M.brier_multiclass(p, [0, 0]) == pytest.approx((0 + 0.5) / 2)
    assert M.brier_binary([0.8, 0.2], [1, 1]) == pytest.approx((0.04 + 0.64) / 2)


def test_threshold_reaches_target_sensitivity():
    for _ in range(20):
        y = rng.random(500) < 0.2
        s = rng.random(500) + 0.5 * y
        t = M.threshold_for_sensitivity(y, s, 0.9)
        sens = (s[y] >= t).mean()
        assert sens >= 0.9
        higher = np.sort(s[y])
        nxt = higher[higher > t]
        if len(nxt):                                        # the next threshold up would fall below the target
            assert (s[y] >= nxt[0]).mean() < 0.9


def test_sens_at_spec():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1], bool)
    s = np.array([0.1, 0.2, 0.3, 0.6, 0.25, 0.5, 0.7, 0.9])
    assert M.sens_at_spec(y, s, 0.75) == pytest.approx(0.75)   # threshold just above 0.3
    assert M.sens_at_spec(y, s, 1.0) == pytest.approx(0.5)     # threshold just above 0.6
    assert M.sens_at_spec(y, s, 0.0) == 1.0


def test_selective_prediction():
    conf = np.array([0.9, 0.8, 0.7, 0.6])
    correct = np.array([1, 1, 0, 0])
    assert M.risk_at_coverage(conf, correct, 0.5) == 0.0
    assert M.risk_at_coverage(conf, correct, 1.0) == 0.5
    assert M.aurc(conf, correct) == pytest.approx(np.mean([0, 0, 1 / 3, 0.5]))
    assert M.coverage_at_accuracy(conf, correct, 0.95) == 0.5


def test_holm():
    assert M.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_temperature_recovers_known_value():
    n, k, true_t = 20000, 5, 2.0
    logits = rng.normal(0, 2, (n, k))
    p_true = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
    y = np.array([rng.choice(k, p=row) for row in p_true])
    sharp = np.exp(logits * true_t)                          # an over-confident model: logits multiplied by 2
    sharp /= sharp.sum(1, keepdims=True)
    t = calibrate.fit_temperature(sharp, y)
    assert t == pytest.approx(true_t, rel=0.05)
    p_cal, _ = calibrate.apply_temperature(sharp, None, t)
    conf, ok = p_cal.max(1), p_cal.argmax(1) == y
    assert M.ece(conf, ok) < 0.02 < M.ece(sharp.max(1), sharp.argmax(1) == y)


def test_temperature_keeps_unknown_separate():
    p = np.array([[0.7, 0.3], [0.2, 0.8]])
    u = np.array([0.1, 0.5])
    p2, u2 = calibrate.apply_temperature(p, u, 1.0)
    assert np.allclose(p2, p) and np.allclose(u2, u)
    p3, u3 = calibrate.apply_temperature(p, u, 3.0)
    assert np.allclose(p3.sum(1), 1) and (u3 > 0).all() and p3[0, 0] < 0.7    # softened, still a distribution
