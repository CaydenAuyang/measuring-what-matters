"""The board poster: eight pieces on a 710 x 550 mm board (landscape), built to match
poster/design_reference_landscape.html. Every number and both charts are filled from
data/public/results.json and data/public/yearly_changes.csv at run time.

Writes:
  poster/letter_pieces.pdf   one piece per US Letter page at true size, with light cut lines. Every piece fits inside
                             266 x 203 mm, so it prints on a normal printer with a 6.35 mm margin on all sides
                             (the 330 mm tall numbers piece is longer than a sheet, so it prints as two halves)
  poster/board_layout.pdf    where each piece goes on the board, in mm
  poster/board_preview.png   the finished board
  poster/board.html          the board as a web page (the source of the preview)
  poster/board_manifest.json the numbers and wording used, and the rule that picked each title

Layout unit: the reference draws the board at 1420 x 1100 px, so 1 px = 0.5 mm.
Rendering uses headless Google Chrome (no network). Fonts are the Inter and Lora files in poster/fonts.
Usage: python src/poster_board.py
"""
import json, math, os, shutil, subprocess, sys, tempfile
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTER = os.path.join(ROOT, "poster")
FONTS = os.path.join(POSTER, "fonts")
REPO_URL = "https://github.com/CaydenAuyang/measuring-what-matters"
PX_PER_MM = 2.0                       # reference pixels per board millimetre
CSS_SCALE = 0.5 * 96 / 25.4           # one reference pixel printed as 0.5 mm
BOARD_MM = (710, 550)
NAVY, CORAL, TEAL, GREY = "#14213D", "#E76F51", "#2A9D8F", "#7A8499"

# name, left, top, width, height in mm (from the board's top-left corner), css class
# Columns are 215, 266 and 161 mm wide (22 mm outer margin, 12 mm gaps) so that every piece fits a US Letter sheet.
# The three center heights are set at build time by fit_center(): they always add up to 482 mm.
PAGE_MM = (215.9, 279.4)              # US Letter
FIT_MM = (266, 203)                   # the largest piece a Letter sheet takes with a 6.35 mm margin on all sides
PIECES = [
    ("title", "Title", 22, 22, 215, 150, "dark"),
    ("question", "The question", 22, 184, 215, 150, "cream"),
    ("method", "The method", 22, 346, 215, 182, ""),
    ("answer", "The answer (chart)", 249, 22, 266, 170, ""),
    ("case", "When they disagree (case study)", 249, 204, 266, 190, ""),
    ("surprised", "What surprised me", 249, 406, 266, 122, ""),
    ("numbers", "By the numbers", 527, 22, 161, 330, "cream"),
    ("qr", "QR card", 527, 364, 161, 164, ""),
]
ANSWER_MIN_MM = 170                   # what the answer chart needs; spare height in the center column goes to the case study
# Cayden's own words for the "What surprised me" piece (his message of November 18). Kept word for word in every rebuild.
SURPRISED = ["I expected the news to track real problems better than Google searches. It was the opposite: what people search for follows the official numbers far more closely than what papers cover.",
             "I assumed that when the news and official data disagreed, one of them was wrong. Often they were measuring different things, like Hong Kong's economy news covering business worries while unemployment fell."]
SURPRISED_STYLE = "font-size:15px;line-height:1.3;color:#14213D"          # the size of the reference's other body text
CITY = {"hk": "Hong Kong", "nyc": "New York", "london": "London"}
CAT = {"safety": "Safety", "economy": "Economy", "housing": "Housing", "transport": "Transport", "environment": "Environment",
       "health": "Health", "education": "Education", "cost_of_living": "Cost of living"}


def font_css(base):
    return f"""
@font-face{{font-family:'Inter';src:url('{base}/InterVariable.woff2') format('woff2');font-weight:100 900;font-style:normal}}
@font-face{{font-family:'Inter';src:url('{base}/InterVariable-Italic.woff2') format('woff2');font-weight:100 900;font-style:italic}}
@font-face{{font-family:'Inter Display';src:url('{base}/InterVariable.woff2') format('woff2');font-weight:100 900;font-style:normal}}
@font-face{{font-family:'Lora';src:url('{base}/Lora-wght.ttf') format('truetype');font-weight:400 700;font-style:normal}}
"""

