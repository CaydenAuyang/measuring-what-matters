"""Build the research paper from its template.

    src/templates/paper.template.md  ->  paper/paper.md  ->  paper/paper.docx

Every number in the paper is a {{token}} that fill_template.fill replaces. Most tokens walk
data/public/results.json and the other files fill_template.py already knows (v. cmp. idx. hc. run.).
This script adds two more token sources, both computed from saved files and never typed:

    off.<series_id>.<field>   one entry of data/interim/official/<city>_meta.json
                              (first_period, last_period, n_obs, frequency, status, indicator_name)
    paper.<name>              tables and phrases built here:
        indicator_table        the 24 main indicators with frequency and coverage (from the meta files)
        main_built, main_missing, backup_built
        sparse_hk, sparse_nyc, sparse_london   search sets flagged sparse (data/interim/trends/trends_shares.csv)
        check_sample           how much of the "all listed outlets" sample was labeled (index_info.json)
        bootstrap_reps_checks  resamples used for the checks (same formula as analysis.py)
        cost_per_1000_items    labeling cost per 1,000 items (run_facts.json)
        checks_news, checks_search   the checks with p-values and sample sizes (results.json)
        runs_read_coverage, runs_by_rule_only   how many disconnection causes rest on an AI-read sample
                               of stories and how many on the rule alone (results.json, h3.runs)

Because of these two extra sources, build the paper with this script, not with fill_template.py alone.

Usage: python src/build_paper.py
Prints the word count, the tokens that were not available, and a short style check.
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fill_template, md_to_docx, outlets

ROOT = fill_template.ROOT
TEMPLATE = os.path.join(ROOT, "src/templates/paper.template.md")
OUT_MD = os.path.join(ROOT, "paper/paper.md")
OUT_DOCX = os.path.join(ROOT, "paper/paper.docx")
FREQ = {"M": "Monthly", "Q": "Quarterly", "A": "Annual"}
STATUS = {"ok": "built", "partial": "built, with gaps or a later start than planned", "missing": "missing"}
CN, KN = outlets.CITY_NAMES, outlets.CATEGORY_NAMES


def jload(rel, default=None):
    p = os.path.join(ROOT, rel)
    return json.load(open(p)) if os.path.exists(p) else default

def join_names(names, empty="none"):
    names = list(names)
    if not names: return empty
    if len(names) == 1: return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]

def f2(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"

def ci(d):
    return f"{f2(d['est'])} ({f2(d['ci_low'])} to {f2(d['ci_high'])})"


# ------------------------------------------------------------------ extra token sources
def official_meta():
    off = {}
    for c in outlets.CITIES:
        for m in jload(f"data/interim/official/{c}_meta.json", []) or []:
            off[m["series_id"]] = m
    return off

def indicator_table(off):
    rows = ["| City | Category | Main indicator as built | Frequency | Coverage obtained | Values | Status |",
            "| :-- | :-- | :-- | :-- | :-- | --: | :-- |"]
    built, missing = 0, []
    for c in outlets.CITIES:
        for k in outlets.COMPARED:
            m = off.get(f"{c}_{k}_main")
            if not m or not m.get("n_obs"):
                missing.append(f"{CN[c]} {KN[k]}")
                name = (m or {}).get("indicator_name") or ""
                rows.append(f"| {CN[c]} | {KN[k]} | {name} | | none | 0 | missing |")
                continue
            built += 1
            n = f"{m['n_obs']:,}"
            if m.get("components"): n += f" ({len(m['components'])} components)"
            rows.append(f"| {CN[c]} | {KN[k]} | {m['indicator_name']} | {FREQ.get(m['frequency'], m['frequency'])} | "
                        f"{m['first_period']} to {m['last_period']} | {n} | {STATUS.get(m.get('status'), m.get('status') or '')} |")
    return "\n".join(rows), built, missing

def backups_built(off):
    return sum(1 for c in outlets.CITIES for k in outlets.COMPARED if (off.get(f"{c}_{k}_backup") or {}).get("n_obs"))

def sparse_sets():
    """Search sets flagged sparse in any month of the shares file (the same reading analysis.py uses)."""
    out = {c: None for c in outlets.CITIES}
    p = os.path.join(ROOT, "data/interim/trends/trends_shares.csv")
    if not os.path.exists(p):
        return out
    flagged = {c: set() for c in outlets.CITIES}
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            if str(r.get("sparse_flag", "")).strip().lower() in ("1", "true", "1.0") and r["city"] in flagged:
                flagged[r["city"]].add(r["category"])
    return {c: join_names(KN[k] for k in outlets.CATEGORIES if k in flagged[c]) for c in outlets.CITIES}

def check_sample(idx):
    chk = (idx or {}).get("check_cap")
    if chk == "full":
        caps = outlets.CHECK_CAP
        return f"the full check sample ({caps['hk']} articles per outlet per month in Hong Kong, {caps['nyc']} in New York and {caps['london']} in London)"
    if chk:
        return f"up to {int(chk)} articles per outlet per month"
    return None

def checks_table(R, source):
    m = (R.get("main") or {}).get(source)
    if not m:
        return None
    rows = ["| Check | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |",
            "| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |"]
    def row(label, mm):
        if not mm:
            return f"| {label} | not run | | | | | | | |"
        h1, h2 = mm["h1"], mm["h2"]
        return (f"| {label} | {ci(h1)} | {f2(h1['p_boot'], 3)} | {h1['n_pairs']} | {h1['n_obs']:,} | {h1['n_eff_years']:.0f} | "
                f"{ci(h2['worse'])} | {ci(h2['better'])} | {ci(h2['diff'])} |")
    rows.append(row("Main model", m))
    for name, c in (R.get("checks") or {}).items():
        if source in c:                       # checks that were set up for this source ("not run" if they gave no result)
            rows.append(row(c.get("label", name), c.get(source)))
    return "\n".join(rows)

def extra_sources(src):
    R, idx, run = src[""], src["idx"], src["run"]
    off = official_meta()
    table, built, missing = indicator_table(off)
    sp = sparse_sets()
    reps = R.get("bootstrap_reps")
    cpi = run.get("cost_per_item_usd")
    paper = {
        "indicator_table": table if off else None,
        "main_built": built if off else None,
        "main_missing": join_names(missing) if off else None,
        "backup_built": backups_built(off) if off else None,
        "sparse_hk": sp["hk"], "sparse_nyc": sp["nyc"], "sparse_london": sp["london"],
        "check_sample": check_sample(idx),
        "bootstrap_reps_checks": max(200, reps // 2) if isinstance(reps, int) else None,
        "cost_per_1000_items": cpi * 1000 if isinstance(cpi, (int, float)) else None,
        "checks_news": checks_table(R, "news"),
        "checks_search": checks_table(R, "search"),
    }
    runs = (R.get("h3") or {}).get("runs")
    if runs is not None:                      # how each disconnection's cause was proposed (results.json, h3.runs[].proposed_by)
        read = sum(1 for r in runs if "sample" in str(r.get("proposed_by", "")))
        paper["runs_read_coverage"] = read
        paper["runs_by_rule_only"] = len(runs) - read
    return {"off": off, "paper": paper}


# ------------------------------------------------------------------ counting and checking
COMMENT = re.compile(r"<!--.*?-->", re.S)
BANNED = ["leverage", "robust", "comprehensive", "crucial", "nuanced", "straightforward", "genuinely", "arguably",
          "deep dive", "unpack", "landscape", "synergy", "significant", "todo", "lorem"]
MODEL_NAMES = ["claude", "haiku", "sonnet", "opus", "gemini", "anthropic", "openai", "gpt-"]

def n_words(text, tables=False):
    n = 0
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("|") and not tables:
            continue
        s = re.sub(r"[`*#>|]", " ", s)
        n += sum(1 for w in s.split() if re.search(r"[A-Za-z0-9]", w))
    return n

def split_parts(md):
    text = COMMENT.sub("", md)
    body, _, appendix = text.partition("\n## Appendix")
    main, _, refs = body.partition("\n## References")
    return main, refs, appendix

def style_check(md):
    main, refs, appendix = split_parts(md)
    visible = main + refs + appendix
    notes = []
    if "—" in visible: notes.append(f"em dash: {visible.count(chr(0x2014))}")
    prose = "\n".join(l for l in (main + appendix).split("\n") if not l.strip().startswith("|"))
    if "!" in prose: notes.append(f"exclamation mark: {prose.count('!')}")
    low = visible.lower()
    for w in BANNED:
        hits = len(re.findall(r"\b" + re.escape(w), low))
        if hits: notes.append(f"'{w}': {hits}")
    low_no_refs = (main + appendix).lower()               # a reference title may name a product; the body may not
    for w in MODEL_NAMES:
        hits = len(re.findall(r"\b" + re.escape(w), low_no_refs))
        if hits: notes.append(f"model or product name '{w}': {hits}")
    if "{{" in visible or "}}" in visible: notes.append("unfilled token braces left in the text")
    return notes


def main():
    src = fill_template.sources()
    src.update(extra_sources(src))
    text, missing = fill_template.fill(open(TEMPLATE, encoding="utf-8").read(), src)
    # the template's own header comment is replaced by a note that this file is generated
    note = (f"<!--\nGENERATED FILE. Built by src/build_paper.py from src/templates/paper.template.md and the results file "
            f"generated at {src[''].get('generated_utc')} (UTC).\nEdit the template and rebuild. Changes made here are lost at the next build.\n-->")
    text = re.sub(r"\A\s*<!--.*?-->", lambda m: note, text, count=1, flags=re.S)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w", encoding="utf-8").write(text)
    md_to_docx.convert(text, OUT_DOCX)

    main_part, refs, appendix = split_parts(text)
    prose = n_words(main_part)
    print(f"wrote {os.path.relpath(OUT_MD, ROOT)} and {os.path.relpath(OUT_DOCX, ROOT)}")
    print(f"results file generated: {src[''].get('generated_utc')} | validation status: {(src['v'] or {}).get('status')}")
    print(f"words, prose from the Abstract through the AI-use disclosure (no tables): {prose:,}")
    print(f"words, tables in those sections: {n_words(main_part, tables=True) - prose:,}")
    print(f"words, references: {n_words(refs):,}")
    print(f"words, appendix (tables included): {n_words(appendix, tables=True):,}")
    print(f"placeholders '[not available]' in the text: {text.count('[not available]')}")
    print(f"'[CAYDEN TO CONFIRM' lines: {text.count('[CAYDEN TO CONFIRM')}")
    marks = re.findall(r"<!--\s*FINAL PASS:\s*([^.]+)\.", text)
    print(f"places marked for the final pass ({len(marks)}): " + "; ".join(marks))
    uniq = sorted(set(missing))
    if uniq:
        print(f"{len(uniq)} token(s) not available:")
        for t in uniq: print("   ", t)
    else:
        print("every token was available")
    notes = style_check(text)
    print("style check: " + ("; ".join(notes) if notes else "clean"))

if __name__ == "__main__":
    main()
