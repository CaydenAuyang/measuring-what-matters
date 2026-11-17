"""Collect facts about the run itself (costs, counts, times) from the logs into data/interim/run_facts.json,
so documents can quote them by token."""
import csv, glob, json, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    F = {}
    bq = pd.read_csv(os.path.join(ROOT, "logs/bigquery_costs.csv"))
    billed = pd.to_numeric(bq.actual_bytes_billed, errors="coerce").fillna(0).sum()
    F["bigquery_queries"] = int(len(bq)); F["bigquery_tb_billed"] = round(billed / 1e12, 2)
    F["bigquery_cost_usd"] = round(billed / 1e12 * 6.25, 2); F["bigquery_cap_tb"] = 8
    api = pd.read_csv(os.path.join(ROOT, "logs/api_costs.csv"))
    api["est_cost_usd"] = pd.to_numeric(api.est_cost_usd, errors="coerce").fillna(0)
    claude = api[api.model.astype(str).str.startswith("claude")]
    gem = api[api.model.astype(str).str.startswith("gemini")]
    F["anthropic_cost_usd"] = round(float(claude.est_cost_usd.sum()), 2)
    F["anthropic_requests"] = int(pd.to_numeric(claude.requests, errors="coerce").fillna(0).sum())
    F["gemini_requests"] = int(pd.to_numeric(gem.requests, errors="coerce").fillna(0).sum())
    F["gemini_cost_usd"] = 0.0      # free tier: nothing was billed
    F["language_model_cap_usd"] = 100
    st = os.path.join(ROOT, "data/interim/labels/first2000_haiku_stats.json")
    if os.path.exists(st):
        s = json.load(open(st)); F["cost_per_item_usd"] = s["cost_per_item_usd"]; F["first2000_cost_usd"] = s["cost_usd"]
        F["largest_request_tokens"] = s["largest_request_input_tokens"]
    try:
        lab = pd.read_json(os.path.join(ROOT, "data/interim/labels/labels_main.jsonl"), lines=True).drop_duplicates("item_id")
        F["items_labeled_total"] = int(len(lab))
        smp = pd.read_parquet(os.path.join(ROOT, "data/interim/gdelt/sample.parquet"), columns=["item_id", "no_input"])
        F["items_sampled_total"] = int(len(smp)); F["items_no_input"] = int(smp.no_input.sum())
        F["items_unlabeled"] = int(len(smp) - smp.no_input.sum() - len(lab))
    except Exception:
        pass
    tr = glob.glob(os.path.join(ROOT, "data/raw/trends/*.csv"))
    tr = [t for t in tr if "manifest" not in os.path.basename(t)]
    F["trends_files"] = len(tr); F["trends_downloads"] = len(tr) // 9
    pages = 0; tried = 0
    for p in glob.glob(os.path.join(ROOT, "data/interim/validation/*_pages_v*.jsonl")):
        d = pd.read_json(p, lines=True)
        if len(d): tried += len(d); pages += int(d.source.isin(["live", "archive"]).sum())
    F["pages_tried_total"] = tried; F["pages_fetched_total"] = pages
    F["prereg_commit"] = "e8d5f32"; F["prereg_utc"] = "2026-11-17T20:31:07Z"; F["prereg_tag"] = "prereg-v1"
    F["repository"] = "https://github.com/CaydenAuyang/measuring-what-matters"
    off = []
    for c in ["hk", "nyc", "london"]:
        p = os.path.join(ROOT, f"data/raw/official/{c}/manifest.csv")
        if os.path.exists(p): off.append(len(pd.read_csv(p)))
    F["official_raw_files"] = int(sum(off))
    mf = os.path.join(ROOT, "logs/morning_failures.md")
    F["morning_failures"] = open(mf).read().strip() if os.path.exists(mf) else "Nothing recorded."
    json.dump(F, open(os.path.join(ROOT, "data/interim/run_facts.json"), "w"), indent=1)
    print(json.dumps(F, indent=1))

if __name__ == "__main__":
    main()
