"""The one allowed revision (methodology, "AI labeling and validation", decision rule).

A category whose kappa falls below 0.61 in a city gets ONE revision of its wording. Both coders then label
a fresh sample with the revised codebook, and the category is tested again. If it still falls short it is
dropped for that city.

The revised wording lives in src/codebook_revision.json:
  {"categories": {"<category>": "<category> | <Covers> | <Goes elsewhere>"}, "note": "...", "written_utc": "..."}
Usage:
  python src/revision.py prompts                      # write the two revised prompt files
  python src/revision.py first  --cities hk,nyc       # first coder labels the fresh sample with the revised prompt
  python src/revision.py second --cities hk,nyc --model gemini-3.5-flash-lite   # second coder, blind
  python src/revision.py score                        # kappa for each failed category on the fresh sample
"""
import argparse, json, os, subprocess, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets, validation_lib as VL, validation_score as VS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")
REV = os.path.join(ROOT, "src/codebook_revision.json")
P1 = os.path.join(ROOT, "src/prompt_first_coder_revised.txt")
P2 = os.path.join(ROOT, "src/prompt_second_coder_revised.md")

def revised(text, rows):
    out = []
    for line in text.split("\n"):
        key = line.split(" | ")[0].strip()
        out.append(rows[key] if key in rows and " | " in line else line)
    return "\n".join(out)

def prompts():
    rows = json.load(open(REV))["categories"]
    for k, v in rows.items():
        assert k in outlets.CATEGORIES and v.startswith(k + " | "), (k, v)
    open(P1, "w").write(revised(codebook.SYSTEM_PROMPT, rows))
    open(P2, "w").write(revised(open(os.path.join(ROOT, "src/coder2_prompt.md")).read(), rows))
    print("revised prompts written for:", list(rows))

def first(cities):
    items = pd.read_parquet(os.path.join(ROOT, "data/interim/labels/items_ordered.parquet"), columns=["item_id", "city", "outlet", "headline", "themes"])
    for c in cities:
        vs = pd.read_csv(os.path.join(V, f"{c}_validation_set_v2.csv"), dtype=str)
        sub = items[items.item_id.isin(vs.item_id)]
        p = os.path.join(V, f"{c}_fresh_items_v2.parquet"); sub.to_parquet(p, index=False)
        out = os.path.join(V, f"{c}_first_revised_labels_v2.jsonl")
        subprocess.run([sys.executable, "-W", "ignore", os.path.join(ROOT, "src/labeler_claude.py"), "--items", p, "--out", out, "--system", P1,
                        "--workers", "8", "--budget", "2", "--task", f"revision: first coder, fresh sample, {c}"], check=True)

def second(cities, model, rpm):
    for c in cities:
        subprocess.run([sys.executable, "-W", "ignore", os.path.join(ROOT, "src/coder2_gemini.py"), "--city", c, "--model", model, "--role", "coder2rev",
                        "--tag", "v2", "--system", P2, "--rpm", str(rpm)], check=True)

def score(role="coder2", status_role="coder2rev"):
    res = {}
    summary = json.load(open(os.path.join(ROOT, "data/public/validation_summary.json")))
    for c in outlets.CITIES:
        failed = (summary["cities"].get(c) or {}).get("failed_first_test") or []
        p1 = os.path.join(V, f"{c}_first_revised_labels_v2.jsonl"); p2 = os.path.join(V, f"{c}_{status_role}_labels_v2.csv")
        if not failed or not (os.path.exists(p1) and os.path.exists(p2)):
            continue
        vs = pd.read_csv(os.path.join(V, f"{c}_validation_set_v2.csv"), dtype={"item_id": str, "vid": str})
        a = pd.read_json(p1, lines=True, dtype={"item_id": str}).drop_duplicates("item_id")[["item_id", "category"]].rename(columns={"category": "c1_revised"})
        b = pd.read_csv(p2, dtype={"vid": str}).drop_duplicates("vid")[["vid", "category"]].rename(columns={"category": "c2_category"})
        d = vs.merge(a, on="item_id").merge(b, on="vid")
        d["stratum"] = d["c1_category"]          # the fresh sample was stratified by the first coder's original label
        d["retained"] = True
        for e in VS.excluded_rules():
            if e["city"] == c:
                d.loc[d.outlet.isin(e["outlets"]) & (d.month >= e["from"]) & (d.month <= e["to"]), "retained"] = False
        d = d[d.retained]
        pc, _ = VS.pool_counts(c, retained_only=True)
        sc = VL.score(d, pc, a_col="c1_revised", b_col="c2_category")
        res[c] = {k: {"kappa": sc["by_category"][k]["kappa_weighted"], "ci_low": sc["by_category"][k]["ci_low"], "ci_high": sc["by_category"][k]["ci_high"],
                      "n": int(len(d)), "n_first": sc["by_category"][k]["n_coder1"], "n_second": sc["by_category"][k]["n_coder2"],
                      "pass": bool(sc["by_category"][k]["kappa_weighted"] >= 0.61)} for k in failed}
        res[c]["_all_categories_on_fresh_sample"] = {k: sc["by_category"][k]["kappa_weighted"] for k in codebook.LABELS}
    json.dump(res, open(os.path.join(V, "revision_result.json"), "w"), indent=1)
    for c, r in res.items():
        print(c, {k: (round(v["kappa"], 2), v["pass"]) for k, v in r.items() if not k.startswith("_")})
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("--cities", default="hk,nyc,london"); ap.add_argument("--model", default="gemini-3.5-flash-lite"); ap.add_argument("--rpm", type=float, default=6)
    a = ap.parse_args()
    cities = a.cities.split(",")
    if a.step == "prompts": prompts()
    elif a.step == "first": first(cities)
    elif a.step == "second": second(cities, a.model, a.rpm)
    elif a.step == "score": score()
