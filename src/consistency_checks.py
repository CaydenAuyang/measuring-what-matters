"""Phase 4, step 6: the two consistency checks.

1. Third pass: a different AI model codes the same validation items from the same real text (in place of
   the classmate's 150 items). Reported on a seeded subset of 150 items (50 per city) and on all items.
2. Re-label: the second coder labels 50 of the same items again in a fresh request (in place of Cayden's
   two-week re-label).
Writes data/interim/validation/consistency_result.json. Also writes the 50-item re-label input file.
"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets, validation_lib as VL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")

def kap(a, b):
    a = np.asarray(a); b = np.asarray(b)
    return float(VL.wkappa(a, b, np.ones(len(a)), codebook.LABELS)) if len(a) else None

def load(role):
    parts = []
    for c in outlets.CITIES:
        p = os.path.join(V, f"{c}_{role}_labels_v1.csv")
        if os.path.exists(p):
            d = pd.read_csv(p, dtype=str).drop_duplicates("vid"); d["city"] = c; parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else None

def relabel_input():
    """50 validation items (17, 17, 16 by city), seeded, written once for the second coder's fresh request."""
    path = os.path.join(V, "relabel50_input.jsonl")
    if os.path.exists(path):
        return path
    rows = []
    for c, n in [("hk", 17), ("nyc", 17), ("london", 16)]:
        items = [json.loads(l) for l in open(os.path.join(V, f"{c}_coder2_input_v1.jsonl"))]
        idx = np.random.default_rng(5050 + n).choice(len(items), n, replace=False)
        rows += [items[i] for i in sorted(idx)]
    with open(path, "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return path

def main():
    out = {"gemini_repeat": True}
    first = pd.concat([pd.read_csv(os.path.join(V, f"{c}_validation_set_v1.csv"), dtype=str)[["vid", "c1_category"]].assign(city=c)
                       for c in outlets.CITIES if os.path.exists(os.path.join(V, f"{c}_validation_set_v1.csv"))])
    third = load("thirdpass"); second = load("coder2")
    if third is not None:
        t = third.merge(first, on=["vid", "city"])
        sub_ids = set()
        for c, g in t.groupby("city"):
            sub_ids |= set(g.sample(min(50, len(g)), random_state=150).vid)
        ts = t[t.vid.isin(sub_ids)]
        tp = {"model_note": "a different AI model from the second coder, reading the same real headlines and opening lines",
              "n": int(len(ts)), "kappa_vs_first": kap(ts.category, ts.c1_category), "n_all": int(len(t)), "kappa_vs_first_all": kap(t.category, t.c1_category),
              "kappa_vs_second": None, "kappa_vs_second_all": None}
        if second is not None:
            j = t.merge(second[["vid", "category", "about_city"]].rename(columns={"category": "c2", "about_city": "ab2"}), on="vid")
            js = j[j.vid.isin(sub_ids)]
            tp.update({"kappa_vs_second": kap(js.category, js.c2), "kappa_vs_second_all": kap(j.category, j.c2), "n_vs_second": int(len(js)),
                       "about_city_agreement_all": float((j.about_city == j.ab2).mean())})
        out["third_pass"] = tp
    rp = os.path.join(V, "relabel50_labels.csv")
    if second is not None and os.path.exists(rp):
        r = pd.read_csv(rp, dtype=str).drop_duplicates("vid").merge(second[["vid", "category", "tone"]].rename(columns={"category": "c2", "tone": "t2"}), on="vid")
        out["relabel"] = {"n": int(len(r)), "kappa": kap(r.category, r.c2), "agreement": float((r.category == r.c2).mean()),
                          "tone_agreement": float((r.tone == r.t2).mean())}
    json.dump(out, open(os.path.join(V, "consistency_result.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    relabel_input()
    main()
