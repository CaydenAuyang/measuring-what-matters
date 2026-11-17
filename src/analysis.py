"""Phase 7: the pre-registered analysis. Writes data/public/results.json with every reported number.

Main tests (four): pooled H1 and H2 models, for news and for search.
Everything else is description or a check that the results hold. Lead/lag is exploratory.

Usage: python src/analysis.py [--reps 2000] [--cities hk,nyc,london] [--quick]
"""
import argparse, datetime, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import outlets, codebook, stats_lib as S, pairs as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "data/public")
INT = os.path.join(ROOT, "data/interim")
SOURCES = ["news", "search"]

def jload(path, default=None):
    return json.load(open(path)) if os.path.exists(path) else default

def skip_sets(cities):
    """Pairs left out of the tests, with the reason: news categories that failed validation; search sets too sparse."""
    cfg = jload(os.path.join(INT, "index_config.json"), {})
    tm = jload(os.path.join(INT, "trends/trends_meta.json"), {})
    news = {}
    for c, cats in cfg.get("dropped_categories", {}).items():
        for k in cats: news[(c, k)] = "dropped: agreement between the two AI coders below 0.61"
    search = {}
    sparse = tm.get("sparse_sets") or {}
    for c in outlets.CITIES:
        for k in sparse.get(c, []):
            search[(c, k)] = "search set too sparse to test (zero in more than 10% of months)"
    for d in (news, search):
        for c in outlets.CITIES:
            if c not in cities:
                for k in outlets.COMPARED: d[(c, k)] = "city not in this run"
    return {"news": news, "search": search}

