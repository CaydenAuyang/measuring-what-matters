"""Tests of the analysis code on made-up series where the answer is known. Run before any real result is trusted."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import stats_lib as S

def make_pair(name, n, beta, rng, freq="M", asym=None):
    # AR(1) official change, attention = beta * official + noise
    o = np.zeros(n); e = rng.normal(size=n)
    for i in range(1, n): o[i] = 0.8 * o[i - 1] + e[i]
    noise = np.zeros(n); e2 = rng.normal(size=n)
    for i in range(1, n): noise[i] = 0.8 * noise[i - 1] + e2[i]
    if asym:
        a = asym[0] * np.clip(o, 0, None) + asym[1] * np.clip(o, None, 0) + noise
    else:
        a = beta * o + noise
    t = pd.period_range("2015-01", periods=n, freq="M")
    return pd.DataFrame({"pair": name, "t": t, "a": a / a.std(), "o": o / o.std(), "freq": freq})

def main():
    rng = np.random.default_rng(0); ok = True; OUT = {}
    # 1. yearly change rules
    idx = pd.period_range("2010-01", periods=48, freq="M")
    s = pd.Series(100 * 1.02 ** (np.arange(48) / 12), index=idx)           # grows 2% a year
    ch = S.yearly_change(s, "pct_log", "higher")
    assert abs(ch.iloc[-1] - 100 * np.log(1.02)) < 1e-9, ch.iloc[-1]
    assert abs(S.yearly_change(s, "points", "lower").iloc[-1] + (s.iloc[-1] - s.iloc[-13])) < 1e-9
    infl = S.yearly_change(s, "inflation_points", "faster")                # constant inflation -> zero change
    assert abs(infl.iloc[-1]) < 1e-9 and len(infl) == 24
    print("PASS yearly change: log percent, points with sign reversal, inflation points")
    # 2. two series that move together: slope recovered, interval excludes zero
    df = pd.concat([make_pair(f"p{i}", 120, 0.6, rng) for i in range(12)])
    r = S.pooled_bootstrap(df, reps=400)
    print("together: beta", round(r["beta"]["est"], 3), "CI", round(r["beta"]["ci_low"], 3), round(r["beta"]["ci_high"], 3), r["_n"])
    ok &= r["beta"]["ci_low"] > 0 and 0.2 < r["beta"]["est"] < 0.8
    OUT["series_that_move_together"] = {"slope": r["beta"]["est"], "ci_low": r["beta"]["ci_low"], "ci_high": r["beta"]["ci_high"], "interval_excludes_zero": bool(r["beta"]["ci_low"] > 0)}
    # 3. two series that do not move together: interval includes zero
    df0 = pd.concat([make_pair(f"p{i}", 120, 0.0, rng) for i in range(12)])
    r0 = S.pooled_bootstrap(df0, reps=400)
    print("unrelated: beta", round(r0["beta"]["est"], 3), "CI", round(r0["beta"]["ci_low"], 3), round(r0["beta"]["ci_high"], 3))
    ok &= r0["beta"]["ci_low"] < 0 < r0["beta"]["ci_high"]
    OUT["series_that_do_not"] = {"slope": r0["beta"]["est"], "ci_low": r0["beta"]["ci_low"], "ci_high": r0["beta"]["ci_high"], "interval_includes_zero": bool(r0["beta"]["ci_low"] < 0 < r0["beta"]["ci_high"])}
    # 4. false positive rate of the bootstrap on unrelated AR(1) series (should be near 5%, not 30%)
    fp = 0; trials = 40
    for k in range(trials):
        d = pd.concat([make_pair(f"p{i}", 120, 0.0, rng) for i in range(8)])
        rr = S.pooled_bootstrap(d, reps=200, seed=k)
        fp += not (rr["beta"]["ci_low"] < 0 < rr["beta"]["ci_high"])
    print(f"false positive rate on unrelated autocorrelated series: {fp}/{trials}")
    ok &= fp / trials <= 0.2
    OUT["false_positive_check"] = {"trials": trials, "intervals_that_wrongly_excluded_zero": int(fp), "rate": fp / trials, "nominal_rate": 0.05,
                                   "setup": "8 unrelated pairs of 120 months each, both series with month-to-month persistence 0.8, 12-month blocks"}
    # 5. asymmetry recovered
    dfa = pd.concat([make_pair(f"p{i}", 120, None, rng, asym=(0.9, 0.1)) for i in range(12)])
    ra = S.pooled_bootstrap(dfa, split=True, reps=400)
    print("asymmetry: worse", round(ra["beta_worse"]["est"], 2), "better", round(ra["beta_better"]["est"], 2), "diff CI", round(ra["diff"]["ci_low"], 2), round(ra["diff"]["ci_high"], 2))
    ok &= ra["diff"]["ci_low"] > 0
    OUT["asymmetry_built_in"] = {"worse": ra["beta_worse"]["est"], "better": ra["beta_better"]["est"], "diff_ci_low": ra["diff"]["ci_low"], "diff_ci_high": ra["diff"]["ci_high"]}
    rs = S.pooled_bootstrap(df, split=True, reps=400)
    print("symmetric case: diff", round(rs["diff"]["est"], 2), "CI", round(rs["diff"]["ci_low"], 2), round(rs["diff"]["ci_high"], 2))
    ok &= rs["diff"]["ci_low"] < 0 < rs["diff"]["ci_high"]
    # 6. equal weight per pair: one long pair must not swamp short ones
    mix = pd.concat([make_pair("long", 240, 0.9, rng)] + [make_pair(f"s{i}", 10, 0.0, rng, freq="A") for i in range(9)])
    print("equal weights: beta", round(S.pooled_fit(mix)["beta"], 3), "(long pair alone would give about 0.7)")
    ok &= S.pooled_fit(mix)["beta"] < 0.4
    # 7. lead/lag: attention follows official by 3 months
    n = 140; o = pd.Series(rng.normal(size=n)).rolling(6).mean().dropna().to_numpy()
    t = pd.period_range("2015-01", periods=len(o), freq="M")
    os_ = pd.Series(o, index=t); as_ = pd.Series(np.roll(o, 3) + 0.05 * rng.normal(size=len(o)), index=t)
    ll = S.lag_perm_test(as_.iloc[3:], os_.iloc[3:], reps=200)
    print("lead/lag: best lag", ll["best_lag"], "r", round(ll["best_r"], 2), "p", round(ll["p_perm"], 3))
    ok &= ll["best_lag"] == 3 and ll["p_perm"] < 0.05
    OUT["lead_lag_built_in_3_months"] = {"best_lag": ll["best_lag"], "r": ll["best_r"], "p_perm": ll["p_perm"]}
    # 8. opposite-direction share and runs
    a = np.array([1, 1, -1, -1, -1, -1, -1, -1, 1, 1.0]); o2 = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1.0])
    sh, m = S.opposite_share(a, o2); assert abs(sh - 0.6) < 1e-9
    runs = S.opposite_runs(pd.DataFrame({"t": pd.period_range("2020-01", periods=10, freq="M"), "a": a, "o": o2}))
    assert len(runs) == 1 and runs[0]["months"] == 6 and runs[0]["start"] == "2020-03", runs
    print("PASS opposite-direction share and six-month runs")
    # 9. Benjamini-Hochberg against a hand-worked case
    adj = S.benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(adj, [0.04, 0.0533333, 0.0533333, 0.5], atol=1e-5), adj
    print("PASS Benjamini-Hochberg")
    OUT["all_passed"] = bool(ok)
    import json
    pub = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "public")
    json.dump(OUT, open(os.path.join(pub, "synthetic_test_results.json"), "w"), indent=1)
    print("ALL SYNTHETIC TESTS PASSED" if ok else "SOME SYNTHETIC TESTS FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
