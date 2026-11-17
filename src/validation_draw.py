"""Phase 4, step 1: draw the validation candidates for one city.

About 300 items per city, at least 20 per category, spread across years, languages and outlets.
Candidates are listed in a fixed seeded order per category, three times as many as needed, so an
item whose page cannot be fetched is replaced by the next one from the same category and city.

Usage: python src/validation_draw.py <city> [--groups L0-hk,L0-rest] [--tag v1]
"""
import argparse, os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20261117

def load_labeled(groups=None):
    items = pd.read_parquet(os.path.join(ROOT, "data/interim/labels/items_ordered.parquet"))
    lab = pd.read_json(os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True).drop_duplicates("item_id")
    d = items.merge(lab[["item_id", "category", "tone"]], on="item_id", how="inner")
    if groups:
        d = d[d.grp.isin(groups)]
    return d

def period(month):
    y = int(month[:4])
    return "2015-2018" if y <= 2018 else ("2019-2022" if y <= 2022 else "2023-2026")

def draw(city, groups, tag, total=300, floor=20, oversample=3, only_categories=None, exclude_ids=None):
    d = load_labeled(groups)
    d = d[(d.city == city) & d.in_main].copy()
    if exclude_ids is not None:
        d = d[~d.item_id.isin(exclude_ids)]
    d["period"] = d.month.map(period)
    shares = d.category.value_counts(normalize=True).reindex(codebook.LABELS).fillna(0)
    extra = total - floor * len(codebook.LABELS)
    need = {c: floor + int(round(extra * shares[c])) for c in codebook.LABELS}
    rng = np.random.default_rng(SEED + sum(ord(ch) for ch in city + tag))
    out = []
    for c in codebook.LABELS:
        if only_categories and c not in only_categories:
            continue
        pool = d[d.category == c]
        cells = {}
        for key, g in pool.groupby(["outlet", "period"]):
            idx = g.index.to_numpy().copy(); rng.shuffle(idx); cells[key] = list(idx)
        keys = sorted(cells.keys()); rng.shuffle(keys)
        order = []
        while any(cells[k] for k in keys) and len(order) < need[c] * oversample:
            for k in keys:
                if cells[k]:
                    order.append(cells[k].pop())
        sub = pool.loc[order].copy()
        sub["order_in_category"] = range(1, len(sub) + 1)
        sub["need"] = need[c]
        out.append(sub)
    o = pd.concat(out, ignore_index=True)
    o = o.rename(columns={"category": "c1_category", "tone": "c1_tone"})
    cols = ["item_id", "city", "outlet", "month", "pdate", "url", "lang", "period", "headline", "c1_category", "c1_tone", "order_in_category", "need"]
    path = os.path.join(ROOT, f"data/interim/validation/{city}_candidates_{tag}.csv")
    o[cols].to_csv(path, index=False)
    meta = dict(city=city, tag=tag, groups=groups, pool_size=int(len(d)), shares={k: float(v) for k, v in shares.items()}, need=need,
                available={c: int((d.category == c).sum()) for c in codebook.LABELS})
    json.dump(meta, open(os.path.join(ROOT, f"data/interim/validation/{city}_draw_{tag}.json"), "w"), indent=1)
    print(city, "pool", len(d), "candidates", len(o))
    print(pd.DataFrame({"share": shares.round(3), "need": pd.Series(need), "cands": o.c1_category.value_counts()}).to_string())
    return o

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("city"); ap.add_argument("--groups", default=""); ap.add_argument("--tag", default="v1")
    a = ap.parse_args()
    draw(a.city, a.groups.split(",") if a.groups else None, a.tag)
