"""Poster kit generator for Measuring What Matters.

One command:  .venv/bin/python src/poster.py

Reads   data/public/results.json, data/public/yearly_changes.csv,
        data/public/validation_summary.json (optional), poster/poster_text.json
Writes  poster/print_me.pdf        16 US Letter pages (11 x 8.5 in, sideways), print order A1..D4
        poster/layout_map.pdf      one page: the 48 x 36 in board with every piece in place
        poster/figures/*.png       300 dpi, every chart at its printed size
        poster/build_manifest.json what was drawn (text, font size, box per page) for src/poster_check.py

Every number and every finding sentence is computed here from the data files at run time.
No result number is typed into this file or into poster_text.json. A missing field prints as
"not available" and is listed on stdout.

Options: --results PATH --changes PATH --validation PATH --text PATH --out DIR --list-placeholders
"""
import argparse, datetime, hashlib, json, math, os, re, sys, traceback

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.textpath import TextPath
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------------------------- page geometry (points)
PAGE_W, PAGE_H = 792.0, 612.0            # US Letter, 11 in wide by 8.5 in tall
MARGIN = 0.4 * 72                        # 0.4 in
X0, X1 = MARGIN, PAGE_W - MARGIN
Y0, Y1 = MARGIN, PAGE_H - MARGIN
CODE_STRIP = 16.0                        # bottom strip kept clear for the grey corner code
BOARD_W_IN, BOARD_H_IN = 48.0, 36.0
ROWS, COLS = "ABCD", 4

# ----------------------------------------------------------------------------- sizes (points)
TITLE_MIN, HEAD_MIN, BODY_MIN, CHART_MIN = 120, 54, 26, 20
HEAD_CHART = 54                          # chart cards: the heading is the chart's title
HEAD_TEXT = 64                           # text cards
BODY = 26
CODE_SIZE = 11
SIDE_TEXT_FRAC, SIDE_TEXT_FRAC_MAX = 0.29, 0.42   # share of the card width given to the text column beside a chart

# ----------------------------------------------------------------------------- decision rules (not results)
STRENGTH_WEAK_BELOW = 0.30               # |slope| below this is called weak (slopes are in SD per SD)
STRENGTH_STRONG_FROM = 0.50              # |slope| from this up is called strong; between the two is moderate
CASE_PAD_MONTHS = 36                     # months shown on each side of the case-study period

# ----------------------------------------------------------------------------- colors (Okabe-Ito)
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "yellow": "#F0E442",
      "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
INK, MUTED, GRID, PALE = "#1A1A1A", "#5F5F5F", "#D9D9D9", "#EEF4FA"
SRC = {"news": {"color": OI["blue"], "marker": "o", "name": "News", "dash": (0, (5, 2))},
       "search": {"color": OI["vermillion"], "marker": "s", "name": "Search", "dash": (0, (2.2, 1.4))}}
SOURCES = ["news", "search"]

CITY_ORDER = ["hk", "nyc", "london"]
CITY = {"hk": "Hong Kong", "nyc": "New York City", "london": "London"}
COMPARED = ["safety", "economy", "housing", "transport", "environment", "health", "education", "cost_of_living"]
SIGNAL_ONLY = ["governance", "culture", "technology", "community"]
CAT = {"safety": "Safety", "economy": "Economy", "housing": "Housing", "transport": "Transport",
       "environment": "Environment", "health": "Health", "education": "Education", "cost_of_living": "Cost of Living",
       "governance": "Governance", "culture": "Culture", "technology": "Technology", "community": "Community",
       "not_civic": "Not a civic problem"}
NA, NA_YET = "not available", "not available yet"

PIECES = [  # code, piece number, short name, kind
    ("A1", 1, "Title banner (left)", "banner"), ("A2", 1, "Title banner (middle)", "banner"),
    ("A3", 1, "Title banner (right)", "banner"), ("A4", 14, "QR code and AI use", "card"),
    ("B1", 2, "The question", "card"), ("B2", 3, "Why it matters", "card"),
    ("B3", 4, "Method diagram", "card"), ("B4", 5, "The data in numbers", "card"),
    ("C1", 6, "Can the labels be trusted", "card"), ("C2", 7, "Result 1 (H1)", "card"),
    ("C3", 8, "Result 2 (H2)", "card"), ("C4", 9, "Result 3 (H3)", "card"),
    ("D1", 10, "Case study", "card"), ("D2", 11, "What surprised me", "card"),
    ("D3", 12, "Limits and changes", "card"), ("D4", 13, "What comes next", "card"),
]

NOTES = {"missing": [], "fallback": [], "warn": [], "errors": []}


def note(kind, msg):
    if msg not in NOTES[kind]:
        NOTES[kind].append(msg)


# ============================================================================= fonts
def setup_fonts():
    """Arial for body, Arial Narrow Bold for headings (more words per line at 54 pt). Falls back to the
    DejaVu fonts that ship with matplotlib, so this never depends on a download."""
    sup = "/System/Library/Fonts/Supplemental/"
    dj = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
    want = {"MWM-Body": [sup + "Arial.ttf", os.path.join(dj, "DejaVuSans.ttf")],
            "MWM-Bold": [sup + "Arial Bold.ttf", os.path.join(dj, "DejaVuSans-Bold.ttf")],
            "MWM-Head": [sup + "Arial Narrow Bold.ttf", sup + "Arial Bold.ttf", os.path.join(dj, "DejaVuSans-Bold.ttf")]}
    used = {}
    for name, paths in want.items():
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(name, p)); used[name] = p; break
                except Exception:
                    continue
        if name not in used:
            used[name] = "builtin"
    builtin = {"MWM-Body": "Helvetica", "MWM-Bold": "Helvetica-Bold", "MWM-Head": "Helvetica-Bold"}
    fonts = {k: (k if used[k] != "builtin" else builtin[k]) for k in used}
    fam = "DejaVu Sans"
    if used["MWM-Body"] != "builtin":
        try:
            for k in ("MWM-Body", "MWM-Bold"):
                if used[k] != "builtin": font_manager.fontManager.addfont(used[k])
            fam = font_manager.FontProperties(fname=used["MWM-Body"]).get_name()
        except Exception:
            fam = "DejaVu Sans"
    plt.rcParams.update({
        "font.family": fam, "font.size": 20, "axes.labelsize": 20, "axes.titlesize": 22,
        "xtick.labelsize": 20, "ytick.labelsize": 20, "axes.linewidth": 1.5, "lines.linewidth": 3.5,
        "xtick.major.width": 1.5, "ytick.major.width": 1.5, "xtick.major.size": 6, "ytick.major.size": 6,
        "axes.edgecolor": MUTED, "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.unicode_minus": False, "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white", "hatch.linewidth": 1.2,
    })
    return fonts, used, fam


FONT = {"body": "Helvetica", "bold": "Helvetica-Bold", "head": "Helvetica-Bold"}
MPL_FAMILY = "DejaVu Sans"


def sw(s, font, size):
    return pdfmetrics.stringWidth(s, font, size)


def asc_desc(font, size):
    try:
        a, d = pdfmetrics.getAscentDescent(font, size)
    except Exception:
        a, d = 0.73 * size, -0.21 * size
    return a, d


# ============================================================================= small helpers
def g(obj, *path):
    """Safe nested lookup. Returns None when any step is missing."""
    for k in path:
        if isinstance(obj, dict):
            obj = obj.get(k)
        elif isinstance(obj, list) and isinstance(k, int) and -len(obj) <= k < len(obj):
            obj = obj[k]
        else:
            return None
        if obj is None:
            return None
    return obj


def isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def f2(x):
    """Two decimals, as the brief asks for slopes and kappas."""
    if not isnum(x): return NA
    s = f"{x:.2f}"
    return "0.00" if s == "-0.00" else s


def pct(x):
    """Whole percent from a share between 0 and 1 (half rounds up)."""
    if not isnum(x): return NA
    return f"{int(math.floor(x * 100 + 0.5))}%"


def fint(x):
    if not isnum(x): return NA
    return f"{int(round(x)):,}"


def p_text(p):
    if not isnum(p): return "p " + NA
    if p < 0.0005: return "p < 0.001"
    return f"p = {p:.3f}"


def ordinal(n):
    if not isnum(n): return NA
    n = int(n)
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def month_name(ym):
    try:
        d = datetime.datetime.strptime(str(ym)[:7], "%Y-%m")
        return d.strftime("%B %Y")
    except Exception:
        return NA


def year_of(ym):
    m = re.match(r"^(\d{4})", str(ym or ""))
    return m.group(1) if m else None


def join_and(items):
    items = [str(i) for i in items]
    if not items: return ""
    if len(items) == 1: return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def city_name(c):
    return CITY.get(c, str(c).replace("_", " ").title())


def cat_name(k):
    return CAT.get(k, str(k).replace("_", " ").title())


def cat_lower(k):
    return cat_name(k).lower()


def count_words(text):
    return sum(1 for t in str(text).split() if re.search(r"[A-Za-z0-9]", t))


def strength_word(est):
    a = abs(est)
    return "weak" if a < STRENGTH_WEAK_BELOW else ("strong" if a >= STRENGTH_STRONG_FROM else "moderate")


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        note("warn", f"could not read {path}: {e}")
        return None


