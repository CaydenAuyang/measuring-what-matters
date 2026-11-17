"""Fill every template in src/templates/ (except the paper's) and write it to deliverables/.

src/templates/X.template.md  ->  deliverables/X.md

Tokens are filled by fill_template.fill, so no number is typed by hand. On top of the usual
sources (results.json and the prefixes v. cmp. hc. idx. run.) this script adds one more prefix,
"calc.", for values that are simple arithmetic or a plain reading of numbers already in those
files. Each calc value is listed in derived() with the fields it comes from. A calc value whose
inputs are missing is left out, so its token prints "[not available]" like any other.

Comments that start with "<!-- TEMPLATE:" are notes for whoever edits the template and are not
copied to the output. Comments that start with "<!-- FINAL PASS:" are copied, so the last pass
can find them.

Usage: .venv/bin/python src/build_docs.py            (every template)
       .venv/bin/python src/build_docs.py defense_brief civic_signal_framework
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fill_template as F

ROOT = F.ROOT
TPL_DIR = os.path.join(ROOT, "src/templates")
OUT_DIR = os.path.join(ROOT, "deliverables")
SKIP = {"paper"}                      # the paper has its own build
SUFFIX = ".template.md"
TEMPLATE_NOTE = re.compile(r"<!-- TEMPLATE:.*?-->\n?", re.S)

SOURCES = ["news", "search"]
CAUSE_KEYS = {
    "the official measure changed how it counts": "counting_change",
    "a real event drew coverage the indicator does not capture": "real_event",
    "attention followed a news cycle rather than conditions": "news_cycle",
    "the two measure different parts of the problem": "different_parts",
    "unclear": "unclear",
}

try:
    import outlets
    COMPARED, CATEGORY_NAMES = outlets.COMPARED, outlets.CATEGORY_NAMES
except Exception:                     # the list below is the codebook's eight compared categories
    COMPARED = ["safety", "economy", "housing", "transport", "environment", "health", "education", "cost_of_living"]
    CATEGORY_NAMES = {k: k.replace("_", " ").title().replace(" Of ", " of ") for k in COMPARED}


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def join_words(items, empty="none"):
    items = list(items)
    if not items: return empty
    if len(items) == 1: return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def interval_reading(d):
    """Where a 95% interval sits against zero, in words. None if there is no interval."""
    if not isinstance(d, dict) or not is_num(d.get("ci_low")) or not is_num(d.get("ci_high")):
        return None
    if d["ci_low"] > 0: return "is above zero"
    if d["ci_high"] < 0: return "is below zero"
    return "includes zero"


def derived(src):
    """The calc.* values. Every one is arithmetic on, or a reading of, fields in the results files."""
    R, run = src[""], src["run"]
    C = {}

    # ---- costs: run.cost_per_item_usd is too small to print as dollars and cents per item
    per_item = run.get("cost_per_item_usd")
    if is_num(per_item):
        C["cost_per_1000_items_usd"] = per_item * 1000
        C["cost_per_100k_items_usd"] = per_item * 100000
        # minimum viable version: one city, up to 1,000 articles a month (the pre-registered cap)
        # for as many months of news as this study has (counts.news_months)
        months = (R.get("counts") or {}).get("news_months")
        if is_num(months):
            C["mvp_items"] = 1000 * months
            C["mvp_label_cost_usd"] = 1000 * months * per_item
            if is_num(run.get("bigquery_cost_usd")):
                C["mvp_total_cost_usd"] = C["mvp_label_cost_usd"] + run["bigquery_cost_usd"]
    if is_num(run.get("pages_fetched_total")) and is_num(run.get("pages_tried_total")) and run["pages_tried_total"] > 0:
        C["pages_fetch_rate"] = run["pages_fetched_total"] / run["pages_tried_total"]

    # ---- checks that the results hold: how each check's H1 interval sits against zero
    checks = R.get("checks") or {}
    C["checks"] = {}
    for s in SOURCES:
        run_labels, above, not_above, not_run = [], [], [], []
        for name, c in checks.items():
            if s + "_pairs_excluded" not in c and s not in c:
                continue                              # this check was never meant for this source
            label = c.get("label", name)
            reading = interval_reading(((c.get(s) or {}).get("h1")))
            if reading is None:
                not_run.append(label); continue
            C["checks"].setdefault(name, {}).setdefault(s, {})["h1_interval"] = reading
            run_labels.append(label)
            (above if reading == "is above zero" else not_above).append(label)
        C[s] = {}
        if checks:                                    # no checks block yet: leave the tokens unavailable
            C[s] = {"checks_run": len(run_labels), "checks_h1_above_zero": len(above),
                    "checks_h1_not_above_zero_labels": "; ".join(not_above) or "none",
                    "checks_not_run_labels": "; ".join(not_run) or "none"}

    # ---- H1 by category: which categories' intervals sit above zero, highest slope first
    for s in SOURCES:
        by_cat = (R.get("h1_by_category") or {}).get(s) or {}
        groups = {"is above zero": [], "includes zero": [], "is below zero": []}
        for k in sorted(by_cat, key=lambda k: -(by_cat[k].get("est") or 0)):
            reading = interval_reading(by_cat[k])
            if reading: groups[reading].append(CATEGORY_NAMES.get(k, k))
        if by_cat:
            C[s]["h1_categories_above_zero"] = join_words(groups["is above zero"])
            C[s]["h1_categories_including_zero"] = join_words(groups["includes zero"])
            C[s]["h1_categories_below_zero"] = join_words(groups["is below zero"])
            C[s]["h1_categories_not_tested"] = join_words([CATEGORY_NAMES.get(k, k) for k in COMPARED if k not in by_cat])

    # ---- validation: how many category checks reached the threshold, counted exactly the way
    # src/poster.py counts them for card C1: the twelve categories in each city ("not a civic problem"
    # is reported but is not a category the 0.61 rule can drop), and a category counts as passed when
    # it is in the city's "kept" list (so a category kept after its one revision counts as kept).
    V = src["v"]
    n_total = n_passed = 0
    for city in (V.get("cities") or {}).values():
        if not isinstance(city, dict): continue
        kept, dropped = city.get("kept"), city.get("dropped")
        use_lists = isinstance(kept, list) and isinstance(dropped, list)
        for lab, e in (city.get("categories") or {}).items():
            if not isinstance(e, dict) or lab == "not_civic": continue
            passed = (lab in kept) if use_lists else e.get("pass")
            if passed is None and is_num(e.get("kappa")) and is_num(V.get("threshold")):
                passed = e["kappa"] >= V["threshold"]
            if passed is None: continue
            n_total += 1; n_passed += 1 if passed else 0
    if n_total:
        C["validation"] = {"checks_total": n_total, "checks_passed": n_passed}

    # ---- disconnections of six months or more, counted by proposed cause (h3.runs), and by direction:
    # worsening_falling counts every run where the official measure worsened while attention's share fell,
    # whatever cause was proposed for it (some of those runs carry a cause other than "news cycle")
    runs = (R.get("h3") or {}).get("runs")
    if isinstance(runs, list):
        C["runs"] = {v: 0 for v in CAUSE_KEYS.values()}
        C["runs"]["worsening_falling"] = 0
        for r in runs:
            key = CAUSE_KEYS.get(r.get("proposed_cause"))
            if key: C["runs"][key] += 1
            if r.get("official_direction") == "worsening" and r.get("attention_direction") == "falling":
                C["runs"]["worsening_falling"] += 1
    return C


def sources():
    src = F.sources()
    # analysis.py copies the made-up-series test into results.json. If results.json is older than
    # the test file, read the test file directly so the token still resolves.
    if not src[""].get("synthetic_tests"):
        p = os.path.join(ROOT, "data/public/synthetic_test_results.json")
        if os.path.exists(p):
            src[""] = dict(src[""], synthetic_tests=json.load(open(p)))
    src["calc"] = derived(src)
    return src


def build(name, src):
    tpl = os.path.join(TPL_DIR, name + SUFFIX)
    out = os.path.join(OUT_DIR, name + ".md")
    text = TEMPLATE_NOTE.sub("", open(tpl, encoding="utf-8").read())
    filled, missing = F.fill(text, src)
    header = f"<!-- Built by src/build_docs.py from src/templates/{name}{SUFFIX}. Edit the template, then rebuild. -->\n"
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(header + filled)
    return out, sorted(set(missing))


def main(argv):
    wanted = argv or sorted(os.path.basename(p)[:-len(SUFFIX)] for p in glob.glob(os.path.join(TPL_DIR, "*" + SUFFIX)))
    src = sources()
    all_missing = {}
    for name in wanted:
        if name in SKIP:
            print(f"{name}: skipped (built elsewhere)"); continue
        if not os.path.exists(os.path.join(TPL_DIR, name + SUFFIX)):
            print(f"{name}: no template at src/templates/{name}{SUFFIX}"); continue
        out, missing = build(name, src)
        rel = os.path.relpath(out, ROOT)
        if missing:
            all_missing[rel] = missing
            print(f"{rel}: {len(missing)} token(s) not available:")
            for m in missing: print(f"    {m}")
        else:
            print(f"{rel}: filled, nothing missing")
    if not wanted:
        print("no templates found in src/templates/")
    return all_missing


if __name__ == "__main__":
    main(sys.argv[1:])
