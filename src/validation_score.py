"""Phase 4, steps 4 to 6: score agreement between the first coder and the blind second coder, apply the
0.61 rule, and write the validation summary, the report, and the index configuration.

Usage: python src/validation_score.py --role coder2 --status final
       python src/validation_score.py --role thirdpass --status provisional   (before the second coder has run)

Reads  data/interim/validation/<city>_validation_set_<tag>.csv   (first coder's labels; never shown to the second coder)
       data/interim/validation/<city>_<role>_labels_<tag>.csv    (second coder: vid, category, tone, about_city)
       data/interim/validation/headline_check_result.json, revision_result.json (if present)
Writes data/public/validation_summary.json, data/public/validation_report.md, data/interim/index_config.json
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets, validation_lib as VL, build_index

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")
PUB = os.path.join(ROOT, "data/public")
THRESHOLD = 0.61
ANALYZED = outlets.CATEGORIES            # the twelve categories; not_civic is reported but is not a category to drop

def jload(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default

def load_city(city, role, tag="v1"):
    p = os.path.join(V, f"{city}_{role}_labels_{tag}.csv")
    vsp = os.path.join(V, f"{city}_validation_set_{tag}.csv")
    if not os.path.exists(p) or not os.path.exists(vsp):
        return None
    vs = pd.read_csv(vsp, dtype={"item_id": str, "vid": str})
    c2 = pd.read_csv(p, dtype={"vid": str}).drop_duplicates("vid")
    d = vs.merge(c2.rename(columns={"category": "c2_category", "tone": "c2_tone"}), on="vid", how="inner")
    d["stratum"] = d["c1_category"]
    return d

def pool_counts(city):
    d = build_index.load()
    level = build_index.levels_done(d)
    order = list(build_index.LEVEL_CAPS)
    use = order[: order.index(level) + 1] if level else order[:1]
    m = d[d.in_main & d.level.isin(use) & (d.city == city) & d.category.notna()]
    return m.category.value_counts().to_dict(), level

def city_block(city, role, tag="v1"):
    d = load_city(city, role, tag)
    if d is None or len(d) < 50:
        return None
    pc, level = pool_counts(city)
    sc = VL.score(d, pc)
    N = sum(pc.values()); n_s = d.stratum.value_counts()
    w = d.stratum.map(lambda s: (pc.get(s, 0) / N) / (n_s[s] / len(d))).to_numpy()
    not_about = (d.about_city == "no").to_numpy()
    tone_k = VL.wkappa(d.c1_tone.to_numpy(), d.c2_tone.to_numpy(), w, codebook.TONES)
    fetch = jload(os.path.join(V, f"{city}_fetch_report_{tag}.json"), {})
    block = {
        "n_items": int(len(d)), "labeling_round_for_weights": level,
        "overall_kappa": sc["overall"]["kappa_weighted"], "overall_ci_low": sc["overall"]["ci_low"], "overall_ci_high": sc["overall"]["ci_high"],
        "overall_kappa_unweighted": sc["overall"]["kappa_unweighted"],
        "overall_agreement": sc["overall"]["agreement_weighted"], "overall_agreement_unweighted": sc["overall"]["agreement_unweighted"],
        "tone_kappa": tone_k,
        "categories": {k: {"kappa": v["kappa_weighted"], "kappa_unweighted": v["kappa_unweighted"], "ci_low": v["ci_low"], "ci_high": v["ci_high"],
                           "pass": bool(v["kappa_weighted"] >= THRESHOLD), "n_first": v["n_coder1"], "n_second": v["n_coder2"]}
                       for k, v in sc["by_category"].items()},
        "confusion_counts": sc["confusion_counts"],
        "not_about_city_share": float((w * not_about).sum() / w.sum()),
        "not_about_city_share_unweighted": float(not_about.mean()),
        "not_about_city_by_category": {k: {"n": int((d.c1_category == k).sum()), "share_not_about_city": float(not_about[(d.c1_category == k).to_numpy()].mean())}
                                       for k in codebook.LABELS if (d.c1_category == k).sum() > 0},
        "not_about_city_by_outlet": {o: {"n": int(len(g)), "share_not_about_city": float((g.about_city == "no").mean())} for o, g in d.groupby("outlet")},
        "spread": {"by_outlet": d.outlet.value_counts().to_dict(), "by_period": d.period.value_counts().to_dict(), "by_language": d.lang.value_counts().to_dict(),
                   "by_page_source": d.source.value_counts().to_dict()},
        "fetch": {"tried": fetch.get("tried"), "fetched": fetch.get("fetched"), "by_source": fetch.get("by_source"),
                  "short_categories": fetch.get("short_categories"), "fetch_rate_by_outlet_period": fetch.get("fetch_rate_by_outlet_period")},
    }
    block["failed_first_test"] = [k for k in ANALYZED if not block["categories"][k]["pass"]]
    return block

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default="coder2"); ap.add_argument("--status", default="final"); ap.add_argument("--tag", default="v1")
    a = ap.parse_args()
    S = {"threshold": THRESHOLD, "status": a.status, "scored_against": a.role,
         "what_this_measures": "Agreement between two independent AI coders. It does not show that either coder matches a human reader.",
         "first_coder": "An AI language model reading headline words from the web address plus GDELT theme tags.",
         "second_coder": "A second AI language model from a different model family, blind to the first coder's labels, reading the real headline and opening lines.",
         "cities": {}}
    rev = jload(os.path.join(V, "revision_result.json"), {}) if a.status == "final" else {}
    dropped = {}
    for city in outlets.CITIES:
        b = city_block(city, a.role, a.tag)
        if b is None:
            continue
        b["revised"] = {}
        kept, drop = [], []
        for k in ANALYZED:
            if b["categories"][k]["pass"]:
                kept.append(k); continue
            r = (rev.get(city) or {}).get(k)
            if r:
                b["revised"][k] = {"kappa_first": b["categories"][k]["kappa"], "kappa_after_revision": r["kappa"], "n_fresh": r["n"], "kept": bool(r["kappa"] >= THRESHOLD)}
                (kept if r["kappa"] >= THRESHOLD else drop).append(k)
            else:
                drop.append(k)
        b["kept"] = kept; b["dropped"] = drop; dropped[city] = drop
        S["cities"][city] = b
    hc = jload(os.path.join(V, "headline_check_result.json"))
    if hc:
        S["headline_check"] = {**{c: {g: {"n": v[g].get("n"), "kappa": v[g].get("kappa"), "ci_low": v[g].get("ci_low"), "ci_high": v[g].get("ci_high")} for g in v} for c, v in hc["cities"].items()},
                               "rule": {"applied": hc["rule"]["applied"], "text": hc["rule"]["text"]}}
    cons = {}
    cmp_ = jload(os.path.join(ROOT, "data/interim/labels/compare300_result.json"))
    if cmp_:
        cons["first_coder_vs_larger_model"] = {"n": cmp_["n"], "kappa": cmp_["kappa_category"], "agreement": cmp_["agreement_category"], "tone_kappa": cmp_["kappa_tone"]}
    extra = jload(os.path.join(V, "consistency_result.json"), {})
    cons.update(extra)
    S["consistency"] = cons
    json.dump(S, open(os.path.join(PUB, "validation_summary.json"), "w"), indent=1)
    # index configuration used by build_index.py and analysis.py
    cfg_path = os.path.join(ROOT, "data/interim/index_config.json")
    cfg = jload(cfg_path, {})
    cfg["dropped_categories"] = dropped
    cfg["validation_status"] = a.status
    if hc: cfg["excluded"] = hc["rule"]["excluded"]
    json.dump(cfg, open(cfg_path, "w"), indent=1)
    write_report(S)
    for c, b in S["cities"].items():
        print(c, "n", b["n_items"], "overall kappa", round(b["overall_kappa"], 3), "| kept", len(b["kept"]), "dropped", b["dropped"], "| not about city", round(b["not_about_city_share"], 3))
        print("   ", {k: round(v["kappa"], 2) for k, v in b["categories"].items()})

def fmt(x, nd=2):
    return "n/a" if x is None or (isinstance(x, float) and x != x) else f"{x:.{nd}f}"

def write_report(S):
    L = []
    L.append("# Validation report\n")
    L.append(f"Status: **{S['status']}**. " + ("These numbers come from the third AI pass and will be replaced when the blind second coder has run." if S["status"] != "final" else "These numbers come from the blind second coder.") + "\n")
    L.append("## What this report measures\n")
    L.append("Two AI language models labeled the same news articles without seeing each other's labels. The first coder read headline words from each article's web address plus GDELT's theme tags. The second coder, from a different model family, read the article's real headline and opening lines from the live page or the Internet Archive. Cohen's kappa measures how far they agree beyond chance.\n")
    L.append("This is agreement between two independent AI coders. It does not show that either coder matches a human reader. Nobody hand-coded any article in this run.\n")
    L.append(f"A category is analyzed in a city only if its kappa is at least {S['threshold']}. A category that falls short gets one revision of its wording and a fresh sample. If it still falls short it is dropped for that city.\n")
    names = outlets.CATEGORY_NAMES; cn = outlets.CITY_NAMES
    for city, b in S["cities"].items():
        L.append(f"## {cn[city]}\n")
        L.append(f"- Items in the validation set: {b['n_items']}")
        f = b.get("fetch") or {}
        if f.get("tried"):
            L.append(f"- Pages tried: {f['tried']}. Fetched: {f['fetched']} ({(f.get('by_source') or {}).get('live', 0)} from the live site, {(f.get('by_source') or {}).get('archive', 0)} from the Internet Archive). Items that could not be fetched were replaced by the next item from the same category and city in a fixed random order.")
            if f.get("short_categories"): L.append(f"- Categories that ended below their target count because too few pages could be fetched: {f['short_categories']}")
        L.append(f"- Overall kappa, weighted back to the full sample: {fmt(b['overall_kappa'])} (95% interval {fmt(b['overall_ci_low'])} to {fmt(b['overall_ci_high'])}). Unweighted: {fmt(b['overall_kappa_unweighted'])}.")
        L.append(f"- Weighted agreement: {b['overall_agreement'] * 100:.0f}%.")
        L.append(f"- Tone kappa (negative, neutral, positive): {fmt(b['tone_kappa'])}.")
        L.append(f"- Share of articles the second coder judged not really about the city: {b['not_about_city_share'] * 100:.0f}% weighted ({b['not_about_city_share_unweighted'] * 100:.0f}% of the validation items).\n")
        L.append("| Category | Kappa | 95% interval | First coder n | Second coder n | Result |")
        L.append("| :-- | --: | :-- | --: | --: | :-- |")
        for k in codebook.LABELS:
            v = b["categories"][k]
            res = "reported only" if k == "not_civic" else ("kept" if k in b["kept"] else "dropped")
            if k in b.get("revised", {}):
                r = b["revised"][k]; res += f" (after revision: {fmt(r['kappa_after_revision'])} on {r['n_fresh']} fresh items)"
            L.append(f"| {names[k]} | {fmt(v['kappa'])} | {fmt(v['ci_low'])} to {fmt(v['ci_high'])} | {v['n_first']} | {v['n_second']} | {res} |")
        L.append("")
        L.append(f"Kept: {', '.join(names[k] for k in b['kept']) or 'none'}.")
        L.append(f"Dropped: {', '.join(names[k] for k in b['dropped']) or 'none'}.\n")
        L.append("City filter error by outlet (share of validation items the second coder judged not about the city):\n")
        L.append("| Outlet | Items | Not about the city |")
        L.append("| :-- | --: | --: |")
        for o, v in sorted(b["not_about_city_by_outlet"].items(), key=lambda kv: -kv[1]["n"]):
            L.append(f"| {outlets.BY_KEY[o]['name']} | {v['n']} | {v['share_not_about_city'] * 100:.0f}% |")
        L.append("")
        L.append("City filter error by the first coder's category:\n")
        L.append("| Category | Items | Not about the city |")
        L.append("| :-- | --: | --: |")
        for k, v in b["not_about_city_by_category"].items():
            L.append(f"| {names[k]} | {v['n']} | {v['share_not_about_city'] * 100:.0f}% |")
        L.append("")
        L.append("Confusion table (rows: first coder, columns: second coder, counts in the validation set):\n")
        short = {k: names[k][:6] for k in codebook.LABELS}
        L.append("| | " + " | ".join(short[k] for k in codebook.LABELS) + " |")
        L.append("| :-- |" + " --: |" * len(codebook.LABELS))
        for r in codebook.LABELS:
            L.append(f"| {names[r]} | " + " | ".join(str(b["confusion_counts"][r][c]) for c in codebook.LABELS) + " |")
        L.append("")
        sp = b["spread"]
        L.append(f"Spread of the validation set. By outlet: {sp['by_outlet']}. By period: {sp['by_period']}. By language: {sp['by_language']}. By page source: {sp['by_page_source']}.\n")
    hc = S.get("headline_check")
    if hc:
        L.append("## Headline check (2020 onward)\n")
        L.append("GDELT stores real page titles only from 2020. For a sample of 2020 to 2026 articles, the first coder labeled each article twice: once from the real stored headline alone, and once the way every year is labeled (headline words in the web address plus theme tags). The table shows how well the two agree.\n")
        L.append("| City | Items with headline words in the address | Kappa | Items with theme tags alone | Kappa |")
        L.append("| :-- | --: | --: | --: | --: |")
        for c in outlets.CITIES:
            if c in hc:
                a_, t_ = hc[c].get("with_headline_words", {}), hc[c].get("theme_tags_only", {})
                L.append(f"| {cn[c]} | {a_.get('n', 0)} | {fmt(a_.get('kappa'))} | {t_.get('n', 0)} | {fmt(t_.get('kappa'))} |")
        L.append("")
        L.append(hc["rule"]["text"] + "\n")
        L.append("London's papers had number-only addresses for part of 2015 and 2016 (87% of sampled items in 2015 and about 40% in 2016). The rule in the methodology is written for outlets, and these papers have headline words in every later year, so they stay in. Their 2015 and 2016 labels rest mostly on theme tags and should be read with the Hong Kong result above in mind.\n")
    c = S.get("consistency") or {}
    L.append("## Consistency checks\n")
    if "first_coder_vs_larger_model" in c:
        v = c["first_coder_vs_larger_model"]
        L.append(f"- First coder against a larger model from the same family, same inputs, {v['n']} items: kappa {fmt(v['kappa'])} on category ({v['agreement'] * 100:.0f}% agreement), {fmt(v['tone_kappa'])} on tone.")
    if "third_pass" in c:
        v = c["third_pass"]
        L.append(f"- Third pass (a different AI model reading the same real headlines and opening lines, in place of the classmate): {v['n']} items, kappa {fmt(v.get('kappa_vs_second'))} against the second coder and {fmt(v.get('kappa_vs_first'))} against the first coder.")
    if "relabel" in c:
        v = c["relabel"]
        L.append(f"- Re-label (the second coder labels {v['n']} of the same items again in a fresh request, in place of Cayden's two-week re-label): kappa {fmt(v['kappa'])}.")
    if "gemini_repeat" in c:
        L.append(f"- Earlier repeat tests with two Gemini models on 2,000 Hong Kong items (same inputs as the first coder): kappa 0.68 for one model against itself at a different request size, 0.66 to 0.72 between the two models.")
    L.append("")
    L.append("## Optional human check\n")
    L.append("`deliverables/optional_hand_check_50.csv` holds 50 validation items with a blank label column. If Cayden fills it in, `src/score_hand_check.py` computes his kappa against both AI coders. It has not been filled in.\n")
    open(os.path.join(PUB, "validation_report.md"), "w").write("\n".join(L))

if __name__ == "__main__":
    main()
