"""Build the matched yearly-change series for every city, category and source (Appendix C)."""
import glob, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import outlets, stats_lib as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITIES = outlets.CITIES
COMPARED = outlets.COMPARED
MIN_OBS = {"M": 24, "Q": 8, "A": 5}

_cache = {}

def official_tables():
    if "off" not in _cache:
        frames, meta = [], {}
        for c in CITIES:
            p = os.path.join(ROOT, f"data/interim/official/{c}_official.csv")
            if os.path.exists(p):
                frames.append(pd.read_csv(p, dtype={"period": str, "component": str}))
                for m in json.load(open(os.path.join(ROOT, f"data/interim/official/{c}_meta.json"))):
                    meta[m["series_id"]] = m
        d = pd.concat(frames, ignore_index=True)
        d["component"] = d["component"].fillna("")
        d["end"] = pd.PeriodIndex(pd.to_datetime(d["period_end_date"]), freq="M")
        # Education is matched to the September-to-August school year (Appendix C)
        edu = (d.category == "education") & (d.frequency == "A")
        d.loc[edu, "end"] = pd.PeriodIndex([pd.Period(f"{str(p)[:4]}-08", freq="M") for p in d.loc[edu, "period"]], freq="M")
        d.loc[edu, "window_months"] = 12
        _cache["off"] = (d, meta)
    return _cache["off"]

def official_series(city, category, role="main"):
    """Returns (change Series indexed by end month [worse = positive], info dict) or (None, info)."""
    d, meta = official_tables()
    sid = f"{city}_{category}_{role}"
    sub = d[(d.series_id == sid) & d.value.notna()]
    if sub.empty:
        return None, {"status": "missing"}
    freq = sub.frequency.iloc[0]; window = int(sub.window_months.iloc[0]); rule = sub.change_rule.iloc[0]; worse = sub.worse_when.iloc[0]
    changes, flags = [], []
    for comp, g in sub.groupby("component"):
        s = pd.Series(g["value"].to_numpy(float), index=pd.PeriodIndex(g["end"], freq="M")).sort_index()
        s = s[~s.index.duplicated()]
        changes.append(S.yearly_change(s, rule, worse))
        fl = pd.Series(g["break_flag"].fillna(0).to_numpy(int), index=pd.PeriodIndex(g["end"], freq="M")).sort_index()
        fl = fl[~fl.index.duplicated()]
        if rule == "inflation_points":       # the change in a 12-month rate straddles a break for two years
            fl = ((fl == 1) | (pd.Series(fl.reindex(fl.index - 12).to_numpy(), index=fl.index).fillna(0) == 1)).astype(int)
        flags.append(fl)
    ch = pd.concat(changes, axis=1).mean(axis=1, skipna=False).dropna() if len(changes) > 1 else changes[0]
    fl = pd.concat(flags, axis=1).max(axis=1)
    m = meta.get(sid, {})
    info = {"series_id": sid, "freq": freq, "window": window, "rule": rule, "worse_when": worse, "status": m.get("status", "ok"),
            "name": sub.indicator_name.iloc[0], "release_lag_months": int(round(float(m.get("release_lag_months") or 0))),
            "n_components": len(changes)}
    return (ch, fl), info

def attention_tables(source, variant="main", measure="share"):
    """dict city -> DataFrame(index month Period, columns categories)."""
    key = (source, variant, measure)
    if key not in _cache:
        if source == "news":
            a = pd.read_csv(os.path.join(ROOT, "data/public/news_attention_monthly.csv"))
            a = a[a.variant == variant]
            val = measure
        else:
            a = pd.read_csv(os.path.join(ROOT, "data/interim/trends/trends_shares.csv"))
            val = "share"
        out = {}
        for c, g in a.groupby("city"):
            pv = g.pivot(index="month", columns="category", values=val)
            pv.index = pd.PeriodIndex(pv.index, freq="M")
            out[c] = pv.sort_index()
        _cache[key] = out
    return _cache[key]

def news_outlet_tables(variant="main", measure="share"):
    """dict city -> {outlet: DataFrame(index month Period, columns categories)} for matched-panel changes."""
    key = ("outlet", variant, measure)
    if key not in _cache:
        a = pd.read_parquet(os.path.join(ROOT, "data/interim/news_outlet_monthly.parquet"))
        a = a[a.variant == variant]
        out = {}
        for (c, o), g in a.groupby(["city", "outlet"]):
            pv = g.pivot(index="month", columns="category", values=measure)
            pv.index = pd.PeriodIndex(pv.index, freq="M")
            out.setdefault(c, {})[o] = pv.sort_index()
        _cache[key] = out
    return _cache[key]

