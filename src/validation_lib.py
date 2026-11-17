"""Phase 4 helpers: pick the validation set from fetched candidates, build the blind package for the
second coder, and score agreement (Cohen's kappa per category and overall, weighted back to the full sample)."""
import hashlib, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")

def vid(item_id, salt="mwm-blind"):
    return hashlib.sha1((salt + item_id).encode()).hexdigest()[:10]

def select(city, tag="v1"):
    """First `need` fetched candidates per category, in the seeded order. Records what could not be fetched."""
    c = pd.read_csv(os.path.join(V, f"{city}_candidates_{tag}.csv"), dtype={"item_id": str})
    f = pd.read_json(os.path.join(V, f"{city}_pages_{tag}.jsonl"), lines=True, dtype={"item_id": str}).drop_duplicates("item_id")
    d = c.merge(f, on="item_id", how="left")
    d["tried"] = d.source.notna()
    d["fetched"] = d.source.isin(["live", "archive", "gdelt_title"])   # gdelt_title: real headline from GDELT's stored page title, no opening lines
    picks = []
    for cat, g in d.sort_values("order_in_category").groupby("c1_category"):
        need = int(g.need.iloc[0])
        ok = g[g.fetched].head(need)
        picks.append(ok)
    sel = pd.concat(picks, ignore_index=True)
    sel["vid"] = sel.item_id.map(vid)
    n_title_only = int((sel.source == "gdelt_title").sum())
    tried = d[d.tried]
    fetch_report = {"tried": int(len(tried)), "fetched": int(tried.fetched.sum()),
                    "by_source": tried.source.value_counts().to_dict(),
                    "unfetched_by_outlet": tried[~tried.fetched].outlet.value_counts().to_dict(),
                    "blocked_site_items": int((tried.source == "blocked").sum()), "headline_only_items_selected": 0,
                    "fetch_rate_by_outlet_period": {f"{o}|{p}": round(float(v), 3) for (o, p), v in tried.groupby(["outlet", "period"]).fetched.mean().items()},
                    "selected": int(len(sel)), "selected_by_category": sel.c1_category.value_counts().to_dict(),
                    "short_categories": {k: int(g.need.iloc[0] - g.fetched.sum()) for k, g in d.groupby("c1_category") if g.fetched.sum() < g.need.iloc[0]}}
    fetch_report["headline_only_items_selected"] = n_title_only
    return sel, fetch_report

def write_package(city, tag="v1", shuffle_seed=7):
    sel, rep = select(city, tag)
    sel = sel.sample(frac=1, random_state=shuffle_seed).reset_index(drop=True)
    path = os.path.join(V, f"{city}_coder2_input_{tag}.jsonl")
    with open(path, "w") as f:
        for i, r in sel.iterrows():
            f.write(json.dumps({"vid": r.vid, "n": i + 1, "city": outlets.CITY_NAMES[city], "outlet": outlets.BY_KEY[r.outlet]["name"],
                                "headline": r.title, "summary_line": (r.desc if isinstance(r.desc, str) else ""),
                                "opening_lines": r.opening}, ensure_ascii=False) + "\n")
    sel.to_csv(os.path.join(V, f"{city}_validation_set_{tag}.csv"), index=False)     # holds first-coder labels; never shown to coder 2
    json.dump(rep, open(os.path.join(V, f"{city}_fetch_report_{tag}.json"), "w"), indent=1)
    return path, rep

# ------------------------------------------------------------------------------------------- scoring
def wkappa(a, b, w, labels):
    a = np.asarray(a); b = np.asarray(b); w = np.asarray(w, float); W = w.sum()
    po = (w * (a == b)).sum() / W
    pe = sum(((w * (a == k)).sum() / W) * ((w * (b == k)).sum() / W) for k in labels)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")

def score(df, pool_counts, labels=None, reps=1000, seed=5, a_col="c1_category", b_col="c2_category"):
    """df: one row per validation item with the stratum (first coder's label), both coders' labels.
    pool_counts: first-coder label counts in the full labeled sample of the city (for the weights)."""
    labels = labels or codebook.LABELS
    n_s = df["stratum"].value_counts()
    N = sum(pool_counts.values())
    w = df["stratum"].map(lambda s: (pool_counts.get(s, 0) / N) / (n_s[s] / len(df))).to_numpy()
    a = df[a_col].to_numpy(); b = df[b_col].to_numpy()
    out = {"n": int(len(df)), "overall": {"kappa_weighted": wkappa(a, b, w, labels), "kappa_unweighted": wkappa(a, b, np.ones(len(df)), labels),
                                          "agreement_weighted": float((w * (a == b)).sum() / w.sum()), "agreement_unweighted": float((a == b).mean())},
           "by_category": {}}
    rng = np.random.default_rng(seed)
    strata_idx = [np.where(df["stratum"].to_numpy() == s)[0] for s in n_s.index]
    boots = {k: [] for k in labels}; boot_all = []
    for _ in range(reps):
        idx = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in strata_idx])
        boot_all.append(wkappa(a[idx], b[idx], w[idx], labels))
        for k in labels:
            boots[k].append(wkappa(a[idx] == k, b[idx] == k, w[idx], [True, False]))
    lo, hi = np.nanpercentile(boot_all, [2.5, 97.5]); out["overall"]["ci_low"] = float(lo); out["overall"]["ci_high"] = float(hi)
    for k in labels:
        kw = wkappa(a == k, b == k, w, [True, False]); ku = wkappa(a == k, b == k, np.ones(len(df)), [True, False])
        lo, hi = np.nanpercentile(boots[k], [2.5, 97.5])
        out["by_category"][k] = {"kappa_weighted": kw, "kappa_unweighted": ku, "ci_low": float(lo), "ci_high": float(hi),
                                 "n_coder1": int((a == k).sum()), "n_coder2": int((b == k).sum()), "pass": bool(kw >= 0.61)}
    conf = pd.crosstab(pd.Categorical(a, labels), pd.Categorical(b, labels), dropna=False)
    out["confusion_counts"] = {r: {c: int(conf.loc[r, c]) for c in labels} for r in labels}
    return out