# ============================================================================= the data, and every computed value
class Data:
    def __init__(self, a):
        self.R = load_json(a.results) or {}
        if not self.R: note("missing", f"results file {a.results}")
        self.V = load_json(a.validation)
        self.T = load_json(a.text) or {}
        if not self.T: note("warn", f"text file {a.text} missing or unreadable: built-in wording used")
        try:
            self.YC = pd.read_csv(a.changes)
        except Exception as e:
            self.YC = None; note("missing", f"yearly changes file {a.changes} ({e.__class__.__name__})")
        self.P = {}        # placeholder name -> (text, data path it came from, missing?)
        self.lead = None
        self.build()

    # ---- placeholder plumbing
    def put(self, name, text, path, missing=False):
        self.P[name] = (str(text), path, bool(missing))

    def put_num(self, name, value, path, fmt=f2, zero_is_missing=False):
        if isnum(value) and not (zero_is_missing and value == 0):
            self.put(name, fmt(value), path)
        else:
            self.put(name, NA, path, True)

    def tx(self, *path, default=""):
        v = g(self.T, *path)
        return default if v is None else v

    def fill(self, template, extra=None, quiet=False):
        """Fill {placeholders}. Missing data prints as 'not available'. An unknown name stays in braces.
        After a call, self.fill_missing says whether any value was missing. quiet=True records nothing."""
        extra = extra or {}
        self.fill_missing = False

        def rep(m):
            k = m.group(1)
            if k in extra:
                return str(extra[k])
            if k in self.P:
                text, path, missing = self.P[k]
                if missing:
                    fb = g(self.T, "fallbacks", k)
                    if isinstance(fb, str) and fb.strip():
                        if not quiet: note("fallback", f"{{{k}}}: no value in {path}; used the plan value from poster_text.json ('{fb}')")
                        return fb
                    self.fill_missing = True
                    if not quiet: note("missing", f"{{{k}}} <- {path}")
                return text
            self.fill_missing = True
            if not quiet: note("warn", f"unknown placeholder {{{k}}} left in the text")
            return m.group(0)

        return re.sub(r"\{([A-Za-z0-9_]+)\}", rep, str(template))

    def src_ok(self, s):
        return isnum(g(self.R, "main", s, "h1", "est"))

    # ---- everything computed from the files
    def build(self):
        R, put, put_num = self.R, self.put, self.put_num
        c = g(R, "counts") or {}
        cl = c.get("city_list") or R.get("cities") or []
        put_num("n_cities", c.get("cities"), "counts.cities", fint)
        put("city_names", join_and([city_name(x) for x in cl]) if cl else NA, "counts.city_list", not cl)
        put_num("outlets_main", c.get("outlets_main_panel_total"), "counts.outlets_main_panel_total", fint, True)
        put_num("outlets_listed", c.get("outlets_listed_total"), "counts.outlets_listed_total", fint, True)
        put_num("articles_labeled_main", c.get("articles_labeled_main_panel_total"), "counts.articles_labeled_main_panel_total", fint, True)
        put_num("articles_labeled_all", c.get("articles_labeled_all"), "counts.articles_labeled_all", fint, True)
        put_num("articles_after_city_filter", c.get("articles_after_city_filter"), "counts.articles_after_city_filter", fint, True)
        put_num("official_series_main", c.get("official_series_main"), "counts.official_series_main", fint, True)
        put_num("official_series_total", c.get("official_series_total"), "counts.official_series_total", fint, True)
        put_num("official_values", c.get("official_values"), "counts.official_values", fint, True)
        put_num("search_months", c.get("search_months"), "counts.search_months", fint, True)
        put_num("news_months", c.get("news_months"), "counts.news_months", fint, True)
        put_num("search_term_sets", c.get("search_term_sets"), "counts.search_term_sets", fint, True)
        for s in SOURCES:
            a, b = year_of(c.get(f"{s}_first_month")), year_of(c.get(f"{s}_last_month"))
            put(f"{s}_years", f"{a} to {b}" if a and b else NA, f"counts.{s}_first_month, counts.{s}_last_month", not (a and b))
        n_dl = c.get("search_downloads_per_request")
        put("search_downloads", (f"{int(n_dl)} download" + ("" if int(n_dl) == 1 else "s")) if isnum(n_dl) else NA,
            "counts.search_downloads_per_request", not isnum(n_dl))
        put_num("bootstrap_reps", R.get("bootstrap_reps"), "bootstrap_reps", fint)

        # which source leads: news when it has a result, search beside it
        self.lead = "news" if self.src_ok("news") else ("search" if self.src_ok("search") else None)
        other = {"news": "search", "search": "news"}.get(self.lead)
        put("lead_source", self.lead or NA, "main.news.h1.est / main.search.h1.est", self.lead is None)
        put("Lead_source", (self.lead or NA).capitalize() if self.lead else NA, "main.news.h1.est / main.search.h1.est", self.lead is None)
        put("other_source", other or NA, "main", other is None)
        put("Other_source", other.capitalize() if other else NA, "main", other is None)

        for s in SOURCES:
            h1, h2 = g(R, "main", s, "h1") or {}, g(R, "main", s, "h2") or {}
            for k in ("est", "ci_low", "ci_high"):
                put_num(f"h1_{s}_{k}", h1.get(k), f"main.{s}.h1.{k}")
            put(f"h1_{s}_p", p_text(h1.get("p_boot")), f"main.{s}.h1.p_boot", not isnum(h1.get("p_boot")))
            put_num(f"h1_{s}_pairs", h1.get("n_pairs"), f"main.{s}.h1.n_pairs", fint)
            put_num(f"h1_{s}_n_obs", h1.get("n_obs"), f"main.{s}.h1.n_obs", fint)
            put_num(f"h1_{s}_years", h1.get("n_eff_years"), f"main.{s}.h1.n_eff_years", fint)
            for part in ("worse", "better", "diff"):
                for k in ("est", "ci_low", "ci_high"):
                    put_num(f"h2_{s}_{part}_{k}", g(h2, part, k), f"main.{s}.h2.{part}.{k}")
            put(f"h2_{s}_diff_p", p_text(g(h2, "diff", "p_boot")), f"main.{s}.h2.diff.p_boot", not isnum(g(h2, "diff", "p_boot")))
            sr = g(R, "h3", "safety_rank", s) or {}
            put_num(f"h3_{s}_cities_top", sr.get("cities_where_safety_is_largest"), f"h3.safety_rank.{s}.cities_where_safety_is_largest", fint)

        # lead-source facts for the candidate sentences and the limits card
        L = self.lead
        bc = {k: v for k, v in (g(R, "h1_by_category", L) or {}).items() if isnum(g(v, "est"))} if L else {}
        if bc:
            top = max(bc, key=lambda k: bc[k]["est"]); bot = min(bc, key=lambda k: bc[k]["est"])
            pth = f"h1_by_category.{L}"
            put("h1_top_category", cat_name(top), pth); put("h1_top_est", f2(bc[top]["est"]), pth)
            put("h1_bottom_category", cat_name(bot), pth); put("h1_bottom_est", f2(bc[bot]["est"]), pth)
            put("h1_n_categories", str(len(bc)), pth)
        else:
            for k in ("h1_top_category", "h1_top_est", "h1_bottom_category", "h1_bottom_est", "h1_n_categories"):
                put(k, NA, f"h1_by_category.{L or 'news'}", True)
        clear = {k: v for k, v in bc.items() if isnum(v.get("ci_low")) and v["ci_low"] > 0}   # interval above zero
        pth = f"h1_by_category.{L or 'news'}"
        put("h1_n_clear", str(len(clear)) if bc else NA, pth, not bc)
        put("h1_clear_list", join_and([cat_name(k) for k in sorted(clear, key=lambda k: -clear[k]["est"])]) if clear else NA, pth, not clear)
        if clear:
            tc = max(clear, key=lambda k: clear[k]["est"])
            put("h1_top_clear_category", cat_name(tc), pth); put("h1_top_clear_est", f2(clear[tc]["est"]), pth)
        else:
            put("h1_top_clear_category", NA, pth, True); put("h1_top_clear_est", NA, pth, True)
        both = sorted([(g(R, "main", s, "h1", "est"), s) for s in SOURCES if self.src_ok(s)], reverse=True)
        pth = "main.news.h1.est, main.search.h1.est"
        if len(both) == 2 and both[0][0] != both[1][0]:
            put("h1_higher_source", both[0][1], pth); put("H1_higher_source", both[0][1].capitalize(), pth); put("h1_higher_est", f2(both[0][0]), pth)
            put("h1_lower_source", both[1][1], pth); put("h1_lower_est", f2(both[1][0]), pth)
        else:
            for k in ("h1_higher_source", "H1_higher_source", "h1_higher_est", "h1_lower_source", "h1_lower_est"):
                put(k, NA, pth, True)
        cells = []
        for city, d in (g(R, "h3", "opposite_share", L) or {}).items() if L else []:
            for cat, v in (d or {}).items():
                if isnum(g(v, "share")): cells.append((v["share"], city, cat))
        pth = f"h3.opposite_share.{L or 'news'}"
        if cells:
            lo, hi = min(cells), max(cells)
            put("h3_min_share", pct(lo[0]), pth); put("h3_min_pair", f"{city_name(lo[1])} {cat_name(lo[2])}", pth)
            put("h3_max_share", pct(hi[0]), pth); put("h3_max_pair", f"{city_name(hi[1])} {cat_name(hi[2])}", pth)
            put("h3_n_pairs", str(len(cells)), pth)
        else:
            for k in ("h3_min_share", "h3_min_pair", "h3_max_share", "h3_max_pair", "h3_n_pairs"):
                put(k, NA, pth, True)
        pl = [p for p in (R.get("pair_level") or []) if isinstance(p, dict) and p.get("source") == L] if L else []
        put("lead_pairs_planned", str(len(pl)) if pl else NA, "pair_level", not pl)
        put("lead_pairs_tested", str(sum(1 for p in pl if not p.get("excluded"))) if pl else NA, "pair_level", not pl)
        runs = [r for r in (g(R, "h3", "runs") or []) if isinstance(r, dict) and (not L or r.get("source") == L)]
        put("h3_n_runs", str(len(runs)) if g(R, "h3", "runs") is not None else NA, "h3.runs", g(R, "h3", "runs") is None)

        # case study
        cs = R.get("case_study") or {}
        ok = bool(cs)
        put("case_city", city_name(cs.get("city")) if cs.get("city") else NA, "case_study.city", not cs.get("city"))
        put("case_category", cat_lower(cs.get("category")) if cs.get("category") else NA, "case_study.category", not cs.get("category"))
        put_num("case_months", cs.get("months"), "case_study.months", fint)
        put("case_start", month_name(cs.get("start")), "case_study.start", month_name(cs.get("start")) == NA)
        put("case_end", month_name(cs.get("end")), "case_study.end", month_name(cs.get("end")) == NA)
        put("case_source", cs.get("source") or NA, "case_study.source", not cs.get("source"))
        ov = {"worsening": "worsened", "improving": "improved"}.get(cs.get("official_direction"))
        av = {"rising": "rose", "falling": "fell"}.get(cs.get("attention_direction"))
        put("case_official_verb", ov or NA, "case_study.official_direction", not ov)
        put("case_attention_verb", av or NA, "case_study.attention_direction", not av)
        put("case_cause", cs.get("proposed_cause") or NA, "case_study.proposed_cause", not cs.get("proposed_cause"))
        ind = None
        for p in (R.get("pair_level") or []):
            if isinstance(p, dict) and ok and (p.get("city"), p.get("category"), p.get("source")) == (cs.get("city"), cs.get("category"), cs.get("source")):
                ind = p.get("indicator")
        put("case_indicator", ind or NA, "pair_level[].indicator", not ind)

        # validation (file may not exist yet)
        V = self.V or {}
        vp = "validation_summary.json"
        put_num("threshold", V.get("threshold"), f"{vp}: threshold")
        put("val_status", V.get("status") or NA, f"{vp}: status", not V.get("status"))
        cities = V.get("cities") if isinstance(V.get("cities"), dict) else {}
        n_tot = n_pass = 0; overall = []; dropped = []
        for city in [x for x in CITY_ORDER if x in cities] + [x for x in cities if x not in CITY_ORDER]:
            cv = cities.get(city) or {}
            for lab, e in (cv.get("categories") or {}).items():
                if not isinstance(e, dict) or lab == "not_civic": continue      # the 0.61 rule covers the twelve categories
                ps = (lab in cv["kept"]) if isinstance(cv.get("kept"), list) and isinstance(cv.get("dropped"), list) else e.get("pass")
                if ps is None and isnum(e.get("kappa")) and isnum(V.get("threshold")): ps = e["kappa"] >= V["threshold"]
                if ps is None: continue
                n_tot += 1; n_pass += 1 if ps else 0
            if isnum(cv.get("overall_kappa")): overall.append(f"{city_name(city)} {f2(cv['overall_kappa'])}")
            put_num(f"val_kappa_{city}", cv.get("overall_kappa"), f"{vp}: cities.{city}.overall_kappa")
            put_num(f"val_n_items_{city}", cv.get("n_items"), f"{vp}: cities.{city}.n_items", fint)
            put(f"val_not_about_city_{city}", pct(cv.get("not_about_city_share")), f"{vp}: cities.{city}.not_about_city_share", not isnum(cv.get("not_about_city_share")))
            if cv.get("dropped"):
                dropped.append(f"{city_name(city)}: {', '.join(cat_name(x) for x in cv['dropped'])}.")
        put("val_n_total", str(n_tot) if n_tot else NA, f"{vp}: cities.*.categories", not n_tot)
        put("val_n_pass", str(n_pass) if n_tot else NA, f"{vp}: cities.*.categories.*.pass", not n_tot)
        put("val_overall_by_city", ", ".join(overall) if overall else NA, f"{vp}: cities.*.overall_kappa", not overall)
        put("val_dropped_list", " ".join(dropped) if dropped else "none", f"{vp}: cities.*.dropped")
        self.val_dropped = dropped
        for k in ("third_pass", "relabel", "first_coder_vs_larger_model"):
            e = g(V, "consistency", k) or {}
            kap = e.get("kappa_vs_second") if k == "third_pass" else e.get("kappa")
            put_num(f"val_{k}_kappa", kap, f"{vp}: consistency.{k}")
            put_num(f"val_{k}_n", e.get("n"), f"{vp}: consistency.{k}.n", fint)

    # ---- the finding sentences (decision rules are here, wording forms are in poster_text.json)
    def other_line(self, key, s, default_ok, default_missing, extra):
        if self.src_ok(s):
            return self.fill(self.tx(key, "other_available", default=default_ok), extra)
        return self.fill(self.tx(key, "other_missing", default=default_missing), extra)

    def h1_text(self):
        L = self.lead
        if not L:
            return self.fill(self.tx("C2_h1", "title_missing", default="Result 1 (H1): not available yet")), \
                   self.fill(self.tx("C2_h1", "detail_missing", default="News: not available yet. Search: not available yet."))
        h = g(self.R, "main", L, "h1") or {}
        est, lo, hi = h.get("est"), h.get("ci_low"), h.get("ci_high")
        ex = {"source": L, "Source": L.capitalize(), "est": f2(est), "abs_est": f2(abs(est)) if isnum(est) else NA,
              "ci_low": f2(lo), "ci_high": f2(hi), "p_text": p_text(h.get("p_boot")), "n_pairs": fint(h.get("n_pairs")),
              "strength": strength_word(est) if isnum(est) else NA}
        for k, v in (("ci_low", lo), ("ci_high", hi), ("p_boot", h.get("p_boot")), ("n_pairs", h.get("n_pairs"))):
            if not isnum(v): note("missing", f"main.{L}.h1.{k}")
        if isnum(lo) and isnum(hi) and est > 0 and lo > 0:          # H1 supported: positive and interval excludes zero
            title = self.tx("C2_h1", "title_supported", default="{Source} attention rose {est} SD per 1 SD of worsening: a {strength} link")
        elif isnum(lo) and isnum(hi) and est < 0 and hi < 0:        # clear link, wrong direction
            title = self.tx("C2_h1", "title_negative", default="H1 failed for {source}: attention fell {abs_est} SD per 1 SD of worsening")
        elif isnum(lo) and isnum(hi):                               # interval includes zero
            title = self.tx("C2_h1", "title_unclear", default="H1 failed for {source}: no clear link (slope {est}, interval includes zero)")
        else:
            title = self.tx("C2_h1", "title_no_interval", default="H1 for {source}: slope {est}, interval not available")
        detail = self.tx("C2_h1", "detail", default="95% interval {ci_low} to {ci_high}, bootstrap {p_text}, {n_pairs} city and category pairs.")
        o = "search" if L == "news" else "news"
        ho = g(self.R, "main", o, "h1") or {}
        exo = {"Other": o.capitalize(), "other": o, "other_est": f2(ho.get("est")), "other_ci_low": f2(ho.get("ci_low")), "other_ci_high": f2(ho.get("ci_high"))}
        tail = self.other_line("C2_h1", o, "{Other}: slope {other_est} ({other_ci_low} to {other_ci_high}).", "{Other}: not available yet.", exo)
        return self.fill(title, ex), self.fill(detail, ex) + " " + tail

    def h2_text(self):
        L = self.lead
        h = (g(self.R, "main", L, "h2") or {}) if L else {}
        w, b = g(h, "worse", "est"), g(h, "better", "est")
        d, dlo, dhi = g(h, "diff", "est"), g(h, "diff", "ci_low"), g(h, "diff", "ci_high")
        if not L or not (isnum(w) and isnum(b)):
            return self.fill(self.tx("C3_h2", "title_missing", default="Result 2 (H2): not available yet")), \
                   self.fill(self.tx("C3_h2", "detail_missing", default="News: not available yet. Search: not available yet."))
        ex = {"source": L, "Source": L.capitalize(), "worse": f2(w), "better": f2(b), "diff": f2(d), "diff_low": f2(dlo),
              "diff_high": f2(dhi), "p_text": p_text(g(h, "diff", "p_boot"))}
        for k, v in (("diff.est", d), ("diff.ci_low", dlo), ("diff.ci_high", dhi), ("diff.p_boot", g(h, "diff", "p_boot"))):
            if not isnum(v): note("missing", f"main.{L}.h2.{k}")
        if isnum(dlo) and isnum(dhi) and dlo > 0:                   # H2 supported: the whole interval of the difference is above zero
            title = self.tx("C3_h2", "title_supported", default="{Source} attention reacted more to worsening ({worse}) than improving ({better})")
            detail = self.tx("C3_h2", "detail_supported", default="Difference {diff} SD, 95% interval {diff_low} to {diff_high}, bootstrap {p_text}.")
        elif isnum(dlo) and isnum(dhi) and dhi < 0:                 # clear difference, wrong direction
            title = self.tx("C3_h2", "title_reverse", default="H2 failed for {source}: stronger reaction to improving ({better}) than worsening ({worse})")
            detail = self.tx("C3_h2", "detail_reverse", default="Difference {diff} SD, 95% interval {diff_low} to {diff_high}, bootstrap {p_text}.")
        elif isnum(dlo) and isnum(dhi):
            title = self.tx("C3_h2", "title_not_supported", default="H2 not supported for {source}: worsening {worse}, improving {better}, no clear gap")
            detail = self.tx("C3_h2", "detail_not_supported", default="Difference {diff} SD, 95% interval {diff_low} to {diff_high}, which includes zero (bootstrap {p_text}).")
        else:
            title = self.tx("C3_h2", "title_no_interval", default="H2 for {source}: worsening {worse}, improving {better}, interval not available")
            detail = self.tx("C3_h2", "detail_supported", default="Difference {diff} SD, 95% interval {diff_low} to {diff_high}, bootstrap {p_text}.")
        o = "search" if L == "news" else "news"
        ho = g(self.R, "main", o, "h2") or {}
        exo = {"Other": o.capitalize(), "other": o, "other_worse": f2(g(ho, "worse", "est")), "other_better": f2(g(ho, "better", "est")),
               "other_diff": f2(g(ho, "diff", "est")), "other_diff_low": f2(g(ho, "diff", "ci_low")), "other_diff_high": f2(g(ho, "diff", "ci_high"))}
        tail = self.other_line("C3_h2", o, "{Other}: worsening {other_worse}, improving {other_better}, difference {other_diff} ({other_diff_low} to {other_diff_high}).",
                               "{Other}: not available yet.", exo)
        return self.fill(title, ex), self.fill(detail, ex) + " " + tail

    def h3_rank_bits(self, s):
        """(ranked cities as (city, rank, of, share), untestable cities, supported?, n cities where Safety is largest)."""
        sr = g(self.R, "h3", "safety_rank", s) or {}
        by = sr.get("by_city") or {}
        ranked, untest = [], []
        for city in [x for x in CITY_ORDER if x in by] + [x for x in by if x not in CITY_ORDER]:
            e = by.get(city) or {}
            if isnum(e.get("safety_rank")):
                ranked.append((city, int(e["safety_rank"]), e.get("of"), e.get("safety_share")))
            else:
                untest.append(city)
        return ranked, untest, sr.get("h3_supported"), sr.get("cities_where_safety_is_largest"), len(by)

    def h3_has(self, s):
        return any(isnum(g(v, "share")) for d in (g(self.R, "h3", "opposite_share", s) or {}).values() for v in (d or {}).values())

    def h3_text(self, fits=None):
        L = self.lead if (self.lead and self.h3_has(self.lead)) else next((s for s in SOURCES if self.h3_has(s)), None)
        if not L:
            return None, self.fill(self.tx("C4_h3", "title_missing", default="Result 3 (H3): not available yet")), \
                   self.fill(self.tx("C4_h3", "detail_missing", default="News: not available yet. Search: not available yet."))
        ranked, untest, supported, n_top, n_cities = self.h3_rank_bits(L)
        ex = {"source": L, "Source": L.capitalize(), "n_top": fint(n_top), "n_cities": str(n_cities),
              "rank_list": join_and([f"{ordinal(r)} in {city_name(c)}" for c, r, of, sh in ranked]),
              "rank_list_of": join_and([f"{ordinal(r)} of {fint(of)} in {city_name(c)}" for c, r, of, sh in ranked])}
        if supported is None: note("missing", f"h3.safety_rank.{L}.h3_supported")
        if not ranked:
            forms = [self.tx("C4_h3", "title_untestable", default="H3 could not be tested for {source}: no usable Safety pair")]
        elif supported:
            forms = [self.tx("C4_h3", "title_supported", default="Safety had the largest gap in {n_top} of {n_cities} cities ({source})")]
        else:
            forms = self.tx("C4_h3", "title_failed_forms", default=["H3 failed for {source}: Safety ranked {rank_list}", "H3 failed: Safety ranked {rank_list}"])
            if isinstance(forms, str): forms = [forms]
        title = None
        for f in forms:                                             # first form that fits in three heading lines
            t = self.fill(f, ex)
            if fits is None or fits(t):
                title = t; break
        title = title or self.fill(forms[-1], ex)
        bits = [self.fill(self.tx("C4_h3", "detail", default="Each number is the share of periods when attention and official data moved in opposite directions."), ex)]
        if untest:
            bits.append(self.fill(self.tx("C4_h3", "detail_untestable", default="Safety could not be tested in {cities}."),
                                  {**ex, "cities": join_and([city_name(c) for c in untest])}))
        o = "search" if L == "news" else "news"
        if self.h3_has(o):
            ro, uo, so, no, nco = self.h3_rank_bits(o)
            exo = {"Other": o.capitalize(), "other": o, "other_rank_list_of": join_and([f"{ordinal(r)} of {fint(of)} in {city_name(c)}" for c, r, of, sh in ro]) or NA}
            bits.append(self.fill(self.tx("C4_h3", "other_available", default="{Other}: Safety ranked {other_rank_list_of}."), exo))
        else:
            bits.append(self.fill(self.tx("C4_h3", "other_missing", default="{Other}: not available yet."), {"Other": o.capitalize(), "other": o}))
        return L, title, " ".join(bits)

    def case_text(self):
        cs = self.R.get("case_study") or {}
        if not cs or not cs.get("city"):
            return self.fill(self.tx("D1_case", "title_missing", default="Case study: not available yet")), \
                   self.fill(self.tx("D1_case", "detail_missing", default="No period of opposite movement is listed in the results file yet."))
        title = self.tx("D1_case", "title", default="For {case_months} months, {case_city} {case_category} {case_official_verb} while {case_source} attention {case_attention_verb}")
        detail = self.tx("D1_case", "detail", default="{case_start} to {case_end}. Proposed cause: {case_cause}. Cause proposed by AI, for Cayden to confirm.")
        return self.fill(title), self.fill(detail)

    def val_text(self):
        V = self.V
        if not V or not isinstance(V.get("cities"), dict) or not V["cities"]:
            return None
        n_tot, n_pass = self.P["val_n_total"][0], self.P["val_n_pass"][0]
        if n_tot != NA and n_tot == n_pass:
            title = self.tx("C1_validation", "title_all_pass", default="All {val_n_total} category checks reached kappa {threshold}")
        else:
            title = self.tx("C1_validation", "title_some_fail", default="{val_n_pass} of {val_n_total} category checks reached kappa {threshold}")
        dropped = self.tx("C1_validation", "dropped_some", default="Dropped. {val_dropped_list}") if self.val_dropped \
            else self.tx("C1_validation", "dropped_none", default="No category was dropped.")
        detail = self.tx("C1_validation", "detail", default="{dropped_sentence} Two AI coders agreed this much. No human checked the labels.")
        detail = self.fill(detail, {"dropped_sentence": self.fill(dropped)})
        if str(V.get("status", "")).lower() != "final":
            tag = self.tx("C1_validation", "provisional_tag", default="PROVISIONAL.")
            detail = f"**{tag}** " + detail
            if str(V.get("status", "")).lower() != "provisional":
                note("warn", f"validation status is '{V.get('status')}', shown as provisional")
        return self.fill(title), detail


