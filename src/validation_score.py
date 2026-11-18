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
    # items from outlet-years that the headline-check rule leaves out of the main series are not part of the measure being analyzed
    d["retained"] = True
    for e in excluded_rules():
        if e["city"] == city:
            d.loc[d.outlet.isin(e["outlets"]) & (d.month >= e["from"]) & (d.month <= e["to"]), "retained"] = False
    return d

def excluded_rules():
    hc = jload(os.path.join(V, "headline_check_result.json"))
    return (hc or {}).get("rule", {}).get("excluded", [])

def pool_counts(city, retained_only=True):
    d = build_index.load(build_index.first_codebook_labels())     # the labels the validation samples were drawn from
    level = build_index.levels_done(d)
    order = list(build_index.LEVEL_CAPS)
    use = order[: order.index(level) + 1] if level else order[:1]
    m = d[d.in_main & d.level.isin(use) & (d.city == city) & d.category.notna()]
    if retained_only:
        m = build_index.apply_exclusions(m, excluded_rules())
    # each outlet counts equally in each month of the attention index, so the outlet margin is outlet-months, not article volume
    _OUTLETS[(city, retained_only)] = m.groupby("outlet").month.nunique().to_dict()
    return m.category.value_counts().to_dict(), level

_OUTLETS = {}

