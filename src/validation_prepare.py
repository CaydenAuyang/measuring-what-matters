"""Wait for a labeling round to finish for a city, then draw the validation candidates, fetch their
pages (live, then Internet Archive) and write the blind package for the second coder.

Usage: python src/validation_prepare.py <city> <group[,group]> [--tag v1]
"""
import argparse, os, subprocess, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import validation_draw, validation_lib as VL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def round_done(city, groups, tol=0.01):
    it = pd.read_parquet(os.path.join(ROOT, "data/interim/labels/items_ordered.parquet"), columns=["item_id", "grp", "city"])
    ids = set(it[(it.city == city) & it.grp.isin(groups)].item_id)
    try:
        lab = set(pd.read_json(os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True).item_id)
    except Exception:
        return False
    return len(ids - lab) <= tol * len(ids)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("city"); ap.add_argument("groups"); ap.add_argument("--tag", default="v1"); ap.add_argument("--nowait", action="store_true")
    ap.add_argument("--exclude-tag", default="")      # a fresh sample: leave out every candidate of an earlier draw
    a = ap.parse_args()
    groups = a.groups.split(",")
    while not a.nowait and not round_done(a.city, groups):
        if os.path.exists(os.path.join(ROOT, "logs/gemini_daily_quota.flag")):
            print("daily quota flag present; drawing from what is labeled", flush=True); break
        time.sleep(30)
    print("round done at", time.strftime("%H:%M:%S"), flush=True)
    if not os.path.exists(os.path.join(ROOT, f"data/interim/validation/{a.city}_candidates_{a.tag}.csv")):
        excl = None
        if a.exclude_tag:
            excl = set(pd.read_csv(os.path.join(ROOT, f"data/interim/validation/{a.city}_candidates_{a.exclude_tag}.csv"), dtype=str).item_id)
        validation_draw.draw(a.city, groups, a.tag, exclude_ids=excl)       # the draw is made once; a restart reuses it
    V = os.path.join(ROOT, "data/interim/validation")
    c = pd.read_csv(os.path.join(V, f"{a.city}_candidates_{a.tag}.csv"), dtype=str)
    c["order_in_category"] = c.order_in_category.astype(int); c["need"] = c.need.astype(int)
    pages = os.path.join(V, f"{a.city}_pages_{a.tag}.jsonl")
    # fetch in rounds: for each category only as many further candidates as are still needed (in the seeded order)
    for rnd in range(8):
        got = pd.read_json(pages, lines=True, dtype={"item_id": str}).drop_duplicates("item_id") if os.path.exists(pages) and os.path.getsize(pages) else pd.DataFrame({"item_id": [], "source": []})
        m = c.merge(got[["item_id", "source"]], on="item_id", how="left")
        todo = []
        for cat, g in m.sort_values("order_in_category").groupby("c1_category"):
            have = int(g.source.isin(["live", "archive", "gdelt_title"]).sum()); short = int(g.need.iloc[0]) - have
            if short > 0:
                todo.append(g[g.source.isna()].head(int(short * 1.5) + 2))
        todo = pd.concat(todo) if todo else pd.DataFrame()
        if len(todo) == 0:
            break
        print(f"fetch round {rnd + 1}: {len(todo)} pages", flush=True)
        todo[["item_id", "url", "pdate"]].to_csv(os.path.join(V, f"{a.city}_fetchlist_{a.tag}.csv"), index=False)
        subprocess.run([sys.executable, "-W", "ignore", os.path.join(ROOT, "src/fetch_pages.py"), "--in", os.path.join(V, f"{a.city}_fetchlist_{a.tag}.csv"),
                        "--out", pages, "--workers", "12"], check=False)
    path, rep = VL.write_package(a.city, a.tag)
    print("PACKAGE", path, "selected", rep["selected"], "tried", rep["tried"], "fetched", rep["fetched"], "short", rep["short_categories"], flush=True)
    print("FINISHED at", time.strftime("%H:%M:%S"), flush=True)
