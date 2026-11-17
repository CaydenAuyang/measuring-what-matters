"""Check poster/print_me.pdf against the poster rules. Exits non-zero on any failure.

Usage:  .venv/bin/python src/poster_check.py [--dir poster]

It reads poster/build_manifest.json (what src/poster.py recorded while drawing: every text, its font size and
its box on the page) and the PDF itself, and checks:
  1. 16 pages, each US Letter turned sideways (792 x 612 pt), codes A1..D4 in print order
  2. the manifest belongs to this PDF (hash)
  3. no card over 60 words (chart titles, text inside charts, the corner code and the banner do not count;
     the words in the method diagram do count)
  4. font sizes: title >= 120 pt, card headings >= 54 pt, body >= 26 pt, text inside charts >= 20 pt at print size
  5. no text outside the 0.4 in margin (manifest boxes, and the real text positions in the PDF when PyMuPDF is installed)
  6. no leftover {placeholder} braces
  7. none of the banned words, no em dashes, no exclamation marks, no AI product names, no "significant"
  8. piece 11 carries the exact line "[CAYDEN TO WRITE, 2 sentences]"; nothing drawn failed or ran off a figure
Anything shown as "not available" is listed as a note, not a failure.
"""
import argparse, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_W, PAGE_H, MARGIN = 792.0, 612.0, 0.4 * 72
N_PAGES = 16
CODES = [r + str(c) for r in "ABCD" for c in range(1, 5)]
TITLE_MIN, HEAD_MIN, BODY_MIN, CHART_MIN, MAX_WORDS = 120, 54, 26, 20, 60
TOL = 0.75                                # points of slack for rounding
BANNED = ["leverage", "robust", "comprehensive", "crucial", "nuanced", "straightforward", "genuinely", "arguably",
          "deep dive", "unpack", "landscape", "synergy", "significant"]
BANNED_STEMS = ["leverag", "robust", "nuance", "unpack", "synerg", "significan"]
PRODUCT_NAMES = ["claude", "gemini", "gpt", "chatgpt", "openai", "anthropic", "haiku", "sonnet", "opus", "llama", "mistral", "copilot", "deepseek", "grok"]
BRITISH = ["colour", "labelled", "labelling", "analyse", "analysed", "behaviour", "centre", "programme", "organisation", "neighbourhood", "favour", "modelling"]
MUST_HAVE = {"D2": "[CAYDEN TO WRITE, 2 sentences]", "A1": "Measuring"}


