"""Statistics used in the analysis plan: yearly change, pooled regression with pair intercepts,
moving-block bootstrap, lead/lag with permutation tests, opposite-direction share, Benjamini-Hochberg.

Everything here is tested on made-up series in src/test_synthetic.py before it touches real data.
"""
import numpy as np, pandas as pd

BLOCK = {"M": 12, "Q": 4, "A": 1}      # a 12-month block in each frequency
STEP = {"M": 12, "Q": 4, "A": 1}

# ------------------------------------------------------------------ yearly change (Appendix C)
def yearly_change(s: pd.Series, rule: str, worse_when: str) -> pd.Series:
    """s is indexed by pandas Period('M') at the END month of each period. Compares each value with the
    value exactly 12 months earlier. Positive = the problem got worse."""
    s = s.dropna().sort_index()
    prev = pd.Series(s.reindex(s.index - 12).to_numpy(), index=s.index)
    if rule == "pct_log":
        ok = (s > 0) & (prev > 0)
        ch = pd.Series(np.nan, index=s.index)
        ch[ok] = 100 * np.log(s[ok] / prev[ok])
    elif rule == "points":
        ch = s - prev
    elif rule == "inflation_points":
        infl = 100 * (s / prev - 1)
        ch = infl - pd.Series(infl.reindex(infl.index - 12).to_numpy(), index=infl.index)
    else:
        raise ValueError(rule)
    if worse_when == "lower":
        ch = -ch
    return ch.dropna()

def window_mean(att: pd.Series, end_periods, window: int, min_frac=0.75) -> pd.Series:
    """Mean of a monthly attention series over the `window` months ending at each period end."""
    out = {}
    for t in end_periods:
        idx = [t - k for k in range(window)]
        v = att.reindex(idx).dropna()
        if len(v) >= max(1, int(np.ceil(window * min_frac))):
            out[t] = v.mean()
    return pd.Series(out, dtype=float)

# ------------------------------------------------------------------ pooled regression
def _fit_arrays(a, o, gid, ng, w, split):
    """Weighted least squares with a separate intercept per pair (weighted demeaning inside each pair)."""
    sw = np.bincount(gid, w, ng)
    def dm(x):
        return x - (np.bincount(gid, w * x, ng) / sw)[gid]
    ad = dm(a)
    if not split:
        od = dm(o); den = np.sum(w * od * od)
        return {"beta": float(np.sum(w * od * ad) / den) if den > 0 else np.nan}
    op = dm(np.clip(o, 0, None)); om = dm(np.clip(o, None, 0))
    X = np.column_stack([op, om]); XtX = X.T @ (X * w[:, None]); Xty = X.T @ (w * ad)
    try:
        bb = np.linalg.solve(XtX, Xty)
    except np.linalg.LinAlgError:
        bb = np.array([np.nan, np.nan])
    return {"beta_worse": float(bb[0]), "beta_better": float(bb[1]), "diff": float(bb[0] - bb[1])}

def _arrays(df):
    df = df.sort_values(["pair", "t"])
    codes, uniq = pd.factorize(df["pair"])
    n = np.bincount(codes)
    w = 1.0 / n[codes]                      # every pair gets equal total weight
    return df["a"].to_numpy(float), df["o"].to_numpy(float), codes, len(uniq), w, df

def pooled_fit(df: pd.DataFrame, split=False):
    """df columns: pair, t, a (attention change, standardized), o (official change, standardized).
    Separate intercept per pair; every pair gets equal total weight.
    Returns dict(beta) or dict(beta_worse, beta_better, diff) when split=True."""
    a, o, gid, ng, w, _ = _arrays(df)
    return _fit_arrays(a, o, gid, ng, w, split)

def block_resample_index(n, block, rng):
    """Moving-block bootstrap: indices for one resample of a series of length n."""
    if block <= 1 or n <= block:
        return rng.integers(0, n, n)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, nb)
    return (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]

def pooled_bootstrap(df: pd.DataFrame, split=False, reps=2000, seed=1, block_months=12):
    """Block bootstrap with 12-month blocks inside every pair. Returns point estimates, 95% intervals and p-values."""
    rng = np.random.default_rng(seed)
    a, o, gid, ng, w, d = _arrays(df)
    point = _fit_arrays(a, o, gid, ng, w, split)
    bounds = np.concatenate([[0], np.cumsum(np.bincount(gid))])
    freqs = d.groupby("pair", sort=True)["freq"].first().to_numpy()
    blocks = [max(1, int(round(BLOCK[f] * block_months / 12))) for f in freqs]
    draws = {k: np.empty(reps) for k in point}
    for r in range(reps):
        idx = np.concatenate([bounds[g] + block_resample_index(bounds[g + 1] - bounds[g], blocks[g], rng) for g in range(ng)])
        est = _fit_arrays(a[idx], o[idx], gid, ng, w, split)
        for k in point: draws[k][r] = est[k]
    out = {}
    for k in point:
        dd = draws[k][~np.isnan(draws[k])]
        lo, hi = np.percentile(dd, [2.5, 97.5])
        pv = 2 * min((dd <= 0).mean(), (dd >= 0).mean()); pv = min(1.0, max(pv, 1.0 / (len(dd) + 1)))
        out[k] = {"est": point[k], "ci_low": float(lo), "ci_high": float(hi), "p_boot": float(pv)}
    n_eff = sum((bounds[g + 1] - bounds[g]) / BLOCK[freqs[g]] for g in range(ng))
    out["_n"] = {"n_obs": int(len(d)), "n_pairs": int(ng), "n_eff_years": float(round(n_eff, 1))}
    return out

