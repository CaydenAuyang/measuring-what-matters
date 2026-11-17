"""Fill a text template with numbers from the results files, so no number is ever retyped.

Tokens: {{path.to.value}} or {{path.to.value|fmt}} where the path walks data/public/results.json
(prefix "v." walks data/public/validation_summary.json; "cmp." the model comparison; "idx." the index info).
Formats: 2f (default for floats), 1f, 3f, 0f, pct (0.153 -> 15%), pct1, int, comma (1,234), money, raw.
A token whose value is missing is replaced by "[not available]" and reported on stderr.

Usage: python src/fill_template.py <template> <output>
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.\-|]+?)\s*(?:\|\s*([a-z0-9]+))?\s*\}\}")

def _load(p):
    return json.load(open(p)) if os.path.exists(p) else {}

def sources():
    return {"": _load(os.path.join(ROOT, "data/public/results.json")),
            "v": _load(os.path.join(ROOT, "data/public/validation_summary.json")),
            "cmp": _load(os.path.join(ROOT, "data/interim/labels/compare300_result.json")),
            "idx": _load(os.path.join(ROOT, "data/interim/index_info.json")),
            "hc": _load(os.path.join(ROOT, "data/interim/validation/headline_check_result.json")),
            "run": _load(os.path.join(ROOT, "data/interim/run_facts.json"))}

def lookup(src, path):
    parts = path.split(".")
    root = src[""]
    if parts[0] in src and parts[0] != "":
        root = src[parts[0]]; parts = parts[1:]
    cur = root
    for p in parts:
        if isinstance(cur, dict) and p in cur: cur = cur[p]
        elif isinstance(cur, list) and p.lstrip("-").isdigit() and -len(cur) <= int(p) < len(cur): cur = cur[int(p)]
        else: return None
    return cur

def fmt(v, f):
    if v is None: return None
    if isinstance(v, bool): return "yes" if v else "no"
    if isinstance(v, (int, float)):
        if f == "pct": return f"{v * 100:.0f}%"
        if f == "pct1": return f"{v * 100:.1f}%"
        if f == "int": return f"{int(round(v))}"
        if f == "comma": return f"{int(round(v)):,}"
        if f == "money": return f"${v:,.2f}"
        if f in ("0f", "1f", "2f", "3f", "4f"): return f"{v:.{f[0]}f}"
        if f == "raw": return str(v)
        return f"{v:,}" if isinstance(v, int) else f"{v:.2f}"
    return str(v)

def fill(text, src=None):
    src = src or sources(); missing = []
    def rep(m):
        val = fmt(lookup(src, m.group(1)), m.group(2) or "")
        if val is None:
            missing.append(m.group(1)); return "[not available]"
        return val
    return TOKEN.sub(rep, text), missing

if __name__ == "__main__":
    tpl, out = sys.argv[1], sys.argv[2]
    text, missing = fill(open(tpl).read())
    open(out, "w").write(text)
    if missing: print(f"{out}: {len(missing)} token(s) not available: {sorted(set(missing))}", file=sys.stderr)
    else: print(f"{out}: filled, nothing missing")
