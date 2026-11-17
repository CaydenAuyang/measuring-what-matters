"""BigQuery helper: every query gets a dry run, a cost-log line, and a 1.2x byte cap."""
import csv, datetime, os, sys
from google.cloud import bigquery

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = "ourcityhealth"
DATASET = "mwm"
COST_LOG = os.path.join(ROOT, "logs", "bigquery_costs.csv")
CAP_TOTAL_BYTES = 8 * 1024**4  # 8 TB billed in total (spend cap)

_client = None
def client():
    global _client
    if _client is None:
        _client = bigquery.Client(project=PROJECT)
    return _client

def billed_so_far():
    tot = 0
    if os.path.exists(COST_LOG):
        with open(COST_LOG) as f:
            for r in csv.DictReader(f):
                try: tot += int(r["actual_bytes_billed"] or 0)
                except ValueError: pass
    return tot

def run(sql, phase, label, destination=None, write="WRITE_TRUNCATE", dry_only=False, to_df=False):
    """Dry run, log, then run with maximum_bytes_billed = 1.2 x estimate. Returns (job or df, est_bytes)."""
    c = client()
    dry = c.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
    est = dry.total_bytes_processed
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if dry_only:
        with open(COST_LOG, "a") as f:
            csv.writer(f).writerow([phase, label + " (dry run only)", est, "", 0, now])
        return None, est
    if billed_so_far() + est > CAP_TOTAL_BYTES:
        raise RuntimeError(f"Spend cap: {label} would pass 8 TB billed (est {est/1e9:.1f} GB)")
    cap = max(int(est * 1.2), 10 * 1024**2)
    cfg = bigquery.QueryJobConfig(maximum_bytes_billed=cap, use_query_cache=False)
    if destination:
        cfg.destination = f"{PROJECT}.{DATASET}.{destination}"
        cfg.write_disposition = write
    job = c.query(sql, job_config=cfg)
    job.result()
    with open(COST_LOG, "a") as f:
        csv.writer(f).writerow([phase, label, est, cap, job.total_bytes_billed or 0, now])
    print(f"[bq] {label}: est {est/1e9:.2f} GB, billed {(job.total_bytes_billed or 0)/1e9:.2f} GB", file=sys.stderr)
    if to_df:
        return job.to_dataframe(), est
    return job, est

def ensure_dataset():
    c = client()
    ds = bigquery.Dataset(f"{PROJECT}.{DATASET}")
    ds.location = "US"
    c.create_dataset(ds, exists_ok=True)