# ------------------------------------------------------------------ pair level
def pair_corr_boot(a, o, block, reps=2000, seed=2):
    a = np.asarray(a, float); o = np.asarray(o, float); n = len(a)
    if n < 4 or np.std(a) == 0 or np.std(o) == 0:
        return {"r": np.nan, "p": np.nan, "ci_low": np.nan, "ci_high": np.nan, "n": int(n)}
    r = float(np.corrcoef(a, o)[0, 1])
    rng = np.random.default_rng(seed); d = []
    for _ in range(reps):
        idx = block_resample_index(n, block, rng)
        aa, oo = a[idx], o[idx]
        if np.std(aa) > 0 and np.std(oo) > 0:
            d.append(np.corrcoef(aa, oo)[0, 1])
    d = np.array(d)
    p = 2 * min((d <= 0).mean(), (d >= 0).mean()); p = min(1.0, max(p, 1.0 / (len(d) + 1)))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"r": r, "p": float(p), "ci_low": float(lo), "ci_high": float(hi), "n": int(n)}

def benjamini_hochberg(pvals):
    p = np.asarray(pvals, float); out = np.full(len(p), np.nan)
    ok = ~np.isnan(p); m = ok.sum()
    if m == 0: return out
    order = np.argsort(p[ok]); ranked = p[ok][order]
    adj = ranked * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    res = np.empty(m); res[order] = np.minimum(adj, 1.0)
    out[ok] = res
    return out

# ------------------------------------------------------------------ lead / lag
def _grid(a: pd.Series, o: pd.Series):
    idx = pd.period_range(min(a.index.min(), o.index.min()), max(a.index.max(), o.index.max()), freq="M")
    return a.reindex(idx).to_numpy(float), o.reindex(idx).to_numpy(float)

def _lagc(av, ov, lags, min_n=24):
    out = {}
    n = len(av)
    for k in lags:                      # corr(a[t+k], o[t])
        if k >= 0: x, y = av[k:], ov[:n - k]
        else:      x, y = av[:n + k], ov[-k:]
        m = ~np.isnan(x) & ~np.isnan(y)
        if m.sum() >= min_n and np.std(x[m]) > 0 and np.std(y[m]) > 0:
            out[k] = float(np.corrcoef(x[m], y[m])[0, 1])
        else:
            out[k] = np.nan
    return out

def lag_corr(a: pd.Series, o: pd.Series, lags=range(-12, 13)):
    """corr(a[t+k], o[t]). k > 0 means attention moves AFTER the official series (official leads)."""
    av, ov = _grid(a, o)
    return _lagc(av, ov, lags)

def lag_perm_test(a: pd.Series, o: pd.Series, reps=1000, seed=3, lags=range(-12, 13)):
    """Permutation test by circular shifts of the attention series (keeps its own time pattern).
    Returns the lag with the largest |r|, that r, and the share of shifted series with a peak at least as large."""
    av, ov = _grid(a, o)
    obs = _lagc(av, ov, lags)
    vals = {k: v for k, v in obs.items() if not np.isnan(v)}
    if not vals:
        return {"best_lag": None, "best_r": np.nan, "p_perm": np.nan, "by_lag": obs}
    best = max(vals, key=lambda k: abs(vals[k])); peak = abs(vals[best])
    rng = np.random.default_rng(seed); n = len(av); cnt = 0; done = 0
    for _ in range(reps):
        sh = int(rng.integers(13, n - 13)) if n > 40 else int(rng.integers(1, max(2, n)))
        v = [abs(x) for x in _lagc(np.roll(av, sh), ov, lags).values() if not np.isnan(x)]
        if v:
            done += 1; cnt += max(v) >= peak
    return {"best_lag": int(best), "best_r": float(vals[best]), "p_perm": float((cnt + 1) / (done + 1)), "by_lag": obs}

# ------------------------------------------------------------------ disconnection (H3)
def opposite_share(a, o):
    a = np.asarray(a, float); o = np.asarray(o, float)
    m = (a != 0) & (o != 0) & ~np.isnan(a) & ~np.isnan(o)
    if m.sum() == 0: return np.nan, 0
    return float((np.sign(a[m]) != np.sign(o[m])).mean()), int(m.sum())

def opposite_runs(df: pd.DataFrame, min_len=6):
    """df: t (monthly Period), a, o. Returns runs of consecutive months moving in opposite directions."""
    d = df.sort_values("t").reset_index(drop=True)
    opp = (np.sign(d.a) != np.sign(d.o)) & (d.a != 0) & (d.o != 0)
    runs, start = [], None
    for i in range(len(d)):
        consecutive = i > 0 and (d.t[i] - d.t[i - 1]).n == 1
        if opp[i] and start is not None and consecutive:
            continue
        if start is not None and (not opp[i] or not consecutive):
            if i - start >= min_len: runs.append((start, i - 1))
            start = None
        if opp[i] and start is None:
            start = i
    if start is not None and len(d) - start >= min_len: runs.append((start, len(d) - 1))
    out = []
    for s, e in runs:
        seg = d.iloc[s:e + 1]
        out.append({"start": str(seg.t.iloc[0]), "end": str(seg.t.iloc[-1]), "months": int(len(seg)),
                    "official_direction": "worsening" if seg.o.mean() > 0 else "improving",
                    "attention_direction": "rising" if seg.a.mean() > 0 else "falling",
                    "mean_official_change_sd": float(seg.o.mean()), "mean_attention_change_sd": float(seg.a.mean())})
    return out
