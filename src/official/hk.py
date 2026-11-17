#!/usr/bin/env python
"""Hong Kong official indicators.

    python src/official/hk.py --download   fetch raw files (skips files already saved)
    python src/official/hk.py              rebuild interim outputs from saved raw files only

Raw files are saved unchanged under data/raw/official/hk/ and listed in manifest.csv.
Nothing here estimates, interpolates or fills in a number. Missing stays missing.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import calendar

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "official", "hk")
OUT = os.path.join(ROOT, "data", "interim", "official")
PLOTS = os.path.join(OUT, "plots")
MANIFEST = os.path.join(RAW, "manifest.csv")
PART_MANIFEST = os.path.join(RAW, "_manifest_part_backups.csv")
UA = {"User-Agent": "Mozilla/5.0 (research data fetch)"}
MAN_COLS = ["path", "source_url", "retrieved_utc", "sha256", "status", "note"]

CSD = "https://www.censtatd.gov.hk/api/get.php?id=%s&lang=en&full_series=1"
HA_JSON_HTTPS = "https://www.ha.org.hk/opendata/sop/sop-waiting-time-en.json"
HA_JSON_HTTP = "http://www.ha.org.hk/opendata/sop/sop-waiting-time-en.json"
DGHK_LIST = "https://api.data.gov.hk/v1/historical-archive/list-file-versions?url=%s&start=20150101&end=%s"
DGHK_GET = "https://api.data.gov.hk/v1/historical-archive/get-file?url=%s&time=%s"
EPIC_URL = "https://cd.epic.epd.gov.hk/EPICDI/air/station/?lang=en"
CHP_INDEX = "https://www.chp.gov.hk/en/static/24012.html"
HKEAA = "https://www.hkeaa.edu.hk/DocLibrary/HKDSE/Exam_Report/Examination_Statistics/dseexamstat%02d_3.pdf"

# (relative path under RAW, url, note)
SIMPLE = [
    ("economy/csd_210-06101.json", CSD % "210-06101", "C&SD table 210-06101, labour force, unemployment, underemployment"),
    ("cost_of_living/csd_510-60001.json", CSD % "510-60001", "C&SD table 510-60001, Composite CPI all items"),
    ("cost_of_living/csd_510-60002.json", CSD % "510-60002", "C&SD table 510-60002, Underlying CPI"),
    ("cost_of_living/csd_510-60003.json", CSD % "510-60003", "C&SD table 510-60003, CPI at COICOP division level (saved, not used)"),
    ("cost_of_living/csd_510-60001A.json", CSD % "510-60001A", "C&SD table 510-60001A, CPI at commodity/service section level"),
    ("cost_of_living/cpi_rebasing_report_2009_10.pdf", "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082010XXXXB0100.pdf", "C&SD 2009/10 HES and rebasing of the CPIs (section weights 2004/05 and 2009/10)"),
    ("cost_of_living/cpi_rebasing_report_2014_15.pdf", "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082015XXXXB0100.pdf", "C&SD 2014/15 HES and rebasing of the CPIs (section weights 2009/10 and 2014/15)"),
    ("cost_of_living/cpi_rebasing_report_2019_20.pdf", "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082020XXXXB0100.pdf", "C&SD 2019/20 HES and rebasing of the CPIs (section weights 2014/15 and 2019/20)"),
    ("cost_of_living/cpi_monthly_report_2026_09.pdf", "https://www.censtatd.gov.hk/wbr/B1060001/B10600012026MM09/att/en/B10600012026MM09.pdf", "C&SD Monthly Report on the CPI, September 2026 (notes on weights)"),
    ("cost_of_living/cpi_report_annex1_weights.xlsx", "https://www.censtatd.gov.hk/wbr/B1060001/B10600012026MM09/att/en/54/Annex_1%20to%20CPI%20Report%20%28last%20update%20in%20April%202026%20issue%29_v1.3.xlsx", "C&SD CPI report Annex 1: expenditure weights, reference years 2024 and 2025 (saved for documentation)"),
    ("cost_of_living/cpi_report_concepts_and_methods.pdf", "https://www.censtatd.gov.hk/wbr/B1060001/B10600012026MM09/att/en/54/Concepts%20and%20methods%20to%20CPI%20Report%20%28last%20update%20in%20May%202026%20issue%29.pdf", "C&SD CPI report: concepts and methods"),
    ("housing/his_data_3.xls", "https://www.rvd.gov.hk/doc/en/statistics/his_data_3.xls", "RVD private domestic rental indices by class"),
    ("transport/table71_eng.csv", "https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table71_eng.csv", "TD monthly digest table 7.1, road accidents by severity"),
    ("safety/csc_2001_2013.html", "https://www.police.gov.hk/ppp_en/09_statistics/csc_2001_2013.html", "HK Police crime statistics comparison 2001-2013"),
    ("safety/statistics_charts.xls", "https://www.police.gov.hk/info/doc/statistics_charts.xls", "HK Police crime statistics in detail, current file"),
    ("safety/crime_situation_comparison.xls", "https://www.police.gov.hk/info/doc/crime_situation_comparison.xls", "HK Police latest period comparison"),
    ("safety/statistics_charts_wayback_20170623010845.xls",
     "https://web.archive.org/web/20170623010845id_/http://www.police.gov.hk/info/doc/statistics_charts.xls",
     "Internet Archive raw capture of the same police file as published in 2017 (holds 2006-2016)"),
    ("environment/hko_vhotday_statistic.json", "https://www.hko.gov.hk/cis/statistic/vhotday_statistic_e_html.json", "HKO number of very hot days by month since 1884"),
    ("health/chp_index_24012.html", CHP_INDEX, "CHP index of notifiable infectious diseases by month"),
    ("health/ha_sop_live.json", HA_JSON_HTTPS, "Hospital Authority SOP waiting time, live file"),
]
for _y in range(12, 27):
    SIMPLE.append(("education/dseexamstat%02d_3.pdf" % _y, HKEAA % _y, "HKEAA HKDSE exam statistics 20%02d, table 3 series" % _y))

EPIC_RANGES = [(2000, 1, 2009, 12), (2010, 1, 2019, 12), (2020, 1, 2026, 10)]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest():
    rows = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows[r["path"]] = r
    return rows


def write_manifest(rows):
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MAN_COLS)
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k].get(c, "") for c in MAN_COLS})


def relpath(rel):
    return os.path.relpath(os.path.join(RAW, rel), ROOT)


def record(rows, rel, url, status, note):
    p = os.path.join(RAW, rel)
    rows[relpath(rel)] = {
        "path": relpath(rel), "source_url": url, "retrieved_utc": now_utc(),
        "sha256": sha256(p) if os.path.exists(p) else "", "status": status, "note": note,
    }
    write_manifest(rows)


def looks_wrong(rel, content, ctype):
    """A PDF/XLS/JSON/CSV request that comes back as an HTML error page is a failure."""
    ext = rel.rsplit(".", 1)[-1].lower()
    head = content[:400].lstrip().lower()
    if ext == "pdf":
        return not content.startswith(b"%PDF")
    if ext in ("xls", "xlsx", "json", "csv"):
        return head.startswith(b"<!doctype") or head.startswith(b"<html")
    return False


def fetch(session, rows, rel, url, note, pause=0.5, tries=2):
    p = os.path.join(RAW, rel)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        if relpath(rel) not in rows:
            record(rows, rel, url, "ok", note + " (file was already on disk; hash recorded later)")
        return True
    os.makedirs(os.path.dirname(p), exist_ok=True)
    err = ""
    for i in range(tries):
        try:
            r = session.get(url, timeout=180)
            if r.status_code == 200 and r.content and not looks_wrong(rel, r.content, r.headers.get("content-type", "")):
                with open(p, "wb") as f:
                    f.write(r.content)
                record(rows, rel, url, "ok", note)
                time.sleep(pause)
                return True
            err = "http %s, %d bytes" % (r.status_code, len(r.content))
        except Exception as e:  # network error
            err = repr(e)[:120]
        time.sleep(3 + 5 * i)
    record(rows, rel, url, "failed", note + " | " + err)
    print("FAILED", rel, err)
    return False


def ocr_scanned(rows):
    import shutil, subprocess, tempfile
    import pdfplumber
    for rel in ("education/dseexamstat12_3.pdf",):
        src = os.path.join(RAW, rel)
        out_rel = "education/derived_ocr_" + os.path.basename(rel).replace(".pdf", ".txt")
        out = os.path.join(RAW, out_rel)
        if not os.path.exists(src) or os.path.exists(out):
            continue
        exe = shutil.which("tesseract")
        if not exe:
            print("tesseract not installed; %s stays unread" % rel)
            continue
        pages = []
        with pdfplumber.open(src) as pdf, tempfile.TemporaryDirectory() as td:
            for i, p in enumerate(pdf.pages):
                png = os.path.join(td, "p%02d.png" % i)
                p.to_image(resolution=300).save(png)
                subprocess.run([exe, png, png[:-4], "--psm", "6"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                pages.append(open(png[:-4] + ".txt", encoding="utf-8", errors="replace").read() if os.path.exists(png[:-4] + ".txt") else "")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\f".join(pages))
        record(rows, out_rel, "derived from " + relpath(rel), "ok",
               "DERIVED, not a download: tesseract OCR (300 dpi, psm 6) of the scanned PDF, pages separated by form feeds")


def download():
    import requests
    from bs4 import BeautifulSoup
    os.makedirs(RAW, exist_ok=True)
    rows = read_manifest()
    s = requests.Session()
    s.headers.update(UA)

    for rel, url, note in SIMPLE:
        fetch(s, rows, rel, url, note)

    # Hospital Authority: every archived version of the open-data file kept by data.gov.hk
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    for tag, u in (("http", HA_JSON_HTTP), ("https", HA_JSON_HTTPS)):
        from urllib.parse import quote
        rel = "health/ha_sop_versions_%s.json" % tag
        if fetch(s, rows, rel, DGHK_LIST % (quote(u, safe=""), today), "data.gov.hk archive: list of versions of the HA SOP waiting time file (%s address)" % tag):
            for ts in json.load(open(os.path.join(RAW, rel)))["timestamps"]:
                fetch(s, rows, "health/ha_sop/ha_sop_%s_%s.json" % (tag, ts), DGHK_GET % (quote(u, safe=""), ts),
                      "data.gov.hk archived version %s of HA SOP waiting time file" % ts, pause=0.3)

    # CHP: one page per year, linked from the index
    idx = os.path.join(RAW, "health/chp_index_24012.html")
    if os.path.exists(idx):
        soup = BeautifulSoup(open(idx, encoding="utf-8", errors="replace").read(), "lxml")
        for a in soup.find_all("a", href=True):
            t = a.get_text(strip=True)
            if re.fullmatch(r"(19|20)\d\d", t) and "/statistics/data/10/26/43/" in a["href"]:
                fetch(s, rows, "health/chp/chp_notifiable_monthly_%s.html" % t, "https://www.chp.gov.hk" + a["href"],
                      "CHP number of notifiable infectious diseases by month, %s" % t, pause=0.3)

    # EPD EPIC: official monthly averages by station. A plain data-search form, no terms, no captcha.
    for (y0, m0, y1, m1) in EPIC_RANGES:
        rel = "environment/epic_monthly_no2_rsp_%d%02d_%d%02d.csv" % (y0, m0, y1, m1)
        p = os.path.join(RAW, rel)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            continue
        note = ("EPD EPIC air data export: Download, Nitrogen Dioxide + Respirable Suspended Particulates, 15 general stations, "
                "Monthly Average, %d-%02d to %d-%02d, CSV by parameter" % (y0, m0, y1, m1))
        try:
            r = s.get(EPIC_URL, timeout=120)
            if "captcha" in r.text.lower():
                record(rows, rel, EPIC_URL, "failed", note + " | captcha shown, stopped")
                break
            fm = BeautifulSoup(r.text, "lxml").find("form", id="form")
            data = {"requestType": "download", "timerange": "monthly", "monthlyFromYear": str(y0), "monthlyFromMonth": str(m0),
                    "monthlyToYear": str(y1), "monthlyToMonth": str(m1), "downloadToken": str(int(time.time() * 1000)),
                    "form_SUBMIT": "1", "form:_idcl": "excel",
                    "jakarta.faces.ViewState": fm.find("input", attrs={"name": "jakarta.faces.ViewState"})["value"]}
            for inp in fm.find_all("input", attrs={"type": "checkbox"}):
                lab = fm.find("label", attrs={"for": inp.get("id")})
                lab = lab.get_text(strip=True) if lab else ""
                nm = inp.get("name", "")
                if nm.endswith(":parameters") and lab in ("Nitrogen Dioxide", "Respirable Suspended Particulates"):
                    data[nm] = "true"
                if nm.startswith("j_id_4w:") and nm.endswith(":stations"):  # the general stations block
                    data[nm] = "true"
            r2 = s.post("https://cd.epic.epd.gov.hk" + fm["action"], data=data, timeout=300)
            ctype = r2.headers.get("content-type", "")
            if r2.status_code == 200 and "html" not in ctype and len(r2.content) > 500:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "wb") as f:
                    f.write(r2.content)
                record(rows, rel, EPIC_URL, "ok", note)
            else:
                record(rows, rel, EPIC_URL, "failed", note + " | http %s %s %d bytes" % (r2.status_code, ctype, len(r2.content)))
                print("FAILED", rel, r2.status_code, ctype)
        except Exception as e:
            record(rows, rel, EPIC_URL, "failed", note + " | " + repr(e)[:120])
        time.sleep(2)

    # Files found by the helper search (MTR incidents, teacher wastage, public housing waiting time)
    if os.path.exists(PART_MANIFEST):
        with open(PART_MANIFEST, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rel = os.path.relpath(os.path.join(ROOT, r["path"]), RAW)
                if os.path.exists(os.path.join(ROOT, r["path"])):
                    if r["path"] not in rows:
                        rows[r["path"]] = {c: r.get(c, "") for c in MAN_COLS}
                else:
                    fetch(s, rows, rel, r["source_url"], r.get("note", ""), pause=1.5)
        write_manifest(rows)

    # scanned PDFs (no text layer): OCR once and keep the text as a clearly named derived file
    ocr_scanned(rows)

    # refresh hashes for anything recorded before the file hash was known
    for k, r in rows.items():
        p = os.path.join(ROOT, k)
        if os.path.exists(p) and r.get("status") == "ok":
            r["sha256"] = sha256(p)
    write_manifest(rows)
    print("download done:", sum(1 for r in rows.values() if r["status"] == "ok"), "ok,",
          sum(1 for r in rows.values() if r["status"] != "ok"), "failed")


# ====================================================================== build
from glob import glob

ROWS = []
META = {}
LOG = []          # things worth reading after a build
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
MON3 = [m[:3] for m in MONTHS]


def P(rel):
    return os.path.join(RAW, rel)


def mend(y, m):
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def define(sid, category, role, name, freq, window, unit, worse, rule, urls, lag, construction,
           caveats="", breaks=None, fallback=None, components=None):
    META[sid] = dict(series_id=sid, category=category, role=role, indicator_name=name,
                     components=components or [], frequency=freq, window_months=window, unit=unit,
                     worse_when=worse, change_rule=rule, source_urls=urls, first_period=None,
                     last_period=None, n_obs=0, release_lag_months=lag, status="missing",
                     fallback_used=fallback, construction=construction, breaks=breaks or [],
                     caveats=caveats)


def add(sid, period, end, value, comp="", prov=0):
    ROWS.append(dict(series_id=sid, component=comp, period=period, period_end_date=end.isoformat(),
                     value=float(value), provisional=int(prov)))


def soup_of(path):
    from bs4 import BeautifulSoup
    return BeautifulSoup(open(path, encoding="utf-8", errors="replace").read(), "lxml")


def page_text(path):
    s = soup_of(path)
    for x in s(["script", "style"]):
        x.decompose()
    return re.sub(r"\s+", " ", s.get_text(" ", strip=True))


def num(x):
    x = re.sub(r"[,\s]", "", str(x))
    return float(x) if re.fullmatch(r"-?\d+(\.\d+)?", x) else None


# ---------------------------------------------------------------- economy
def b_economy():
    url = CSD % "210-06101"
    define("hk_economy_main", "economy", "main", "Unemployment rate, seasonally adjusted, 3-month moving average",
           "M", 3, "percent", "higher", "points", [url], 1,
           "C&SD table 210-06101, series SAUR (seasonally adjusted unemployment rate), both sexes, frequency M3M. "
           "Each value is the published 3-month moving average; the period is the last month of the 3 months "
           "(checked: Dec 2020 to Feb 2021 is 7.2). Nothing is recomputed.",
           "Smoothing delays turning points. The latest figure is provisional in C&SD releases but the API carries no flag. "
           "The API series starts in 1985-86, not 1981 as the source inventory says.",
           breaks=[dict(start="2007-01", end="2007-12", kind="method",
                        note="Seasonal adjustment moved from X-11 ARIMA to X-12 ARIMA. C&SD made the switch in May 2008 and revised "
                             "the series back to Nov 2006-Jan 2007. In the published series the seam is at the period ending "
                             "2007-01, so the year-over-year comparisons that straddle it are the periods ending 2007-01 to 2007-12.")])
    define("hk_economy_backup", "economy", "backup", "Underemployment rate, 3-month moving average",
           "M", 3, "percent", "higher", "points", [url], 1,
           "C&SD table 210-06101, series UDR (underemployment rate), both sexes, frequency M3M, as published. "
           "The period is the last month of the 3-month window.",
           "Not seasonally adjusted (C&SD does not publish an adjusted underemployment rate).")
    d = json.load(open(P("economy/csd_210-06101.json"), encoding="utf-8"))["dataSet"]
    for sid, sv in (("hk_economy_main", "SAUR"), ("hk_economy_backup", "UDR")):
        for r in d:
            if r["sv"] == sv and r["freq"] == "M3M" and r.get("SEX", "") == "" and r["figure"] not in ("", None):
                y, m = int(r["period"][:4]), int(r["period"][4:])
                add(sid, "%04d-%02d" % (y, m), mend(y, m), r["figure"])


# ---------------------------------------------------------------- housing
def b_housing_main():
    import pandas as pd
    url = "https://www.rvd.gov.hk/doc/en/statistics/his_data_3.xls"
    define("hk_housing_main", "housing", "main", "Private domestic rental index, all classes (1999 = 100)",
           "M", 1, "index (1999=100)", "faster", "inflation_points", [url], 1.5,
           "Rating and Valuation Department file his_data_3.xls, sheet 'Monthly', column 'All Classes', as published. "
           "Rows marked * by RVD are provisional and carry provisional = 1.",
           "Leaves out subdivided flats. Nominal rents. Recent months are provisional and get revised.")
    df = pd.read_excel(P("housing/his_data_3.xls"), sheet_name=0, header=None)
    col = None
    for i in range(0, 12):
        for j, v in df.iloc[i].items():
            if str(v).strip() == "All Classes":
                col = j + 1
    assert col is not None, "All Classes column not found"
    year = None
    for i in range(len(df)):
        r = df.iloc[i]
        y = num(r[1])
        if y and 1990 <= y <= 2100:
            year = int(y)
        m = num(r[5])
        v = num(str(r[col]).replace("(", "").replace(")", ""))
        if year and m and 1 <= m <= 12 and v is not None:
            prov = any(str(c).strip() == "*" for c in r.tolist())
            add("hk_housing_main", "%04d-%02d" % (year, int(m)), mend(year, int(m)), v, prov=prov)


PRH_A = re.compile(r"(?:average waiting time|AWT)\W{0,3}(?:\([Nn]ote[^)]*\))?\W{0,6}(?:for|of) general applicants(?: \([^)]*\))?"
                   r"(?: who were housed to PRH in the past 12 months)? "
                   r"(?:was|is|has (?:been )?(?:maintained|remained) at|has (?:slightly )?(?:increased|decreased|dropped|risen|fallen|reduced)"
                   r"(?: slightly)? by [\d.]+ years? to) (?:about )?(\d+(?:\.\d)?) years")
PRH_Q = re.compile(r"average waiting time in the (first|second|third|fourth) quarter of (\d{4}) has "
                   r"(?:increased|decreased|dropped)(?: slightly)? by [\d.]+ years? to (\d+(?:\.\d)?) years")
PRH_TC = re.compile(r"(?:截至|在)\s*(\d{4})\s*年\s*(\d{1,2})\s*月底.{0,260}?一般申請[者人]的平均輪候時間\*?[^\d。]{0,30}?(\d+(?:\.\d)?)\s*年")
PRH_AT = re.compile(r"[Aa]s at (?:the )?end[- ]?(?:of )?([A-Z][a-z]+),? (\d{4})")


def b_housing_backup():
    urls = ["https://www.housingauthority.gov.hk/en/about-us/publications-and-statistics/prh-applications-average-waiting-time/index.html",
            "https://www.hb.gov.hk/eng/publications/housing/cwt/index.html",
            "https://web.archive.org/ (raw captures of the two pages above, listed in the manifest)",
            "https://www.info.gov.hk/gia/ (press releases listed in the manifest)"]
    define("hk_housing_backup", "housing", "backup",
           "Public rental housing: average waiting time for general applicants",
           "Q", 12, "years", "higher", "pct_log", urls, 2,
           "Read from the sentence 'As at end-<month> <year> ... the average waiting time for general applicants ... X years' on the "
           "Housing Authority page (live page and Internet Archive raw captures of it), the Housing Bureau page, and government press "
           "releases. One value per quarter end. Each value is the average wait of general applicants housed in the past 12 months, "
           "so window_months is 12. No machine-readable history exists.",
           "Built from dated copies of an official web page, not from one file. Quarters with no saved statement are missing, not filled. "
           "From 2024 the Housing Bureau also publishes a composite waiting time that counts Light Public Housing; it is not used here. "
           "Overlapping 12-month windows smooth out change.")
    found = {}
    for f in sorted(glob(P("housing_backup_prh/*.htm*"))):
        b = os.path.basename(f)
        if b.startswith("HB_press_"):
            continue  # composite waiting time only
        t = page_text(f)
        hits = []
        ats = list(PRH_AT.finditer(t))
        for k, m in enumerate(ats):
            if m.group(1) not in MONTHS:
                continue
            end = ats[k + 1].start() if k + 1 < len(ats) else len(t)
            seg = t[m.start():min(end, m.start() + 900)]
            a = PRH_A.search(seg)
            if a:
                hits.append((int(m.group(2)), MONTHS.index(m.group(1)) + 1, a.group(1)))
        for q in PRH_Q.finditer(t):
            hits.append((int(q.group(2)), 3 * (["first", "second", "third", "fourth"].index(q.group(1)) + 1), q.group(3)))
        for c in PRH_TC.finditer(t):
            hits.append((int(c.group(1)), int(c.group(2)), c.group(3)))
        for (y, mo, v) in hits:
            if mo in (3, 6, 9, 12):
                found.setdefault((y, mo), {}).setdefault(float(v), []).append(b)
    for (y, mo) in sorted(found):
        vals = found[(y, mo)]
        if len(vals) > 1:
            LOG.append("PRH waiting time: conflicting values for %d-%02d: %s. Quarter left out." % (y, mo, {k: v[:2] for k, v in vals.items()}))
            continue
        add("hk_housing_backup", "%04d-Q%d" % (y, mo // 3), mend(y, mo), list(vals)[0])


# ---------------------------------------------------------------- transport
def b_transport_main():
    url = "https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table71_eng.csv"
    define("hk_transport_main", "transport", "main", "Fatal and serious road traffic accidents",
           "M", 1, "accidents", "higher", "pct_log", [url], 2.5,
           "Transport Department monthly digest table 7.1 (CSV): SOA_FATAL + SOA_SERIOUS for each month, as published. "
           "Months that TD marks with # are provisional.",
           "Starts in 2013. The 2003-2012 months exist only in PDF digests and were not extracted tonight. "
           "Serious accidents fall steeply from 2022 (about 1,800 a year in 2019-2021, 1,046 in 2022, 467 in 2025) while slight accidents rise. "
           "The CSV gives no reason. This looks like a change in how severity is recorded and should be treated with care.")
    with open(P("transport/table71_eng.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            ym = r["YR_MTH"].strip()
            fa, se = num(r["SOA_FATAL"]), num(r["SOA_SERIOUS"])
            if re.fullmatch(r"\d{6}", ym) and fa is not None and se is not None:
                y, m = int(ym[:4]), int(ym[4:])
                prov = "#" in (r.get("SOA_FATAL_INDI", "") + r.get("SOA_SERIOUS_INDI", ""))
                add("hk_transport_main", "%04d-%02d" % (y, m), mend(y, m), fa + se, prov=prov)


def b_transport_backup():
    import pdfplumber
    urls = ["https://www.legco.gov.hk/research-publications/english/1718issh07-mtr-train-service-performance-20171220-e.pdf",
            "https://www.tlb.gov.hk/eng/legislative/transport/replies/2025/20250514c_e.pdf"]
    define("hk_transport_backup", "transport", "backup", "MTR incidents causing delays of 8 minutes or more",
           "A", 12, "incidents", "higher", "pct_log", urls, 5,
           "2008-2016: LegCo Research Office statistical highlight ISSH07/17-18, Figure 4, the 8-30 minute row plus the over-30-minute row "
           "(checked against the printed total where it could be read). 2020-2024: annex to the government reply to LegCo question 13 of "
           "14 May 2025, sum of the three cause columns (equipment failure, human factors, passenger behaviour and external factors). "
           "2017-2019 and 2025 were not found in an official document and are missing.",
           "Two documents with a gap between them. The 2025 reply covers heavy rail and Light Rail; the 2008-2016 figure does not say, "
           "but its 2008 and 2009 totals match a 2010 LegCo paper whose incident list includes Light Rail. Heavy-rail-only totals exist "
           "for 2021-2024 (194, 154, 174, 155) in other LegCo papers and are not used. The network grew over the period.")
    p1 = P("transport_backup_mtr/legco_ISSH07_1718_mtr_train_service_performance.pdf")
    with pdfplumber.open(p1) as pdf:
        t = pdf.pages[1].extract_text() or ""
    i = t.find("Figure 4")
    seg = t[i:i + 1500]
    yrs = re.search(r"Delays\s+((?:20\d\d\s+){8}20\d\d)", seg)
    short = re.search(r"8-30 min\*?\s+((?:\d{3}\s+){8}\d{3})", seg)
    long_ = re.search(r"\n((?:\d{1,2}\s+){8}\d{1,2})\s*\n", seg)
    if yrs and short and long_:
        ys = [int(x) for x in yrs.group(1).split()]
        a = [int(x) for x in short.group(1).split()]
        b = [int(x) for x in long_.group(1).split()]
        tot = re.search(r"((?:\d{3}\s+){8}\d{3})", seg[seg.find("Total"):]) if "Total" in seg else None
        if tot:
            tt = [int(x) for x in tot.group(1).split()]
            if tt != [x + y for x, y in zip(a, b)]:
                LOG.append("MTR 2008-2016: printed total row %s differs from the sum of the two duration rows %s." % (tt, [x + y for x, y in zip(a, b)]))
        for y, x, z in zip(ys, a, b):
            add("hk_transport_backup", str(y), dt.date(y, 12, 31), x + z)
    else:
        LOG.append("MTR 2008-2016: Figure 4 could not be parsed.")
    p2 = P("transport_backup_mtr/tlb_LCQ13_20250514_annex.pdf")
    with pdfplumber.open(p2) as pdf:
        t2 = pdf.pages[0].extract_text() or ""
    for m in re.finditer(r"(?m)^(20\d\d) (\d{1,3}) (\d{1,3}) (\d{1,3}) ", t2):
        y = int(m.group(1))
        add("hk_transport_backup", str(y), dt.date(y, 12, 31), int(m.group(2)) + int(m.group(3)) + int(m.group(4)))


# ---------------------------------------------------------------- environment
def b_environment():
    from bs4 import BeautifulSoup
    define("hk_environment_main", "environment", "main",
           "NO2 and PM10 (respirable suspended particulates), monthly mean across general stations running since 2005",
           "M", 1, "micrograms per cubic metre", "higher", "pct_log", [EPIC_URL], 5,
           "EPD's own monthly average concentration for each general station (EPIC air data export, 'Monthly Average'), for nitrogen dioxide "
           "and respirable suspended particulates. The panel is the general stations with readings in 2005 and in 2025. Each value is the plain "
           "mean across the panel stations that have a monthly figure that month. Two components, no2 and pm10; the yearly changes are averaged later.",
           "Station monthly averages come rounded to whole micrograms. A few months have fewer panel stations because a station has no figure "
           "(listed in hk_build_log.txt). Roadside stations are left out. EPD had published monthly averages only up to May 2026 on 17 November 2026, "
           "a lag of about five months.",
           components=["no2", "pm10"])
    data = {}
    for f in sorted(glob(P("environment/epic_monthly_no2_rsp_*.csv"))):
        lines = open(f, encoding="utf-8-sig", errors="replace").read().splitlines()
        start = [i for i, l in enumerate(lines) if l.startswith("YEAR,POLLUTANT")][0]
        for row in csv.reader(lines[start + 1:]):
            if len(row) < 15 or not row[0].strip().isdigit():
                continue
            y, pol, st = int(row[0]), row[1].strip(), row[2].strip()
            for m in range(1, 13):
                v = row[2 + m].strip()
                if re.fullmatch(r"\d+(\.\d+)?", v):
                    data.setdefault((pol, st), {})[(y, m)] = float(v)
    for comp, pol in (("no2", "Nitrogen Dioxide"), ("pm10", "Respirable Suspended Particulates")):
        sts = sorted(st for (p, st), d in data.items() if p == pol
                     and any(k[0] == 2005 for k in d) and any(k[0] == 2025 for k in d))
        months = sorted({k for (p, st), d in data.items() if p == pol and st in sts for k in d})
        short = []
        for (y, m) in months:
            vals = [data[(pol, st)][(y, m)] for st in sts if (y, m) in data[(pol, st)]]
            if len(vals) < len(sts):
                short.append("%04d-%02d (%d of %d)" % (y, m, len(vals), len(sts)))
            if len(vals) >= max(1, len(sts) - 3):
                add("hk_environment_main", "%04d-%02d" % (y, m), mend(y, m), sum(vals) / len(vals), comp=comp)
            else:
                LOG.append("Environment %s %04d-%02d: only %d of %d panel stations, month left out." % (comp, y, m, len(vals), len(sts)))
        LOG.append("Environment %s panel (%d stations): %s. Months with an incomplete panel: %s" % (comp, len(sts), ", ".join(sts), "; ".join(short) or "none"))

    hko = "https://www.hko.gov.hk/en/cis/statistic/vhotday_statistic.htm"
    cav = ("A very hot day is a day with a maximum temperature of 33.0 C or above at the Observatory headquarters, one site only. "
           "In the HKO table a dash means no very hot day; this reading is checked by adding the months up to the printed annual total.")
    define("hk_environment_backup", "environment", "backup", "Very hot days per year, Hong Kong Observatory",
           "A", 12, "days", "higher", "pct_log", [hko, "https://www.hko.gov.hk/cis/statistic/vhotday_statistic_e_html.json"], 0,
           "HKO table 'Number of Very Hot days observed at the Hong Kong Observatory', column Annual Total, complete years from 1990. "
           "The current year is left out until HKO prints its annual total.", cav)
    define("hk_environment_backup_monthly", "environment", "backup", "Very hot days per month, Hong Kong Observatory (extra series)",
           "M", 1, "days", "higher", "points", [hko, "https://www.hko.gov.hk/cis/statistic/vhotday_statistic_e_html.json"], 0,
           "Same HKO table, one value per month from 1990. A dash is read as zero days. Blank months (not yet published) are left out. "
           "Extra series: the annual series hk_environment_backup is the backup named in the plan.",
           cav + " Most winter months are zero, so a log change is undefined; change_rule is points (difference in days).")
    j = json.load(open(P("environment/hko_vhotday_statistic.json"), encoding="utf-8-sig"))["ext_temp_statistic_html"]
    for r in BeautifulSoup(j["html_table1"][0], "lxml").find_all("tr"):
        c = [x.get_text(strip=True) for x in r.find_all(["td", "th"])]
        if len(c) >= 14 and re.fullmatch(r"(18|19|20)\d\d", c[0]) and int(c[0]) >= 1990:
            y = int(c[0])
            mv = []
            for m in range(1, 13):
                v = 0 if c[m] == "-" else (int(c[m]) if re.fullmatch(r"\d+", c[m]) else None)
                mv.append(v)
                if v is not None:
                    add("hk_environment_backup_monthly", "%04d-%02d" % (y, m), mend(y, m), v)
            if re.fullmatch(r"\d+", c[13]):
                assert None not in mv and sum(mv) == int(c[13]), "HKO very hot days: months do not add to annual total in %d" % y
                add("hk_environment_backup", str(y), dt.date(y, 12, 31), int(c[13]))


# ---------------------------------------------------------------- health
def b_health():
    define("hk_health_main", "health", "main",
           "Median waiting time for stable new specialist outpatient cases, mean over cluster and specialty pairs",
           "Q", 12, "weeks", "higher", "pct_log",
           ["https://data.gov.hk/en-data/dataset/hospital-hadata-sop-waiting-time", HA_JSON_HTTPS,
            "https://api.data.gov.hk/v1/historical-archive/list-file-versions (archived versions of the HA file)"], 1,
           "Hospital Authority open-data file 'SOP waiting time', category 'Stable Case - Median', by cluster and specialty. Each quarterly "
           "release covers a 12-month window; every archived version of the file kept by data.gov.hk was read and the newest version per window kept. "
           "The value is the plain mean of the median wait (weeks) over the cluster and specialty pairs that have a number in every window in the series.",
           "The data.gov.hk archive starts with the window ending September 2018, so the series starts at 2018-Q3, not 2015 as planned. "
           "Earlier quarters exist only as old web pages. Overlapping 12-month windows smooth out change. A mean of medians is not a system-wide median.")
    wins = {}
    for f in sorted(glob(P("health/ha_sop/*.json"))):
        ts = re.search(r"_(\d{8}-\d{4})\.json$", f).group(1)
        try:
            d = json.load(open(f, encoding="utf-8-sig"))
        except Exception as e:
            LOG.append("HA file %s unreadable: %r" % (os.path.basename(f), e))
            continue
        frm = {str(r["date_id_from"]) for r in d}
        to = {str(r["date_id_to"]) for r in d}
        if len(frm) != 1 or len(to) != 1:
            LOG.append("HA file %s has mixed windows %s %s, skipped." % (os.path.basename(f), frm, to))
            continue
        frm, to = frm.pop(), to.pop()
        vals = {}
        for r in d:
            if str(r["Category"]).strip() == "Stable Case - Median" and not str(r["cluster"]).startswith("Overall"):
                m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*weeks?\s*", str(r["Value"]))
                vals[(str(r["cluster"]).strip(), str(r["specialty"]).strip())] = float(m.group(1)) if m else None
        if to not in wins or ts > wins[to][0]:
            wins[to] = (ts, frm, vals)
    pairs = None
    for to, (ts, frm, vals) in wins.items():
        ok = {k for k, v in vals.items() if v is not None}
        pairs = ok if pairs is None else (pairs & ok)
    allpairs = set().union(*[set(v[2]) for v in wins.values()]) if wins else set()
    LOG.append("Health main: %d windows, %d of %d cluster x specialty pairs have a number in every window. Dropped: %s"
               % (len(wins), len(pairs or []), len(allpairs), sorted(allpairs - (pairs or set())) or "none"))
    for to in sorted(wins):
        ts, frm, vals = wins[to]
        y, m, dd = int(to[:4]), int(to[4:6]), int(to[6:])
        fy, fm = int(frm[:4]), int(frm[4:6])
        nmon = (y - fy) * 12 + (m - fm) + 1
        if m not in (3, 6, 9, 12) or nmon != 12:
            LOG.append("HA window %s-%s is not a 12-month window ending on a quarter, skipped." % (frm, to))
            continue
        add("hk_health_main", "%04d-Q%d" % (y, m // 3), mend(y, m), sum(vals[k] for k in pairs) / len(pairs))

    define("hk_health_backup", "health", "backup", "Notifiable infectious disease notifications, monthly total",
           "M", 1, "notifications", "higher", "pct_log", [CHP_INDEX], 1,
           "Centre for Health Protection yearly pages 'Number of notifiable infectious diseases by month', row Total, one value per month, as published.",
           "The list of notifiable diseases changes over time, so the total is not like-for-like across decades. COVID-19 cases are in the total "
           "for the months CHP counted them (2020 to early 2023), which makes those months enormous. Current-year figures are provisional.")
    chp_files = sorted(glob(P("health/chp/chp_notifiable_monthly_*.html")))
    latest = max(int(re.search(r"_(\d{4})\.html$", f).group(1)) for f in chp_files)
    for f in chp_files:
        y = int(re.search(r"_(\d{4})\.html$", f).group(1))
        s = soup_of(f)
        prov = 1 if (y == latest and re.search(r"provisional", s.get_text(" ", strip=True), re.I)) else 0
        done = False
        for tr in s.find_all("tr"):
            c = [x.get_text(" ", strip=True) for x in tr.find_all(["td", "th"], recursive=False)]
            if len(c) >= 13 and c[0].strip().lower() == "total":
                for m in range(1, 13):
                    v = num(c[m])
                    if v is not None:
                        add("hk_health_backup", "%04d-%02d" % (y, m), mend(y, m), v, prov=prov)
                done = True
                break
        if not done:
            LOG.append("CHP %d: Total row not found." % y)


# ---------------------------------------------------------------- education
def b_education():
    import pdfplumber
    define("hk_education_main", "education", "main",
           "Share of day-school HKDSE candidates with core subjects at 3322 or better (332A from 2024)",
           "A", 12, "percent", "lower", "points",
           ["https://www.hkeaa.edu.hk/DocLibrary/HKDSE/Exam_Report/Examination_Statistics/dseexamstatYY_3.pdf (YY = 12 to 25)"], 0,
           "HKEAA examination statistics, one PDF per year, Table 3d 'Statistics related to university admission', row (a) "
           "'Core subjects at 3322 or better' (from 2024 'Core subjects at 332A or better'), day school candidates, Total, the printed percentage. "
           "The period is the exam year, treated as the school year ending 31 August. The 2012 PDF is a scanned image, so its page text comes from OCR "
           "(saved as a derived text file) and the 2012 row was checked by hand against the printed counts (26,515 of 70,109 is 37.8 percent).",
           "HKEAA calls this the general minimum requirement for first-degree courses. The requirement changed in 2024 when Liberal Studies "
           "(level 2) was replaced by Citizenship and Social Development (Attained), so 2024 is not like 2023.",
           breaks=[dict(start="2024-01", end="2024-12", kind="method",
                        note="Entrance requirement changed from 3322 to 332A in 2024; the 2024 against 2023 comparison straddles it.")])
    for f in sorted(glob(P("education/dseexamstat*_3.pdf"))):
        year = 2000 + int(re.search(r"dseexamstat(\d\d)_3", f).group(1))
        got = None
        txts = []
        try:
            with pdfplumber.open(f) as pdf:
                txts = [p.extract_text() or "" for p in pdf.pages]
        except Exception as e:
            LOG.append("HKEAA %d: PDF unreadable %r" % (year, e))
        ocr = P("education/derived_ocr_dseexamstat%02d_3.txt" % (year - 2000))
        if not any(txts) and os.path.exists(ocr):
            txts = open(ocr, encoding="utf-8").read().split("\f")
        # first the page headed Table 3d; if the header is unreadable (OCR), any page with the row
        cand = [t for t in txts if re.search(r"Table\s*3d\s*:", t)] + txts
        for t in cand:
            for l in t.split("\n"):
                m = re.search(r"Core subjects at (3322|332A) or better\s*((?:[|\s]*\(\s*\d+\.\d\s*%\)){6})\s*$", l.strip())
                if m:
                    got = (m.group(1), float(re.findall(r"(\d+\.\d)\s*%", m.group(2))[2]))
                    break
            if got:
                break
        if got:
            add("hk_education_main", str(year), dt.date(year, 8, 31), got[1])
        else:
            LOG.append("HKEAA %d: Table 3d row (a) not readable (PDF has %s text). Year missing." % (year, "some" if any(txts) else "no"))

    import pandas as pd
    urls = ["https://www.edb.gov.hk/attachment/en/about-edb/publication-stat/figures/pri.xlsx",
            "https://www.edb.gov.hk/attachment/en/about-edb/publication-stat/figures/sec.xlsx",
            "https://www.info.gov.hk/gia/general/202110/27/P2021102700368.htm"]
    define("hk_education_backup", "education", "backup", "Teacher wastage rate, local primary and secondary schools",
           "A", 12, "percent", "higher", "points", urls, 6,
           "Education Bureau 'figures and statistics' workbooks for primary and secondary education, row 'Wastage rate of teachers (%)' "
           "(2020/21 onward), and the government reply to LegCo question 11 of 27 October 2021 (2017/18 to 2020/21). Two components, primary and "
           "secondary; where both sources give a year the workbook is used. The period is the year in which the labelled school year ends.",
           "The rate labelled with a school year counts teachers who left between the previous autumn and that autumn, as a share of the previous "
           "year's teachers, so it mostly describes the year before. 2020/21 is as at mid-October, other years mid-September. "
           "Covers government, aided, Direct Subsidy Scheme and private local schools; special and international schools are left out. "
           "The latest year is marked * in the workbook (teacher figures revised) and carries provisional = 1.",
           components=["primary", "secondary"])
    vals = {}
    t = soup_of(P("education_backup_wastage/LCQ11_teacher_wastage_P2021102700368.htm")).get_text(" | ", strip=True)
    i = t.find("Wastage rate of teachers")
    for m in re.finditer(r"(20\d\d)/(\d\d) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+)", t[i:i + 900]):
        y = int(m.group(1)) + 1
        vals[("primary", y)] = (float(m.group(4)), 0, "lcq")
        vals[("secondary", y)] = (float(m.group(5)), 0, "lcq")
    for comp, fn in (("primary", "edb_figures_primary_pri.xlsx"), ("secondary", "edb_figures_secondary_sec.xlsx")):
        df = pd.read_excel(P("education_backup_wastage/" + fn), sheet_name="English", header=None)
        hdr = None
        for i in range(len(df)):
            cells = [str(c).strip() for c in df.iloc[i].tolist()]
            if hdr is None and sum(bool(re.fullmatch(r"20\d\d/\d\d\*?", c)) for c in cells) >= 3:
                hdr = cells
            if hdr and any(c.startswith("Wastage rate of teachers") for c in cells):
                for j, h in enumerate(hdr):
                    mm = re.fullmatch(r"(20\d\d)/(\d\d)(\*?)", h)
                    v = num(cells[j])
                    if mm and v is not None:
                        y = int(mm.group(1)) + 1
                        new = round(v * 100, 1) if v < 1 else v
                        old = vals.get((comp, y))
                        if old and abs(old[0] - new) > 1e-9:
                            LOG.append("Teacher wastage %s %d: LegCo reply says %s, EDB workbook says %s. Workbook used." % (comp, y, old[0], new))
                        vals[(comp, y)] = (new, 1 if mm.group(3) else 0, "xlsx")
                break
    for (comp, y) in sorted(vals):
        add("hk_education_backup", str(y), dt.date(y, 8, 31), vals[(comp, y)][0], comp=comp, prov=vals[(comp, y)][1])


# ---------------------------------------------------------------- safety
def b_safety():
    import pandas as pd
    urls = ["https://www.police.gov.hk/ppp_en/09_statistics/csc_2001_2013.html",
            "https://www.police.gov.hk/info/doc/statistics_charts.xls",
            "https://web.archive.org/web/20170623010845id_/http://www.police.gov.hk/info/doc/statistics_charts.xls"]
    cav = ("Reported crime only. Three official files are joined: the 2001-2013 comparison page, the police chart workbook as published in 2017 "
           "(Internet Archive raw capture, used for 2014 and 2015), and the current chart workbook (2016 onward). Where years overlap the files "
           "agree unless the notes file says otherwise.")
    define("hk_safety_main", "safety", "main", "Overall reported crime, annual total", "A", 12, "crimes", "higher", "pct_log", urls, 2,
           "Hong Kong Police 'Overall Crime' count per calendar year. 2001-2013 from the police comparison page, 2014-2015 from the 2017 copy of the "
           "police chart workbook, 2016 onward from the current workbook. For a year in more than one file the newest file is used.",
           cav + " The rise from 2023 is driven by online fraud.",
           breaks=[dict(start="2023-01", end=None, kind="event", note="Online fraud drives the rise in reported crime from 2023 onward.")])
    define("hk_safety_backup", "safety", "backup", "Violent crime, annual total", "A", 12, "crimes", "higher", "pct_log", urls, 2,
           "Hong Kong Police 'Violent Crime' count per calendar year, same three files and same rule as the main series.", cav)
    series = {"overall": {}, "violent": {}}   # year -> list of (priority, value, source)
    # 1) comparison page 2001-2013
    for tb in soup_of(P("safety/csc_2001_2013.html")).find_all("table"):
        rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in tb.find_all("tr")]
        yrs = None
        for c in rows:
            ys = [x for x in c if re.fullmatch(r"(19|20)\d\d", x)]
            if yrs is None and len(ys) >= 2:
                yrs = [int(ys[0]), int(ys[1])]
            lab = re.sub(r"\s+", " ", c[1]) if len(c) > 3 else ""
            key = "overall" if lab == "Overall Crime" else ("violent" if lab == "Violent Crime" else None)
            if yrs and key:
                for k in (0, 1):
                    v = num(c[2 + k])
                    if v is not None:
                        series[key].setdefault(yrs[k], []).append((1 + 0.1 * k, v, "csc page table %d-%d" % tuple(yrs)))
    # 2) 2017 copy of the chart workbook
    wb = pd.ExcelFile(P("safety/statistics_charts_wayback_20170623010845.xls"))
    for key, sheet in (("overall", "Crime Rate"), ("violent", "Violent Crime Rate")):
        df = pd.read_excel(wb, sheet, header=None)
        for i in range(len(df)):
            y, v = num(df.iloc[i, 0]), num(df.iloc[i, 1])
            if y and 1990 <= y <= 2100 and v is not None:
                series[key].setdefault(int(y), []).append((2, v, "chart workbook, 2017 copy"))
    # 3) current chart workbook: the yearly block ends at the first blank row
    wb = pd.ExcelFile(P("safety/statistics_charts.xls"))
    for key, sheet, col in (("overall", "Figures Overall Crime", 3), ("violent", "Figures Violent Crime", 2)):
        df = pd.read_excel(wb, sheet, header=None)
        for i in range(1, len(df)):
            lab = str(df.iloc[i, 0]).strip()
            if lab in ("nan", ""):
                break
            if "*" in lab:
                continue   # part-year
            y = num(lab)
            v = num(df.iloc[i, col])
            if y is None or v is None:
                continue
            y = int(y) + (2000 if y < 100 else 0)
            series[key].setdefault(y, []).append((3, v, "chart workbook, current"))
    for key, sid in (("overall", "hk_safety_main"), ("violent", "hk_safety_backup")):
        for y in sorted(series[key]):
            c = sorted(series[key][y])
            if len({v for _, v, _ in c}) > 1:
                LOG.append("Crime %s %d: sources differ %s. Newest file used." % (key, y, [(s, v) for _, v, s in c]))
            add(sid, str(y), dt.date(y, 12, 31), c[-1][1])
    # extra: the latest months printed in the current workbook
    define("hk_safety_main_monthly", "safety", "main", "Overall reported crime, monthly (extra series, latest months only)",
           "M", 1, "crimes", "higher", "pct_log", [urls[1]], 2,
           "Sheet 'data' of the current police chart workbook: overall crime for each month of the two latest October-to-September blocks. "
           "Extra series. The annual series is the main indicator.",
           "Only the months printed in the current workbook (about 21). The separate monthly file for 2022-2024 named in the plan was not found tonight.",
           breaks=[dict(start="2023-01", end=None, kind="event", note="Online fraud drives the rise in reported crime from 2023 onward.")])
    df = pd.read_excel(wb, "data", header=None)
    for j in range(df.shape[1]):
        h = str(df.iloc[1, j])
        m = re.match(r"Overall Crime for (\w{3}) (\d{4}) to (\w{3}) (\d{4})", h)
        if not m:
            continue
        y, mo = int(m.group(2)), MON3.index(m.group(1)) + 1
        ey, emo = int(m.group(4)), MON3.index(m.group(3)) + 1
        for i in range(2, len(df)):
            lab = str(df.iloc[i, 1]).strip()[:3]
            v = num(df.iloc[i, j])
            if lab not in MON3:
                continue
            yy = y + (1 if MON3.index(lab) + 1 < mo else 0)
            mm = MON3.index(lab) + 1
            if v is not None and (yy, mm) <= (ey, emo):
                add("hk_safety_main_monthly", "%04d-%02d" % (yy, mm), mend(yy, mm), v)


# ---------------------------------------------------------------- cost of living
CPI_REGIMES = [  # (first month the weights apply, base period first month, report file, column label)
    ((2004, 10), (2004, 10), "cost_of_living/cpi_rebasing_report_2009_10.pdf", "2004/05"),
    ((2009, 10), (2009, 10), "cost_of_living/cpi_rebasing_report_2009_10.pdf", "2009/10"),
    ((2014, 10), (2014, 10), "cost_of_living/cpi_rebasing_report_2014_15.pdf", "2014/15"),
    ((2019, 10), (2019, 10), "cost_of_living/cpi_rebasing_report_2019_20.pdf", "2019/20"),
]


def cpi_housing_weights():
    """Housing section weight (%) of the Composite CPI for each base period, read from C&SD rebasing reports."""
    import pdfplumber
    out = {}
    for rel in sorted({r[2] for r in CPI_REGIMES} | {"cost_of_living/cpi_rebasing_report_2014_15.pdf"}):
        with pdfplumber.open(P(rel)) as pdf:
            for p in pdf.pages[:25]:
                t = p.extract_text() or ""
                m = re.search(r"Expenditure [Ww]eights of (\d{4}/\d{2})-based and (\d{4}/\d{2})-based Composite CPI", t)
                if not m:
                    continue
                h = re.search(r"Housing\s+(\d{2}\.\d{2})\s+(\d{2}\.\d{2})", t[m.end():])
                if h:
                    for lab, v in ((m.group(1), h.group(1)), (m.group(2), h.group(2))):
                        if lab in out and abs(out[lab] - float(v)) > 1e-9:
                            LOG.append("CPI housing weight %s differs between reports: %s vs %s" % (lab, out[lab], v))
                        out[lab] = float(v)
                    break
    return out


def b_cost_of_living():
    u1 = CSD % "510-60001A"
    w = cpi_housing_weights()
    LOG.append("CPI housing section weights read from C&SD rebasing reports (percent of Composite CPI): %s" % w)
    define("hk_cost_of_living_main", "cost_of_living", "main",
           "Composite CPI excluding the housing section (Oct 2019 to Sep 2020 = 100)",
           "M", 1, "index (Oct 2019-Sep 2020=100)", "faster", "inflation_points",
           [u1, "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082010XXXXB0100.pdf",
            "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082015XXXXB0100.pdf",
            "https://www.censtatd.gov.hk/en/data/stat_report/product/B1060003/att/B10600082020XXXXB0100.pdf"], 1,
           "From C&SD table 510-60001A (Composite CPI, all items and the Housing section, monthly). For each base period b "
           "(2004/05, 2009/10, 2014/15, 2019/20) both indices are re-expressed so that they average 100 over that base period, and "
           "E_b = (All - w_b x Housing) / (1 - w_b), with w_b the Housing section weight of the Composite CPI published for that base period "
           "(%s percent). The weights of base period b are used from October of its first year. Month-to-month growth of E_b is chained "
           "into one index, scaled to average 100 over Oct 2019 to Sep 2020." % ", ".join("%s: %s" % (k, w[k]) for k in sorted(w)),
           "Starts October 2004 because the 1999/2000 weights were not found. Built from indices rounded to one decimal, so the 12-month rate "
           "carries rounding noise of roughly 0.1 point. Since 2021 C&SD updates the weights every April; those yearly weights are published "
           "only for reference years 2024 and 2025, so the 2019/20 weight is used for every month from October 2019. Table 510-60001 named in "
           "the plan holds only the all-items index; the section indices are in table 510-60001A. The Housing section holds private and public "
           "rent plus management fees and other housing charges. Government one-off relief (public rent waivers) sits in Housing, so removing "
           "Housing also removes most of that distortion.")
    d = json.load(open(P("cost_of_living/csd_510-60001A.json"), encoding="utf-8"))["dataSet"]
    S = {"": {}, "S2": {}}
    for r in d:
        if r["freq"] == "M" and r["sv"] == "CC_CM_1920" and r["svDesc"] == "Index" and r.get("GROUP", "x") in S and r["figure"] not in ("", None):
            S[r["GROUP"]][(int(r["period"][:4]), int(r["period"][4:]))] = float(r["figure"])
    allm = sorted(k for k in S[""] if k in S["S2"] and k >= CPI_REGIMES[0][0])

    def regime(k):
        cur = None
        for rg in CPI_REGIMES:
            if k >= rg[0]:
                cur = rg
        return cur

    def E(rg, k):
        by, bm = rg[1]
        base = [(by + (bm + i - 1) // 12, (bm + i - 1) % 12 + 1) for i in range(12)]
        ma = sum(S[""][b] for b in base) / 12.0
        mh = sum(S["S2"][b] for b in base) / 12.0
        wb = w[rg[3]] / 100.0
        return (100 * S[""][k] / ma - wb * 100 * S["S2"][k] / mh) / (1 - wb)

    X = {}
    prev = None
    for k in allm:
        rg = regime(k)
        if prev is None:
            X[k] = E(rg, k)
        else:
            X[k] = X[prev] * E(rg, k) / E(rg, prev)
        prev = k
    basem = [(2019, 10), (2019, 11), (2019, 12)] + [(2020, i) for i in range(1, 10)]
    scale = 100.0 / (sum(X[b] for b in basem) / 12.0)
    for k in allm:
        add("hk_cost_of_living_main", "%04d-%02d" % k, mend(*k), round(X[k] * scale, 4))

    u2 = CSD % "510-60002"
    define("hk_cost_of_living_backup", "cost_of_living", "backup", "Underlying Composite CPI (Oct 2019 to Sep 2020 = 100)",
           "M", 1, "index (Oct 2019-Sep 2020=100)", "faster", "inflation_points", [u2], 1,
           "C&SD table 510-60002, series UCC_CM_1920 (underlying Composite CPI, which nets out the Government's one-off relief measures), "
           "monthly index as published.",
           "Starts January 2007. Includes rent, so it overlaps with the Housing category.")
    d = json.load(open(P("cost_of_living/csd_510-60002.json"), encoding="utf-8"))["dataSet"]
    for r in d:
        if r["freq"] == "M" and r["sv"] == "UCC_CM_1920" and r["svDesc"] == "Index" and r["figure"] not in ("", None):
            y, m = int(r["period"][:4]), int(r["period"][4:])
            add("hk_cost_of_living_backup", "%04d-%02d" % (y, m), mend(y, m), r["figure"])


# ---------------------------------------------------------------- outputs
COLS = ["city", "category", "role", "series_id", "component", "indicator_name", "frequency", "period", "period_end_date",
        "window_months", "value", "unit", "worse_when", "change_rule", "break_flag", "break_note", "provisional"]
ORDER = ["safety", "economy", "housing", "transport", "environment", "health", "education", "cost_of_living"]


FALLBACK = {
    "hk_transport_main": "CSV only; the 2003-2012 PDF digests were not extracted, so the series starts in 2013.",
    "hk_transport_backup": "Two official documents joined; 2017-2019 and 2025 not found and left missing.",
    "hk_health_main": "data.gov.hk archive of the Hospital Authority file used; it starts with the window ending September 2018. "
                      "For 2015 to mid-2018 only the backup (hk_health_backup) is available.",
    "hk_housing_backup": "No data file exists; values read from dated copies of the official page and press releases. Three quarters missing.",
    "hk_cost_of_living_main": "Section table 510-60001A used in place of 510-60001; starts October 2004 because earlier weights were not found.",
    "hk_safety_main": "2014 and 2015 come from an Internet Archive copy of the police workbook; the live site no longer shows those years.",
    "hk_safety_backup": "2014 and 2015 come from an Internet Archive copy of the police workbook; the live site no longer shows those years.",
    "hk_safety_main_monthly": "The 2022-2024 monthly file was not found; only the months in the current police workbook are included.",
    "hk_environment_main": "EPD's published station monthly averages used instead of averaging hourly readings; the hourly export is limited to 5 years a request.",
    "hk_education_main": "2012 read by OCR from a scanned PDF; 2026 statistics not found at the usual address.",
}


def finish():
    os.makedirs(PLOTS, exist_ok=True)
    seen = set()
    out = []
    for r in ROWS:
        k = (r["series_id"], r["component"], r["period"])
        assert k not in seen, "duplicate period %s" % (k,)
        seen.add(k)
        m = META[r["series_id"]]
        ym = r["period_end_date"][:7]
        notes = [b["note"] for b in m["breaks"] if b["start"] <= ym and (b["end"] is None or ym <= b["end"])]
        out.append(dict(city="hk", category=m["category"], role=m["role"], series_id=r["series_id"], component=r["component"],
                        indicator_name=m["indicator_name"], frequency=m["frequency"], period=r["period"],
                        period_end_date=r["period_end_date"], window_months=m["window_months"], value=r["value"], unit=m["unit"],
                        worse_when=m["worse_when"], change_rule=m["change_rule"], break_flag=1 if notes else 0,
                        break_note=" | ".join(notes), provisional=r["provisional"]))
    sid_order = sorted(META, key=lambda s: (ORDER.index(META[s]["category"]), 0 if META[s]["role"] == "main" else 1, s))
    out.sort(key=lambda r: (sid_order.index(r["series_id"]), r["component"], r["period_end_date"]))
    with open(os.path.join(OUT, "hk_official.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=COLS)
        wr.writeheader()
        for r in out:
            r = dict(r)
            r["value"] = repr(round(r["value"], 6))
            wr.writerow(r)
    metas = []
    for sid in sid_order:
        m = dict(META[sid])
        rs = [r for r in out if r["series_id"] == sid]
        if rs:
            m["first_period"] = min(rs, key=lambda r: r["period_end_date"])["period"]
            m["last_period"] = max(rs, key=lambda r: r["period_end_date"])["period"]
            m["n_obs"] = len(rs)
            m["status"] = STATUS.get(sid, "ok")
            m["fallback_used"] = FALLBACK.get(sid)
            lastym = max(r["period_end_date"] for r in rs)[:7]
            m["breaks"] = [dict(b, end=b["end"] or lastym) for b in m["breaks"]]
        metas.append(m)
    with open(os.path.join(OUT, "hk_meta.json"), "w", encoding="utf-8") as f:
        json.dump(metas, f, indent=1, ensure_ascii=False)
    plot(out, metas)
    with open(os.path.join(OUT, "hk_build_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    for m in metas:
        print("%-32s %-8s %s %-8s %-8s n=%d" % (m["series_id"], m["status"], m["frequency"], m["first_period"], m["last_period"], m["n_obs"]))
    print("\n".join(LOG))


# series that are present but shorter or thinner than the plan asks for
STATUS = {
    "hk_transport_main": "partial",      # starts 2013, not 2003
    "hk_transport_backup": "partial",    # 2017-2019 and 2025 missing
    "hk_health_main": "partial",         # starts 2018-Q3, not 2015
    "hk_housing_backup": "partial",      # some quarters missing, starts 2014
    "hk_education_main": "ok",
    "hk_cost_of_living_main": "partial", # starts 2004-10
    "hk_safety_main_monthly": "partial",
}


def plot(out, metas):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for m in metas:
        rs = [r for r in out if r["series_id"] == m["series_id"]]
        if not rs:
            continue
        fig, ax = plt.subplots(figsize=(9, 3.6))
        comps = sorted({r["component"] for r in rs})
        for c in comps:
            pts = [(dt.date.fromisoformat(r["period_end_date"]), r["value"]) for r in rs if r["component"] == c]
            step = {"M": 31, "Q": 92, "A": 366}[m["frequency"]]
            xs, ys = [], []
            for i, (x, y) in enumerate(pts):
                if i and (x - pts[i - 1][0]).days > 1.5 * step:   # a gap in the data: break the line, do not bridge it
                    xs.append(x)
                    ys.append(float("nan"))
                xs.append(x)
                ys.append(y)
            ax.plot(xs, ys, marker="o" if len(xs) < 60 else None, markersize=3, linewidth=1.2, label=c or None)
        for b in m["breaks"]:
            y0, m0 = map(int, b["start"].split("-"))
            y1, m1 = map(int, b["end"].split("-"))
            ax.axvspan(dt.date(y0, m0, 1), mend(y1, m1), color="0.85", zorder=0)
        ax.set_title("%s (%s, %s)" % (m["indicator_name"][:80], m["frequency"], m["status"]), fontsize=9)
        ax.set_ylabel(m["unit"], fontsize=8)
        ax.grid(True, linewidth=0.3)
        if any(comps):
            ax.legend(fontsize=8)
        suffix = m["series_id"].replace("hk_%s_%s" % (m["category"], m["role"]), "")
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "hk_%s_%s%s.png" % (m["category"], m["role"], suffix)), dpi=110)
        plt.close(fig)


def build():
    del ROWS[:]
    META.clear()
    del LOG[:]
    for fn in (b_safety, b_economy, b_housing_main, b_transport_main, b_environment, b_health, b_education, b_cost_of_living,
               b_housing_backup, b_transport_backup):
        try:
            fn()
        except Exception as e:
            import traceback
            LOG.append("BUILDER FAILED %s: %r" % (fn.__name__, e))
            traceback.print_exc()
    finish()


if __name__ == "__main__":
    if "--download" in sys.argv:
        download()
    else:
        build()