# ============================================================================= figures (matplotlib, 300 dpi, drawn at print size)
def mpl_width(s, size, bold=False):
    fp = font_manager.FontProperties(family=MPL_FAMILY, weight="bold" if bold else "normal", size=size)
    try:
        return TextPath((0, 0), s, prop=fp).get_extents().width
    except Exception:
        return len(s) * size * 0.52


def mpl_wrap(text, size, max_w, bold=False):
    lines, cur = [], ""
    for w in str(text).split():
        t = (cur + " " + w).strip()
        if cur and mpl_width(t, size, bold) > max_w:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur: lines.append(cur)
    return lines or [""]


def collect_texts(fig):
    """Every text the figure shows, with its size, and any that runs off the figure."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    seen, out, over = set(), [], []

    def add(t, check=True):
        s = t.get_text().strip()
        if not s or not t.get_visible() or id(t) in seen: return
        seen.add(id(t))
        out.append({"text": " ".join(s.split()), "size": round(float(t.get_fontsize()), 1)})
        if check:
            bb = t.get_window_extent(r)
            if bb.x0 < -2 or bb.y0 < -2 or bb.x1 > W + 2 or bb.y1 > H + 2: over.append(" ".join(s.split()))

    for t in fig.texts: add(t)
    for ax in fig.axes:
        if not ax.get_visible(): continue
        for t in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None), ax.xaxis.label, ax.yaxis.label):
            if t is not None: add(t)
        for t in ax.texts: add(t)
        for axis, lim in ((ax.xaxis, sorted(ax.get_xlim())), (ax.yaxis, sorted(ax.get_ylim()))):
            if not axis.get_visible(): continue
            span = (lim[1] - lim[0]) or 1.0
            for tick in axis.get_major_ticks():
                if lim[0] - 1e-9 * span <= tick.get_loc() <= lim[1] + 1e-9 * span:
                    for lab in (tick.label1, tick.label2): add(lab)
    return out, over


def finish(fig, path, role="chart_text"):
    texts, over = collect_texts(fig)
    W, H = fig.canvas.get_width_height()
    img = Image.frombuffer("RGBA", (W, H), fig.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).convert("RGB")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, dpi=(300, 300))
    plt.close(fig)
    if over: note("warn", f"{os.path.basename(path)}: text runs off the figure: {over}")
    return {"file": path, "px": [W, H], "texts": texts, "overflow": over, "text_role": role}


def new_fig(w, h, **kw):
    return plt.figure(figsize=(w, h), dpi=300, layout="constrained", **kw)


def clean_axes(ax, grid="x"):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_axisbelow(True)
    if grid: ax.grid(axis=grid, color=GRID, lw=1.2)


def caption(fig, text, size=20):
    """A caption under the plot, wrapped to the figure's width."""
    w_pt = fig.get_figwidth() * 72 - 12
    lines = mpl_wrap(text, size, w_pt)
    fig.supxlabel("\n".join(lines), fontsize=size, color=INK, linespacing=1.15)