def matched_panel_change(city, category, ends, window, variant, measure):
    """Yearly change in a city's news share using only outlets present in BOTH periods.

    Each outlet's share is averaged over the window, the outlet's own change from a year earlier is taken,
    and the changes are averaged across outlets with equal weights. When every outlet is present in both
    periods this equals the change in the city average. When the panel differs between the two periods
    (an outlet with no articles, or outlets left out of some years) it keeps the comparison like for like.
    """
    tabs = news_outlet_tables(variant, measure).get(city, {})
    diffs = []
    for o, pv in tabs.items():
        if category not in pv.columns: continue
        a = pv[category].dropna() * 100.0
        lvl = S.window_mean(a, list(ends) + [e - 12 for e in ends], window)
        diffs.append(pd.Series({e: lvl.get(e, np.nan) - lvl.get(e - 12, np.nan) for e in ends}, dtype=float))
    if not diffs:
        return pd.Series(dtype=float)
    return pd.concat(diffs, axis=1).mean(axis=1, skipna=True)

def attention_break(city, source, t):
    y = t.year
    if city == "hk" and y in (2019, 2020):          # protests and the National Security Law dominate coverage and search
        return True
    if source == "search" and y in (2011, 2016, 2022):   # Google changed how Trends collects data on 1 January of these years
        return True
    return False

def make_pair(city, category, source, role="main", variant="main", measure="share", align="period"):
    """Matched yearly changes for one pair. Returns (DataFrame, info) or (None, info)."""
    res, info = official_series(city, category, role)
    info.update({"city": city, "category": category, "source": source, "role": role, "pair": f"{city}|{category}|{source}"})
    if res is None:
        info["excluded"] = "no official series"; return None, info
    ch, fl = res
    att = attention_tables(source, variant, measure).get(city)
    if att is None or category not in att.columns:
        info["excluded"] = "no attention series"; return None, info
    a_month = att[category].dropna() * 100.0                     # percent of coverage or of search interest
    lag = info["release_lag_months"] if align == "release" else 0
    ends = ch.index + lag                                        # month the attention window ends
    if source == "news":
        a_change = matched_panel_change(city, category, list(ends), info["window"], variant, measure)
    else:
        level = S.window_mean(a_month, list(ends) + [e - 12 for e in ends], info["window"])
        a_change = pd.Series({e: level.get(e, np.nan) - level.get(e - 12, np.nan) for e in ends}, dtype=float)
    df = pd.DataFrame({"t": ch.index, "o_raw": ch.to_numpy(), "a_raw": a_change.reindex(ends).to_numpy()}).dropna()
    if len(df) < MIN_OBS[info["freq"]]:
        info["excluded"] = f"too few matched periods ({len(df)})"; return None, info
    df["covid"] = [2020 <= t.year <= 2022 for t in df.t]
    df["brk_official"] = [bool(fl.get(t, 0)) for t in df.t]
    df["brk_attention"] = [attention_break(city, source, t + lag) for t in df.t]
    df["brk_any"] = df.covid | df.brk_official | df.brk_attention
    # standard deviations from periods outside the marked breaks, so COVID does not set the scale
    base = df[~df.brk_any] if (~df.brk_any).sum() >= max(3, MIN_OBS[info["freq"]] // 2) else df
    sd_o, sd_a = base.o_raw.std(ddof=1), base.a_raw.std(ddof=1)
    if not (sd_o > 0 and sd_a > 0):
        info["excluded"] = "no variation"; return None, info
    df["o"] = df.o_raw / sd_o; df["a"] = df.a_raw / sd_a
    df["pair"] = info["pair"]; df["freq"] = info["freq"]; df["city"] = city; df["category"] = category
    info.update({"n": int(len(df)), "first": str(df.t.min()), "last": str(df.t.max()), "sd_official": float(sd_o), "sd_attention": float(sd_a),
                 "n_break": int(df.brk_any.sum())})
    return df, info

def build_pairs(source, role="main", variant="main", measure="share", align="period", skip=None, categories=None):
    """All city x category pairs for one source. skip: set of (city, category) left out (dropped or too sparse)."""
    dfs, infos = [], []
    for city in CITIES:
        for cat in (categories or COMPARED):
            if skip and (city, cat) in skip:
                infos.append({"city": city, "category": cat, "source": source, "pair": f"{city}|{cat}|{source}", "excluded": skip[(city, cat)]}); continue
            df, info = make_pair(city, cat, source, role, variant, measure, align)
            infos.append(info)
            if df is not None: dfs.append(df)
    return (pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()), infos