def city_block(city, role, tag="v1"):
    d_all = load_city(city, role, tag)
    if d_all is None or len(d_all) < 50:
        return None
    # kappa on every validation item, reported for openness
    pc_all, _ = pool_counts(city, retained_only=False)
    sc_all = VL.score(d_all, pc_all, reps=300, outlet_counts=_OUTLETS[(city, False)])
    # the 0.61 rule uses the items that remain in the main series (decided before the second coder ran)
    d = d_all[d_all.retained].copy()
    pc, level = pool_counts(city, retained_only=True)
    oc = _OUTLETS[(city, True)]
    sc = VL.score(d, pc, outlet_counts=oc)
    w = sc["weights"]
    M = sum(oc.values())
    outlet_table = {o: {"n_validation": int((d.outlet == o).sum()), "share_of_validation": float((d.outlet == o).mean()),
                        "share_of_index_weight": float(oc.get(o, 0) / M), "weighted_share": float(w[(d.outlet == o).to_numpy()].sum() / w.sum())} for o in sorted(oc)}
    not_about = (d.about_city == "no").to_numpy()
    tone_k = VL.wkappa(d.c1_tone.to_numpy(), d.c2_tone.to_numpy(), w, codebook.TONES)
    fetch = jload(os.path.join(V, f"{city}_fetch_report_{tag}.json"), {})
    block = {
        "n_items": int(len(d)), "n_items_all": int(len(d_all)), "n_items_left_out_by_headline_rule": int((~d_all.retained).sum()),
        "all_items": {"overall_kappa": sc_all["overall"]["kappa_weighted"], "categories": {k: v["kappa_weighted"] for k, v in sc_all["by_category"].items()}},
        "headline_only_items": int((d.source == "gdelt_title").sum()),
        "effective_n": sc["effective_n"], "outlet_weights": outlet_table,
        "outlets_with_no_validation_items": [o for o, v in outlet_table.items() if v["n_validation"] == 0],
        "labeling_round_for_weights": level,
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
    # The same test under simpler rules, so a reader can see how much the three rules set during the run matter.
    def variant(label, dd, pcx, oc_):
        scx = VL.score(dd, pcx, reps=50, outlet_counts=oc_)
        return {"label": label, "n": int(len(dd)), "overall_kappa": scx["overall"]["kappa_weighted"],
                "failed": [k for k in ANALYZED if scx["by_category"][k]["kappa_weighted"] < THRESHOLD]}
    block["rule_variants"] = {
        "plan_as_written": variant("Every validation item, weights by category only (the plan as written)", d_all, pc_all, None),
        "retained_category_only": variant("Items that remain in the main series, weights by category only", d, pc, None),
        "rule_used": {"label": "Items that remain in the main series, weights by category and outlet (the rule used)", "n": block["n_items"],
                      "overall_kappa": block["overall_kappa"], "failed": block["failed_first_test"]},
    }
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
        S.setdefault("rule_variants", {})[city] = b["rule_variants"]
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
        L.append(f"- Items in the validation set: {b['n_items_all']}. Items used for the 0.61 rule: {b['n_items']}." + (f" {b['n_items_left_out_by_headline_rule']} items come from outlet-years that the headline-check rule leaves out of the main series, so they are not part of the measure being analyzed. Kappa on all {b['n_items_all']} items is {fmt(b['all_items']['overall_kappa'])}." if b['n_items_left_out_by_headline_rule'] else ""))
        if b.get("headline_only_items"):
            L.append(f"- For {b['headline_only_items']} of these items the second coder read the real headline alone, taken from GDELT's stored page title, because no page could be read. One site (scmp.com) answered automated requests with a challenge page, and the run stopped using it and did not fetch its pages from anywhere else. Other pages were gone from both the live site and the Internet Archive.")
        f = b.get("fetch") or {}
        if f.get("tried"):
            L.append(f"- Pages tried: {f['tried']}. Fetched: {f['fetched']} ({(f.get('by_source') or {}).get('live', 0)} from the live site, {(f.get('by_source') or {}).get('archive', 0)} from the Internet Archive). Items that could not be fetched were replaced by the next item from the same category and city in a fixed random order.")
            if f.get("short_categories"): L.append("- Categories that ended below their target count because too few pages could be read: " + ", ".join(f"{names.get(k, k)} (short by {v})" for k, v in f["short_categories"].items()) + ".")
        L.append(f"- Overall kappa, weighted back to the full sample: {fmt(b['overall_kappa'])} (95% interval {fmt(b['overall_ci_low'])} to {fmt(b['overall_ci_high'])}). Unweighted: {fmt(b['overall_kappa_unweighted'])}.")
        L.append(f"- Weighted agreement: {b['overall_agreement'] * 100:.0f}%.")
        L.append(f"- Weights match the validation set to the measure on two margins: the first coder's category (in proportion to the labeled sample) and the outlet (in proportion to its weight in the index). Effective sample size after weighting: {b['effective_n']:.0f}.")
        ow = b.get("outlet_weights") or {}
        big = sorted(ow.items(), key=lambda kv: -kv[1]["share_of_index_weight"])[:4]
        L.append("- Outlet weights follow the attention index, where each outlet counts equally in each month it has articles. " + "; ".join(f"{outlets.BY_KEY[o]['name']} carries {v['share_of_index_weight'] * 100:.0f}% of the index weight and is {v['share_of_validation'] * 100:.0f}% of the validation items" for o, v in big) + ".")
        if b.get("outlets_with_no_validation_items"):
            L.append("- Outlets with no validation items at all: " + ", ".join(outlets.BY_KEY[o]['name'] for o in b['outlets_with_no_validation_items']) + ".")
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
        def lst(dct, namer=str):
            return ", ".join(f"{namer(k)} {v}" for k, v in dct.items())
        src_names = {"live": "live page", "archive": "Internet Archive", "gdelt_title": "stored headline only"}
        lang_names = {"eng": "English", "zho": "Chinese"}
        L.append("Spread of the scored items. By outlet: " + lst(sp["by_outlet"], lambda k: outlets.BY_KEY[k]["name"]) + ". By period: " + lst(sp["by_period"]) +
                 ". By language of the article: " + lst(sp["by_language"], lambda k: lang_names.get(k, k)) + ". By source of the text: " + lst(sp["by_page_source"], lambda k: src_names.get(k, k)) + ".\n")
        rv = b.get("rule_variants") or {}
        if rv:
            L.append("The same test under simpler rules. Three rules were set during the run, after provisional scores from the third pass had been seen and before the second coder ran: which items count, the stored-headline fallback, and the outlet weights. This table shows what the first two alternatives would give.\n")
            L.append("| Rule | Items | Overall kappa | Categories below 0.61 |")
            L.append("| :-- | --: | --: | :-- |")
            for v in rv.values():
                L.append(f"| {v['label']} | {v['n']} | {fmt(v['overall_kappa'])} | {', '.join(names[k] for k in v['failed']) or 'none'} |")
            L.append("")
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
        try:
            dd = build_index.load()
            lon = dd[(dd.city == "london") & dd.in_main]
            sh = lon.assign(y=lon.month.str[:4], no=(lon.headline.fillna("") == "")).groupby("y").no.mean()
            L.append(f"Some London papers had number-only addresses in 2015 and 2016: {sh.get('2015', float('nan')) * 100:.0f}% of London's sampled items in 2015 and {sh.get('2016', float('nan')) * 100:.0f}% in 2016 carry no headline words, against {sh.get('2017', float('nan')) * 100:.0f}% in 2017. The rule in the methodology is written for outlets, and these papers have headline words in every later year, so they stay in. Their theme-tag-only labels in 2015 and 2016 should be read with the Hong Kong result above in mind.\n")
        except Exception:
            pass
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
        L.append(f"- Earlier repeat tests with two other small models on 2,000 Hong Kong items (same inputs as the first coder; details in the labeling card): kappa 0.68 for one model against itself at a different request size, 0.66 to 0.72 between the two models.")
    L.append("")
    L.append("## Optional human check\n")
    L.append("`deliverables/optional_hand_check_50.csv` holds 50 validation items with a blank label column. If Cayden fills it in, `src/score_hand_check.py` computes his kappa against both AI coders. It has not been filled in.\n")
    open(os.path.join(PUB, "validation_report.md"), "w").write("\n".join(L))

if __name__ == "__main__":
    main()