def pad_limits(lo, hi, frac=0.06, right_extra=0.0):
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    span = (hi - lo) or 1.0
    return lo - frac * span, hi + (frac + right_extra) * span


def fig_h1(D, w, h, path):
    """Forest plot: pooled slope and slope by category, one marker shape and color per source."""
    R = D.R
    srcs = [s for s in SOURCES if D.src_ok(s) or any(isnum(g(v, "est")) for v in (g(R, "h1_by_category", s) or {}).values())]
    lead = D.lead or (srcs[0] if srcs else None)

    def cat_est(s, k):
        return g(R, "h1_by_category", s, k) or {}

    def sort_key(k):
        le = cat_est(lead, k).get("est")
        others = [cat_est(s, k).get("est") for s in srcs if isnum(cat_est(s, k).get("est"))]
        return (0 if isnum(le) else (1 if others else 2), -(le if isnum(le) else (max(others) if others else 0)))

    order = sorted(COMPARED, key=sort_key)
    two = len(srcs) > 1
    rows = [("pooled", "All pairs pooled", 0.0)] + [(k, cat_name(k), (2.05 if two else 1.6) + i) for i, k in enumerate(order)]
    fig = new_fig(w, h); ax = fig.add_subplot()
    xs = [0.0]
    pooled_right = max([v for s in srcs for v in ((g(R, "main", s, "h1") or {}).get("ci_high"), (g(R, "main", s, "h1") or {}).get("est")) if isnum(v)] or [0.0])
    for key, label, y in rows:
        any_est = False
        big = key == "pooled"
        for s in srcs:
            e = (g(R, "main", s, "h1") or {}) if big else cat_est(s, key)
            est, lo, hi = e.get("est"), e.get("ci_low"), e.get("ci_high")
            if not isnum(est): continue
            any_est = True
            yy = y + (0.0 if not two else (-1 if s == "news" else 1) * (0.36 if big else 0.2))
            if isnum(lo) and isnum(hi):
                ax.plot([lo, hi], [yy, yy], color=SRC[s]["color"], lw=6 if big else 3.5, solid_capstyle="butt", zorder=3)
                xs += [lo, hi]
            ax.plot([est], [yy], marker=SRC[s]["marker"], ms=19 if big else 13, color=SRC[s]["color"], mec="white", mew=2, zorder=4, ls="none")
            xs.append(est)
            if big:
                ax.annotate(f"{SRC[s]['name']} {f2(est)}", (pooled_right, yy), xytext=(12, 0), textcoords="offset points",
                            va="center", ha="left", fontsize=22, fontweight="bold", color=INK, zorder=5)
        if not any_est:
            ax.text(0, y, "  not tested" if not big else "  " + NA_YET, va="center", ha="left", fontsize=20, color=MUTED, style="italic")
    lo, hi = pad_limits(min(xs), max(xs), 0.05, 0.0)
    ax.set_xlim(lo, hi)
    ax.set_ylim(rows[-1][2] + 0.7, -0.95 if two else -0.75)
    ax.axvline(0, color=INK, lw=2.2, zorder=2)
    ax.axhline((rows[0][2] + rows[1][2]) / 2 + (0.08 if two else 0), color=GRID, lw=1.5)
    ax.set_yticks([r[2] for r in rows]); ax.set_yticklabels([r[1] for r in rows])
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.tick_params(axis="y", length=0, pad=8)
    clean_axes(ax); ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(6))
    # keep the pooled labels inside the plot: widen the right side until they fit
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    for _ in range(4):
        ax_r = ax.get_window_extent(r).x1
        over = max([t.get_window_extent(r).x1 - ax_r for t in ax.texts] + [0])
        if over <= 0: break
        x0, x1 = ax.get_xlim(); px = ax.get_window_extent(r).width
        ax.set_xlim(x0, x1 + (x1 - x0) * (over + 8) / max(px - over - 8, 1)); fig.canvas.draw()
    caption(fig, "SD of attention per 1 SD of official worsening (bars: 95% intervals)")
    return finish(fig, path)


def fig_h2(D, w, h, path):
    """Two slopes per source: when the problem got worse (filled) and when it got better (hollow)."""
    R = D.R
    fig = new_fig(w, h); ax = fig.add_subplot()
    rows, xs, y = [], [0.0], 0.0
    for s in SOURCES:
        h2 = g(R, "main", s, "h2") or {}
        for part, word in (("worse", "worsening"), ("better", "improving")):
            e = h2.get(part) or {}
            est, lo, hi = e.get("est"), e.get("ci_low"), e.get("ci_high")
            rows.append((y, f"{SRC[s]['name']},\n{word}"))
            if isnum(est):
                if isnum(lo) and isnum(hi):
                    ax.plot([lo, hi], [y, y], color=SRC[s]["color"], lw=5, solid_capstyle="butt", zorder=3); xs += [lo, hi]
                ax.plot([est], [y], marker=SRC[s]["marker"], ms=20, ls="none", zorder=4, color=SRC[s]["color"],
                        mfc=SRC[s]["color"] if part == "worse" else "white", mec=SRC[s]["color"], mew=4)
                ax.annotate(f2(est), (max(hi, est) if isnum(hi) else est, y), xytext=(16, 0), textcoords="offset points", va="center", ha="left",
                            fontsize=22, fontweight="bold", color=INK)
                xs.append(est)
            else:
                ax.text(0, y, "  " + NA_YET, va="center", ha="left", fontsize=20, color=MUTED, style="italic")
            y += 1.0
        y += 0.45
    lo, hi = pad_limits(min(xs), max(xs), 0.06, 0.16)
    ax.set_xlim(lo, hi); ax.set_ylim(rows[-1][0] + 0.6, -0.6)
    ax.axvline(0, color=INK, lw=2.2, zorder=2)
    ax.set_yticks([r[0] for r in rows]); ax.set_yticklabels([r[1] for r in rows], linespacing=1.0)
    ax.tick_params(axis="y", length=0, pad=8)
    clean_axes(ax); ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(6))
    caption(fig, "SD of attention per 1 SD of official change. Bars: 95% intervals. Filled: problem got worse. Hollow: got better.")
    return finish(fig, path)


def fig_h3(D, w, h, path):
    """Heatmap of the share of periods moving in opposite directions, numbers in the cells, Safety outlined."""
    R = D.R
    srcs = [s for s in SOURCES if D.h3_has(s)]
    if not srcs: return None
    cities = [c for c in CITY_ORDER if any(c in (g(R, "h3", "opposite_share", s) or {}) for s in srcs)] or CITY_ORDER
    vals = [v["share"] for s in srcs for d in (g(R, "h3", "opposite_share", s) or {}).values() for v in (d or {}).values() if isnum(g(v, "share"))]
    vmin, vmax = math.floor(min(vals) * 20) / 20, math.ceil(max(vals) * 20) / 20
    if vmax - vmin < 0.1: vmin, vmax = vmin - 0.05, vmax + 0.05
    cmap = LinearSegmentedColormap.from_list("one_hue", ["#F2F7FB", "#9CC4E0", OI["blue"], "#04466F"])
    fig = new_fig(w, h)
    axes = fig.subplots(1, len(srcs), sharey=True, squeeze=False)[0]
    label_w = max(mpl_width(cat_name(k), 20, k == "safety") for k in COMPARED) + 16
    cell_w_pt = (w * 72 - label_w - 14 * len(srcs)) / (len(srcs) * len(cities))
    for ax, s in zip(axes, srcs):
        tab = g(R, "h3", "opposite_share", s) or {}
        best = {}
        for j, c in enumerate(cities):
            col = {k: g(tab, c, k, "share") for k in COMPARED if isnum(g(tab, c, k, "share"))}
            if len(col) >= 2: best[j] = max(col, key=lambda k: col[k])
        for i, k in enumerate(COMPARED):
            for j, c in enumerate(cities):
                v = g(tab, c, k, "share")
                if isnum(v):
                    frac = min(1.0, max(0.0, (v - vmin) / (vmax - vmin)))
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=cmap(frac), edgecolor="white", lw=2.5))
                    ax.text(j, i, pct(v), ha="center", va="center", fontsize=23, fontweight="bold", color="white" if frac > 0.55 else INK)
                else:
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#F1F1F1", edgecolor="#B5B5B5", lw=0, hatch="///"))
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="none", edgecolor="white", lw=2.5))
                    ax.text(j, i, "n/a", ha="center", va="center", fontsize=20, color=MUTED,
                            bbox=dict(boxstyle="round,pad=0.12", fc="#F1F1F1", ec="none"))
        for j, k in best.items():
            i = COMPARED.index(k)
            ax.add_patch(Rectangle((j - 0.455, i - 0.43), 0.91, 0.86, facecolor="none", edgecolor=OI["black"], lw=4, zorder=5))
        i = COMPARED.index("safety")
        ax.add_patch(Rectangle((-0.5, i - 0.5), len(cities), 1, facecolor="none", edgecolor=OI["orange"], lw=6, zorder=6, clip_on=False))
        ax.set_xlim(-0.5, len(cities) - 0.5); ax.set_ylim(len(COMPARED) - 0.5, -0.5)
        names = ["\n".join(mpl_wrap(city_name(c), 20, max(cell_w_pt - 6, 30))) for c in cities]
        ax.set_xticks(range(len(cities))); ax.set_xticklabels(names, linespacing=0.95)
        ax.xaxis.tick_top(); ax.tick_params(axis="both", length=0, pad=6)
        ax.set_yticks(range(len(COMPARED))); ax.set_yticklabels([cat_name(k) for k in COMPARED])
        for sp in ax.spines.values(): sp.set_visible(False)
        if len(srcs) > 1:
            ax.set_xlabel(SRC[s]["name"], fontsize=24, fontweight="bold", labelpad=8)
    for lab in axes[0].get_yticklabels():
        if lab.get_text() == cat_name("safety"): lab.set_fontweight("bold")
    caption(fig, "Orange: Safety. Black box: largest in that city.")
    return finish(fig, path)


