"""Phase 4, step 5: the headline check (2020 onward).

For articles from 2020 on, GDELT stores the real page title. The first coder labels each article twice:
once from the real stored headline alone, and once (the production label) from the headline words in the
web address plus theme tags. Agreement is reported separately for items with and without headline words
in their addresses. If theme-tag-only labels fall below kappa 0.61, the outlets with number-only
addresses are left out of 2015 to 2019 (methodology, "What the model reads").

Writes data/interim/validation/headline_check_result.json and returns the exclusion list.
"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, validation_lib as VL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")
THRESHOLD = 0.61

def kap(a, b):
    return VL.wkappa(np.asarray(a), np.asarray(b), np.ones(len(a)), codebook.LABELS)

def boot_ci(a, b, reps=1000, seed=9):
    rng = np.random.default_rng(seed); a = np.asarray(a); b = np.asarray(b); n = len(a); ks = []
    for _ in range(reps):
        i = rng.integers(0, n, n); ks.append(kap(a[i], b[i]))
    return [float(x) for x in np.nanpercentile(ks, [2.5, 97.5])]

def run():
    s = pd.read_csv(os.path.join(V, "headline_check_set.csv"), dtype={"item_id": str})
    t = pd.read_json(os.path.join(V, "headline_check_title_labels.jsonl"), lines=True, dtype={"item_id": str}).drop_duplicates("item_id")
    p = pd.read_json(os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True, dtype={"item_id": str}).drop_duplicates("item_id")
    d = s.merge(t[["item_id", "category"]].rename(columns={"category": "from_title"}), on="item_id") \
         .merge(p[["item_id", "category"]].rename(columns={"category": "production"}), on="item_id")
    out = {"threshold": THRESHOLD, "n_items": int(len(d)), "n_in_set": int(len(s)), "cities": {}, "by_outlet": {}}
    for city, g in d.groupby("city"):
        res = {}
        for name, sub in [("with_headline_words", g[g.has_addr_headline]), ("theme_tags_only", g[~g.has_addr_headline])]:
            if len(sub) >= 30:
                lo, hi = boot_ci(sub.from_title, sub.production)
                res[name] = {"n": int(len(sub)), "kappa": kap(sub.from_title, sub.production), "ci_low": lo, "ci_high": hi,
                             "agreement": float((sub.from_title == sub.production).mean())}
                cats = {}
                for k in codebook.LABELS:
                    if (sub.from_title == k).sum() + (sub.production == k).sum() >= 10:
                        cats[k] = VL.wkappa((sub.from_title == k).to_numpy(), (sub.production == k).to_numpy(), np.ones(len(sub)), [True, False])
                res[name]["by_category"] = cats
            else:
                res[name] = {"n": int(len(sub)), "kappa": None, "note": "too few items to test"}
        out["cities"][city] = res
    for (city, outlet, has), g in d.groupby(["city", "outlet", "has_addr_headline"]):
        if len(g) >= 30:
            out["by_outlet"][f"{city}|{outlet}|{'headline' if has else 'themes_only'}"] = {"n": int(len(g)), "kappa": kap(g.from_title, g.production)}
    hk = out["cities"].get("hk", {}).get("theme_tags_only", {})
    applied = hk.get("kappa") is not None and hk["kappa"] < THRESHOLD
    excluded = []
    if applied:
        excluded = [{"city": "hk", "outlets": ["hkcna", "orientaldaily"], "from": "2015-01", "to": "2019-12",
                     "reason": "theme-tag-only labels fell below kappa 0.61 in the headline check"}]
        text = (f"Theme-tag-only labels agreed with real-headline labels at kappa {hk['kappa']:.2f}, below 0.61. "
                "HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. "
                "Hong Kong's news series for those years rests on the South China Morning Post alone.")
    else:
        text = (f"Theme-tag-only labels agreed with real-headline labels at kappa {hk.get('kappa'):.2f}, at or above 0.61. No outlet is left out." if hk.get("kappa") is not None
                else "The theme-tag-only group was too small to test.")
    out["rule"] = {"applied": bool(applied), "text": text, "excluded": excluded}
    json.dump(out, open(os.path.join(V, "headline_check_result.json"), "w"), indent=1)
    return out

if __name__ == "__main__":
    o = run()
    print(json.dumps({k: v for k, v in o.items() if k != "by_outlet"}, indent=1)[:3000])
    print(json.dumps(o["by_outlet"], indent=0))
