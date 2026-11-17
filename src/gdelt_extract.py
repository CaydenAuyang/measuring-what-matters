"""Phase 2, step 3: copy every listed outlet's GDELT GKG rows, one year at a time, into ourcityhealth.mwm.

Usage:  python src/gdelt_extract.py            # all years 2015..2026 (skips years already extracted)
        python src/gdelt_extract.py 2019 2020  # only these years
Each query filters on _PARTITIONTIME, gets a dry run, is logged, and is capped at 1.2x the estimate.
"""
import sys, threading, concurrent.futures as cf
sys.path.insert(0, __import__("os").path.dirname(__file__))
import bq_util, outlets
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

START = "2015-02-19"          # GKG version 2 begins
END_EXCL = "2026-11-01"       # through the last full month, October 2026

def host_rx(domains):
    return "(^|[.])(" + "|".join(sorted(d.replace(".", "[.]") for d in domains)) + ")$"

def where_outlets():
    plain, special = [], []
    for o in outlets.OUTLETS:
        doms = [o["domain"]] + o.get("extra_domains", [])
        if o.get("url_regex"):
            special.append(f"(REGEXP_CONTAINS(NET.HOST(DocumentIdentifier), r'{host_rx(doms)}') AND REGEXP_CONTAINS(DocumentIdentifier, r'{o['url_regex']}'))")
        else:
            plain.extend(doms)
    conds = [f"REGEXP_CONTAINS(NET.HOST(DocumentIdentifier), r'{host_rx(plain)}')"] + special
    return "(" + "\n   OR ".join(conds) + ")"

def sql_year(y):
    a = max(f"{y}-01-01", START)
    b = min(f"{y+1}-01-01", END_EXCL)
    return f"""
SELECT DATE(_PARTITIONTIME) AS pdate, DATE AS gkg_datetime, SourceCommonName AS source,
       DocumentIdentifier AS url, V2Locations, V2Themes, V2Tone, TranslationInfo
FROM `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE _PARTITIONTIME >= TIMESTAMP('{a}') AND _PARTITIONTIME < TIMESTAMP('{b}')
  AND {where_outlets()}"""

lock = threading.Lock()
def do_year(y):
    c = bq_util.client()
    try:
        t = c.get_table(f"{bq_util.PROJECT}.{bq_util.DATASET}.gkg_{y}")
        if t.num_rows > 0:
            print(f"{y}: already extracted ({t.num_rows} rows)", flush=True); return y, t.num_rows
    except NotFound:
        pass
    job, est = bq_util.run(sql_year(y), "phase2", f"yearly extract {y}", destination=f"gkg_{y}")
    t = c.get_table(f"{bq_util.PROJECT}.{bq_util.DATASET}.gkg_{y}")
    print(f"{y}: {t.num_rows} rows, est {est/1e9:.1f} GB", flush=True)
    return y, t.num_rows

if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or list(range(2015, 2027))
    bq_util.ensure_dataset()
    if "--dry" in sys.argv:
        pass
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for y, n in ex.map(do_year, years):
            pass
    print("DONE", flush=True)