def count_words(text):
    return sum(1 for t in str(text).split() if re.search(r"[A-Za-z0-9]", t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "poster"))
    a = ap.parse_args()
    pdf_path = os.path.join(a.dir, "print_me.pdf"); man_path = os.path.join(a.dir, "build_manifest.json")
    fails, notes = [], []

    def fail(msg): fails.append(msg)

    if not os.path.exists(pdf_path): print(f"FAIL: {pdf_path} does not exist"); return 1
    if not os.path.exists(man_path): print(f"FAIL: {man_path} does not exist (run src/poster.py)"); return 1
    raw = open(pdf_path, "rb").read()
    try:
        M = json.load(open(man_path))
    except Exception as e:
        print(f"FAIL: cannot read the manifest: {e}"); return 1

    # ---- 2. manifest matches the PDF
    if hashlib.sha256(raw).hexdigest() != M.get("pdf_sha256"):
        fail("build_manifest.json does not belong to this print_me.pdf (hash differs). Re-run src/poster.py.")

    # ---- 1. page count and size, from the PDF itself
    doc = None
    try:
        import warnings
        warnings.simplefilter("ignore")
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(pdf_path)
        n_pdf = doc.page_count
        sizes = [(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc]
    except ImportError:
        notes.append("PyMuPDF is not installed: page size and text positions are read from the PDF's page boxes and the manifest only")
        boxes = re.findall(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*\]", raw)
        n_pdf = len(re.findall(rb"/Type\s*/Page\b(?!s)", raw))
        sizes = [(round(float(b[2]) - float(b[0]), 1), round(float(b[3]) - float(b[1]), 1)) for b in boxes]
    if n_pdf != N_PAGES: fail(f"page count is {n_pdf}, expected {N_PAGES}")
    for i, sz in enumerate(sizes, 1):
        if abs(sz[0] - PAGE_W) > 1 or abs(sz[1] - PAGE_H) > 1:
            fail(f"page {i} is {sz[0]} x {sz[1]} pt, expected {PAGE_W:g} x {PAGE_H:g} (US Letter turned sideways)")
    pages = M.get("pages") or []
    if len(pages) != N_PAGES: fail(f"the manifest lists {len(pages)} pages, expected {N_PAGES}")
    if [p.get("code") for p in pages] != CODES: fail(f"page codes are not A1..D4 in print order: {[p.get('code') for p in pages]}")

    # ---- per page
    all_text = []
    for p in pages:
        code = p.get("code", "?"); kind = p.get("kind")
        items = p.get("items") or []; figs = p.get("figures") or []
        texts = [(i.get("text", ""), i) for i in items]
        fig_texts = [(t.get("text", ""), f, t) for f in figs for t in (f.get("texts") or [])]
        page_text = " ".join(t for t, _ in texts) + " " + " ".join(t for t, _, _ in fig_texts)
        all_text.append((code, page_text))

        # 3. words
        if kind != "banner":
            n = sum(count_words(t) for t, i in texts if i.get("role") not in ("code", "chart_title"))
            n += sum(count_words(t) for t, f, _ in fig_texts if f.get("text_role") == "diagram_text")
            if n > MAX_WORDS: fail(f"{code}: {n} words on the card, limit {MAX_WORDS}")
            if n != p.get("word_count"): notes.append(f"{code}: recount gives {n} words, the manifest says {p.get('word_count')}")

        # 4. sizes
        if not any(i.get("role") == "code" and i.get("text") == code for i in items): fail(f"{code}: the corner code is missing")
        for t, i in texts:
            role, size = i.get("role"), float(i.get("size", 0))
            need = {"title": TITLE_MIN, "heading": HEAD_MIN, "chart_title": HEAD_MIN, "code": 0}.get(role, BODY_MIN)
            if size + 1e-6 < need: fail(f"{code}: {role} text at {size:g} pt, minimum {need}: '{t[:50]}'")
            # 5. margins, from the manifest
            x0, y0, x1, y1 = i.get("bbox", [0, 0, 0, 0])
            if x0 < MARGIN - TOL or y0 < MARGIN - TOL or x1 > PAGE_W - MARGIN + TOL or y1 > PAGE_H - MARGIN + TOL:
                fail(f"{code}: text outside the 0.4 in margin: '{t[:50]}' box {i.get('bbox')}")
        if kind == "banner" and code == "A1" and not any(i.get("role") == "title" for i in items): fail("A1: no title text recorded")
        if kind == "card" and not any(i.get("role") in ("heading", "chart_title") for i in items): fail(f"{code}: the card has no heading")
        for f in figs:
            scale = float(f.get("scale", 1.0)); need = BODY_MIN if f.get("text_role") == "diagram_text" else CHART_MIN
            for t in (f.get("texts") or []):
                eff = float(t.get("size", 0)) * scale
                if eff + 0.05 < need: fail(f"{code}: text inside {os.path.basename(f.get('file', 'figure'))} prints at {eff:.1f} pt, minimum {need}: '{t.get('text', '')[:40]}'")
            if f.get("overflow"): fail(f"{code}: text runs off the edge of {os.path.basename(f.get('file', 'figure'))}: {f['overflow']}")
            x0, y0, x1, y1 = f.get("bbox", [0, 0, 0, 0])
            if x0 < MARGIN - TOL or y0 < MARGIN - TOL or x1 > PAGE_W - MARGIN + TOL or y1 > PAGE_H - MARGIN + TOL:
                fail(f"{code}: figure outside the 0.4 in margin: {f.get('bbox')}")
        # text must not sit on top of a figure (a column that ran long, for example)
        for t, i in texts:
            if i.get("role") == "code": continue
            bx0, by0, bx1, by1 = i.get("bbox", [0, 0, 0, 0])
            for f in figs:
                fx0, fy0, fx1, fy1 = f.get("bbox", [0, 0, 0, 0])
                if min(bx1, fx1) - max(bx0, fx0) > 2 and min(by1, fy1) - max(by0, fy0) > 2:
                    fail(f"{code}: text overlaps a figure: '{t[:40]}'")
        # lines of text must not overlap each other
        boxes = [(i.get("bbox"), t) for t, i in texts if i.get("role") != "code"]
        for n1 in range(len(boxes)):
            for n2 in range(n1 + 1, len(boxes)):
                (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = boxes[n1][0], boxes[n2][0]
                if min(ax1, bx1) - max(ax0, bx0) > 2 and min(ay1, by1) - max(ay0, by0) > 2.5:
                    fail(f"{code}: two lines of text overlap: '{boxes[n1][1][:30]}' and '{boxes[n2][1][:30]}'")

        # 6. braces
        if re.search(r"[{}]", page_text): fail(f"{code}: leftover placeholder braces: {re.findall(r'.{0,15}[{}].{0,15}', page_text)[:3]}")
        # 7. words and marks
        low = page_text.lower()
        for wd in BANNED:
            if re.search(r"\b" + re.escape(wd) + r"\b", low): fail(f"{code}: banned word '{wd}'")
        for st in BANNED_STEMS:
            m = re.search(r"\b" + st + r"\w*", low)
            if m and m.group(0) not in BANNED: fail(f"{code}: banned word form '{m.group(0)}'")
        for wd in PRODUCT_NAMES:
            if re.search(r"\b" + re.escape(wd) + r"\b", low): fail(f"{code}: AI product name '{wd}' (say 'an AI language model')")
        for wd in BRITISH:
            if re.search(r"\b" + wd + r"\b", low): fail(f"{code}: British spelling '{wd}'")
        if "—" in page_text or "–" in page_text or " -- " in page_text: fail(f"{code}: dash character (no em dashes)")
        if "!" in page_text: fail(f"{code}: exclamation mark")
        if code in MUST_HAVE and MUST_HAVE[code] not in page_text: fail(f"{code}: required text missing: {MUST_HAVE[code]}")
        if "not available" in low: notes.append(f"{code}: shows 'not available' ({len(re.findall('not available', low))} place(s))")

    # ---- the PDF's real text, when PyMuPDF is there
    if doc is not None:
        for n, page in enumerate(doc):
            code = CODES[n] if n < len(CODES) else f"page {n + 1}"
            d = page.get_text("dict")
            pdf_words = []
            for b in d.get("blocks", []):
                for ln in b.get("lines", []):
                    for sp in ln.get("spans", []):
                        t = sp.get("text", "").strip()
                        if not t: continue
                        pdf_words.append(t)
                        size = sp.get("size", 0); ox, oy = sp.get("origin", (0, 0))
                        x0, x1 = sp["bbox"][0], sp["bbox"][2]
                        top, bot = oy - 0.74 * size, oy + 0.22 * size           # ink box around the baseline (top-left origin)
                        if x0 < MARGIN - TOL or x1 > PAGE_W - MARGIN + TOL or top < MARGIN - TOL or bot > PAGE_H - MARGIN + TOL:
                            fail(f"{code}: in the PDF, text outside the 0.4 in margin: '{t[:50]}'")
                        if size + 0.01 < BODY_MIN and t != code:
                            fail(f"{code}: in the PDF, text at {size:.1f} pt below the {BODY_MIN} pt minimum: '{t[:50]}'")
            got = re.sub(r"\s+", " ", " ".join(pdf_words))
            if n < len(pages):
                for i in pages[n].get("items") or []:
                    want = re.sub(r"\s+", " ", i.get("text", "")).strip()
                    if want and want not in got and want.replace(" ", "") not in got.replace(" ", ""):
                        fail(f"{code}: the manifest lists text that is not in the PDF: '{want[:50]}'")
            if re.search(r"[{}]", got): fail(f"{code}: in the PDF, leftover placeholder braces")

    for e in M.get("errors") or []: fail(f"poster.py reported an error: {e}")
    for w in M.get("warnings") or []: fail(f"poster.py reported a warning: {w}")
    for m in M.get("missing") or []: notes.append(f"missing data: {m}")
    for m in M.get("fallbacks_used") or []: notes.append(f"plan value used: {m}")

    print(f"poster_check: {pdf_path}")
    print(f"  pages {n_pdf}, lead source {M.get('lead_source')}, validation {M.get('inputs', {}).get('validation_status') or 'no file'}, "
          f"results generated {M.get('inputs', {}).get('results_generated_utc')}")
    print("  words per card: " + ", ".join(f"{p.get('code')} {p.get('word_count')}" for p in pages if p.get("kind") == "card"))
    for nt in notes: print("  note: " + nt)
    if fails:
        for f in fails: print("  FAIL: " + f)
        print(f"FAILED: {len(fails)} problem(s)")
        return 1
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