def fig_kappa(D, w, h, path):
    """Kappa by category, one panel per city, with 95% intervals and the threshold line."""
    V = D.V or {}
    cities_d = V.get("cities") or {}
    cities = [c for c in CITY_ORDER if c in cities_d] + [c for c in cities_d if c not in CITY_ORDER]
    if not cities: return None
    labs = []
    for c in cities:
        for k in ((cities_d[c] or {}).get("categories") or {}):
            if k not in labs: labs.append(k)
    known = COMPARED + SIGNAL_ONLY + ["not_civic"]
    labs = [k for k in known if k in labs] + [k for k in labs if k not in known]
    if not labs: return None
    short = {"not_civic": "Not civic"}
    thr = V.get("threshold")
    lows = [e.get(f) for c in cities for e in ((cities_d[c] or {}).get("categories") or {}).values() if isinstance(e, dict)
            for f in ("kappa", "ci_low") if isnum(e.get(f))]
    xmin = min(0.0, math.floor(min(lows) * 10) / 10) if lows else 0.0
    fig = new_fig(w, h)
    axes = fig.subplots(1, len(cities), sharey=True, squeeze=False)[0]
    label_w = max(mpl_width(short.get(k, cat_name(k)), 20) for k in labs) + 16
    panel_w = (w * 72 - label_w - 16 * len(cities)) / len(cities)
    for ax, c in zip(axes, cities):
        cv = cities_d[c] or {}
        dropped = set(cv.get("dropped") or [])
        if isnum(cv.get("overall_kappa")):
            if isnum(cv.get("overall_ci_low")) and isnum(cv.get("overall_ci_high")):
                ax.plot([cv["overall_ci_low"], cv["overall_ci_high"]], [-1.15, -1.15], color=INK, lw=5, solid_capstyle="butt", zorder=3)
            ax.plot([cv["overall_kappa"]], [-1.15], marker="o", ms=17, ls="none", color=INK, mec="white", mew=2, zorder=4)
        else:
            ax.text(xmin + 0.03, -1.15, "no data", va="center", ha="left", fontsize=20, color=MUTED, style="italic")
        for i, k in enumerate(labs):
            e = (cv.get("categories") or {}).get(k)
            if not isinstance(e, dict) or not isnum(e.get("kappa")):
                ax.text(xmin + 0.03, i, "no data", va="center", ha="left", fontsize=20, color=MUTED, style="italic"); continue
            ok = e.get("pass")
            if ok is None and isnum(thr): ok = e["kappa"] >= thr
            out = (k in dropped) or (ok is False and "dropped" not in cv)
            col = OI["vermillion"] if out else OI["blue"]
            if isnum(e.get("ci_low")) and isnum(e.get("ci_high")):
                ax.plot([e["ci_low"], e["ci_high"]], [i, i], color=col, lw=3.5, solid_capstyle="butt", zorder=3)
            ax.plot([e["kappa"]], [i], marker="D" if out else "o", ms=12 if out else 14, ls="none", color=col,
                    mfc="white" if out else col, mec=col, mew=3.5, zorder=4)
        if isnum(thr): ax.axvline(thr, color=INK, lw=3, ls=(0, (4, 2.5)), zorder=2)
        ax.set_xlim(xmin - 0.09, 1.13); ax.set_ylim(len(labs) - 0.5, -1.75)
        ticks = sorted({0.0, 1.0} | ({float(thr)} if isnum(thr) else set()))
        ax.set_xticks(ticks); ax.set_xticklabels([("0" if t == 0 else "1" if t == 1 else f2(t)) for t in ticks])
        ax.set_title("\n".join(mpl_wrap(city_name(c), 20, max(panel_w + 12, 40), bold=True)), fontsize=20, fontweight="bold", pad=6, linespacing=0.95)
        ax.tick_params(axis="y", length=0, pad=8)
        clean_axes(ax, grid=None); ax.spines["left"].set_visible(False)
        for i in range(len(labs)): ax.axhline(i, color="#ECECEC", lw=1, zorder=1)
        ax.axhline(-0.58, color=GRID, lw=1.5, zorder=1)
    axes[0].set_yticks([-1.15] + list(range(len(labs)))); axes[0].set_yticklabels(["All labels"] + [short.get(k, cat_name(k)) for k in labs])
    axes[0].get_yticklabels()[0].set_fontweight("bold")
    caption(fig, "Dashed: kappa " + (f2(thr) if isnum(thr) else NA) + ". Hollow: dropped.")
    return finish(fig, path)


