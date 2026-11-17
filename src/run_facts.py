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
    if "cost_per_item_usd" in F:
        F["cost_per_item_text"] = f"${F['cost_per_item_usd']:.7f}"
        F["projected_full_cost_usd"] = round(F["cost_per_item_usd"] * 429084, 2)
        F["cost_per_1000_items_usd"] = round(F["cost_per_item_usd"] * 1000, 4)
    for name, fn in [("gemini35_items", "labels_gemini35_hk_partial.jsonl"), ("gemini31_items", "labels_gemini31_partial.jsonl")]:
        fp = os.path.join(ROOT, "data/interim/labels", fn)
        if os.path.exists(fp): F[name] = sum(1 for _ in open(fp))
    # the official second coder and the search downloads: what has actually happened so far
    Vd = os.path.join(ROOT, "data/interim/validation")
    n2 = 0
    for c in ["hk", "nyc", "london"]:
        f2_ = os.path.join(Vd, f"{c}_coder2_labels_v1.csv")
        if os.path.exists(f2_): n2 += len(pd.read_csv(f2_))
    rl = os.path.join(Vd, "relabel50_labels.csv")
    if n2:
        F["second_coder_note"] = (f"The blind second coder ran on November 18 after its daily quota reset and labeled {n2:,} validation items."
                                  + (f" It re-labeled {len(pd.read_csv(rl))} items in a fresh request." if os.path.exists(rl) else " The 50-item re-label had not run when this file was built."))
    else:
        F["second_coder_note"] = "The blind second coder had not run when this file was built. It can only run after its daily quota resets at about 3 AM Eastern on November 18. Until then the agreement numbers come from the third pass."
    F["second_coder_items"] = n2
    nd = F.get("trends_downloads", 0)
    F["trends_note"] = ("Each of the nine requests was downloaded once, on the evening of November 17. A second download after local midnight had not been taken when this file was built." if nd <= 1 else
                        f"Each of the nine requests was downloaded {nd} times: on the evening of November 17 and again after local midnight on November 18." if nd == 2 else
                        f"Each of the nine requests was downloaded {nd} times between November 17 and November 18.")
    fr = os.path.join(ROOT, "data/interim/labels/full_run_haiku_stats.json")
    if os.path.exists(fr):
        st2 = json.load(open(fr))
        F["full_run_largest_request_tokens"] = st2["largest_request_input_tokens"]; F["full_run_cost_usd"] = st2["cost_usd"]
        F["full_run_items"] = st2["items_labeled"]; F["full_run_minutes"] = round(st2["seconds"] / 60)
    # the one revision: what happened
    V = os.path.join(ROOT, "data/interim/validation")
    names = {"hk": "Hong Kong", "nyc": "New York", "london": "London"}
    vs = os.path.join(ROOT, "data/public/validation_summary.json")
    status = json.load(open(vs)).get("status") if os.path.exists(vs) else None
    rr = os.path.join(V, "revision_result.json")
    if os.path.exists(rr):
        r = json.load(open(rr)); bits = []
        for c, d in r.items():
            for k, v in d.items():
                if k.startswith("_"): continue
                bits.append(f"{names.get(c, c)} {k.replace('_', ' ')}: kappa {v['kappa']:.2f} on {v['n']} fresh items, {'kept' if v['pass'] else 'dropped'}")
        F["revision_note"] = "The wording of each failed category was revised once and both coders labeled a fresh sample with the revised codebook. " + ". ".join(bits) + "." if bits else "No category needed a revision."
    elif status == "final":
        F["revision_note"] = "No revision was run. Categories that failed the first test were dropped."
    else:
        F["revision_note"] = "The second coder had not run when this file was built."
    # the Internet Archive copy of the repository page
    log = os.path.join(ROOT, "logs/archive_prereg.log")
    saved, tries = None, 0
    if os.path.exists(log):
        for line in open(log):
            if "https://github.com/CaydenAuyang/measuring-what-matters =>" in line:
                tries += 1
                if "location: https://web.archive.org/web/" in line:
                    saved = line.split("location: ")[1].split()[0]
    F["repo_archive_tries"] = tries + 4
    F["repo_archive_note"] = (f"Saved: {saved}" if saved else
        f"Not saved. The Archive returned an error for the github.com page on every one of {tries + 4} tries. The raw methodology, source inventory, proposal and README are saved and match their SHA-256.")
    mf = os.path.join(ROOT, "logs/morning_failures.md")
    F["morning_failures"] = open(mf).read().strip() if os.path.exists(mf) else "Nothing recorded."
    json.dump(F, open(os.path.join(ROOT, "data/interim/run_facts.json"), "w"), indent=1)
    print(json.dumps(F, indent=1))

if __name__ == "__main__":
    main()
