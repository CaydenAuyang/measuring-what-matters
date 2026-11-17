"""Assemble the public dataset in data/public/: monthly attention shares, official series, yearly changes,
and sample sizes. Monthly shares and official series only. No article-level text.
"""
import json, os, shutil, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import outlets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "data/public"); INT = os.path.join(ROOT, "data/interim")

def main():
    # official series (levels, with break flags) and their descriptions
    frames, meta = [], []
    for c in outlets.CITIES:
        d = pd.read_csv(os.path.join(INT, f"official/{c}_official.csv"), dtype={"period": str})
        frames.append(d)
        meta += json.load(open(os.path.join(INT, f"official/{c}_meta.json")))
    off = pd.concat(frames, ignore_index=True)
    keep = ["city", "category", "role", "series_id", "component", "indicator_name", "frequency", "period", "period_end_date", "window_months",
            "value", "unit", "worse_when", "change_rule", "break_flag", "break_note", "provisional"]
    off = off[off.value.notna()][keep]
    off.to_csv(os.path.join(PUB, "official_series.csv"), index=False)
    json.dump(meta, open(os.path.join(PUB, "official_series_meta.json"), "w"), indent=1)
    # search attention
    t = pd.read_csv(os.path.join(INT, "trends/trends_shares.csv"))
    t.to_csv(os.path.join(PUB, "search_attention_monthly.csv"), index=False)
    # sample sizes per outlet and month
    mc = pd.read_csv(os.path.join(INT, "gdelt/monthly_counts.csv"))
    it = pd.read_parquet(os.path.join(INT, "labels/items_ordered.parquet"), columns=["item_id", "city", "outlet", "month", "in_main", "in_check"])
    lab = pd.read_json(os.path.join(INT, "labels/labels_main.jsonl"), lines=True).drop_duplicates("item_id")[["item_id"]]
    it = it.merge(lab.assign(labeled=1), on="item_id", how="left").fillna({"labeled": 0})
    g = it.groupby(["city", "outlet", "month"]).agg(n_labeled_main=("labeled", lambda s: int(s[it.loc[s.index, "in_main"]].sum())),
                                                     n_labeled_check=("labeled", lambda s: int(s[it.loc[s.index, "in_check"]].sum()))).reset_index()
    ss = mc.merge(g, on=["city", "outlet", "month"], how="left").fillna({"n_labeled_main": 0, "n_labeled_check": 0})
    ss["outlet_name"] = ss.outlet.map(lambda k: outlets.BY_KEY[k]["name"])
    ss["panel"] = ss.outlet.map(lambda k: outlets.BY_KEY[k]["panel"])
    ss = ss.rename(columns={"n_gdelt_rows": "n_gdelt_records", "n_after_filter": "n_after_city_filter_and_dedupe",
                            "n_sample_main": "n_sampled_main_panel", "n_sample_check": "n_sampled_all_outlets_check"})
    cols = ["city", "outlet", "outlet_name", "panel", "month", "n_gdelt_records", "n_after_city_filter_and_dedupe", "n_sampled_main_panel",
            "n_sampled_all_outlets_check", "n_labeled_main", "n_labeled_check"]
    ss[cols].sort_values(["city", "outlet", "month"]).to_csv(os.path.join(PUB, "sample_sizes.csv"), index=False)
    by_city_month = ss[ss.panel == "main"].groupby(["city", "month"]).agg(n_sampled=("n_sampled_main_panel", "sum"), n_labeled=("n_labeled_main", "sum"),
                                                                           outlets_with_articles=("n_sampled_main_panel", lambda s: int((s > 0).sum()))).reset_index()
    by_city_month.to_csv(os.path.join(PUB, "sample_sizes_by_city_month.csv"), index=False)
    # the pre-registered inputs, for convenience
    shutil.copy(os.path.join(ROOT, "src/trends/term_sets.json"), os.path.join(PUB, "search_term_sets.json"))
    pd.DataFrame([{k: o.get(k) for k in ["key", "name", "city", "domain", "panel", "number_only"]} for o in outlets.OUTLETS]).to_csv(os.path.join(PUB, "outlets.csv"), index=False)
    files = sorted(f for f in os.listdir(PUB))
    print("public files:", files)
    print("official rows", len(off), "| search rows", len(t), "| sample-size rows", len(ss))
    s = by_city_month.groupby("city").n_labeled.agg(["min", "median", "max"]); print(s.to_string())

if __name__ == "__main__":
    main()