def fig_case(D, w, h, path):
    """The case-study pair: both yearly-change series on one axis (SD units), the period shaded, breaks marked."""
    cs = D.R.get("case_study") or {}
    yc = D.YC
    if not cs or yc is None: return None
    need = {"city", "category", "source", "period_end_month", "official_change_sd", "attention_change_sd"}
    if not need.issubset(yc.columns):
        note("missing", f"yearly_changes.csv columns {sorted(need - set(yc.columns))}"); return None
    d = yc[(yc.city == cs.get("city")) & (yc.category == cs.get("category")) & (yc.source == cs.get("source"))].copy()
    if d.empty:
        note("missing", f"yearly_changes.csv rows for {cs.get('city')}|{cs.get('category')}|{cs.get('source')}"); return None
    d["t"] = pd.to_datetime(d.period_end_month.astype(str).str[:7] + "-01", errors="coerce")
    d = d.dropna(subset=["t"]).sort_values("t")
    try:
        t0, t1 = pd.Timestamp(str(cs["start"])[:7] + "-01"), pd.Timestamp(str(cs["end"])[:7] + "-01")
    except Exception:
        note("missing", "case_study.start / case_study.end"); return None
    a, b = t0 - pd.DateOffset(months=CASE_PAD_MONTHS), t1 + pd.DateOffset(months=CASE_PAD_MONTHS)
    v = d[(d.t >= a) & (d.t <= b)]
    if v.empty: v = d
    s = cs.get("source") if cs.get("source") in SRC else "search"
    fig = new_fig(w, h); ax = fig.add_subplot()
    ax.axvspan(t0 - pd.DateOffset(days=15), t1 + pd.DateOffset(days=15), color=OI["yellow"], alpha=0.5, lw=0, zorder=1)
    ax.axhline(0, color=MUTED, lw=1.5, zorder=2)
    ax.plot(v.t, v.official_change_sd, color=OI["black"], lw=4, zorder=4, solid_capstyle="round")
    ax.plot(v.t, v.attention_change_sd, color=SRC[s]["color"], lw=4, ls=SRC[s]["dash"], zorder=5)
    ys = pd.concat([v.official_change_sd, v.attention_change_sd]).dropna()
    ylo, yhi = float(ys.min()), float(ys.max()); span = (yhi - ylo) or 1.0
    # marked break months (2020 to 2022, or a change in how either series counts): one grey bar along the bottom
    flag = pd.Series(False, index=v.index)
    for col in ("covid", "brk_official", "brk_attention"):
        if col in v.columns: flag = flag | v[col].astype(str).str.lower().isin(["true", "1", "1.0"])
    has_break = bool(flag.any())
    ax.set_ylim(ylo - (0.30 if has_break else 0.08) * span, yhi + 0.26 * span)
    if has_break:
        yb = ylo - 0.24 * span
        run_start = prev = None
        segs = []
        for t, f in zip(v.t, flag):
            if f and run_start is None: run_start = t
            if not f and run_start is not None: segs.append((run_start, prev)); run_start = None
            prev = t
        if run_start is not None: segs.append((run_start, prev))
        for x0, x1 in segs:
            ax.plot([x0 - pd.DateOffset(days=15), x1 + pd.DateOffset(days=15)], [yb, yb], color=MUTED, lw=9, solid_capstyle="butt", zorder=3)
        x_lo, x_hi = v.t.min(), v.t.max()
        room_right = (x_hi - segs[-1][1]) / max((x_hi - x_lo), pd.Timedelta(days=1))
        if room_right > 0.25:
            ax.annotate("marked break months", (segs[-1][1], yb), xytext=(14, 0), textcoords="offset points", fontsize=20, color=INK, ha="left", va="center")
        else:
            ax.annotate("marked break months", (segs[0][0], yb), xytext=(-14, 0), textcoords="offset points", fontsize=20, color=INK, ha="right", va="center")
    months = cs.get("months")
    ax.annotate((f"{int(months)} months" if isnum(months) else NA), (t0 + (t1 - t0) / 2, yhi + 0.23 * span), ha="center", va="top",
                fontsize=22, fontweight="bold", color=INK)
    # direct labels at the right end of each line, nudged apart if they would touch
    both = v.dropna(subset=["official_change_sd", "attention_change_sd"])
    if len(both):
        last = both.iloc[-1]
        yo, ya = float(last.official_change_sd), float(last.attention_change_sd)
        gap = 0.17 * (ax.get_ylim()[1] - ax.get_ylim()[0])
        if abs(yo - ya) < gap:
            mid = (yo + ya) / 2
            yo, ya = (mid + gap / 2, mid - gap / 2) if yo >= ya else (mid - gap / 2, mid + gap / 2)
        for lab, yy in (("Official data", yo), (("News" if s == "news" else "Search") + " attention", ya)):
            ax.annotate(lab, (last.t, yy), xytext=(10, 0), textcoords="offset points", va="center", ha="left", fontsize=21, fontweight="bold", color=INK)
    ax.set_xlim(v.t.min() - pd.DateOffset(months=2), v.t.max() + (v.t.max() - v.t.min()) * 0.27)
    y_first, y_last = int(v.t.min().year) + (0 if v.t.min().month == 1 else 1), int(v.t.max().year)
    room = max(2, int((w * 72 * 0.62) // 62))                      # year labels that fit without touching
    step = max(1, int(math.ceil((y_last - y_first + 1) / room)))
    ax.set_xticks([pd.Timestamp(year=yy, month=1, day=1) for yy in range(y_first, y_last + 1, step)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4, integer=True))
    ax.set_title("\n".join(mpl_wrap("Yearly change in SD. Up: official data worse, more attention.", 20, w * 72 - 70)), loc="left", fontsize=20, pad=6, linespacing=1.05)
    clean_axes(ax, grid="y")
    ind = None
    for p in (D.R.get("pair_level") or []):
        if isinstance(p, dict) and (p.get("city"), p.get("category"), p.get("source")) == (cs.get("city"), cs.get("category"), cs.get("source")):
            ind = p.get("indicator")
    caption(fig, "Solid: official data" + (f" ({ind})" if ind else "") + ". Dashed: " + ("news" if s == "news" else "search") + " attention.")
    return finish(fig, path)


def fig_method(D, w, h, path):
    """Three voices feeding one comparison. Boxes and arrows drawn in code. Text sizes are print sizes."""
    T = D.T
    voices = D.tx("B3_method", "voices", default=[
        {"who": "Government", "what": "Official statistics", "years": "about 2005 to 2026", "key": "official"},
        {"who": "Residents", "what": "Google search interest", "years": "{search_years}", "key": "search"},
        {"who": "Journalists", "what": "Local news from GDELT", "years": "{news_years}", "key": "news"}])
    comp = D.fill(D.tx("B3_method", "comparison", default="Compare yearly changes: do they move together?"))
    W, H = w * 72, h * 72
    fig = plt.figure(figsize=(w, h), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    n = max(1, len(voices)); gap = 20.0
    right_w = 0.30 * W; arrow_w = 0.085 * W; left_w = W - right_w - arrow_w
    row_h = (H - gap * (n - 1) - 4) / n
    pad = 4
    for i, v in enumerate(voices):
        key = v.get("key") or ("official" if i == 0 else "search" if i == 1 else "news")
        col = OI["black"] if key == "official" else SRC.get(key, SRC["news"])["color"]
        y_top = H - 2 - i * (row_h + gap); yb = y_top - row_h
        ax.add_patch(FancyBboxPatch((pad, yb), left_w - 2 * pad, row_h, boxstyle="round,pad=0,rounding_size=12", fc="white", ec=col, lw=4.5))
        ax.add_patch(Rectangle((pad + 2.2, yb + 10), 13, row_h - 20, fc=col, ec="none"))
        tx = pad + 34
        who = D.fill(v.get("who", "")); what = D.fill(v.get("what", "")); yrs = D.fill(v.get("years", ""))
        line2 = mpl_wrap(what, 26, left_w - tx - 16) + (mpl_wrap(yrs, 26, left_w - tx - 16) if yrs else [])
        block = 34 * 1.15 + len(line2) * 26 * 1.22
        yy = yb + row_h / 2 + block / 2
        ax.text(tx, yy, who, fontsize=34, fontweight="bold", va="top", ha="left", color=INK)
        yy -= 34 * 1.2
        for ln in line2:
            ax.text(tx, yy, ln, fontsize=26, va="top", ha="left", color=INK); yy -= 26 * 1.22
        ax.add_patch(FancyArrowPatch((left_w + 4, yb + row_h / 2), (left_w + arrow_w - 4, yb + row_h / 2), arrowstyle="-|>", mutation_scale=34,
                                     lw=5, color=INK, shrinkA=0, shrinkB=0))
    bx = left_w + arrow_w
    ax.add_patch(FancyBboxPatch((bx, 2), right_w - pad, H - 4, boxstyle="round,pad=0,rounding_size=12", fc=PALE, ec=INK, lw=4.5))
    lines = mpl_wrap(comp, 30, right_w - pad - 36, bold=True)
    yy = H / 2 + len(lines) * 30 * 1.22 / 2
    for ln in lines:
        ax.text(bx + (right_w - pad) / 2, yy, ln, fontsize=30, fontweight="bold", va="top", ha="center", color=INK); yy -= 30 * 1.22
    return finish(fig, path, role="diagram_text")


def make_qr(url, path):
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=24, border=4)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, dpi=(300, 300))
    return path


# ============================================================================= pages (reportlab)
class Page:
    def __init__(self, c, code, piece, name, kind):
        self.c, self.code, self.piece, self.name, self.kind = c, code, piece, name, kind
        self.items, self.figures = [], []

    # ---- text
    @staticmethod
    def tokens(text):
        out, bold = [], False
        for part in re.split(r"(\*\*)", str(text)):
            if part == "**":
                bold = not bold; continue
            out += [(wd, bold) for wd in part.split()]
        return out

    @staticmethod
    def wrap(text, size, width, font=None, bold_font=None):
        font, bold_font = font or FONT["body"], bold_font or FONT["bold"]
        space = sw(" ", font, size)
        lines, cur, cur_w = [], [], 0.0
        for wd, b in Page.tokens(text):
            ww = sw(wd, bold_font if b else font, size)
            if cur and cur_w + space + ww > width:
                lines.append(cur); cur, cur_w = [], 0.0
            cur_w += (space if cur else 0.0) + ww
            cur.append((wd, b))
        if cur: lines.append(cur)
        return lines

    @staticmethod
    def line_width(line, size, font, bold_font):
        space = sw(" ", font, size)
        return sum(sw(wd, bold_font if b else font, size) for wd, b in line) + space * max(0, len(line) - 1)

    def text(self, text, x, y_top, width, size, role, font=None, bold_font=None, color=INK, leading=None, align="left"):
        """Draw wrapped text with its top at y_top. Returns the y of the block's bottom."""
        font, bold_font = font or FONT["body"], bold_font or FONT["bold"]
        leading = leading or size * 1.2
        a, d = asc_desc(font, size)
        c = self.c
        y = y_top
        for line in self.wrap(text, size, width, font, bold_font):
            lw_ = self.line_width(line, size, font, bold_font)
            lx = x + (width - lw_) / 2 if align == "center" else (x + width - lw_ if align == "right" else x)
            base = y - a
            cx = lx; space = sw(" ", font, size)
            c.setFillColor(color)
            i = 0
            while i < len(line):                                   # draw runs of the same weight together
                j = i
                while j < len(line) and line[j][1] == line[i][1]: j += 1
                fnt = bold_font if line[i][1] else font
                run = " ".join(wd for wd, _ in line[i:j])
                c.setFont(fnt, size); c.drawString(cx, base, run)
                cx += sw(run, fnt, size) + space
                i = j
            self.items.append({"role": role, "text": " ".join(wd for wd, _ in line), "size": round(size, 2),
                               "font": font, "bbox": [round(lx, 1), round(base + d, 1), round(lx + lw_, 1), round(base + a, 1)]})
            y -= leading
        return y

    def height(self, text, size, width, font=None, bold_font=None, leading=None):
        return len(self.wrap(text, size, width, font, bold_font)) * (leading or size * 1.2)

    def fit(self, paragraphs, width, height, max_size, min_size, font=None, bold_font=None, lead=1.2, para_gap=0.55):
        """Largest size at which the paragraphs fit the box."""
        size = float(max_size)
        while size > min_size:
            hh = sum(self.height(p, size, width, font, bold_font, size * lead) for p in paragraphs) + para_gap * size * max(0, len(paragraphs) - 1)
            if hh <= height: return size
            size -= 1.0
        return float(min_size)

    def paragraphs(self, paragraphs, x, y_top, width, size, role, bullet=False, lead=1.2, para_gap=0.55, **kw):
        y = y_top
        indent = size * 0.95 if bullet else 0.0
        for p in paragraphs:
            if bullet:
                a, _ = asc_desc(FONT["body"], size)
                self.c.setFillColor(OI["blue"]); self.c.rect(x, y - a * 0.82, size * 0.36, size * 0.36, stroke=0, fill=1)
            y = self.text(p, x + indent, y, width - indent, size, role, leading=size * lead, **kw)
            y -= para_gap * size
        return y + para_gap * size

    # ---- frame, heading, figure
    def frame(self):
        c = self.c
        if self.kind == "card":
            c.setFillColor(OI["blue"]); c.rect(X0, Y1 - 5, X1 - X0, 5, stroke=0, fill=1)
        c.setFillColor(MUTED); c.setFont(FONT["body"], CODE_SIZE)
        w_ = sw(self.code, FONT["body"], CODE_SIZE)
        a, d = asc_desc(FONT["body"], CODE_SIZE)
        c.drawString(X1 - w_, Y0 - d, self.code)
        self.items.append({"role": "code", "text": self.code, "size": CODE_SIZE, "font": FONT["body"],
                           "bbox": [round(X1 - w_, 1), round(Y0, 1), round(X1, 1), round(Y0 - d + a, 1)]})
        return Y1 - 5 - 12                                         # top of the content area

    def heading(self, text, y_top, size, role):
        return self.text(text, X0, y_top, X1 - X0, size, role, font=FONT["head"], bold_font=FONT["head"], leading=size * 1.04) - size * 0.06

    def card_heading(self, text, y_top):
        """Text-card heading: 64 pt, or down to 54 pt when that keeps it on one line."""
        size = HEAD_TEXT
        while size > HEAD_MIN and len(self.wrap(text, size, X1 - X0, FONT["head"], FONT["head"])) > 1: size -= 1
        if len(self.wrap(text, size, X1 - X0, FONT["head"], FONT["head"])) > 1: size = HEAD_TEXT
        return self.heading(text, y_top, size, "heading")

    def heading_lines(self, text, size=HEAD_CHART):
        return len(self.wrap(text, size, X1 - X0, FONT["head"], FONT["head"]))

    def figure(self, rec, x, y_bottom, w_pt, h_pt):
        self.c.drawImage(ImageReader(rec["file"]), x, y_bottom, width=w_pt, height=h_pt, mask=None)
        native_w_pt = rec["px"][0] / 300.0 * 72.0
        self.figures.append({"file": os.path.relpath(rec["file"], ROOT) if rec["file"].startswith(ROOT) else rec["file"],
                             "bbox": [round(x, 1), round(y_bottom, 1), round(x + w_pt, 1), round(y_bottom + h_pt, 1)],
                             "scale": round(w_pt / native_w_pt, 4), "texts": rec.get("texts", []), "overflow": rec.get("overflow", []),
                             "text_role": rec.get("text_role", "chart_text")})

    def empty_box(self, y_top, y_bottom, message, tag=None, x0=None, x1=None):
        c = self.c
        x0 = X0 if x0 is None else x0; x1 = X1 if x1 is None else x1
        c.setStrokeColor(MUTED); c.setLineWidth(2.5); c.setDash(10, 7)
        c.rect(x0 + 2, y_bottom + 2, x1 - x0 - 4, y_top - y_bottom - 4, stroke=1, fill=0)
        c.setDash()
        size = 34
        hh = self.height(message, size, x1 - x0 - 80, FONT["bold"], FONT["bold"])
        y = (y_top + y_bottom) / 2 + hh / 2 + (22 if tag else 0)
        if tag:
            self.text(tag, x0 + 40, y + 44, x1 - x0 - 80, 26, "body", font=FONT["bold"], color=MUTED, align="center")
        self.text(message, x0 + 40, y, x1 - x0 - 80, size, "body", font=FONT["bold"], align="center")

    def words(self):
        if self.kind == "banner": return 0
        n = sum(count_words(i["text"]) for i in self.items if i["role"] not in ("code", "chart_title"))
        n += sum(count_words(t["text"]) for f in self.figures if f["text_role"] == "diagram_text" for t in f["texts"])
        return n

    def record(self, page_no):
        return {"page": page_no, "code": self.code, "piece": self.piece, "name": self.name, "kind": self.kind,
                "width_pt": PAGE_W, "height_pt": PAGE_H, "word_count": self.words(), "items": self.items, "figures": self.figures}


def chart_card(pg, D, title, detail, fig_func, fig_name, out_fig, empty_msg=NA_YET, min_h=2.6, side=False):
    """Heading (the chart's title, a full sentence with the number), the detail text, and the chart at print size.
    side=False: detail under the heading, chart below at full width. side=True: chart on the left, detail in a column on the right."""
    y = pg.frame()
    y = pg.heading(title, y, HEAD_CHART, "chart_title")
    if pg.heading_lines(title) > 3: note("warn", f"{pg.code}: the chart title takes {pg.heading_lines(title)} lines")
    bottom = Y0 + CODE_STRIP
    lead = BODY * 1.17
    if side:
        top = y - 6
        frac = SIDE_TEXT_FRAC
        while detail and frac < SIDE_TEXT_FRAC_MAX and pg.height(detail, BODY, (X1 - X0) * frac, leading=lead) > top - bottom:
            frac += 0.01
        tw = (X1 - X0) * frac if detail else 0.0
        gap = 18.0 if detail else 0.0
        fx, fy, w_pt, h_pt = X0, bottom, X1 - X0 - tw - gap, top - bottom
        if detail:
            end = pg.text(detail, X0 + w_pt + gap, top, tw, BODY, "body", leading=lead)
            if end < bottom - 1: note("warn", f"{pg.code}: the detail text is too long for its column")
        box_top = top
    else:
        if detail:
            y = pg.text(detail, X0, y - 4, X1 - X0, BODY, "body", leading=lead) - 4
        fx, fy, w_pt, h_pt = X0, bottom, X1 - X0, y - bottom
        box_top = y
    if h_pt / 72 < min_h: note("warn", f"{pg.code}: chart area is only {h_pt / 72:.1f} in tall")
    rec = None
    if fig_func is not None:
        try:
            rec = fig_func(D, w_pt / 72, h_pt / 72, os.path.join(out_fig, fig_name))
        except Exception as e:
            note("errors", f"{pg.code}: figure {fig_name} failed: {e.__class__.__name__}: {e}")
            traceback.print_exc()
    if rec:
        pg.figure(rec, fx, fy, w_pt, h_pt)
    else:
        pg.empty_box(box_top, bottom, empty_msg, x0=fx, x1=fx + w_pt)


def band(c):
    """The shared band behind the three banner pages. It runs off both side edges so the pages join."""
    c.setFillColor(PALE); c.rect(0, Y0, PAGE_W, Y1 - Y0, stroke=0, fill=1)
    c.setFillColor(OI["blue"])
    c.rect(0, Y1 - 14, PAGE_W, 14, stroke=0, fill=1)
    c.rect(0, Y0 + CODE_STRIP + 4, PAGE_W, 14, stroke=0, fill=1)
    return Y1 - 14 - 16, Y0 + CODE_STRIP + 4 + 14 + 12                # top and bottom of the text area


def stack_options(words):
    """Ways to break a short title into lines, in order."""
    n = len(words); out = []
    for mask in range(2 ** (n - 1)):
        lines, cur = [], [words[0]]
        for i in range(1, n):
            if mask >> (i - 1) & 1:
                lines.append(" ".join(cur)); cur = [words[i]]
            else:
                cur.append(words[i])
        lines.append(" ".join(cur)); out.append(lines)
    return out


def page_A1(pg, D, out_fig):
    top, bottom = band(pg.c); pg.frame()
    title = D.fill(D.tx("banner", "title", default="Measuring What Matters"))
    font = FONT["head"]; lead = 0.98
    best = (0, [title])
    for lines in stack_options(title.split()):
        w100 = max(sw(l, font, 100) for l in lines)
        size = min((X1 - X0) / w100 * 100, (top - bottom) / (len(lines) * lead) , 190)
        if size > best[0] + 0.5: best = (size, lines)
    size, lines = math.floor(best[0]), best[1]
    if size < TITLE_MIN: note("warn", f"A1: the title only fits at {size} pt")
    y = top - ((top - bottom) - len(lines) * size * lead) / 2
    for l in lines:
        pg.text(l, X0, y, X1 - X0, size, "title", font=font, bold_font=font, leading=size * lead, color="#0B2A4A")
        y -= size * lead


def page_A2(pg, D, out_fig):
    top, bottom = band(pg.c); pg.frame()
    q = D.fill(D.tx("banner", "question", default="When a city's problems get worse, does public attention follow?"))
    font = FONT["head"]
    size = pg.fit([q], X1 - X0, top - bottom, 120, HEAD_MIN, font, font, lead=1.04)
    hh = pg.height(q, size, X1 - X0, font, font, size * 1.04)
    pg.text(q, X0, top - ((top - bottom) - hh) / 2, X1 - X0, size, "banner", font=font, bold_font=font, leading=size * 1.04, color="#0B2A4A")


def page_A3(pg, D, out_fig):
    top, bottom = band(pg.c); pg.frame()
    name = D.fill(D.tx("banner", "name", default="Cayden Auyang"))
    lines = [D.fill(D.tx("banner", "mentors", default="Mentors: Mr. Qua and Mr. Lake")), D.fill(D.tx("banner", "school", default="Pomfret School, fall 2026"))]
    font = FONT["head"]
    ns = min(math.floor((X1 - X0) / sw(name, font, 100) * 100), 120)
    ls = min(min(math.floor((X1 - X0) / sw(l, FONT["bold"], 100) * 100) for l in lines), 52)
    total = ns * 1.1 + 30 + len(lines) * ls * 1.35
    y = top - ((top - bottom) - total) / 2
    y = pg.text(name, X0, y, X1 - X0, ns, "banner", font=font, bold_font=font, leading=ns * 1.1, color="#0B2A4A") - 30
    for l in lines:
        y = pg.text(l, X0, y, X1 - X0, ls, "banner", font=FONT["bold"], bold_font=FONT["bold"], leading=ls * 1.35, color=INK)


def page_A4(pg, D, out_fig):
    y = pg.frame()
    url = D.tx("A4_repo", "url", default="https://github.com/CaydenAuyang/measuring-what-matters")
    shown = re.sub(r"^https?://", "", url)
    us = min(BODY + 4, math.floor((X1 - X0) / sw(shown, FONT["bold"], 100) * 100))
    bottom = Y0 + CODE_STRIP
    url_h = us * 1.3
    qr_side = min(y - bottom - url_h - 10, 0.52 * (X1 - X0))
    y -= max(0.0, (y - bottom - qr_side - 8 - url_h) / 2)
    qr = make_qr(url, os.path.join(out_fig, "qr_repo.png"))
    pg.c.drawImage(ImageReader(qr), X0, y - qr_side, width=qr_side, height=qr_side)
    pg.figures.append({"file": os.path.relpath(qr, ROOT) if qr.startswith(ROOT) else qr, "bbox": [X0, round(y - qr_side, 1), round(X0 + qr_side, 1), round(y, 1)],
                       "scale": 1.0, "texts": [], "overflow": [], "text_role": "chart_text", "qr_url": url})
    pg.text(shown, X0, y - qr_side - 8, X1 - X0, us, "body", font=FONT["bold"])
    if us < BODY: note("warn", f"A4: the address only fits at {us} pt")
    cx = X0 + qr_side + 26; cw = X1 - cx
    head = D.fill(D.tx("A4_repo", "heading", default="Check the data and code"))
    yy = pg.text(head, cx, y, cw, HEAD_MIN, "heading", font=FONT["head"], bold_font=FONT["head"], leading=HEAD_MIN * 1.04) - 14
    ai = D.fill(D.tx("A4_repo", "ai_use", default="AI use: an AI language model labeled the articles, a second AI model from a different family checked the labels, "
                                                  "and AI tools ran the analysis and drafted the text."))
    size = pg.fit([ai], cw, yy - (y - qr_side), 34, BODY)
    pg.text(ai, cx, yy, cw, size, "body")


def text_card(pg, D, key, default_heading, default_paras, bullet=False, max_size=48):
    y = pg.frame()
    head = D.fill(D.tx(key, "heading", default=default_heading))
    y = pg.card_heading(head, y) - 12
    paras = D.tx(key, "body", default=default_paras)
    if isinstance(paras, str): paras = [paras]
    paras = [D.fill(p) for p in paras]
    bottom = Y0 + CODE_STRIP
    size = pg.fit(paras, X1 - X0 - (max_size if bullet else 0), y - bottom, max_size, BODY)
    pg.paragraphs(paras, X0, y, X1 - X0, size, "body", bullet=bullet)


def page_B1(pg, D, out_fig):
    text_card(pg, D, "B1_question", "The question", [
        "Cities publish official statistics on problems like crime and housing.",
        "News coverage and Google searches show what the public pays attention to.",
        "When a problem gets worse in the official numbers, does attention rise with it?"])


def page_B2(pg, D, out_fig):
    text_card(pg, D, "B2_why", "Why it matters", [
        "Official data and public attention are both imperfect measures of the same problems.",
        "Recorded crime counts only what gets reported.",
        "Attention can follow a news cycle and miss slow change.",
        "When the two disagree, either one can be wrong."])


def page_B3(pg, D, out_fig):
    y = pg.frame()
    head = D.fill(D.tx("B3_method", "heading", default="Three voices, one comparison"))
    y = pg.card_heading(head, y) - 12
    bottom = Y0 + CODE_STRIP
    rec = None
    try:
        rec = fig_method(D, (X1 - X0) / 72, (y - bottom) / 72, os.path.join(out_fig, "method_diagram.png"))
    except Exception as e:
        note("errors", f"B3: method diagram failed: {e.__class__.__name__}: {e}"); traceback.print_exc()
    if rec: pg.figure(rec, X0, bottom, X1 - X0, y - bottom)
    else: pg.empty_box(y, bottom, NA)


def page_B4(pg, D, out_fig):
    y = pg.frame()
    head = D.fill(D.tx("B4_numbers", "heading", default="The data in numbers"))
    y = pg.card_heading(head, y) - 6
    tiles = D.tx("B4_numbers", "tiles", default=[
        {"value": "{n_cities}", "label": "cities"},
        {"value": "{outlets_main}", "label": "outlets in the main panel"},
        {"value": "{outlets_listed}", "label": "outlets listed in all"},
        {"value": "{articles_labeled_all}", "label": "articles labeled by AI"},
        {"value": "{official_series_main}", "label": "official data series"},
        {"value": "{search_months}", "label": "months of search data"}])
    tiles = [{"value": D.fill(t.get("value", "")), "label": D.fill(t.get("label", ""))} for t in tiles if isinstance(t, dict)]
    if not tiles: return
    bottom = Y0 + CODE_STRIP
    cols = 2
    rows = int(math.ceil(len(tiles) / cols))
    gap = 10.0
    tw = (X1 - X0 - gap * (cols - 1)) / cols; th = (y - bottom - gap * (rows - 1)) / rows
    inner = tw - 34
    numeric = [t["value"] for t in tiles if re.fullmatch(r"[\d,.%]+", t["value"])]
    label_h = max(pg.height(t["label"], BODY, inner, leading=BODY * 1.15) for t in tiles)
    ns = 170.0
    for v in numeric:
        ns = min(ns, inner / sw(v, FONT["head"], 100) * 100)
    a100, d100 = asc_desc(FONT["head"], 100)
    ns = math.floor(min(ns, (th - label_h - 20) / ((a100 - d100) / 100.0)))
    ns = max(ns, HEAD_MIN)
    a, d = asc_desc(FONT["head"], ns)
    for i, t in enumerate(tiles):
        r, cc = divmod(i, cols)
        x = X0 + cc * (tw + gap); top = y - r * (th + gap)
        pg.c.setFillColor(PALE); pg.c.roundRect(x, top - th, tw, th, 8, stroke=0, fill=1)
        pg.c.setFillColor(OI["blue"]); pg.c.rect(x, top - th, 8, th, stroke=0, fill=1)
        if t["value"] in numeric:
            pg.text(t["value"], x + 24, top - 8, inner, ns, "numeral", font=FONT["head"], bold_font=FONT["head"], leading=ns, color="#0B2A4A")
        else:
            pg.text(t["value"], x + 24, top - 8 - max(0.0, (a - d - 34 * 1.2) / 2), inner, 34, "body", font=FONT["bold"], bold_font=FONT["bold"], color=MUTED)
        pg.text(t["label"], x + 24, top - 8 - a + d - 2, inner, BODY, "body", leading=BODY * 1.15)


def page_C1(pg, D, out_fig):
    vt = D.val_text()
    if vt is None:
        y = pg.frame()
        head = D.fill(D.tx("C1_validation", "placeholder_heading", default="Can the AI's labels be trusted?"))
        y = pg.card_heading(head, y) - 12
        pg.empty_box(y, Y0 + CODE_STRIP, D.fill(D.tx("C1_validation", "placeholder_body", default="Validation results arrive after the second coder runs")),
                     tag=D.fill(D.tx("C1_validation", "placeholder_tag", default="PLACEHOLDER")))
        note("missing", "validation_summary.json (piece 6 shows the placeholder card)")
        return
    chart_card(pg, D, vt[0], vt[1], fig_kappa, "validation_kappa.png", out_fig, side=True)


def page_C2(pg, D, out_fig):
    title, detail = D.h1_text()
    chart_card(pg, D, title, detail, fig_h1 if D.lead else None, "h1_forest.png", out_fig, empty_msg="No pooled result in the results file yet", side=True)


def page_C3(pg, D, out_fig):
    title, detail = D.h2_text()
    has = any(isnum(g(D.R, "main", s, "h2", "worse", "est")) for s in SOURCES)
    chart_card(pg, D, title, detail, fig_h2 if has else None, "h2_worse_better.png", out_fig, empty_msg="No pooled result in the results file yet", side=True)


def page_C4(pg, D, out_fig):
    L, title, detail = D.h3_text(fits=lambda t: pg.heading_lines(t) <= 3)
    chart_card(pg, D, title, detail, fig_h3 if L else None, "h3_opposite_share.png", out_fig, empty_msg="No shares in the results file yet", side=True)


def page_D1(pg, D, out_fig):
    title, detail = D.case_text()
    has = bool((D.R.get("case_study") or {}).get("city"))
    chart_card(pg, D, title, detail, fig_case if has else None, "case_study_timeline.png", out_fig, empty_msg="No case study in the results file yet", side=True)


def page_D2(pg, D, out_fig):
    y = pg.frame()
    head = D.fill(D.tx("D2_surprise", "heading", default="What surprised me"))
    y = pg.card_heading(head, y) - 10
    must = "[CAYDEN TO WRITE, 2 sentences]"                          # fixed text, by instruction
    size = 40
    box_h = size * 1.2 + 34
    pg.c.setStrokeColor(OI["vermillion"]); pg.c.setLineWidth(3); pg.c.setDash(10, 6)
    pg.c.rect(X0 + 1.5, y - box_h, X1 - X0 - 3, box_h, stroke=1, fill=0); pg.c.setDash()
    pg.text(must, X0 + 18, y - 17, X1 - X0 - 36, size, "body", font=FONT["bold"], bold_font=FONT["bold"])
    y -= box_h + 16
    label = D.fill(D.tx("D2_surprise", "candidates_label", default="Two candidates to use or discard:"))
    cands = D.tx("D2_surprise", "candidates", default=[
        "{H1_higher_source} attention followed official change more closely than {h1_lower_source} attention (slope {h1_higher_est} against {h1_lower_est}).",
        "For {lead_source}, {h1_n_clear} of {h1_n_categories} categories showed a clear positive link. The strongest was {h1_top_clear_category} (slope {h1_top_clear_est}).",
        "The share of periods moving in opposite directions ran from {h3_min_share} ({h3_min_pair}) to {h3_max_share} ({h3_max_pair})."])
    if isinstance(cands, str): cands = [cands]
    n_show = D.tx("D2_surprise", "show", default=2)
    n_show = int(n_show) if isnum(n_show) else 2
    ready = []
    for x in cands:                                                 # a candidate with a missing number is passed over
        D.fill(x, quiet=True)
        if not D.fill_missing: ready.append(x)
    chosen = (ready + [x for x in cands if x not in ready])[:n_show]
    cands = [D.fill(x) for x in chosen]
    bottom = Y0 + CODE_STRIP
    size = pg.fit([label] + cands, X1 - X0 - 34, y - bottom, 34, BODY)
    y = pg.text(label, X0, y, X1 - X0, size, "body", font=FONT["bold"], bold_font=FONT["bold"]) - 0.35 * size
    pg.paragraphs(cands, X0, y, X1 - X0, size, "body", bullet=True)


def page_D3(pg, D, out_fig):
    text_card(pg, D, "D3_limits", "Limits and changes to the plan", [
        "AI did the labeling and the checking. The check is agreement between two AI coders from different model families. No human coded the articles.",
        "The whole study ran in one night.",
        "Search data rests on {search_downloads} per request. The plan said three.",
        "{lead_pairs_tested} of {lead_pairs_planned} {lead_source} pairs could be tested."], bullet=True, max_size=40)


def page_D4(pg, D, out_fig):
    text_card(pg, D, "D4_next", "What comes next", [
        "Friday: the full paper.",
        "Then a submission to the Journal of Emerging Investigators.",
        "The dataset and code are public, so anyone can check the numbers."], bullet=True, max_size=48)


BUILDERS = {"A1": page_A1, "A2": page_A2, "A3": page_A3, "A4": page_A4, "B1": page_B1, "B2": page_B2, "B3": page_B3, "B4": page_B4,
            "C1": page_C1, "C2": page_C2, "C3": page_C3, "C4": page_C4, "D1": page_D1, "D2": page_D2, "D3": page_D3, "D4": page_D4}


# ============================================================================= layout map
def layout_map(path, D):
    c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H), invariant=1)
    c.setTitle("Measuring What Matters: layout map")
    items = []

    def put(s, x, y, size, font=None, color=INK, align="left"):
        font = font or FONT["body"]
        w_ = sw(s, font, size)
        xx = x - w_ / 2 if align == "center" else (x - w_ if align == "right" else x)
        c.setFillColor(color); c.setFont(font, size); c.drawString(xx, y, s)
        items.append({"text": s, "size": size, "bbox": [round(xx, 1), round(y, 1), round(xx + w_, 1), round(y + size, 1)]})

    title = D.fill(D.tx("layout_map", "title", default="Layout map: where each printed page goes on the 48 by 36 inch board"))
    put(title, X0, Y1 - 17, 17, FONT["bold"])
    sub = D.fill(D.tx("layout_map", "print_note", default="Print print_me.pdf at 100% (no scaling), pages turned sideways. Page order: A1 to A4, B1 to B4, C1 to C4, D1 to D4."))
    ss = min(11.5, math.floor((X1 - X0) / sw(sub, FONT["body"], 100) * 100 * 10) / 10)
    put(sub, X0, Y1 - 17 - 8 - ss, ss, color=MUTED)
    note_line = D.fill(D.tx("layout_map", "assembly_note", default="Glue pages edge to edge, row A first, starting 2 in from the left edge and 1 in from the top. "
                                                                   "A thin white seam between the banner pages is fine."))
    ns = min(12.5, math.floor((X1 - X0) / sw(note_line, FONT["bold"], 100) * 100 * 10) / 10)
    put(note_line, X0, Y0 + 2, ns, FONT["bold"])
    top, bottom = Y1 - 17 - 8 - ss - 12, Y0 + 2 + ns + 16
    scale = min((X1 - X0 - 40) / BOARD_W_IN, (top - bottom - 14) / BOARD_H_IN)        # points per board inch
    bw, bh = BOARD_W_IN * scale, BOARD_H_IN * scale
    bx, by = X0 + (X1 - X0 - bw) / 2, bottom + 14
    c.setStrokeColor(INK); c.setLineWidth(2); c.setFillColor("#FAFAFA"); c.rect(bx, by, bw, bh, stroke=1, fill=1)
    pw, ph = 11.0 * scale, 8.5 * scale
    gx = bx + (BOARD_W_IN - COLS * 11.0) / 2 * scale
    gy_top = by + bh - (BOARD_H_IN - len(ROWS) * 8.5) / 2 * scale
    n = 0
    for code, piece, name, kind in PIECES:
        r, col = ROWS.index(code[0]), int(code[1]) - 1
        x, ytop = gx + col * pw, gy_top - r * ph
        n += 1
        c.setFillColor(PALE if kind == "banner" else "white"); c.setStrokeColor(MUTED); c.setLineWidth(1)
        c.rect(x, ytop - ph, pw, ph, stroke=1, fill=1)
        put(code, x + 7, ytop - 22, 19, FONT["bold"])
        put(f"page {n}", x + pw - 7, ytop - 15, 9, color=MUTED, align="right")
        yy = ytop - 40
        label = D.tx("layout_map", "names", code, default=name)
        for line in Page.wrap(label, 11, pw - 14):
            put(" ".join(wd for wd, _ in line), x + 7, yy, 11); yy -= 13.5
        if piece:
            put(f"piece {piece}", x + 7, ytop - ph + 6, 9, color=MUTED)
    side = (BOARD_W_IN - COLS * 11.0) / 2; tb = (BOARD_H_IN - len(ROWS) * 8.5) / 2
    put(f"{BOARD_W_IN:g} in wide", bx + bw / 2, by - 12, 10, color=MUTED, align="center")
    c.saveState(); c.translate(bx - 6, by + bh / 2); c.rotate(90)
    c.setFillColor(MUTED); c.setFont(FONT["body"], 10); s = f"{BOARD_H_IN:g} in tall"; c.drawString(-sw(s, FONT["body"], 10) / 2, 0, s); c.restoreState()
    c.saveState(); c.translate(bx + side * scale / 2 + 3.5, by + bh / 2); c.rotate(90)
    c.setFillColor(MUTED); c.setFont(FONT["body"], 9); s = f"{side:g} in gap each side"; c.drawString(-sw(s, FONT["body"], 9) / 2, 0, s); c.restoreState()
    put(f"{tb:g} in gap top and bottom", bx + bw / 2, by + bh - tb * scale + 2.5, 9, color=MUTED, align="center")
    c.showPage(); c.save()
    return {"scale_pt_per_board_inch": round(scale, 4), "items": items}


