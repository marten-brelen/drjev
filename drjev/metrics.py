"""Metric functions on plain numpy arrays. Each returns nan when it is undefined for the data given."""
from __future__ import annotations

import numpy as np
from scipy.stats import rankdata

NAN = float("nan")


def qwk(y, yhat, k: int = 5) -> float:
    """Quadratic weighted kappa between two integer gradings in 0..k-1."""
    if len(y) == 0:
        return NAN
    o = np.zeros((k, k))
    np.add.at(o, (np.asarray(y, int), np.asarray(yhat, int)), 1)
    w = (np.subtract.outer(np.arange(k), np.arange(k)) ** 2) / (k - 1) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    den = (w * e).sum()
    return float(1 - (w * o).sum() / den) if den > 0 else NAN


def auroc(y, s) -> float:
    y = np.asarray(y, bool)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return NAN
    r = rankdata(s)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def sens_spec(y, pred) -> tuple[float, float]:
    y, pred = np.asarray(y, bool), np.asarray(pred, bool)
    n1, n0 = y.sum(), (~y).sum()
    return (float((pred & y).sum() / n1) if n1 else NAN, float((~pred & ~y).sum() / n0) if n0 else NAN)


def threshold_for_sensitivity(y, s, target: float) -> float:
    """Largest threshold t such that calling s >= t positive gives sensitivity >= target."""
    pos = np.sort(np.asarray(s, float)[np.asarray(y, bool)])
    if len(pos) == 0:
        return 0.5
    return float(pos[int(np.floor(len(pos) * (1 - target) + 1e-9))])


def sens_at_spec(y, s, spec: float) -> float:
    """Sensitivity at the lowest threshold whose specificity is at least `spec`."""
    y, s = np.asarray(y, bool), np.asarray(s, float)
    neg = np.sort(s[~y])
    if len(neg) == 0 or y.sum() == 0 or np.isnan(spec):
        return NAN
    k = int(np.ceil(spec * len(neg) - 1e-9))
    if k <= 0:
        return 1.0
    t = neg[k - 1]                       # calls are positive strictly above t, so k negatives fall below
    return float((s[y] > t).mean())


def ece(conf, correct, bins: int = 15) -> float:
    """Expected calibration error: confidence-weighted gap between confidence and accuracy, equal-width bins."""
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    if len(conf) == 0:
        return NAN
    b = np.minimum((conf * bins).astype(int), bins - 1)
    n = np.bincount(b, minlength=bins)
    sc = np.bincount(b, weights=conf, minlength=bins)
    sa = np.bincount(b, weights=correct, minlength=bins)
    m = n > 0
    return float((np.abs(sa[m] - sc[m])).sum() / len(conf))


def brier_multiclass(p, y) -> float:
    p = np.asarray(p, float)
    if len(p) == 0:
        return NAN
    onehot = np.zeros_like(p)
    onehot[np.arange(len(p)), np.asarray(y, int)] = 1
    return float(((p - onehot) ** 2).sum(1).mean())


def brier_binary(p, y) -> float:
    p = np.asarray(p, float)
    return float(((p - np.asarray(y, float)) ** 2).mean()) if len(p) else NAN


def _risk_curve(conf, correct):
    correct = np.asarray(correct, float)
    order = np.lexsort((correct, -np.asarray(conf, float)))   # ties in confidence: errors first, so the curve never depends on row order
    err = 1 - correct[order]
    return np.cumsum(err) / np.arange(1, len(err) + 1)


def aurc(conf, correct) -> float:
    """Area under the risk-coverage curve: mean error over all coverage levels, most confident first."""
    return float(_risk_curve(conf, correct).mean()) if len(conf) else NAN


def risk_at_coverage(conf, correct, coverage: float) -> float:
    if len(conf) == 0:
        return NAN
    r = _risk_curve(conf, correct)
    return float(r[max(1, int(np.ceil(coverage * len(r)))) - 1])


def coverage_at_accuracy(conf, correct, accuracy: float) -> float:
    """Largest share of cases that can be answered (most confident first) while keeping accuracy >= target."""
    if len(conf) == 0:
        return NAN
    ok = np.where(1 - _risk_curve(conf, correct) >= accuracy)[0]
    return float((ok[-1] + 1) / len(conf)) if len(ok) else 0.0


def macro_f1(y, yhat, k: int = 5) -> float:
    y, yhat = np.asarray(y, int), np.asarray(yhat, int)
    f = []
    for c in range(k):
        tp = ((y == c) & (yhat == c)).sum()
        fp = ((y != c) & (yhat == c)).sum()
        fn = ((y == c) & (yhat != c)).sum()
        if tp + fp + fn:
            f.append(2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f)) if f else NAN


def holm(pvals: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the original order."""
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()
