"""Collect facts about the run itself (costs, counts, times) from the logs into data/interim/run_facts.json,
so documents can quote them by token."""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
    # the whole sample labeled again with the revised codebook (only when a revised category passed its retest)
    Ld = os.path.join(ROOT, "data/interim/labels")
    swapped = os.path.exists(os.path.join(Ld, "labels_main_first_codebook.jsonl"))
    F["relabeled"] = bool(swapped)
    F["prompt_first_fixed_utc"] = "2026-11-17T21:00:35Z"
    vsum = json.load(open(vs)) if os.path.exists(vs) else {}
    rv = vsum.get("revision") or {}
    if os.path.exists(rr) and rv.get("run"):
        r_ = json.load(open(rr)); cnames = {"hk": "Hong Kong", "nyc": "New York City", "london": "London"}
        from outlets import CATEGORY_NAMES as CN_
        dropped_bits = [f"{cnames[c]}: " + ", ".join(f"{CN_[k]} ({v['kappa']:.2f})" for k, v in d.items() if not k.startswith("_") and not v["pass"]) for c, d in r_.items() if any((not k.startswith("_")) and (not v["pass"]) for k, v in d.items())]
        ns = ", ".join(f"{next(v['n'] for k, v in d.items() if not k.startswith('_'))} in {cnames[c]}" for c, d in r_.items() if any(not k.startswith("_") for k in d))
        F["revision_note"] = ("The wording of the seven categories that failed in any city was revised once (" + rv["categories_reworded_text"] + "). Both coders then labeled a fresh sample with the revised codebook (scored items: " + ns + "). "
                              + "Passed the retest and kept: " + rv["kept_after_revision_text"] + " Still under 0.61 and dropped: " + ". ".join(dropped_bits) + "."
                              + " A category that passed the first test stays kept, a rule the run set before the retest was scored. Kept categories that scored under 0.61 on the fresh sample, named as cautions: " + rv["caution_text"])
        F["revision_kept_text"] = rv["kept_after_revision_text"]; F["revision_caution_text"] = rv["caution_text"]; F["revision_n_cautions"] = rv["n_cautions"]
    if swapped:
        cmpf, stf = os.path.join(Ld, "relabel_compare.json"), os.path.join(Ld, "full_run_revised_stats.json")
        cm = json.load(open(cmpf)) if os.path.exists(cmpf) else {}
        st3 = json.load(open(stf)) if os.path.exists(stf) else {}
        by = cm.get("by_city") or {}
        F["relabel_items"] = cm.get("labeled_revised_codebook"); F["relabel_cost_usd"] = st3.get("cost_usd")
        F["relabel_minutes"] = round(st3["seconds"] / 60) if st3.get("seconds") else None
        F["relabel_largest_request_tokens"] = st3.get("largest_request_input_tokens")
        F["first_codebook_items"] = cm.get("labeled_first_codebook")
        same = ", ".join(f"{names[c]} {by[c]['same_category_share'] * 100:.0f}% (kappa {by[c]['kappa_first_vs_revised']:.2f})" for c in ["hk", "nyc", "london"] if c in by)
        F["relabel_same_text"] = same
        F["relabel_note"] = (f"Because revised categories passed the retest, every article was labeled a second time on November 18 with the revised prompt, by the same model with the same settings ({F['relabel_items']:,} items"
                             + (f", ${F['relabel_cost_usd']:.2f}" if F.get("relabel_cost_usd") else "") + (f", {F['relabel_minutes']} minutes" if F.get("relabel_minutes") else "")
                             + f"). Every news number in the results rests on this second set of labels. The first validation test, the headline check and the consistency checks were run on the first set of labels. The AI-written notes on causes and events were read from samples drawn under the first labels. The two sets give the same category for these shares of articles: {same}.")
        F["prompt_history_note"] = (f"The first prompt was fixed at {F['prompt_first_fixed_utc']} and labeled every article once. After the validation retest on November 18, seven category lines were reworded once (Section 4.3) and every article was labeled again with the revised prompt. The results use the second set of labels.")
        F["prompt_frozen_note"] = "The first prompt was fixed before the full run and did not change during it. After validation, the one revision the plan allows changed seven category lines, and every article was labeled again with the revised prompt."
        F["cost_twice_note"] = "That total includes labeling every article twice, because the one wording revision came after the first full run."
        F["labels_made_with"] = "the revised prompt (`news-v2`)"
        F["relabel_short_note"] = "After validation, the run reworded seven category lines once, as the plan allows, and labeled every article a second time. Some kept categories scored under the bar on the retest sample. `data/public/validation_report.md` shows both readings."
    else:
        F["relabel_note"] = "No article was labeled a second time."
        F["prompt_history_note"] = f"The prompt has not changed since {F['prompt_first_fixed_utc']}."
        F["prompt_frozen_note"] = "The prompt was frozen once and never changed."
        F["labels_made_with"] = "the frozen prompt (`news-v1`)"
        F["cost_twice_note"] = ""
        F["relabel_short_note"] = ""
    # the same analysis on the labels from the first codebook (snapshot of results.json taken before the relabel)
    fc = os.path.join(ROOT, "data/interim/results_first_codebook.json")
    if swapped and os.path.exists(fc):
        import shutil
        shutil.copyfile(fc, os.path.join(ROOT, "data/public/results_first_codebook.json"))
        R1 = json.load(open(fc)); h = R1["main"]["news"]["h1"]; hc_ = R1["checks"]["without_covid"]["news"]["h1"]
        F["first_codebook_news_h1_est"] = h["est"]; F["first_codebook_news_h1_ci_low"] = h["ci_low"]; F["first_codebook_news_h1_ci_high"] = h["ci_high"]; F["first_codebook_news_h1_pairs"] = h["n_pairs"]
        F["first_codebook_note"] = (f"Exploratory comparison: with the labels from the first codebook, and the categories that failed the first test dropped with no retest, the pooled news slope was {h['est']:.2f} ({h['ci_low']:.2f} to {h['ci_high']:.2f}) across {h['n_pairs']} pairs, "
                                    f"and {hc_['est']:.2f} ({hc_['ci_low']:.2f} to {hc_['ci_high']:.2f}) without 2020 to 2022. News verdicts there: H1 {R1['verdicts']['h1_news']}, H2 {R1['verdicts']['h2_news']}, H3 {R1['verdicts']['h3_news']}. That results file is saved as `data/public/results_first_codebook.json`.")
    else:
        F["first_codebook_note"] = ""
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