# ============================================================================= main
def main():
    global FONT, MPL_FAMILY
    ap = argparse.ArgumentParser(description="Build the poster kit from the data files.")
    ap.add_argument("--results", default=os.path.join(ROOT, "data/public/results.json"))
    ap.add_argument("--changes", default=os.path.join(ROOT, "data/public/yearly_changes.csv"))
    ap.add_argument("--validation", default=os.path.join(ROOT, "data/public/validation_summary.json"))
    ap.add_argument("--text", default=os.path.join(ROOT, "poster/poster_text.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "poster"))
    ap.add_argument("--list-placeholders", action="store_true", help="print every placeholder and its current value, then stop")
    a = ap.parse_args()
    t_start = datetime.datetime.now()

    fonts, used, MPL_FAMILY = setup_fonts()
    FONT = {"body": fonts["MWM-Body"], "bold": fonts["MWM-Bold"], "head": fonts["MWM-Head"]}
    D = Data(a)
    if a.list_placeholders:
        for k in sorted(D.P):
            text, path, missing = D.P[k]
            print(f"{{{k}}} = {text}    <- {path}" + ("   [MISSING]" if missing else ""))
        return 0

    out = os.path.abspath(a.out); out_fig = os.path.join(out, "figures")
    os.makedirs(out_fig, exist_ok=True)
    pdf_path = os.path.join(out, "print_me.pdf")
    c = canvas.Canvas(pdf_path, pagesize=(PAGE_W, PAGE_H), invariant=1)
    c.setTitle("Measuring What Matters: poster pages"); c.setAuthor("Cayden Auyang")
    pages = []
    for n, (code, piece, name, kind) in enumerate(PIECES, 1):
        pg = Page(c, code, piece, name, kind)
        try:
            BUILDERS[code](pg, D, out_fig)
        except Exception as e:                                      # never crash: mark the page and keep going
            note("errors", f"{code}: {e.__class__.__name__}: {e}")
            traceback.print_exc()
            try:
                pg.empty_box(Y1 - 30, Y0 + CODE_STRIP, f"{name}: {NA}")
            except Exception:
                pass
        pages.append(pg.record(n))
        c.showPage()
    c.save()
    lm = layout_map(os.path.join(out, "layout_map.pdf"), D)

    with open(pdf_path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    manifest = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pdf": os.path.basename(pdf_path), "pdf_sha256": sha,
        "page_size_pt": [PAGE_W, PAGE_H], "margin_pt": MARGIN, "n_pages": len(pages),
        "rules": {"title_min_pt": TITLE_MIN, "heading_min_pt": HEAD_MIN, "body_min_pt": BODY_MIN, "chart_text_min_pt": CHART_MIN, "max_words_per_card": 60},
        "inputs": {"results": os.path.abspath(a.results), "results_generated_utc": D.R.get("generated_utc"),
                   "changes": os.path.abspath(a.changes), "validation": os.path.abspath(a.validation) if D.V else None,
                   "validation_status": (D.V or {}).get("status"), "text": os.path.abspath(a.text)},
        "lead_source": D.lead, "sources_with_results": [s for s in SOURCES if D.src_ok(s)],
        "fonts": used, "missing": NOTES["missing"], "fallbacks_used": NOTES["fallback"], "warnings": NOTES["warn"], "errors": NOTES["errors"],
        "placeholders": {k: {"value": v[0], "from": v[1], "missing": v[2]} for k, v in sorted(D.P.items())},
        "pages": pages, "layout_map": lm,
    }
    with open(os.path.join(out, "build_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)

    secs = (datetime.datetime.now() - t_start).total_seconds()
    print(f"print_me.pdf: {len(pages)} pages -> {pdf_path}")
    print(f"layout_map.pdf, build_manifest.json, figures/ -> {out}")
    print(f"lead source: {D.lead or 'none'}; sources with results: {', '.join(s for s in SOURCES if D.src_ok(s)) or 'none'}; "
          f"validation: {(D.V or {}).get('status', 'file not found')}")
    print("words per card: " + ", ".join(f"{p['code']} {p['word_count']}" for p in pages if p["kind"] == "card"))
    for label, key in (("MISSING (shown as 'not available')", "missing"), ("PLAN VALUE USED", "fallback"), ("WARNING", "warn"), ("ERROR", "errors")):
        for m in NOTES[key]:
            print(f"{label}: {m}")
    if not any(NOTES.values()): print("nothing missing")
    print(f"done in {secs:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
