"""Wait for a labeling round to finish for a city, then draw the validation candidates, fetch their
pages (live, then Internet Archive) and write the blind package for the second coder.

Usage: python src/validation_prepare.py <city> <group[,group]> [--tag v1]
"""
import argparse, os, subprocess, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import validation_draw, validation_lib as VL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def blocked_site_titles(city, tag):
    """Candidates from a site that challenged automated requests are never fetched (not from the site and
    not from an archive copy). From 2020 on GDELT stores each page's real title, so those items get the real
    headline alone (source 'gdelt_title'). Earlier items are recorded as 'blocked' and replaced by other items."""
    import html, json, re
    import bq_util, fetch_pages
    from google.cloud import bigquery
    V = os.path.join(ROOT, "data/interim/validation")
    c = pd.read_csv(os.path.join(V, f"{city}_candidates_{tag}.csv"), dtype=str)
    pages = os.path.join(V, f"{city}_pages_{tag}.jsonl")
    have = set()
    if os.path.exists(pages):
        have = {json.loads(l)["item_id"] for l in open(pages) if l.strip()}
    b = c[c.url.map(lambda u: any(d in u for d in fetch_pages.BLOCKED_SITES)) & ~c.item_id.isin(have)]
    if b.empty:
        return
    s = b[b.pdate >= "2020-01-01"][["item_id", "url", "pdate"]]
    titles = {}
    if len(s):
        cl = bq_util.client()
        cl.load_table_from_dataframe(s, "ourcityhealth.mwm.val_title_urls", job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
        dl = ",".join(f"TIMESTAMP('{d}')" for d in sorted(s.pdate.unique()))
        sql = f"""SELECT u.item_id, ANY_VALUE(REGEXP_EXTRACT(g.Extras, r'<PAGE_TITLE>(.*?)</PAGE_TITLE>')) AS page_title
FROM `gdelt-bq.gdeltv2.gkg_partitioned` g JOIN `ourcityhealth.mwm.val_title_urls` u ON g.DocumentIdentifier = u.url
WHERE g._PARTITIONTIME IN ({dl}) GROUP BY 1"""
        t, _ = bq_util.run(sql, "phase4", f"stored page titles for blocked-site validation candidates ({city} {tag})", to_df=True)
        for r in t.itertuples():
            ti = re.sub(r"\s+", " ", html.unescape(r.page_title or "")).strip()
            if len(ti) >= 8: titles[r.item_id] = ti[:300]
    with open(pages, "a") as f:
        for r in b.itertuples():
            if r.item_id in titles:
                f.write(json.dumps(dict(item_id=r.item_id, source="gdelt_title", title=titles[r.item_id], opening="", fetched_url="", desc=""), ensure_ascii=False) + "\n")
            else:
                f.write(json.dumps(dict(item_id=r.item_id, source="blocked", title="", opening="", fetched_url="", desc="")) + "\n")
    print(f"blocked-site candidates: {len(b)}; real headlines from GDELT: {len(titles)}; recorded as blocked: {len(b) - len(titles)}", flush=True)

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
    blocked_site_titles(a.city, a.tag)
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