# The reference's own style rules, unchanged, plus the optical size that makes the variable Inter file draw as Inter or Inter Display.
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,sans-serif;color:#14213D;font-variation-settings:"opsz" 14;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.board{position:relative;width:1420px;height:1100px;background:#FFFFFF}
.piece{position:absolute;background:#fff;border:1px solid #ECE8E0;box-shadow:0 1.5px 4px rgba(20,33,61,.10);padding:24px 28px;overflow:hidden}
.dark{background:#14213D;border-color:#14213D;color:#fff}
.cream{background:#F6F2EA;border-color:#EDE7DB}
.kicker{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:#7A8499;margin-bottom:10px}
h2{font-family:'Inter Display';font-weight:800;font-size:27px;line-height:1.12;letter-spacing:-.01em}
.sub{font-size:15px;color:#7A8499;margin-top:6px}
.num{font-family:'Inter Display';font-weight:800;line-height:1;letter-spacing:-.02em}
.lab{font-size:13.5px;color:#7A8499;line-height:1.3}
h2,.num,.disp{font-variation-settings:"opsz" 32}
svg text{font-family:Inter,sans-serif}
svg text.disp{font-family:'Inter Display'}
"""


# ------------------------------------------------------------------ data
def load():
    R = json.load(open(os.path.join(ROOT, "data/public/results.json")))
    Y = pd.read_csv(os.path.join(ROOT, "data/public/yearly_changes.csv"))
    return R, Y


def need(x, what):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        raise SystemExit(f"poster_board: a value the poster needs is missing from the results file: {what}")
    return x


def answer_wording(R):
    """The two lines of the answer title follow the pre-registered verdicts for H1."""
    vs, vn = R["verdicts"].get("h1_search"), R["verdicts"].get("h1_news")
    est_n = R["main"]["news"]["h1"]["est"]
    if vs == "supported":
        line1 = "Searches follow real problems."
        if vn == "supported":
            line2, rule = ("News barely does.", "news supported and its slope is under 0.15") if est_n < 0.15 else ("News does too.", "news supported, slope 0.15 or more")
        elif vn == "failed":
            line2, rule = "News moves the other way.", "news interval below zero"
        else:
            line2, rule = "News shows no clear link.", "news interval includes zero"
    else:
        line1 = "Searches show no clear link." if vs != "failed" else "Searches fall when problems grow."
        if vn == "supported":
            line2, rule = ("News barely follows them." if est_n < 0.15 else "News follows real problems."), "news supported"
        elif vn == "failed":
            line2, rule = "News moves the other way.", "news interval below zero"
        else:
            line2, rule = "News shows no clear link either.", "news interval includes zero"
        rule = f"search verdict {vs}; " + rule
    return line1, line2, f"search H1 {vs}, news H1 {vn}: {rule}"


def pick_case(R):
    """The Hong Kong case study: the results file's own case study if it is in Hong Kong, else the longest
    Hong Kong news disconnection with a proposed cause other than unclear, else the results file's case study."""
    cs = R.get("case_study") or {}
    if cs.get("city") == "hk" and cs.get("source") == "news":
        return cs, "the case study in the results file"
    runs = [r for r in (R.get("h3") or {}).get("runs") or [] if r.get("city") == "hk" and r.get("source") == "news"]
    named = [r for r in runs if r.get("proposed_cause") != "unclear"]
    for pool, why in ((named, "longest Hong Kong news disconnection with a proposed cause other than unclear"), (runs, "longest Hong Kong news disconnection")):
        if pool:
            return sorted(pool, key=lambda r: (-r["months"], r["start"]))[0], why
    return need(cs or None, "case_study"), "the case study in the results file (no Hong Kong disconnection is listed)"


def case_wording(cs):
    city, cat = CITY.get(cs["city"], cs["city"]), cs["category"]
    y1, y2 = cs["start"][:4], cs["end"][:4]
    when = f"{y1} to {y2}" if y1 != y2 else y1
    improving, rising = cs["official_direction"] == "improving", cs["attention_direction"] == "rising"
    if cat == "economy":
        official, legend = ("jobs recovered" if improving else "jobs got worse"), "Unemployment"
    else:
        official, legend = ("official data improved" if improving else "official data got worse"), "Official measure"
    catl = CAT.get(cat, cat).lower()
    news = "kept rising" if rising else "kept falling"
    return f"{city}, {when}: {official},", f"but {catl} news {news}.", legend, f"{CAT.get(cat, cat)} news coverage"


# ------------------------------------------------------------------ charts (same geometry as the reference)
def answer_svg(R, W=474.0):
    rows = []
    for key, label, color in (("search", "Google searches", TEAL), ("news", "Local news", CORAL)):
        h = R["main"][key]["h1"]
        rows.append((label, color, round(need(h.get("est"), key + " slope"), 2), round(need(h.get("ci_low"), key + " interval"), 2), round(need(h.get("ci_high"), key + " interval"), 2)))
    lo = min(0.0, math.floor(min(r[3] for r in rows) * 10) / 10)
    hi = max(0.5, math.ceil(max(r[4] for r in rows) * 10) / 10)
    xl = 172.0 if W >= 538 else 150.0                      # right edge of the row labels
    x0, x1 = xl + 18, W - 70.0
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    n = int(round((hi - lo) * 10))
    step = 1 if n <= 6 else 2
    s = [f'<svg width="{W:.0f}" height="172" viewBox="0 0 {W:.0f} 172">']
    for i in range(int(round(lo * 10)), int(round(hi * 10)) + 1):
        if i % step:                          # ticks sit on multiples of the step, counted from zero
            continue
        v = i / 10
        s.append(f'<line x1="{X(v):.2f}" y1="30" x2="{X(v):.2f}" y2="142" stroke="#E3E0D8" stroke-width="1"/>'
                 f'<text x="{X(v):.2f}" y="162" font-size="13" fill="{GREY}" text-anchor="middle">{("%.1f" % v) if abs(v) > 1e-9 else "0"}</text>')
    s.append(f'<line x1="{X(0):.2f}" y1="22" x2="{X(0):.2f}" y2="146" stroke="{NAVY}" stroke-width="2"/>'
             f'<text x="{X(0) + 6:.2f}" y="24" font-size="12.5" fill="{NAVY}" font-weight="600">no link</text>')
    for (label, color, est, cl, ch), y in zip(rows, (62, 114)):
        s.append(f'<text x="{xl:.0f}" y="{y + 6}" font-size="17" font-weight="600" fill="{NAVY}" text-anchor="end">{label}</text>'
                 f'<line x1="{X(cl):.2f}" y1="{y}" x2="{X(ch):.2f}" y2="{y}" stroke="{color}" stroke-width="7" stroke-linecap="round" opacity="0.35"/>'
                 f'<circle cx="{X(est):.2f}" cy="{y}" r="13" fill="{color}"/>'
                 f'<text class="disp" x="{max(X(ch), X(est) + 13) + 16:.2f}" y="{y + 11}" font-size="32" font-weight="800" fill="{color}">{est:.2f}</text>')
    s.append("</svg>")
    return "".join(s), {r[0]: {"slope": r[2], "interval": [r[3], r[4]]} for r in rows}


def case_svg(cs, Y, half=83.0, W=474.0):
    """half: half the plot height in reference pixels (83 in the reference; smaller when the piece is made shorter)."""
    d = Y[(Y.city == cs["city"]) & (Y.category == cs["category"]) & (Y.source == cs["source"])].sort_values("period_end_month")
    d = d.dropna(subset=["official_change_sd", "attention_change_sd"])
    start = "2019-07" if cs["start"] >= "2020-01" else str(pd.Period(cs["start"], "M") - 24)
    d = d[d.period_end_month >= start].reset_index(drop=True)
    if len(d) < 12:
        raise SystemExit("poster_board: too few months for the case study chart")
    months = pd.period_range(d.period_end_month.iloc[0], d.period_end_month.iloc[-1], freq="M")
    xr = W - 18.0
    step = (xr - 46) / (len(months) - 1)
    xi = {str(m): 46 + i * step for i, m in enumerate(months)}
    top = max(d.official_change_sd.abs().max(), d.attention_change_sd.abs().max())
    k = half / max(1, math.ceil(top))                      # both lines share one scale, in standard deviations
    mid, bot = 26.0 + half, 26.0 + 2 * half                # zero line and bottom of the plot
    Yp = lambda v: mid - v * k
    xa, xb = xi[cs["start"]], xi[cs["end"]]
    s = [f'<svg width="{W:.0f}" height="{bot + 40:.0f}" viewBox="0 0 {W:.0f} {bot + 40:.0f}">',
         f'<rect x="{xa:.2f}" y="20" width="{xb - xa:.2f}" height="{bot - 20:.1f}" fill="#F4A261" opacity="0.18" rx="4"/>',
         f'<line x1="46" y1="{mid:.1f}" x2="{xr:.0f}" y2="{mid:.1f}" stroke="{NAVY}" stroke-width="1.4" opacity="0.5"/>']
    years = sorted({m.year for m in months if m.month == 1})
    every = 1 if len(years) <= 9 else 2
    for yr in years[::every]:
        x = xi[f"{yr}-01"]
        s.append(f'<text x="{x:.2f}" y="{bot + 24:.1f}" font-size="13" fill="{GREY}" text-anchor="middle">{yr}</text><line x1="{x:.2f}" y1="{bot:.1f}" x2="{x:.2f}" y2="{bot + 6:.1f}" stroke="{GREY}"/>')
    for col, color in (("official_change_sd", NAVY), ("attention_change_sd", CORAL)):
        pts = " ".join(f"{xi[m]:.1f},{Yp(v):.1f}" for m, v in zip(d.period_end_month, d[col]))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>')
    s.append(f'<text x="{(xa + xb) / 2:.2f}" y="38" font-size="14" font-weight="700" fill="#B5542F" text-anchor="middle">{cs["months"]} months apart</text>'
             f'<text x="38" y="44.83" font-size="12" fill="{GREY}" text-anchor="end">worse</text><text x="38" y="{bot - 8.83:.2f}" font-size="12" fill="{GREY}" text-anchor="end">better</text></svg>')
    return "".join(s), {"first_month": str(months[0]), "last_month": str(months[-1]), "px_per_sd": round(k, 3)}


def qr_svg(url, side=170):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    q.add_data(url); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    path = "".join(f"M{x},{y}H{x + 1}V{y + 1}H{x}z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg width="{side}" height="{side}" viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges"><path d="{path}" fill="#000000"/></svg>', n


# ------------------------------------------------------------------ the eight pieces
ICONS = {
    "gov": ('#E8EBF1', f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{NAVY}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.7 10v8M14.3 10v8M19 10v8"/><path d="M3 21h18"/></svg>'),
    "search": ('#E2F2F0', f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{TEAL}" stroke-width="1.9" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>'),
    "news": ('#FBE7E1', f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{CORAL}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="15" height="16" rx="1.5"/><path d="M18 8h3v10.5a1.5 1.5 0 0 1-3 0"/><path d="M6.5 8h8M6.5 11.5h8M6.5 15h5"/></svg>'),
}


def measure(fragment, width=None):
    """Width and height in reference pixels of a piece of the poster's HTML, measured in Chrome with the poster's fonts.
    With a width the fragment wraps inside it; without one it is measured on one line."""
    box = f"width:{width}px" if width else "display:inline-block;white-space:nowrap"
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css("file://" + FONTS)}{BASE_CSS}</style></head><body>'
            f'<div id="t" style="{box}">{fragment}</div>'
            '<script>document.fonts.ready.then(()=>{const r=document.getElementById("t").getBoundingClientRect();document.body.setAttribute("data-m",r.width+","+r.height)})</script></body></html>')
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as prof:
        hp = os.path.join(tmp, "m.html"); open(hp, "w", encoding="utf-8").write(html)
        out = subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}", "--virtual-time-budget=6000", "--dump-dom", "file://" + hp],
                             check=True, timeout=120, capture_output=True, text=True).stdout
    import re
    m = re.search(r'data-m="([0-9.]+),([0-9.]+)"', out)
    if not m:
        raise SystemExit("poster_board: could not measure text for the poster")
    return float(m.group(1)), float(m.group(2))


def inner_px(key):
    w = next(p for p in PIECES if p[0] == key)[4]
    return w * PX_PER_MM - 2 - 56                           # piece width less its border and side padding


def surprised_html():
    return ('<div class="kicker">What surprised me</div><div style="' + SURPRISED_STYLE + '">'
            + "".join(f'<p style="margin:0 0 {0 if i == len(SURPRISED) - 1 else 10}px 0">{t}</p>' for i, t in enumerate(SURPRISED)) + '</div>')


def fit_center(case_header_html):
    """Set the three center heights (they add up to 482 mm). The What surprised me piece is only as tall as its text.
    The answer piece gets what its chart needs. The case study gets the rest, up to the 203 mm a Letter sheet takes;
    anything beyond that goes back to the answer piece. Returns the plot half-height for the case chart."""
    idx = {p[0]: i for i, p in enumerate(PIECES)}
    total = BOARD_MM[1] - 44 - 24
    s_mm = math.ceil((measure(surprised_html(), inner_px("surprised"))[1] + 48 + 2 + 1) / PX_PER_MM)
    c_mm = min(FIT_MM[1], total - ANSWER_MIN_MM - s_mm)
    a_mm = total - s_mm - c_mm
    if a_mm > FIT_MM[1] or s_mm > FIT_MM[1] or c_mm < 100:
        raise SystemExit("poster_board: the center pieces do not fit on Letter sheets with this text")
    y = 22
    for key, h in (("answer", a_mm), ("case", c_mm), ("surprised", s_mm)):
        k, n, x, _, w, _, cls = PIECES[idx[key]]
        PIECES[idx[key]] = (k, n, x, y, w, h, cls); y += h + 12
    head = measure(case_header_html, inner_px("case"))[1]
    half = (c_mm * PX_PER_MM - 2 - 48 - head - 6 - 66 - 2) / 2    # border, padding, text above the chart, gap, axis and label room
    if half < 30:
        raise SystemExit("poster_board: no room left for the case study chart")
    return min(83.0, half)


def build_pieces(R, Y):
    c = R["counts"]
    man = {}
    out = {}
    out["title"] = ('<div style="display:flex;flex-direction:column;justify-content:space-between;height:100%">'
                    f'<div><div style="width:46px;height:6px;background:{CORAL};border-radius:3px;margin-bottom:18px"></div>'
                    '<div class="disp" style="font-family:\'Inter Display\';font-weight:800;font-size:50px;line-height:.98;letter-spacing:-.02em">Measuring<br>What<br>Matters</div></div>'
                    '<div style="font-size:14.5px;line-height:1.45;opacity:.85"><b>Cayden Auyang</b><br>Mentors: Mr. Qua and Mr. Lake<br>Pomfret School</div></div>')
    out["question"] = ('<div style="display:flex;flex-direction:column;justify-content:center;height:100%"><div class="kicker">The question</div>'
                       '<div style="font-family:Lora;font-size:32px;line-height:1.2;font-weight:500">When a city\'s problems get worse, does public attention follow?</div>'
                       '<div class="sub" style="margin-top:14px">Hong Kong · New York · London</div></div>')
    rows = "".join(f'<div style="display:flex;gap:14px;align-items:center"><div style="width:48px;height:48px;border-radius:24px;background:{ICONS[k][0]};display:flex;align-items:center;justify-content:center;flex:none">{ICONS[k][1]}</div>'
                   f'<div><div style="font-weight:700;font-size:16.5px">{who}</div><div style="font-size:14px;color:{GREY}">{what}</div></div></div>'
                   for k, who, what in (("gov", "Government", "Official statistics"), ("search", "Residents", "Google searches"), ("news", "Journalists", "Local news coverage")))
    out["method"] = ('<div class="kicker">The method</div><h2 style="font-size:24px">Three ways to measure the same problem</h2>'
                     f'<div style="margin-top:18px;display:flex;flex-direction:column;gap:16px">{rows}</div>'
                     '<div style="margin-top:20px;padding-top:14px;border-top:1px solid #E3E0D8;font-size:15px;font-weight:600">Do they rise and fall together, year by year?</div>')
    l1, l2, rule = answer_wording(R)
    cs, why = pick_case(R)
    t1, t2, leg_off, leg_news = case_wording(cs)
    sw = lambda col: f'<span style="display:inline-block;width:18px;height:4px;background:{col};vertical-align:middle;margin-right:6px;border-radius:2px"></span>'
    # The case title keeps the reference's 27 px and wraps inside the narrower Letter-width piece.
    case_head = (f'<div class="kicker">When they disagree</div><h2 style="text-wrap:balance">{t1} {t2}</h2>'
                 f'<div style="display:flex;gap:22px;margin-top:10px;font-size:13.5px;font-weight:600"><span>{sw(NAVY)}{leg_off}</span><span>{sw(CORAL)}{leg_news}</span></div>')
    half = fit_center(case_head)
    # The answer title is one line at 34 px in the reference. If the narrower piece cannot hold it, it is set just small enough to fit.
    wa = inner_px("answer")
    widest = max(measure(f'<h2 style="font-size:34px">{t}</h2>')[0] for t in (l1, l2))
    a_size = 34.0 if widest <= wa else math.floor(34.0 * wa / widest * 2) / 2
    svg, vals = answer_svg(R, wa)
    out["answer"] = (f'<div class="kicker">The answer</div><h2 style="font-size:{a_size:g}px">{l1}<br><span style="color:{CORAL}">{l2}</span></h2>'
                     f'<div class="sub">How much attention rises each time a problem gets worse</div><div>{svg}</div>')
    man["answer"] = {"title": [l1, l2], "title_px": a_size, "rule": rule, "values": vals}
    svg, info = case_svg(cs, Y, half, inner_px("case"))
    out["case"] = case_head + f'<div style="margin-top:6px">{svg}</div>'
    man["case"] = {"title": [t1, t2], "picked_by": why, "city": cs["city"], "category": cs["category"], "start": cs["start"], "end": cs["end"], "months": cs["months"],
                   "official_direction": cs["official_direction"], "attention_direction": cs["attention_direction"], **info}
    out["surprised"] = surprised_html()
    man["surprised"] = {"text": SURPRISED}
    y1, y2 = need(c.get("news_first_month"), "news_first_month")[:4], need(c.get("news_last_month"), "news_last_month")[:4]
    nums = [(str(need(c.get("cities"), "cities")), "cities", NAVY),
            (f"{round(need(c.get('articles_labeled_all'), 'articles_labeled_all') / 1000):,}k", "news articles sorted by topic", CORAL),
            (str(need(c.get("official_series_main"), "official_series_main")), "official data series", NAVY),
            (str(need(c.get("search_months"), "search_months") // 12), "years of search data", TEAL),
            (str(need(c.get("outlets_main_panel_total"), "outlets_main_panel_total")), "local news outlets", NAVY),
            (str(need(c.get("news_months"), "news_months")), f"months of news, {y1} to {y2}", NAVY)]
    items = "".join(f'<div><div class="num" style="color:{col};font-size:42px">{n}</div><div class="lab" style="margin-top:4px">{lab}</div></div>' for n, lab, col in nums)
    out["numbers"] = ('<div class="kicker">By the numbers</div>'
                      f'<div style="display:flex;flex-direction:column;justify-content:space-between;height:calc(100% - 34px);padding-top:10px">{items}</div>')
    man["numbers"] = [{"value": n, "label": lab} for n, lab, _ in nums]
    qr, n = qr_svg(REPO_URL)
    out["qr"] = ('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center">'
                 f'<div>{qr}</div><div style="font-weight:700;font-size:15.5px;margin-top:14px">Data, code and paper</div>'
                 f'<div style="font-size:12px;color:{GREY};margin-top:5px;line-height:1.4">Articles sorted by an AI model<br>and checked by a second AI.</div></div>')
    man["qr"] = {"url": REPO_URL, "modules": n}
    return out, man


def piece_div(key, inner, at_origin=False, shadow=True):
    _, _, x, y, w, h, cls = next(p for p in PIECES if p[0] == key)
    left, top = (0, 0) if at_origin else (x * PX_PER_MM, y * PX_PER_MM)
    extra = "" if shadow else ";box-shadow:none"
    return f'<div class="piece {cls}" style="left:{left:g}px;top:{top:g}px;width:{w * PX_PER_MM:g}px;height:{h * PX_PER_MM:g}px{extra}">{inner}</div>'


# ------------------------------------------------------------------ rendering
def find_chrome():
    cands = [os.environ.get("MWM_CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium", shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]
    for p in cands:
        if p and os.path.exists(p):
            return p
    raise SystemExit("poster_board: Google Chrome was not found. Set MWM_CHROME to a Chrome or Chromium binary.")


def chrome(args, html_path):
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                        "--hide-scrollbars", f"--user-data-dir={prof}", "--virtual-time-budget=6000", *args, "file://" + html_path],
                       check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def sheet_plan():
    """One entry per Letter page: piece key, page name, landscape?, the window of the piece shown (top offset and height in mm)."""
    plan = []
    for key, name, x, y, w, h, _ in PIECES:
        if key == "numbers":                 # 330 mm is longer than a sheet: two halves that meet between the third and fourth numbers
            plan.append((key, name + ", top half", False, 0, h / 2, "join this edge to the bottom half"))
            plan.append((key, name + ", bottom half", False, h / 2, h / 2, "join this edge to the top half"))
        else:
            plan.append((key, name, w > FIT_MM[1], 0, h, ""))
    return plan


def sheet_html(key, name, landscape, off, hh, join, inner, page_no, n_pages):
    _, _, bx, by, w, h, _ = next(p for p in PIECES if p[0] == key)
    pw, ph = (PAGE_MM[1], PAGE_MM[0]) if landscape else PAGE_MM
    if w > (FIT_MM[0] if landscape else FIT_MM[1]) or hh > (FIT_MM[1] if landscape else FIT_MM[0]):
        raise SystemExit(f"poster_board: {name} is {w} x {hh} mm and does not fit a Letter sheet's printable area")
    left, top = (pw - w) / 2, (ph - hh) / 2
    marks = []
    line = "position:absolute;background:#B5B5B5"
    def hmark(xm, ym): marks.append(f'<div style="{line};left:{xm}mm;top:{ym - 0.075}mm;width:6mm;height:0.15mm"></div>')
    def vmark(xm, ym): marks.append(f'<div style="{line};left:{xm - 0.075}mm;top:{ym}mm;width:0.15mm;height:6mm"></div>')
    for cx, sx in ((left, -1), (left + w, 1)):
        for cy, sy in ((top, -1), (top + hh, 1)):
            if left >= 14.5:                      # horizontal marks beside the corner
                hmark(cx + (1.5 if sx > 0 else -7.5), cy)
            if top >= 14.5:                       # vertical marks above and below the corner
                vmark(cx, cy + (1.5 if sy > 0 else -7.5))
    note = f"Piece {page_no} of {n_pages}: {name}. {w:g} x {hh:g} mm. Cut along the edge of the piece."
    if join:
        edge = "bottom" if off == 0 else "top"
        note += f" The {edge} edge meets the other half."
    note_y = top - 6 if top >= 13 else None
    label = (f'<div style="position:absolute;left:{max(left, 8)}mm;top:{note_y}mm;font-size:7pt;color:#9A9A9A;font-family:Helvetica,Arial,sans-serif">{note}</div>' if note_y is not None else "")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{font_css('file://' + FONTS)}{BASE_CSS}
@page{{size:{pw}mm {ph}mm;margin:0}}
html,body{{width:{pw}mm;height:{ph}mm;background:#fff;overflow:hidden}}
</style></head><body><div style="position:relative;width:{pw}mm;height:{ph}mm;overflow:hidden">
<div style="position:absolute;left:{left}mm;top:{top}mm;width:{w}mm;height:{hh}mm;overflow:hidden;outline:0.15mm solid #D0D0D0">
<div style="position:absolute;left:0;top:{-off}mm;width:{w * PX_PER_MM:g}px;height:{h * PX_PER_MM:g}px;transform:scale({CSS_SCALE:.9f});transform-origin:0 0">{piece_div(key, inner, at_origin=True, shadow=False)}</div>
</div>{''.join(marks)}{label}</div></body></html>"""


def board_html(pieces, fonts_base):
    body = "".join(piece_div(k, pieces[k]) for k, *_ in PIECES)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Measuring What Matters: poster board</title><style>{font_css(fonts_base)}{BASE_CSS}
html,body{{background:#FFFFFF;width:1420px;height:1100px;overflow:hidden}}
</style></head><body><div class="board">{body}</div></body></html>"""


def layout_pdf(path, plan):
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    W, H = PAGE_MM[1] * mm, PAGE_MM[0] * mm
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Measuring What Matters: board layout")
    s = 0.30
    col = sorted({(p[2], p[4]) for p in PIECES})
    ox, oy = 14 * mm, H - 20 * mm                      # top-left corner of the drawn board
    c.setFont("Helvetica-Bold", 13); c.drawString(ox, H - 12 * mm, "Board layout: where each piece goes")
    c.setFont("Helvetica", 8.5); c.setFillColor(HexColor("#555555"))
    c.drawString(ox + 84 * mm, H - 12 * mm, f"Board {BOARD_MM[0]} x {BOARD_MM[1]} mm, landscape. 22 mm outer margin, 12 mm gaps. All numbers are mm from the board's top-left corner.")
    c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(HexColor("#444444")); c.setLineWidth(1)
    c.rect(ox, oy - BOARD_MM[1] * s * mm, BOARD_MM[0] * s * mm, BOARD_MM[1] * s * mm, stroke=1, fill=1)
    pages = {}
    for i, (key, name, *_rest) in enumerate(plan, 1):
        pages.setdefault(key, []).append(i)
    fills = {"dark": "#14213D", "cream": "#F6F2EA", "": "#FFFFFF"}
    for n, (key, name, x, y, w, h, cls) in enumerate(PIECES, 1):
        px, py = ox + x * s * mm, oy - (y + h) * s * mm
        c.setFillColor(HexColor(fills[cls])); c.setStrokeColor(HexColor("#777777")); c.setLineWidth(0.8)
        c.rect(px, py, w * s * mm, h * s * mm, stroke=1, fill=1)
        ink = HexColor("#FFFFFF" if cls == "dark" else "#14213D")
        c.setFillColor(ink)
        ty = py + h * s * mm - 6 * mm
        c.setFont("Helvetica-Bold", 9.5); c.drawString(px + 2.5 * mm, ty, f"{n}. {name}")
        c.setFont("Helvetica", 8.5)
        pg = pages[key]
        lines = [f"{w} x {h} mm", f"left {x}, top {y}", f"right {x + w}, bottom {y + h}",
                 "Letter page " + (str(pg[0]) if len(pg) == 1 else f"{pg[0]} and {pg[1]} (two halves)")]
        for j, t in enumerate(lines):
            c.drawString(px + 2.5 * mm, ty - (j + 1) * 4.2 * mm, t)
    c.setFillColor(HexColor("#333333")); c.setFont("Helvetica", 8.5)
    tw = next(p for p in PIECES if p[0] == "title")[4]
    notes = [f"Columns: {', '.join(str(w) for _, w in col[:-1])} and {col[-1][1]} mm wide, starting {', '.join(str(x) for x, _ in col[:-1])} and {col[-1][0]} mm from the left edge.",
             f"Print letter_pieces.pdf on US Letter at 100% (no \"fit to page\"). Check one piece with a ruler: the dark title piece is {tw} mm wide.",
             "Every piece is at most 266 x 203 mm, so it sits inside a normal printer's margins. No borderless printing is needed.",
             "Piece 7 is 330 mm tall, longer than a sheet. It prints as two halves that meet between the third and fourth numbers."]
    yy = oy - BOARD_MM[1] * s * mm - 4.5 * mm
    for t in notes:
        c.drawString(ox, yy, t); yy -= 4 * mm
    c.showPage()
    c.setFont("Helvetica-Bold", 13); c.setFillColor(HexColor("#000000")); c.drawString(14 * mm, H - 14 * mm, "Positions in mm")
    cols = [("Piece", 14), ("Letter page", 92), ("Width", 122), ("Height", 142), ("Left", 162), ("Top", 182), ("Right", 202), ("Bottom", 222)]
    yy = H - 26 * mm
    c.setFont("Helvetica-Bold", 10)
    for t, x in cols: c.drawString(x * mm, yy, t)
    c.setFont("Helvetica", 10)
    for n, (key, name, x, y, w, h, cls) in enumerate(PIECES, 1):
        yy -= 8 * mm
        pg = pages[key]
        vals = [f"{n}. {name}", str(pg[0]) if len(pg) == 1 else f"{pg[0]} and {pg[1]}", w, h, x, y, x + w, y + h]
        for (t, cx), v in zip(cols, vals): c.drawString(cx * mm, yy, str(v))
    yy -= 14 * mm
    c.setFont("Helvetica", 9.5)
    for t in ["Left and top are measured from the board's top-left corner to the piece's top-left corner.",
              "Order that works: mark the three column starts along the top edge, then place each column from the top down.",
              "Gaps between pieces in a column and between columns are 12 mm."]:
        c.drawString(14 * mm, yy, t); yy -= 5.5 * mm
    c.showPage(); c.save()


def main():
    import fitz
    R, Y = load()
    pieces, man = build_pieces(R, Y)
    plan = sheet_plan()
    # the board as a web page, and the preview picture (2 screen pixels per reference pixel, 4 per mm)
    board_path = os.path.join(POSTER, "board.html")
    open(board_path, "w", encoding="utf-8").write(board_html(pieces, "fonts"))
    png = os.path.join(POSTER, "board_preview.png")
    chrome([f"--screenshot={png}", "--window-size=1420,1100", "--force-device-scale-factor=2"], board_path)
    # one Letter page per piece
    out = fitz.open()
    with tempfile.TemporaryDirectory() as tmp:
        for i, (key, name, landscape, off, hh, join) in enumerate(plan, 1):
            hp, pp = os.path.join(tmp, f"p{i}.html"), os.path.join(tmp, f"p{i}.pdf")
            open(hp, "w", encoding="utf-8").write(sheet_html(key, name, landscape, off, hh, join, pieces[key], i, len(plan)))
            chrome([f"--print-to-pdf={pp}", "--no-pdf-header-footer"], hp)
            d = fitz.open(pp)
            if len(d) != 1:
                raise SystemExit(f"poster_board: page {i} ({name}) came out as {len(d)} pages")
            r = d[0].rect
            want = (792.0, 612.0) if landscape else (612.0, 792.0)
            if abs(r.width - want[0]) > 1 or abs(r.height - want[1]) > 1:
                raise SystemExit(f"poster_board: page {i} ({name}) is {r.width:.0f} x {r.height:.0f} pt, not US Letter")
            out.insert_pdf(d); d.close()
    a4 = os.path.join(POSTER, "letter_pieces.pdf")
    out.set_metadata({"title": "Measuring What Matters: poster pieces, US Letter, true size", "author": "Cayden Auyang"})
    out.save(a4, deflate=True, garbage=3); out.close()
    layout_pdf(os.path.join(POSTER, "board_layout.pdf"), plan)
    man.update({"results_generated_utc": R.get("generated_utc"), "validation_status": (R.get("text") or {}).get("validation_status"),
                "pages": [{"page": i, "piece": name, "orientation": "landscape" if ls else "portrait"} for i, (k, name, ls, *_r) in enumerate(plan, 1)],
                "pieces_mm": [{"piece": name, "left": x, "top": y, "width": w, "height": h} for k, name, x, y, w, h, _ in PIECES]})
    json.dump(man, open(os.path.join(POSTER, "board_manifest.json"), "w"), indent=1)
    print(f"board poster: {len(plan)} Letter pages | answer: {' / '.join(man['answer']['title'])} | case: {' '.join(man['case']['title'])}")
    print("   answer rule:", man["answer"]["rule"])
    print("   wrote poster/letter_pieces.pdf, poster/board_layout.pdf, poster/board_preview.png")


if __name__ == "__main__":
    main()
