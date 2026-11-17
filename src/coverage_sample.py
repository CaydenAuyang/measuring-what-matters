"""Print a small seeded sample of headline words for one city, category and period (for reading only;
article-level text never goes into the public dataset). Used when proposing causes for disconnections."""
import os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_d = None

def data():
    global _d
    if _d is None:
        it = pd.read_parquet(os.path.join(ROOT, "data/interim/labels/items_ordered.parquet"), columns=["item_id", "city", "outlet", "month", "headline", "in_main"])
        lab = pd.read_json(os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True).drop_duplicates("item_id")
        _d = it.merge(lab[["item_id", "category", "tone"]], on="item_id")
    return _d

def sample(city, category, start, end, n=12, seed=3):
    d = data()
    s = d[(d.city == city) & (d.category == category) & (d.month >= start) & (d.month <= end) & d.in_main & (d.headline != "")]
    tone = s.tone.value_counts(normalize=True).round(2).to_dict()
    return s.sample(min(n, len(s)), random_state=seed), len(s), tone

if __name__ == "__main__":
    city, category, start, end = sys.argv[1:5]
    s, n, tone = sample(city, category, start, end, int(sys.argv[5]) if len(sys.argv) > 5 else 12)
    print(f"{city} {category} {start}..{end}: {n} items with headline words; tone {tone}")
    for r in s.itertuples():
        print(f"  {r.month} {r.outlet[:8]:8s} {r.tone[:3]} | {r.headline[:95]}")
