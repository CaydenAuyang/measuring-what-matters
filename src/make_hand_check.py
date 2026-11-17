"""Build the optional hand-check file: 50 validation items for Cayden to label himself, if he wants to.

Columns: id, city, outlet, web_address, headline, opening_lines, my_label (blank), about_this_city (blank).
The AI coders' labels are NOT in this file. Nobody fills it in during the run.
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import outlets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")

def main():
    parts = []
    for city, n in [("hk", 17), ("nyc", 17), ("london", 16)]:
        d = pd.read_csv(os.path.join(V, f"{city}_validation_set_v1.csv"), dtype=str)
        parts.append(d.sample(n, random_state=50))
    s = pd.concat(parts).sample(frac=1, random_state=51).reset_index(drop=True)
    out = pd.DataFrame({"id": s.vid, "city": s.city.map(outlets.CITY_NAMES), "outlet": s.outlet.map(lambda k: outlets.BY_KEY[k]["name"]),
                        "web_address": s.url, "headline": s.title, "opening_lines": s.opening, "my_label": "", "about_this_city": ""})
    path = os.path.join(ROOT, "deliverables/optional_hand_check_50.csv")
    out.to_csv(path, index=False)
    print("wrote", path, len(out), "items. Allowed labels:", ", ".join(outlets.CATEGORIES + ["not_civic"]), "| about_this_city: yes / no / unclear")

if __name__ == "__main__":
    main()
