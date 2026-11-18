"""Used only when a revised category passed its retest and the whole sample was labeled again
(src/relabel_revised.sh). Checks that the new label file covers the sample, writes how far the two sets
of labels agree, keeps the first file under a new name, and makes the new file the one the index reads.

Usage: python src/swap_revised_labels.py            # check and compare only
       python src/swap_revised_labels.py --swap     # also swap the files (refuses if coverage is under 99.9%)
"""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, validation_lib as VL
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(ROOT, "data/interim/labels")
OLD, NEW, KEEP = os.path.join(L, "labels_main.jsonl"), os.path.join(L, "labels_main_revised.jsonl"), os.path.join(L, "labels_main_first_codebook.jsonl")

def main():
    if os.path.exists(KEEP) and not os.path.exists(NEW):
        print("already swapped"); return
    old = pd.read_json(OLD, lines=True, dtype={"item_id": str}).drop_duplicates("item_id")
    new = pd.read_json(NEW, lines=True, dtype={"item_id": str}).drop_duplicates("item_id")
    items = pd.read_parquet(os.path.join(L, "items_ordered.parquet"), columns=["item_id", "city"])
    cover = float(items.item_id.isin(new.item_id).mean())
    d = old[["item_id", "category", "tone"]].merge(new[["item_id", "category", "tone"]], on="item_id", suffixes=("_first", "_revised")).merge(items, on="item_id")
    out = {"items_in_sample": int(len(items)), "labeled_first_codebook": int(len(old)), "labeled_revised_codebook": int(len(new)),
           "coverage_revised": cover, "by_city": {}}
    for c, g in d.groupby("city"):
        w = np.ones(len(g))
        same = (g.category_first == g.category_revised)
        moved = g[~same].groupby(["category_first", "category_revised"]).size().sort_values(ascending=False).head(15)
        out["by_city"][c] = {
            "n": int(len(g)), "same_category_share": float(same.mean()),
            "kappa_first_vs_revised": float(VL.wkappa(g.category_first.to_numpy(), g.category_revised.to_numpy(), w, codebook.LABELS)),
            "share_first_codebook": {k: float((g.category_first == k).mean()) for k in codebook.LABELS},
            "share_revised_codebook": {k: float((g.category_revised == k).mean()) for k in codebook.LABELS},
            "largest_moves": [{"from": a, "to": b, "n": int(n)} for (a, b), n in moved.items()],
        }
        print(c, "same category:", round(float(same.mean()), 4), "| kappa:", round(out["by_city"][c]["kappa_first_vs_revised"], 4))
    json.dump(out, open(os.path.join(L, "relabel_compare.json"), "w"), indent=1)
    print("coverage of the revised labels:", round(cover, 5))
    if "--swap" in sys.argv:
        if cover < 0.999:
            print("NOT swapped: coverage under 99.9%"); sys.exit(2)
        os.rename(OLD, KEEP); os.rename(NEW, OLD)
        print("swapped: the index now reads the labels made with the revised codebook")

if __name__ == "__main__":
    main()
