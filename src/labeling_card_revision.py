"""Write the section of data/public/labeling_card.md that records the one revision of the codebook and the
second labeling of the whole sample. Runs only when the labels were swapped (src/swap_revised_labels.py).
Everything comes from files: src/codebook_revision.json, src/prompt_first_coder_revised.txt,
data/interim/labels/full_run_revised_stats.json and relabel_compare.json. Safe to run again."""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(ROOT, "data/interim/labels")
CARD = os.path.join(ROOT, "data/public/labeling_card.md")
START, END = "<!-- revision section: start -->", "<!-- revision section: end -->"

def main():
    if not os.path.exists(os.path.join(L, "labels_main_first_codebook.jsonl")):
        print("labeling card: no second labeling, nothing to add"); return
    rev = json.load(open(os.path.join(ROOT, "src/codebook_revision.json")))
    prompt = open(os.path.join(ROOT, "src/prompt_first_coder_revised.txt")).read()
    st = json.load(open(os.path.join(L, "full_run_revised_stats.json")))
    cm = json.load(open(os.path.join(L, "relabel_compare.json")))
    first = {line.split(" | ")[0].strip(): line for line in codebook.CODEBOOK_TABLE.split("\n")}
    names = outlets.CATEGORY_NAMES; cn = outlets.CITY_NAMES
    S = [START, "## The revised prompt (`news-v2`): the labels in use\n",
         "The plan allows one revision of a category's wording when it falls below 0.61. After the blind second coder scored the first validation sample on November 18, 2026, "
         f"an AI agent read where the two coders disagreed and reworded {len(rev['categories'])} category lines (written {rev['written_utc']}). No person reviewed the wording. "
         "Both coders labeled a fresh sample with the revised codebook. Some revised categories passed, so every article was labeled a second time with the revised prompt. "
         "The news series in the results use this second set of labels. The first set is kept, and the first validation test is scored on it.\n",
         "| Setting | Value |", "| :-- | :-- |",
         "| Prompt version | `news-v2` (the `news-v1` prompt with the lines below replaced; nothing else changed) |",
         f"| SHA-256 of the system prompt | `{hashlib.sha256(prompt.encode()).hexdigest()}` |",
         "| Model and settings | The same as the first full run: `claude-haiku-5-5`, provider defaults, 50 items per request |",
         "| Files | `src/codebook_revision.json` (the revised lines), `src/prompt_first_coder_revised.txt` (the full prompt), `src/revision.py`, `src/relabel_revised.sh`, `src/swap_revised_labels.py` |",
         f"| Items labeled | {cm['labeled_revised_codebook']:,} of {cm['items_in_sample']:,} with something to read |",
         f"| Requests | {st['requests']:,} |", f"| Largest request | {st['largest_request_input_tokens']:,} input tokens |",
         f"| Cost | ${st['cost_usd']:.2f} |", f"| Time | {round(st['seconds'] / 60)} minutes |", f"| Refusals | {st['refusals']} |", "",
         "The lines that changed (category, what it covers, what goes elsewhere):\n",
         "| Category | First wording (`news-v1`) | Revised wording (`news-v2`) |", "| :-- | :-- | :-- |"]
    for k, v in rev["categories"].items():
        a = [x.strip() for x in first[k].split("|")]; b = [x.strip() for x in v.split("|")]
        S.append(f"| {names[k]} | Covers: {a[1].strip()}. Goes elsewhere: {(a[2].strip() if len(a) > 2 and a[2].strip() else 'nothing listed')}. | Covers: {b[1].strip()}. Goes elsewhere: {b[2].strip()}. |")
    S += ["", "How far the two sets of labels agree, over every labeled article:\n", "| City | Articles | Same category | Kappa between the two sets |", "| :-- | --: | --: | --: |"]
    for c in outlets.CITIES:
        if c in cm["by_city"]:
            b = cm["by_city"][c]; S.append(f"| {cn[c]} | {b['n']:,} | {b['same_category_share'] * 100:.1f}% | {b['kappa_first_vs_revised']:.2f} |")
    S += ["", "The largest moves between categories, by city (first label to revised label, articles):\n"]
    for c in outlets.CITIES:
        if c in cm["by_city"]:
            S.append(f"- {cn[c]}: " + "; ".join(f"{names[m['from']]} to {names[m['to']]} {m['n']:,}" for m in cm["by_city"][c]["largest_moves"][:6]) + ".")
    S += ["", END]
    s = open(CARD).read()
    if START in s:
        s = s[:s.index(START)] + s[s.index(END) + len(END):].lstrip("\n")
    old = "The prompt has not changed since 2026-11-17T21:00:35Z."
    s = s.replace(old, "The first prompt (`news-v1`) was fixed at 2026-11-17T21:00:35Z and did not change through the first full run. One revision followed on November 18, described in the section \"The revised prompt\" below.")
    s = s.replace("| Prompt version | `news-v1` |", "| Prompt version | `news-v1` for the first full run. The labels in use come from `news-v2` (see \"The revised prompt\" below). |")
    marker = "## How the first coder was chosen"
    assert marker in s
    s = s.replace(marker, "\n".join(S) + "\n\n" + marker, 1)
    open(CARD, "w").write(s)
    print("labeling card: revision section written")

if __name__ == "__main__":
    main()
