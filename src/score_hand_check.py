"""Score Cayden's optional hand check against both AI coders.

Fill in the `my_label` column of deliverables/optional_hand_check_50.csv with one of:
safety, economy, housing, transport, environment, health, education, cost_of_living,
governance, culture, technology, community, not_civic
(and `about_this_city` with yes / no / unclear), then run:  .venv/bin/python src/score_hand_check.py

Prints Cohen's kappa between your labels and (a) the first AI coder, (b) the second AI coder.
With 50 items the kappa is rough: read it with its interval.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, validation_lib as VL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")

def kappa_ci(a, b, reps=2000, seed=1):
    a = np.asarray(a); b = np.asarray(b); n = len(a); rng = np.random.default_rng(seed)
    k = VL.wkappa(a, b, np.ones(n), codebook.LABELS)
    ks = [VL.wkappa(a[i], b[i], np.ones(n), codebook.LABELS) for i in (rng.integers(0, n, n) for _ in range(reps))]
    lo, hi = np.nanpercentile(ks, [2.5, 97.5])
    return k, lo, hi

def main():
    h = pd.read_csv(os.path.join(ROOT, "deliverables/optional_hand_check_50.csv"), dtype=str).fillna("")
    h["my_label"] = h.my_label.str.strip().str.lower().str.replace(" ", "_")
    done = h[h.my_label != ""]
    if len(done) == 0:
        print("The my_label column is empty. Fill it in first."); return 1
    bad = done[~done.my_label.isin(codebook.LABELS)]
    if len(bad):
        print("These labels are not in the codebook:", sorted(bad.my_label.unique())); return 1
    sets, c2 = [], []
    for city in ["hk", "nyc", "london"]:
        sets.append(pd.read_csv(os.path.join(V, f"{city}_validation_set_v1.csv"), dtype=str)[["vid", "c1_category"]])
        p = os.path.join(V, f"{city}_coder2_labels_v1.csv")
        if os.path.exists(p): c2.append(pd.read_csv(p, dtype=str)[["vid", "category", "about_city"]])
    d = done.merge(pd.concat(sets), left_on="id", right_on="vid", how="left")
    k, lo, hi = kappa_ci(d.my_label, d.c1_category)
    print(f"You labeled {len(d)} items.")
    print(f"Your labels against the first AI coder:  kappa {k:.2f} (95% interval {lo:.2f} to {hi:.2f}), agreement {(d.my_label == d.c1_category).mean() * 100:.0f}%")
    if c2:
        d2 = d.merge(pd.concat(c2).rename(columns={"category": "c2_category"}), on="vid", how="inner")
        k, lo, hi = kappa_ci(d2.my_label, d2.c2_category)
        print(f"Your labels against the second AI coder: kappa {k:.2f} (95% interval {lo:.2f} to {hi:.2f}), agreement {(d2.my_label == d2.c2_category).mean() * 100:.0f}%")
        ab = d2[d2.about_this_city.str.strip().str.lower().isin(["yes", "no", "unclear"])]
        if len(ab): print(f"'About this city?' agreement with the second AI coder: {(ab.about_this_city.str.strip().str.lower() == ab.about_city).mean() * 100:.0f}% on {len(ab)} items")
    else:
        print("The second AI coder's labels are not on this machine yet.")
    print("The threshold used in the study is 0.61.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
