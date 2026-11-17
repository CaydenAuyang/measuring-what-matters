"""Validation text, last fallback: the real headline that GDELT stored.

Order of sources for each validation item: the live page, then the Internet Archive. If neither can be read
and the article is from 2020 on (when GDELT began storing page titles), the second coder reads the real
headline alone, taken from GDELT's stored page title. Items before 2020 with no readable page are replaced by
the next item from the same category and city. A site that challenged automated requests is never fetched;
its items go straight to this fallback (see validation_prepare.blocked_site_titles).

Usage: python src/stored_title_fallback.py <city> [--tag v1]
"""
import argparse, html, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import bq_util
from google.cloud import bigquery

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")

def run(city, tag):
    c = pd.read_csv(os.path.join(V, f"{city}_candidates_{tag}.csv"), dtype=str)
    pages = os.path.join(V, f"{city}_pages_{tag}.jsonl")
    rows = [json.loads(l) for l in open(pages) if l.strip()]
    by = {}
    for r in rows: by.setdefault(r["item_id"], r)
    none_ids = {i for i, r in by.items() if r["source"] in ("none", "blocked")}
    s = c[c.item_id.isin(none_ids) & (c.pdate >= "2020-01-01")][["item_id", "url", "pdate"]]
    if s.empty:
        print(city, tag, "nothing to look up"); return 0
    cl = bq_util.client()
    cl.load_table_from_dataframe(s, "ourcityhealth.mwm.val_title_urls", job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    dl = ",".join(f"TIMESTAMP('{d}')" for d in sorted(s.pdate.unique()))
    sql = f"""SELECT u.item_id, ANY_VALUE(REGEXP_EXTRACT(g.Extras, r'<PAGE_TITLE>(.*?)</PAGE_TITLE>')) AS page_title
FROM `gdelt-bq.gdeltv2.gkg_partitioned` g JOIN `ourcityhealth.mwm.val_title_urls` u ON g.DocumentIdentifier = u.url
WHERE g._PARTITIONTIME IN ({dl}) GROUP BY 1"""
    t, _ = bq_util.run(sql, "phase4", f"stored page titles for validation items with no readable page ({city} {tag})", to_df=True)
    n = 0
    for r in t.itertuples():
        ti = re.sub(r"\s+", " ", html.unescape(r.page_title or "")).strip()
        if len(ti) >= 8:
            by[r.item_id] = dict(item_id=r.item_id, source="gdelt_title", title=ti[:300], opening="", fetched_url="", desc=""); n += 1
    with open(pages, "w") as f:
        for r in by.values(): f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(city, tag, f"looked up {len(s)} items with no readable page from 2020 on; real headlines found: {n}")
    return n

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("city"); ap.add_argument("--tag", default="v1")
    a = ap.parse_args()
    run(a.city, a.tag)
