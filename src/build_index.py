"""Phase 7, step 1: monthly news attention shares from the labels.

Each category's share is computed per outlet per month, then averaged across the city's outlets
with equal weights (Appendix A). Also the negative-tone share. Shares use every labeled article,
"not a civic problem" included, as the denominator.

Reads data/interim/index_config.json (written by the validation step) for: the labeling round reached,
outlets left out of some years, and categories dropped. Writes data/public/news_attention_monthly.csv.
"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import outlets, codebook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVEL_CAPS = {"L0": (30, 6), "L1": (60, 12), "L2": (100, 20), "L3": (150, 30), "L4": (220, 44), "L5": (333, 66)}
LEVEL_OF_GRP = {"L0-hk": "L0", "L0-rest": "L0", "L1": "L1", "L2": "L2", "L3": "L3", "L4": "L4", "L5": "L5"}
SEVEN = ["eastlondonadvertiser", "hackneygazette", "hamhigh", "ilfordrecorder", "islingtongazette", "kilburntimes", "romfordrecorder"]

def first_codebook_labels():
    """Path of the labels made with the first codebook. If the whole sample was labeled again with a revised
    codebook (src/swap_revised_labels.py), the first file is kept under a new name and the first validation
    test and the headline check keep using it."""
    p = os.path.join(ROOT, "data/interim/labels/labels_main_first_codebook.jsonl")
    return p if os.path.exists(p) else os.path.join(ROOT, "data/interim/labels/labels_main.jsonl")

def load(labels_path=None):
    items = pd.read_parquet(os.path.join(ROOT, "data/interim/labels/items_ordered.parquet"),
                            columns=["item_id", "city", "outlet", "month", "in_main", "in_check", "rk_main", "rk_all", "grp", "headline"])
    lab = pd.read_json(labels_path or os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True).drop_duplicates("item_id")
    d = items.merge(lab[["item_id", "category", "tone"]], on="item_id", how="left")
    d["level"] = d.grp.map(LEVEL_OF_GRP)
    return d

def levels_done(d, tol=0.005):
    """Highest labeling round that is complete (at most 0.5% of items unlabeled) in all three cities."""
    done = None
    for lv in LEVEL_CAPS:
        sub = d[d.level == lv]
        if len(sub) == 0: break
        miss = sub.groupby("city").category.apply(lambda s: s.isna().mean())
        if (miss <= tol).all() and len(miss) == 3: done = lv
        else: break
    return done

def check_cap_done(d, tol=0.01):
    c = d[~d.in_main]
    if len(c) == 0: return 0
    full = c.category.isna().mean() <= tol
    part = c[c.grp == "chk1"].category.isna().mean() <= tol
    return "full" if full else (15 if part else 0)

def shares(sub, by_outlet=False):
    """sub: labeled items of one variant. Returns city-month-category shares averaged over outlets equally."""
    sub = sub.dropna(subset=["category"])
    g = sub.groupby(["city", "outlet", "month"])
    n = g.size().rename("n")
    cat = sub.groupby(["city", "outlet", "month", "category"]).size().unstack(fill_value=0).reindex(columns=codebook.LABELS, fill_value=0)
    neg = sub[sub.tone == "negative"].groupby(["city", "outlet", "month", "category"]).size().unstack(fill_value=0).reindex(columns=codebook.LABELS, fill_value=0)
    neg = neg.reindex(cat.index, fill_value=0)
    sh = cat.div(n, axis=0); ns = neg.div(n, axis=0)
    if by_outlet:
        return sh, ns, n
    city_sh = sh.groupby(level=["city", "month"]).mean()
    city_ns = ns.groupby(level=["city", "month"]).mean()
    meta = pd.DataFrame({"n_items": n.groupby(level=["city", "month"]).sum(), "n_outlets": n.groupby(level=["city", "month"]).size(),
                         "min_items_per_outlet": n.groupby(level=["city", "month"]).min()})
    return city_sh, city_ns, meta

def apply_exclusions(d, excl):
    for e in excl:
        m = (d.city == e["city"]) & d.outlet.isin(e["outlets"]) & (d.month >= e["from"]) & (d.month <= e["to"])
        d = d[~m]
    return d

def build(write=True):
    cfg_path = os.path.join(ROOT, "data/interim/index_config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    d = load()
    level = cfg.get("level") or levels_done(d)
    if level is None:
        raise SystemExit("no complete labeling round yet")
    order = list(LEVEL_CAPS)
    use_levels = order[: order.index(level) + 1]
    main_all = d[d.in_main & d.level.isin(use_levels)]
    excl = cfg.get("excluded", [])
    variants = {
        "main": apply_exclusions(main_all, excl),                      # the pre-registered series, after the headline-check rule
        "main_no_exclusion": main_all,                                  # every main-panel outlet in every year
        "hk_no_hkcna": apply_exclusions(main_all, excl)[lambda x: ~((x.city == "hk") & (x.outlet == "hkcna"))],
        "london_no_seven": apply_exclusions(main_all, excl)[lambda x: ~((x.city == "london") & x.outlet.isin(SEVEN))],
        # exploratory: Hong Kong built only from articles whose address carries headline words (no theme-tag-only labels)
        "hk_headline_only": main_all[lambda x: ~((x.city == "hk") & (x.headline.fillna("") == ""))],
    }
    chk = cfg.get("check_cap") or check_cap_done(d)
    if chk:
        cap = {c: (outlets.CHECK_CAP[c] if chk == "full" else int(chk)) for c in outlets.CITIES}
        al = d[d.in_check & d.category.notna()]
        al = al[al.rk_all <= al.city.map(cap)]
        variants["all_listed"] = al
    rows = []; orows = []
    for name, sub in variants.items():
        osh, ons, on = shares(sub, by_outlet=True)       # outlet-level shares, used for matched-panel yearly changes
        ol = osh.stack().rename("share").reset_index().rename(columns={"level_3": "category"})
        ol["neg_share"] = ons.stack().to_numpy()
        ol = ol.merge(on.reset_index(), on=["city", "outlet", "month"]); ol["variant"] = name
        orows.append(ol)
        sh, ns, meta = shares(sub)
        long = sh.stack().rename("share").reset_index().rename(columns={"level_2": "category"})
        long["neg_share"] = ns.stack().to_numpy()
        long = long.merge(meta.reset_index(), on=["city", "month"])
        long["variant"] = name
        rows.append(long)
    out = pd.concat(rows, ignore_index=True)
    # flags: months where a main-panel outlet has no articles
    exp = {c: set(outlets.MAIN_PANEL[c]) for c in outlets.CITIES}
    present = variants["main_no_exclusion"].dropna(subset=["category"]).groupby(["city", "month"]).outlet.agg(lambda s: set(s))
    miss = {k: ";".join(sorted(exp[k[0]] - v)) for k, v in present.items()}
    out["missing_main_outlets"] = [miss.get((c, m), "") for c, m in zip(out.city, out.month)]
    info = {"level": level, "caps_hk_nyc_london": [LEVEL_CAPS[level][0], LEVEL_CAPS[level][0], LEVEL_CAPS[level][1]],
            "check_cap": chk, "excluded": excl,
            "n_labeled_main": {c: int(((main_all.city == c) & main_all.category.notna()).sum()) for c in outlets.CITIES},
            "n_labeled_all": int(d.category.notna().sum()),
            "n_labeled_by_city": {c: int(((d.city == c) & d.category.notna()).sum()) for c in outlets.CITIES}}
    if write:
        os.makedirs(os.path.join(ROOT, "data/public"), exist_ok=True)
        out.to_csv(os.path.join(ROOT, "data/public/news_attention_monthly.csv"), index=False)
        pd.concat(orows, ignore_index=True).to_parquet(os.path.join(ROOT, "data/interim/news_outlet_monthly.parquet"), index=False)
        json.dump(info, open(os.path.join(ROOT, "data/interim/index_info.json"), "w"), indent=1)
    return out, info

if __name__ == "__main__":
    out, info = build()
    print(json.dumps(info, indent=1))
    chk = out[out.variant == "main"].groupby(["city", "month"]).share.sum()
    print("shares sum to 1 in every city-month:", bool(np.allclose(chk, 1.0)), "| rows", len(out))