def trends_sparse_from_meta():
    """Fill sparse sets from the trends meta file whatever its exact layout."""
    tm = jload(os.path.join(INT, "trends/trends_meta.json"), {})
    out = {c: [] for c in outlets.CITIES}
    def walk(node, city=None):
        if isinstance(node, dict):
            if "sparse" in node and ("category" in node or city):
                pass
            for k, v in node.items():
                walk(v, city)
    # preferred: recompute from the shares file, which carries sparse_flag per city and category
    p = os.path.join(INT, "trends/trends_shares.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        if "sparse_flag" in d.columns:
            for (c, k), g in d.groupby(["city", "category"]):
                if g.sparse_flag.astype(str).str.lower().isin(["1", "true", "1.0"]).any(): out[c].append(k)
    return out

def subset(df, mode):
    if mode == "all": return df
    if mode == "no_covid": return df[~df.covid]
    if mode == "no_breaks": return df[~df.brk_any]
    raise ValueError(mode)

def pooled(df, reps, seed=1, block_months=12):
    if df.empty or df.pair.nunique() < 2:
        return None
    h1 = S.pooled_bootstrap(df, split=False, reps=reps, seed=seed, block_months=block_months)
    h2 = S.pooled_bootstrap(df, split=True, reps=reps, seed=seed + 1, block_months=block_months)
    return {"h1": {**h1["beta"], **h1["_n"]}, "h2": {"worse": h2["beta_worse"], "better": h2["beta_better"], "diff": h2["diff"], **h2["_n"]}}

def run_models(source, skips, reps, **kw):
    mode = kw.pop("mode", "all"); block_months = kw.pop("block_months", 12)
    if source == "news" and not os.path.exists(os.path.join(PUB, "news_attention_monthly.csv")):
        return None, [], pd.DataFrame()
    df, infos = P.build_pairs(source, skip=skips[source], **kw)
    if df.empty: return None, infos, df
    d = subset(df, mode)
    # a pair needs enough periods left after the cut
    keep = [p for p, g in d.groupby("pair") if len(g) >= P.MIN_OBS[g.freq.iloc[0]] // 2]
    d = d[d.pair.isin(keep)]
    return pooled(d, reps, block_months=block_months), infos, d

def by_group(df, col, reps):
    out = {}
    for k, g in df.groupby(col):
        if g.pair.nunique() >= 1 and len(g) >= 5:
            r = S.pooled_bootstrap(g, split=False, reps=reps, seed=11)
            out[k] = {**r["beta"], **r["_n"], "pairs": sorted(g.pair.unique())}
    return out

def pair_table(dfs, infos_all, reps):
    rows = []
    for source in SOURCES:
        df = dfs[source]
        for info in infos_all[source]:
            row = {"pair": info["pair"], "city": info["city"], "category": info["category"], "source": source,
                   "indicator": info.get("name"), "freq": info.get("freq"), "excluded": info.get("excluded")}
            if not info.get("excluded") and not df.empty:
                g = df[df.pair == info["pair"]].sort_values("t")
                c = S.pair_corr_boot(g.a.to_numpy(), g.o.to_numpy(), S.BLOCK[info["freq"]], reps=reps)
                opp, m = S.opposite_share(g.a.to_numpy(), g.o.to_numpy())
                slope = float(np.polyfit(g.o, g.a, 1)[0]) if len(g) > 2 else np.nan
                row.update({"n": c["n"], "n_eff_years": round(len(g) / S.BLOCK[info["freq"]], 1), "first": info["first"], "last": info["last"],
                            "r": c["r"], "r_ci_low": c["ci_low"], "r_ci_high": c["ci_high"], "slope_sd": slope, "p": c["p"],
                            "opposite_share": opp, "opposite_n": m})
            rows.append(row)
    t = pd.DataFrame(rows)
    t["p_bh"] = S.benjamini_hochberg(t["p"].to_numpy(float)) if "p" in t.columns else np.nan
    return t

EVENTS = [  # known events used when proposing a cause for a disconnection (from the methodology's breaks table)
    ("all", None, "2020-01", "2022-12", "event", "COVID-19 distorts nearly every series"),
    ("hk", None, "2019-01", "2020-12", "event", "2019 protests and the 2020 National Security Law dominate coverage"),
    ("hk", None, "2021-01", "2021-12", "event", "several major outlets closed in 2021"),
    ("hk", "safety", "2023-01", "2026-12", "different", "online fraud drives the rise in reported crime from 2023"),
    ("nyc", "housing", "2022-04", "2024-12", "event", "asylum-seeker arrivals raise the shelter count"),
    ("nyc", "environment", "2023-06", "2024-06", "event", "June 2023 wildfire smoke"),
    ("london", "environment", "2019-04", "2024-08", "event", "Ultra Low Emission Zone start and expansions cut pollution"),
]

def propose_cause(city, category, run, brk_method, source):
    """A first-pass cause from the methodology's five options. Proposed by AI for Cayden to confirm."""
    s, e = pd.Period(run["start"], "M"), pd.Period(run["end"], "M")
    def overlaps(a, b): return not (pd.Period(b, "M") < s or pd.Period(a, "M") > e)
    if brk_method >= 0.5:
        return "the official measure changed how it counts", "at least half of these months are marked as a counting break in the official series"
    for c, k, a, b, kind, note in EVENTS:
        if c in (city, "all") and k in (category, None) and overlaps(a, b):
            if kind == "different":
                return "the two measure different parts of the problem", note
            if run["attention_direction"] == "rising" and run["official_direction"] == "improving":
                return "a real event drew coverage the indicator does not capture", note
            if run["attention_direction"] == "falling" and run["official_direction"] == "worsening":
                return "attention followed a news cycle rather than conditions", f"attention share fell while the indicator worsened; the period overlaps: {note} (a spike elsewhere lowers every other share)"
    if run["attention_direction"] == "falling" and run["official_direction"] == "worsening":
        return "attention followed a news cycle rather than conditions", "the indicator kept worsening while attention's share fell (Downs's issue-attention cycle); no marked break or event overlaps"
    return "unclear", "no marked break or named event overlaps this period"

def h3_block(dfs, infos_all):
    out = {"opposite_share": {}, "safety_rank": {}, "runs": []}
    for source in SOURCES:
        df = dfs[source]; tab = {}
        for city in outlets.CITIES:
            tab[city] = {}
            for cat in outlets.COMPARED:
                g = df[(df.city == city) & (df.category == cat)] if not df.empty else pd.DataFrame()
                if len(g):
                    sh, m = S.opposite_share(g.a.to_numpy(), g.o.to_numpy())
                    tab[city][cat] = {"share": sh, "n": m, "freq": g.freq.iloc[0]}
                    if g.freq.iloc[0] == "M":
                        for run in S.opposite_runs(g[["t", "a", "o"]]):
                            seg = g[(g.t >= pd.Period(run["start"], "M")) & (g.t <= pd.Period(run["end"], "M"))]
                            cause, evidence = propose_cause(city, cat, run, float(seg.brk_official.mean()), source)
                            run.update({"city": city, "category": cat, "source": source, "proposed_cause": cause, "evidence": evidence,
                                        "proposed_by": "AI, for Cayden to confirm"})
                            out["runs"].append(run)
        out["opposite_share"][source] = tab
        rank = {}
        for city in outlets.CITIES:
            cats = {k: v["share"] for k, v in tab[city].items() if v["share"] == v["share"]}
            if "safety" in cats and len(cats) >= 2:
                order = sorted(cats, key=lambda k: -cats[k])
                rank[city] = {"safety_rank": order.index("safety") + 1, "of": len(order), "largest": order[0], "largest_share": cats[order[0]],
                              "safety_share": cats["safety"], "order": order}
            else:
                rank[city] = {"safety_rank": None, "of": len(cats), "note": "Safety not testable in this city"}
        n_top = sum(1 for c in rank.values() if c.get("safety_rank") == 1)
        out["safety_rank"][source] = {"by_city": rank, "cities_where_safety_is_largest": n_top, "h3_supported": bool(n_top >= 2)}
    out["runs"] = sorted(out["runs"], key=lambda r: -r["months"])
    return out

def leadlag_block(dfs, reps):
    out = {"by_pair": [], "by_category": {}}
    for source in SOURCES:
        df = dfs[source]
        if df.empty: continue
        curves = {}
        for pair, g in df[df.freq == "M"].groupby("pair"):
            g = g.sort_values("t")
            a = pd.Series(g.a.to_numpy(), index=pd.PeriodIndex(g.t, freq="M")); o = pd.Series(g.o.to_numpy(), index=pd.PeriodIndex(g.t, freq="M"))
            r = S.lag_perm_test(a, o, reps=reps)
            city, cat, _ = pair.split("|")
            out["by_pair"].append({"pair": pair, "city": city, "category": cat, "source": source, "best_lag_months": r["best_lag"],
                                   "best_r": r["best_r"], "p_perm": r["p_perm"], "r_at_lag0": r["by_lag"].get(0)})
            curves.setdefault(cat, []).append(r["by_lag"])
        cat_out = {}
        for cat, lst in curves.items():
            mean = {k: float(np.nanmean([c[k] for c in lst])) for k in range(-12, 13)}
            best = max(mean, key=lambda k: abs(mean[k]) if mean[k] == mean[k] else -1)
            cat_out[cat] = {"mean_r_by_lag": mean, "best_lag_months": int(best), "best_mean_r": mean[best], "n_cities": len(lst)}
        out["by_category"][source] = cat_out
    # news against search, all twelve categories
    try:
        news = P.attention_tables("news"); search = P.attention_tables("search")
        ns = {}
        for cat in outlets.CATEGORIES:
            curves = []
            for city in outlets.CITIES:
                if city in news and city in search and cat in news[city] and cat in search[city]:
                    a = (news[city][cat] * 100).dropna(); b = (search[city][cat] * 100).dropna()
                    da = (a - pd.Series(a.reindex(a.index - 12).to_numpy(), index=a.index)).dropna()
                    db = (b - pd.Series(b.reindex(b.index - 12).to_numpy(), index=b.index)).dropna()
                    if len(da) >= 36 and len(db) >= 36 and da.std() > 0 and db.std() > 0:
                        curves.append(S.lag_corr(da / da.std(), db / db.std()))   # k > 0: news moves after search
            if curves:
                mean = {k: float(np.nanmean([c[k] for c in curves])) for k in range(-12, 13)}
                best = max(mean, key=lambda k: abs(mean[k]) if mean[k] == mean[k] else -1)
                ns[cat] = {"mean_r_by_lag": mean, "best_lag_months": int(best), "best_mean_r": mean[best], "r_at_lag0": mean[0], "n_cities": len(curves)}
        out["news_vs_search"] = ns
    except Exception as e:  # pragma: no cover
        out["news_vs_search"] = {"error": str(e)}
    return out

def ranking_block(cities):
    """Current-year summary: how far each official indicator sits from its 2015-2019 average (in SDs, worse = positive),
    next to the ranking by news attention over the latest 12 months."""
    d, meta = P.official_tables()
    try: news = P.attention_tables("news")
    except Exception: news = {}
    out = {}
    for city in cities:
        rows = []
        for cat in outlets.COMPARED:
            sub = d[(d.city == city) & (d.category == cat) & (d.role == "main")]
            z = None; latest = None; n_base = 0
            if len(sub):
                rule = sub.change_rule.iloc[0]; worse = sub.worse_when.iloc[0]; zs = []
                for comp, g in sub.groupby("component"):
                    s = pd.Series(g["value"].to_numpy(float), index=pd.PeriodIndex(g["end"], freq="M")).sort_index()
                    if rule == "inflation_points":     # the problem is how fast prices rise: use the 12-month rate
                        s = (100 * (s / pd.Series(s.reindex(s.index - 12).to_numpy(), index=s.index) - 1)).dropna()
                    base = s[(s.index >= pd.Period("2015-01", "M")) & (s.index <= pd.Period("2019-12", "M"))]
                    last12 = s[s.index > s.index.max() - 12] if sub.frequency.iloc[0] == "M" else s.iloc[-1:]
                    if len(base) >= 3 and base.std(ddof=1) > 0:
                        zc = (last12.mean() - base.mean()) / base.std(ddof=1)
                        zs.append(-zc if worse == "lower" else zc); n_base = len(base); latest = str(s.index.max())
                z = float(np.mean(zs)) if zs else None
            att = None
            if city in news and cat in news[city]:
                a = news[city][cat].dropna(); att = float(a[a.index > a.index.max() - 12].mean() * 100) if len(a) else None
            rows.append({"category": cat, "official_z_vs_2015_2019": z, "official_latest_period": latest, "baseline_points": n_base, "news_share_pct_latest_12m": att})
        zr = sorted([r for r in rows if r["official_z_vs_2015_2019"] is not None], key=lambda r: -r["official_z_vs_2015_2019"])
        ar = sorted([r for r in rows if r["news_share_pct_latest_12m"] is not None], key=lambda r: -r["news_share_pct_latest_12m"])
        for r in rows:
            r["official_rank"] = zr.index(r) + 1 if r in zr else None
            r["attention_rank"] = ar.index(r) + 1 if r in ar else None
        both = [r for r in rows if r["official_rank"] and r["attention_rank"]]
        rho = float(pd.Series([r["official_rank"] for r in both]).corr(pd.Series([r["attention_rank"] for r in both]), method="spearman")) if len(both) >= 4 else None
        out[city] = {"rows": rows, "spearman_rank_correlation": rho, "n_categories": len(both)}
    return out

def signal_only_block(cities):
    out = {}
    for source in SOURCES:
        try: tabs = P.attention_tables(source)
        except Exception: continue
        out[source] = {}
        for city in cities:
            if city not in tabs: continue
            out[source][city] = {}
            for cat in outlets.SIGNAL_ONLY:
                if cat not in tabs[city]: continue
                s = (tabs[city][cat] * 100).dropna()
                s = s[s.index >= pd.Period("2015-01", "M")]
                yearly = s.groupby(s.index.year).mean()
                out[source][city][cat] = {"yearly_mean_share_pct": {int(y): float(v) for y, v in yearly.items()},
                                          "peak_month": str(s.idxmax()) if len(s) else None, "peak_share_pct": float(s.max()) if len(s) else None,
                                          "mean_2015_2019": float(s[s.index.year <= 2019].mean()), "mean_2023_2026": float(s[s.index.year >= 2023].mean())}
    return out

def counts_block(cities):
    info = jload(os.path.join(INT, "index_info.json"), {})
    mc = pd.read_csv(os.path.join(INT, "gdelt/monthly_counts.csv"))
    d, meta = P.official_tables()
    ts = pd.read_csv(os.path.join(INT, "trends/trends_shares.csv"))
    tm = jload(os.path.join(INT, "trends/trends_meta.json"), {})
    npath = os.path.join(PUB, "news_attention_monthly.csv")
    news = pd.read_csv(npath) if os.path.exists(npath) else pd.DataFrame({"variant": [], "month": []})
    nm = news[news.variant == "main"]
    return {
        "cities": len(cities), "city_list": cities,
        "outlets_main_panel": {c: len(outlets.MAIN_PANEL[c]) for c in cities}, "outlets_main_panel_total": sum(len(outlets.MAIN_PANEL[c]) for c in cities),
        "outlets_listed": {c: len(outlets.ALL_LISTED[c]) for c in cities}, "outlets_listed_total": sum(len(outlets.ALL_LISTED[c]) for c in cities),
        "gdelt_rows_listed_outlets": int(mc.n_gdelt_rows.sum()), "articles_after_city_filter": int(mc.n_after_filter.sum()),
        "articles_labeled_main_panel": info.get("n_labeled_main"), "articles_labeled_main_panel_total": int(sum((info.get("n_labeled_main") or {}).values())),
        "articles_labeled_all": info.get("n_labeled_all"), "labeling_round": info.get("level"), "caps_hk_nyc_london": info.get("caps_hk_nyc_london"),
        "news_months": int(nm.month.nunique()), "news_first_month": str(nm.month.min()) if len(nm) else None, "news_last_month": str(nm.month.max()) if len(nm) else None,
        "official_series_main": int(d[d.role == "main"].series_id.nunique()), "official_series_backup": int(d[d.role == "backup"].series_id.nunique()),
        "official_series_total": int(d.series_id.nunique()), "official_values": int(len(d)),
        "search_months": int(ts.month.nunique()), "search_first_month": str(ts.month.min()), "search_last_month": str(ts.month.max()),
        "search_downloads_per_request": int(ts.n_downloads.max()) if "n_downloads" in ts.columns else None,
        "search_requests": 9, "search_term_sets": 36,
    }

SRC_NAME = {"news": "news coverage", "search": "search interest"}

def verdicts_block(R):
    """Plain sentences for each hypothesis, built from the numbers, so every document says the same thing."""
    V = {}
    for s in SOURCES:
        m = (R.get("main") or {}).get(s)
        nm = SRC_NAME[s]
        if not m:
            V[f"h1_{s}"] = "not available"; V[f"h1_{s}_sentence"] = f"No pooled result is available for {nm}."
            V[f"h2_{s}"] = "not available"; V[f"h2_{s}_sentence"] = f"No pooled result is available for {nm}."
        else:
            h = m["h1"]; e, lo, hi = h["est"], h["ci_low"], h["ci_high"]
            rng = f"(95% interval {lo:.2f} to {hi:.2f}, {h['n_pairs']} city and category pairs, about {h['n_eff_years']:.0f} independent pair-years)"
            if lo > 0:
                V[f"h1_{s}"] = "supported"
                size = "a weak link" if e < 0.3 else ("a moderate link" if e < 0.5 else "a strong link")
                V[f"h1_{s}_sentence"] = f"For {nm}, attention rose {e:.2f} standard deviations for each standard deviation the official measure worsened {rng}. That is {size}, and the interval excludes zero, so H1 is supported for {nm}."
            elif hi < 0:
                V[f"h1_{s}"] = "failed"
                V[f"h1_{s}_sentence"] = f"For {nm}, attention moved the opposite way: the pooled slope was {e:.2f} {rng}. H1 failed for {nm}."
            else:
                V[f"h1_{s}"] = "not supported"
                V[f"h1_{s}_sentence"] = f"For {nm}, the pooled slope was {e:.2f} {rng}. The interval includes zero, so H1 is not supported for {nm}."
            h2 = m["h2"]; w, b, d = h2["worse"], h2["better"], h2["diff"]
            det = f"The slope was {w['est']:.2f} when the problem worsened and {b['est']:.2f} when it improved. The difference was {d['est']:.2f} (95% interval {d['ci_low']:.2f} to {d['ci_high']:.2f})."
            if d["ci_low"] > 0:
                V[f"h2_{s}"] = "supported"; V[f"h2_{s}_sentence"] = f"For {nm}, attention reacted more to worsening than to improving. {det} H2 is supported for {nm}."
            elif d["ci_high"] < 0:
                V[f"h2_{s}"] = "failed"; V[f"h2_{s}_sentence"] = f"For {nm}, attention reacted more to improving than to worsening, the opposite of H2. {det}"
            else:
                V[f"h2_{s}"] = "not supported"; V[f"h2_{s}_sentence"] = f"For {nm}, the reaction to worsening and to improving could not be told apart. {det} The interval includes zero, so H2 is not supported for {nm}."
        sr = ((R.get("h3") or {}).get("safety_rank") or {}).get(s)
        if not m:
            V[f"h3_{s}"] = "not available"; V[f"h3_{s}_sentence"] = f"No result is available for {nm}."
        elif sr:
            parts = []
            for c in outlets.CITIES:
                bc = sr["by_city"].get(c, {})
                if bc.get("safety_rank"):
                    parts.append(f"{outlets.CITY_NAMES[c]}: Safety ranked {bc['safety_rank']} of {bc['of']} ({bc['safety_share'] * 100:.0f}% of periods moved in opposite directions; the largest was {outlets.CATEGORY_NAMES[bc['largest']]} at {bc['largest_share'] * 100:.0f}%)")
                else:
                    parts.append(f"{outlets.CITY_NAMES[c]}: Safety could not be tested")
            V[f"h3_{s}"] = "supported" if sr["h3_supported"] else "not supported"
            V[f"h3_{s}_sentence"] = (f"For {nm}, Safety showed the largest gap in {sr['cities_where_safety_is_largest']} of 3 cities. " + ". ".join(parts) + ". "
                                     + ("H3 is supported." if sr["h3_supported"] else "H3 predicted the largest gap in at least two cities, so it is not supported."))
    return V

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2000); ap.add_argument("--cities", default="hk,nyc,london"); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    cities = a.cities.split(",")
    reps = 300 if a.quick else a.reps
    creps = max(200, reps // 2)
    skips = skip_sets(cities)
    sp = trends_sparse_from_meta()
    for c in outlets.CITIES:
        for k in sp[c]:
            if k in outlets.COMPARED: skips["search"].setdefault((c, k), "search set too sparse to test (zero in more than 10% of months)")
    R = {"generated_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "cities": cities, "bootstrap_reps": reps,
         "note": "Main tests: pooled H1 and H2 for news and for search. All else is description, checks, or exploratory."}
    R["counts"] = counts_block(cities)
    R["validation"] = jload(os.path.join(PUB, "validation_summary.json"), {})
    main_res, dfs, infos_all = {}, {}, {}
    for source in SOURCES:
        res, infos, d = run_models(source, skips, reps)
        main_res[source] = res; dfs[source] = d; infos_all[source] = infos
    R["main"] = main_res
    R["pairs_used"] = {s: [i for i in infos_all[s]] for s in SOURCES}
    R["h1_by_category"] = {s: by_group(dfs[s], "category", creps) if not dfs[s].empty else {} for s in SOURCES}
    R["h1_by_city"] = {s: by_group(dfs[s], "city", creps) if not dfs[s].empty else {} for s in SOURCES}
    pt = pair_table(dfs, infos_all, creps)
    R["pair_level"] = json.loads(pt.to_json(orient="records"))
    R["h3"] = h3_block(dfs, infos_all)
    R["leadlag"] = leadlag_block(dfs, 300 if a.quick else 1000)
    # the single clearest disconnection for the poster's case study: the longest run in the news series
    # (search if there is no news run), preferring runs whose proposed cause is not "unclear"
    runs = R["h3"]["runs"]
    cand = [r for r in runs if r["source"] == "news"] or runs
    named = [r for r in cand if r["proposed_cause"] != "unclear"] or cand
    R["case_study"] = dict(named[0], selection_rule="longest run of opposite movement in the news series with a proposed cause other than unclear") if named else None
    # ---- checks that the results hold
    checks = {}
    def chk(name, sources, label, **kw):
        checks[name] = {"label": label}
        for s in sources:
            try:
                res, infos, d = run_models(s, skips, creps, **kw)
                checks[name][s] = res
                checks[name][s + "_pairs_excluded"] = [f'{i["pair"]}: {i["excluded"]}' for i in infos if i.get("excluded")]
            except Exception as e:
                checks[name][s] = None; checks[name][s + "_error"] = str(e)[:200]
    chk("backup_indicators", SOURCES, "Backup indicators in place of the main ones", role="backup")
    chk("without_covid", SOURCES, "Without 2020 to 2022", mode="no_covid")
    chk("without_all_breaks", SOURCES, "Without 2020 to 2022 and every other marked break month", mode="no_breaks")
    chk("release_date", SOURCES, "Official series aligned by release date", align="release")
    chk("all_listed_outlets", ["news"], "All listed outlets in place of the fixed panel", variant="all_listed")
    chk("negative_tone", ["news"], "Negative-tone share in place of all coverage", measure="neg_share")
    chk("hk_without_hkcna", ["news"], "Hong Kong without HK China News Agency", variant="hk_no_hkcna")
    chk("london_without_seven", ["news"], "London without the seven borough papers that jumped in volume", variant="london_no_seven")
    chk("exploratory_all_main_outlets_every_year", ["news"], "Exploratory: every main-panel outlet in every year (no outlets left out of 2015 to 2019)", variant="main_no_exclusion")
    chk("exploratory_24_month_blocks", SOURCES, "Exploratory: bootstrap with 24-month blocks (wider intervals if changes are persistent)", block_months=24)
    R["checks"] = checks
    R["verdicts"] = verdicts_block(R)
    R["ranking"] = ranking_block(cities)
    R["signal_only"] = signal_only_block(cities)
    R["synthetic_tests"] = jload(os.path.join(PUB, "synthetic_test_results.json"), {})
    def clean(o):
        if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)): return None if (o != o) else round(float(o), 6)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, pd.Period): return str(o)
        return o
    out = clean(R)
    json.dump(out, open(os.path.join(PUB, "results.json"), "w"), indent=1, sort_keys=False)
    # tidy yearly changes for the public dataset
    yc = pd.concat([dfs[s].assign(source=s) for s in SOURCES if not dfs[s].empty], ignore_index=True)
    yc["t"] = yc["t"].astype(str)
    yc[["city", "category", "source", "freq", "t", "o_raw", "a_raw", "o", "a", "covid", "brk_official", "brk_attention"]].rename(columns={
        "t": "period_end_month", "o_raw": "official_change_worse_positive", "a_raw": "attention_change_points",
        "o": "official_change_sd", "a": "attention_change_sd"}).to_csv(os.path.join(PUB, "yearly_changes.csv"), index=False)
    for s in SOURCES:
        m = out["main"][s]
        if m: print(s, "H1 beta", m["h1"]["est"], "CI", m["h1"]["ci_low"], m["h1"]["ci_high"], "p", m["h1"]["p_boot"], "| pairs", m["h1"]["n_pairs"], "n", m["h1"]["n_obs"], "n_eff", m["h1"]["n_eff_years"],
                    "| H2 worse", m["h2"]["worse"]["est"], "better", m["h2"]["better"]["est"], "diff CI", m["h2"]["diff"]["ci_low"], m["h2"]["diff"]["ci_high"])
    print("results.json written")

if __name__ == "__main__":
    main()
