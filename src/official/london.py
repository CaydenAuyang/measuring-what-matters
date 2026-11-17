#!/usr/bin/env python
"""Official indicators for London.

    python src/official/london.py --download            fetch raw files (skips files already saved)
    python src/official/london.py --download --only air fetch one group only (air, dft, small, ta, dfe)
    python src/official/london.py                       rebuild every output from the saved raw files (offline)

Raw files are saved unchanged under data/raw/official/london/ and listed in
data/raw/official/london/manifest.csv. The build step never touches the network.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import hashlib
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "official" / "london"
OUT = ROOT / "data" / "interim" / "official"
PLOTS = OUT / "plots"
MANIFEST = RAW / "manifest.csv"
UA = "Mozilla/5.0 (research data fetch)"
LAST_FULL_MONTH = "2026-10"

MANIFEST_COLS = ["path", "source_url", "retrieved_utc", "sha256", "status", "note"]


# --------------------------------------------------------------------------- #
# download helpers
# --------------------------------------------------------------------------- #

def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def manifest_add(relpath: str, url: str, sha: str, status: str, note: str) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    if new:
        w.writerow(MANIFEST_COLS)
    w.writerow([relpath, url, utcnow(), sha, status, note])
    with open(MANIFEST, "a", encoding="utf-8") as f:
        f.write(buf.getvalue())


def fetch(url: str, rel: str, note: str = "", timeout: int = 180, retries: int = 2,
          pause: float = 0.0, min_bytes: int = 1, headers: dict | None = None) -> Path | None:
    """Download url to RAW/rel unchanged. Skip if the file is already there."""
    import requests

    dest = RAW / rel
    if dest.exists() and dest.stat().st_size >= min_bytes:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    relpath = str(dest.relative_to(ROOT))
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    last = ""
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=h, timeout=timeout)
            if r.status_code == 200 and len(r.content) >= min_bytes:
                dest.write_bytes(r.content)
                manifest_add(relpath, url, sha256_bytes(r.content), "ok", note)
                print(f"  saved {relpath} ({len(r.content):,} bytes)", flush=True)
                if pause:
                    time.sleep(pause)
                return dest
            last = f"http {r.status_code}, {len(r.content)} bytes"
        except Exception as e:  # network errors are logged, never hidden
            last = f"{type(e).__name__}: {e}"[:200]
        time.sleep(3 + 5 * attempt)
    manifest_add(relpath, url, "", "failed", f"{note} | {last}".strip(" |"))
    print(f"  FAILED {url} -> {last}", flush=True)
    return None


def fetch_stream(url: str, rel: str, note: str = "", timeout: int = 120,
                 retries: int = 1, min_bytes: int = 1000) -> Path | None:
    """Streamed download for large files. Saved unchanged; sha256 computed on the bytes."""
    import requests

    dest = RAW / rel
    if dest.exists() and dest.stat().st_size >= min_bytes:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    relpath = str(dest.relative_to(ROOT))
    tmp = dest.with_suffix(dest.suffix + ".part")
    last = ""
    for attempt in range(retries + 1):
        try:
            h = hashlib.sha256()
            n = 0
            with requests.get(url, headers={"User-Agent": UA}, timeout=timeout, stream=True) as r:
                if r.status_code != 200:
                    last = f"http {r.status_code}"
                    time.sleep(5)
                    continue
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        if chunk:
                            f.write(chunk)
                            h.update(chunk)
                            n += len(chunk)
            if n >= min_bytes:
                tmp.rename(dest)
                manifest_add(relpath, url, h.hexdigest(), "ok", note)
                print(f"  saved {relpath} ({n:,} bytes)", flush=True)
                return dest
            last = f"only {n} bytes"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"[:200]
        time.sleep(5)
    if tmp.exists():
        tmp.unlink()
    manifest_add(relpath, url, "", "failed", f"{note} | {last}".strip(" |"))
    print(f"  FAILED {url} -> {last}", flush=True)
    return None


# --------------------------------------------------------------------------- #
# air quality (London Air Quality Network API)
# --------------------------------------------------------------------------- #

AIR_API = ("https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={site}/"
           "SpeciesCode={sp}/StartDate={a}/EndDate={b}/Json")
AIR_SITES_URL = "https://api.erg.ic.ac.uk/AirQuality/Information/MonitoringSiteSpecies/GroupName=All/Json"
# (site, species, first year, last year). MY1 has no PM2.5 instrument in the network;
# Marylebone Road PM2.5 is published under MY7 (FDMS, opened 2004, closed Dec 2021)
# and MR8 (BAM, opened 2012). A few MY1/PM25 years are fetched so the empty
# responses are on file.
AIR_PAIRS = [("MY1", "NO2", 2004, 2026), ("BL0", "NO2", 2004, 2026),
             ("BL0", "PM25", 2004, 2026), ("MY7", "PM25", 2004, 2021),
             ("MR8", "PM25", 2012, 2026), ("MY1", "PM25", 2010, 2010),
             ("MY1", "PM25", 2020, 2020), ("MY1", "PM25", 2026, 2026)]
AIR_LAST_YEAR = 2026
AIR_END_EXCLUSIVE = "2026-11-01"  # the API's EndDate is exclusive


def download_air(pairs: str = "") -> None:
    """pairs: optional comma list like 'MY7:PM25,MR8:PM25' to fetch a subset."""
    print("air quality (LAQN API)", flush=True)
    fetch(AIR_SITES_URL, "air/laqn_sites_species_all.json",
          "LAQN site and species list (shows which species each site code carries)")
    want = {tuple(x.split(":")) for x in pairs.split(",") if x}
    for site, sp, y0, y1 in AIR_PAIRS:
        if want and (site, sp) not in want:
            continue
        for y in range(y0, y1 + 1):
            a = f"{y}-01-01"
            b = f"{y + 1}-01-01" if y < AIR_LAST_YEAR else AIR_END_EXCLUSIVE
            url = AIR_API.format(site=site, sp=sp, a=a, b=b)
            fetch(url, f"air/{site}_{sp}_{y}.json",
                  f"LAQN hourly {sp} at {site}, {a} to {b} (end exclusive)",
                  timeout=300, pause=1.0, min_bytes=50)


# --------------------------------------------------------------------------- #
# transport: DfT road safety open data (STATS19)
# --------------------------------------------------------------------------- #

DFT_BASE = "https://data.dft.gov.uk/road-accidents-safety-data/"
DFT_FILES = {
    "dft/collision_1979_latest.csv": "dft-road-casualty-statistics-collision-1979-latest-published-year.csv",
    "dft/casualty_1979_latest.csv": "dft-road-casualty-statistics-casualty-1979-latest-published-year.csv",
}


def download_dft() -> None:
    print("DfT road safety open data", flush=True)
    for rel, name in DFT_FILES.items():
        fetch_stream(DFT_BASE + name, rel, "DfT STATS19 open data, all years; used from 2004", timeout=180)


# --------------------------------------------------------------------------- #
# small files: ONS, London Datastore, Home Office, MHCLG, DfE
# --------------------------------------------------------------------------- #

ONS_GEN = "https://www.ons.gov.uk/generator?format=csv&uri="
ONS_FILE = "https://www.ons.gov.uk/file?uri="
LDS = "https://data.london.gov.uk/download/"
GOVUK = "https://assets.publishing.service.gov.uk/media/"

SMALL_FILES = [
    # economy
    ("ons/ycni_lms.csv", ONS_GEN + "/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/ycni/lms",
     "ONS YCNI: LFS unemployment rate, London, all aged 16+, %, SA"),
    ("ons/dpdk_unem.csv", ONS_GEN + "/employmentandlabourmarket/peoplenotinwork/outofworkbenefits/timeseries/dpdk/unem",
     "ONS DPDK: claimant count, London, people, SA, thousands"),
    # cost of living
    ("ons/d7g7_mm23.csv", ONS_GEN + "/economy/inflationandpriceindices/timeseries/d7g7/mm23",
     "ONS D7G7: CPI annual rate, all items, UK"),
    # housing
    ("ons/pipr_monthly_price_statistics_21october2026.xlsx",
     ONS_FILE + "/economy/inflationandpriceindices/datasets/priceindexofprivaterentsukmonthlypricestatistics/"
                "21october2026/priceindexofprivaterentsukmonthlypricestatistics.xlsx",
     "ONS Price Index of Private Rents, monthly price statistics, 21 Oct 2026 edition"),
    ("ons/iphrp_reference_table_january2024.xlsx",
     ONS_FILE + "/economy/inflationandpriceindices/datasets/indexofprivatehousingrentalpricesreferencetables/"
                "current/iphrpreferencetablejanuary2024accessible1.xlsx",
     "ONS Index of Private Housing Rental Prices, final edition (data to Jan 2024)"),
    # safety main
    ("crime/lds_dataset_exy3m.json", "https://data.london.gov.uk/api/v2/dataset/mps-recorded-crime-geographic-breakdown-exy3m",
     "London Datastore dataset record: lists every published version of the MPS crime files"),
    ("crime/mps_borough_historical_201004_202404_pub20260505.csv",
     LDS + "exy3m/3kv/MPS%20Borough%20Level%20Crime%20(Historical).csv",
     "MPS borough crime, historical file published 2026-05-05: the last version with the full history from Apr 2010"),
    ("crime/mps_borough_historical_202011_202410_pub20261106.csv",
     LDS + "exy3m/bkb/MPS%20Borough%20Level%20Crime%20(Historical).csv",
     "MPS borough crime, historical file published 2026-11-06 (rolling 48 months)"),
    ("crime/mps_borough_recent24_202411_202610_pub20261106.csv",
     LDS + "exy3m/3xb/MPS%20Borough%20Level%20Crime%20(most%20recent%2024%20months).csv",
     "MPS borough crime, most recent 24 months, published 2026-11-06"),
    # safety backup
    ("homeoffice/open_data_tables_page.json",
     "https://www.gov.uk/api/content/government/statistical-data-sets/police-recorded-crime-and-outcomes-open-data-tables",
     "GOV.UK record of the Home Office open data tables page (source of the file links)"),
    ("homeoffice/prc-pfa-mar2013-onwards-tables-221026.ods", GOVUK + "6ad234c767af5c09d047971d/prc-pfa-mar2013-onwards-tables-221026.ods",
     "Home Office police recorded crime by police force area, year ending March 2013 onwards"),
    ("homeoffice/prc-pfa-mar2008-mar2012-tabs.ods", GOVUK + "680799ed8c1316be7978e6cd/prc-pfa-mar2008-mar2012-tabs.ods",
     "Home Office police recorded crime by police force area, 2007/08 to 2011/12"),
    ("homeoffice/prc-pfa-0203-to-0607-tabs.ods", GOVUK + "68079a4f3bdfd1243078e6d2/prc-pfa-0203-to-0607-tabs.ods",
     "Home Office police recorded crime by police force area, 2002/03 to 2006/07"),
    # housing backup
    ("mhclg/live_tables_on_homelessness_page.json",
     "https://www.gov.uk/api/content/government/statistical-data-sets/live-tables-on-homelessness",
     "GOV.UK record of the MHCLG homelessness live tables page (source of the file links)"),
    ("mhclg/Temporary_accommodation2018Q1.xlsx", GOVUK + "5d00bd40e5274a3d4b416479/Temporary_accommodation2018Q1.xlsx",
     "MHCLG temporary accommodation live tables to Jan-Mar 2018 (Table 775 London)"),
    # education main, school years before 2018/19
    ("lds/gcse_results_by_sex.xlsx",
     LDS + "20pd9/a8a71d73-cc48-4b30-9eb5-c5f605bc845c/GCSE%20results%20by%20sex.xlsx",
     "London Datastore 'GCSE Results by Borough': GLA workbook of DfE key stage 4 figures, 2015/16 to 2024/25"),
    # transport backup
    ("tfl/tfl-tube-performance.xlsx", LDS + "em8qy/c3ecab2b-5acf-4124-8dd5-fb4ae7c016e5/tfl-tube-performance.xlsx",
     "TfL London Underground performance (London Datastore), periods May 2011 to Mar 2020"),
]

DFE_KS4_URL = ("https://explore-education-statistics.service.gov.uk/data-catalogue/data-set/"
               "9e761bdf-fe02-4e1e-9d3d-b32dac9fa6ef/csv")
DFE_KS4_REL = "dfe/ks4_all_state_funded_characteristics_geography_202425_revised.csv"


def download_small() -> None:
    print("ONS, London Datastore, Home Office, MHCLG, TfL", flush=True)
    for rel, url, note in SMALL_FILES:
        fetch(url, rel, note, timeout=240, pause=0.5, min_bytes=500)
    print("DfE key stage 4", flush=True)
    fetch_stream(DFE_KS4_URL, DFE_KS4_REL,
                 "DfE key stage 4 performance 2024/25 revised: all state-funded pupils, characteristics and geography",
                 timeout=180, min_bytes=1_000_000)


TA_PAGE_REL = "mhclg/live_tables_on_homelessness_page.json"
TA_TS_URL = GOVUK + "6a82eee63bd75b81e2329a7b/Statutory_Homelessness_England_Time_Series_202603.ods"
TA_TS_REL = "mhclg/Statutory_Homelessness_England_Time_Series_202603.ods"
QUARTER_OF = {"January to March": 1, "April to June": 2, "July to September": 3, "October to December": 4}


def ta_quarter_files() -> dict:
    """quarter -> (url, title) for the detailed local authority workbooks listed on the saved GOV.UK page.
    Where a quarter is listed more than once, a revised edition is preferred; 'Accessible' copies are skipped."""
    body = json.loads((RAW / TA_PAGE_REL).read_text())["details"]["body"]
    out: dict = {}
    for url, title in re.findall(r'<a[^>]+href="(https://assets\.publishing\.service\.gov\.uk/[^"]+)"[^>]*>(.*?)</a>',
                                 body, flags=re.S):
        title = re.sub(r"<[^>]+>", " ", title)
        title = " ".join(title.split())
        m = re.match(r"Detailed local authority level tables: (January to March|April to June|July to September|"
                     r"October to December) (\d{4})(.*)$", title)
        if not m or "ccessible" in title:
            continue
        q = f"{m.group(2)}-Q{QUARTER_OF[m.group(1)]}"
        revised = "revised" in m.group(3).lower()
        if q not in out or (revised and not out[q][2]):
            out[q] = (url, title, revised)
    return {q: (u, t) for q, (u, t, _r) in sorted(out.items())}


def download_ta() -> None:
    print("MHCLG detailed local authority homelessness tables (temporary accommodation)", flush=True)
    fetch(TA_TS_URL, TA_TS_REL, "MHCLG statutory homelessness England time series (used to cross-check England totals)")
    for q, (url, title) in ta_quarter_files().items():
        fetch(url, "mhclg/detailed_la/" + url.rsplit("/", 1)[-1], f"MHCLG {title} ({q})",
              timeout=240, pause=0.5, min_bytes=50000)


DFE_API = "https://api.education.gov.uk/statistics/v1/data-sets/"
DFE_ABSENCE_ID = "019d209b-b031-7497-8205-af255b581d91"   # Absence sessions by reason, 2006/07 to 2024/25
DFE_ABSENCE_REL = "dfe/absence_sessions_by_reason_api.csv"
DFE_KS4_NEW_ID = "b3e19901-5d2b-b676-bb4c-e60937d74725"   # same KS4 data set, 2025/26 release (provisional)
DFE_KS4_NEW_REL = "dfe/ks4_all_state_funded_characteristics_geography_api_202526.csv"


def download_dfe_api() -> None:
    print("DfE statistics API", flush=True)
    for dsid, rel, note in (
            (DFE_ABSENCE_ID, DFE_ABSENCE_REL, "DfE pupil absence in schools in England: absence sessions by reason"),
            (DFE_KS4_NEW_ID, DFE_KS4_NEW_REL, "DfE key stage 4 performance, 2025/26 release: all state-funded "
                                              "pupil characteristics and geography data")):
        fetch(DFE_API + dsid, rel.replace(".csv", "_record.json"), note + " (data set record)", min_bytes=100)
        fetch(DFE_API + dsid + "/meta", rel.replace(".csv", "_meta.json"), note + " (column and filter list)",
              min_bytes=100)
        fetch_stream(DFE_API + dsid + "/csv", rel, note, timeout=300, min_bytes=100000)


DOWNLOADERS = {"air": download_air, "dft": download_dft, "small": download_small, "ta": download_ta,
               "dfe": download_dfe_api}


# =========================================================================== #
# BUILD (offline, deterministic: reads only files under data/raw/official/london)
# =========================================================================== #

CITY = "london"
COLS = ["city", "category", "role", "series_id", "component", "indicator_name", "frequency",
        "period", "period_end_date", "window_months", "value", "unit", "worse_when",
        "change_rule", "break_flag", "break_note", "provisional", "source_note"]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
CHECKS: dict = {}


def ym_add(ym: str, k: int) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    n = y * 12 + (m - 1) + k
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


def month_last_day(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"


def period_end_month(period: str, freq: str, school_year: bool = False) -> str:
    if freq == "M":
        return period
    if freq == "Q":
        return f"{period[:4]}-{int(period[-1]) * 3:02d}"
    return f"{period}-08" if school_year else f"{period}-12"


def point_break(month: str, note: str, kind: str = "method") -> dict:
    """A break at one month: the break month and the 11 months after it are flagged,
    because every year-over-year comparison in that window straddles the break."""
    return {"start": month, "end": ym_add(month, 11), "kind": kind, "note": note}


def span_break(start: str, end: str, note: str, kind: str = "method") -> dict:
    return {"start": start, "end": end, "kind": kind, "note": note}


def tidy(spec: dict, df) -> list[dict]:
    """df has columns: period, value and optionally provisional, source_note."""
    rows = []
    for r in df.to_dict("records"):
        pem = period_end_month(r["period"], spec["frequency"], spec.get("school_year", False))
        notes = [f"{b['kind']}: {b['note']}" for b in spec["breaks"] if b["start"] <= pem <= b["end"]]
        v = r["value"]
        prov, src = r.get("provisional", 0), r.get("source_note", "")
        rows.append({
            "city": CITY, "category": spec["category"], "role": spec["role"],
            "series_id": spec["series_id"], "component": "",
            "indicator_name": spec["indicator_name"], "frequency": spec["frequency"],
            "period": r["period"], "period_end_date": month_last_day(pem),
            "window_months": spec["window_months"],
            "value": "" if v is None or v != v else repr(float(v)),
            "unit": spec["unit"], "worse_when": spec["worse_when"], "change_rule": spec["change_rule"],
            "break_flag": 1 if notes else 0, "break_note": "; ".join(notes),
            "provisional": 0 if (prov is None or prov != prov) else int(prov),
            "source_note": "" if (src is None or src != src) else str(src),
        })
    return rows


def read_ons_csv(path: Path):
    """ONS time series generator CSV -> dict with title and lists of annual, quarterly, monthly rows."""
    out = {"title": "", "release": "", "A": [], "Q": [], "M": []}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            k, v = row[0].strip(), row[1].strip()
            if k == "Title":
                out["title"] = v
            elif k == "Release date":
                out["release"] = v
            elif re.fullmatch(r"\d{4}", k):
                out["A"].append((k, float(v)))
            elif re.fullmatch(r"\d{4} Q[1-4]", k):
                out["Q"].append((k, float(v)))
            elif re.fullmatch(r"\d{4} [A-Z]{3}", k):
                out["M"].append((f"{k[:4]}-{MONTHS[k[5:]]:02d}", float(v)))
    return out


# ---- economy ---------------------------------------------------------------

def build_economy_main():
    import pandas as pd
    d = read_ons_csv(RAW / "ons/ycni_lms.csv")
    # ONS labels each rolling three-month LFS estimate with its MIDDLE month
    # (the quarterly value for Q2, April to June, equals the monthly value labelled May).
    mid = dict(d["M"])
    bad = 0
    for q, v in d["Q"]:
        m = f"{q[:4]}-{int(q[-1]) * 3 - 1:02d}"
        if m in mid and abs(mid[m] - v) > 1e-9:
            bad += 1
    CHECKS["economy_main"] = {"title": d["title"], "release_date": d["release"],
                              "quarters_checked": len(d["Q"]), "quarters_not_equal_to_middle_month_label": bad}
    df = pd.DataFrame([{"period": ym_add(m, 1), "value": v,
                        "source_note": f"ONS label {m} (middle month of the three)"} for m, v in d["M"]])
    return df


def build_economy_backup():
    import pandas as pd
    d = read_ons_csv(RAW / "ons/dpdk_unem.csv")
    CHECKS["economy_backup"] = {"title": d["title"], "release_date": d["release"]}
    return pd.DataFrame([{"period": m, "value": v} for m, v in d["M"]])


def build_cost_of_living_main():
    import pandas as pd
    d = read_ons_csv(RAW / "ons/d7g7_mm23.csv")
    CHECKS["cost_of_living_main"] = {"title": d["title"], "release_date": d["release"]}
    return pd.DataFrame([{"period": m, "value": v} for m, v in d["M"]])


# ---- safety ----------------------------------------------------------------

CRIME_FILES = [
    ("crime/mps_borough_historical_201004_202404_pub20260505.csv", "historical file published 2026-05-05"),
    ("crime/mps_borough_historical_202011_202410_pub20261106.csv", "historical file published 2026-11-06"),
    ("crime/mps_borough_recent24_202411_202610_pub20261106.csv", "last-24-months file published 2026-11-06"),
]


def _crime_totals(rel: str):
    import pandas as pd
    df = pd.read_csv(RAW / rel)
    cols = [c for c in df.columns if re.fullmatch(r"\d{6}", str(c))]
    tot = df[cols].sum()
    fraud = df[df.iloc[:, 0].isin(["FRAUD AND FORGERY", "NFIB FRAUD"])][cols].sum()
    return ({f"{c[:4]}-{c[4:]}": float(tot[c]) for c in cols},
            {f"{c[:4]}-{c[4:]}": float(fraud[c]) for c in cols},
            int(df.iloc[:, 2].nunique()))


def build_safety_main():
    import pandas as pd
    (old, old_fraud, nb1), (mid, _f2, nb2), (new, _f3, nb3) = [_crime_totals(rel) for rel, _ in CRIME_FILES]
    rows = []
    for ym in sorted(set(old) | set(mid) | set(new)):
        if ym in new:
            rows.append({"period": ym, "value": new[ym], "source_note": CRIME_FILES[2][1]})
        elif ym in mid:
            rows.append({"period": ym, "value": mid[ym], "source_note": CRIME_FILES[1][1]})
        else:
            rows.append({"period": ym, "value": old[ym], "source_note": CRIME_FILES[0][1]})
    ov = sorted(set(old) & set(mid))
    ratios = [mid[m] / old[m] for m in ov]
    big = {m: round(mid[m] / old[m], 4) for m in ov if abs(mid[m] / old[m] - 1) > 0.005}
    CHECKS["safety_main"] = {
        "geography_rows_per_file": [nb1, nb2, nb3],
        "overlap_months_between_2026-05_and_2026-11_vintages": len(ov),
        "overlap_first": ov[0], "overlap_last": ov[-1],
        "overlap_ratio_new_over_old_min": round(min(ratios), 4),
        "overlap_ratio_new_over_old_max": round(max(ratios), 4),
        "overlap_ratio_new_over_old_mean": round(sum(ratios) / len(ratios), 4),
        "overlap_months_differing_by_more_than_half_percent": big,
        "overlap_between_the_two_2026-11_files": sorted(set(mid) & set(new)),
        "fraud_and_forgery_monthly_2012-03_2013-03_2014-03": [old_fraud.get("2012-03"), old_fraud.get("2013-03"),
                                                             old_fraud.get("2014-03")],
    }
    return pd.DataFrame(rows)


T_NS = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
X_NS = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
O_NS = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"


def ods_rows(path: Path):
    """Stream (sheet, row values) from an .ods file without loading it whole."""
    from lxml import etree
    sheet = None
    with zipfile.ZipFile(path) as z, z.open("content.xml") as f:
        for ev, el in etree.iterparse(f, events=("start", "end"), tag=(T_NS + "table", T_NS + "table-row")):
            if el.tag == T_NS + "table":
                if ev == "start":
                    sheet = el.get(T_NS + "name")
                else:
                    el.clear()
                continue
            if ev != "end":
                continue
            row = []
            for c in el:
                if c.tag not in (T_NS + "table-cell", T_NS + "covered-table-cell"):
                    continue
                rep = int(c.get(T_NS + "number-columns-repeated", "1"))
                v = c.get(O_NS + "value")
                if v is None:
                    v = "".join("".join(p.itertext()) for p in c.iter(X_NS + "p"))
                if rep > 200 and v == "":
                    rep = 1
                row.extend([v] * rep)
            while row and row[-1] == "":
                row.pop()
            yield sheet, row
            el.clear()


HO_FILES = ["homeoffice/prc-pfa-0203-to-0607-tabs.ods", "homeoffice/prc-pfa-mar2008-mar2012-tabs.ods",
            "homeoffice/prc-pfa-mar2013-onwards-tables-221026.ods"]


def build_safety_backup():
    import pandas as pd
    tot: dict = {}
    fraud: dict = {}
    names = set()
    for rel in HO_FILES:
        hdr = None
        for sheet, row in ods_rows(RAW / rel):
            if not re.fullmatch(r"\d{4}[-_]\d{2}", sheet or ""):
                continue
            if row and row[0] == "Financial Year":
                hdr = {h: i for i, h in enumerate(row)}
                continue
            if hdr is None or len(row) < 8:
                continue
            force = row[hdr["Force Name"]]
            if "Metropolitan" not in force:
                continue
            names.add(force)
            fy, fq = row[hdr["Financial Year"]], int(float(row[hdr["Financial Quarter"]]))
            y0 = int(fy[:4])
            period = f"{y0}-Q{fq + 1}" if fq <= 3 else f"{y0 + 1}-Q1"  # financial Q1 = Apr to Jun
            n = float(row[hdr["Number of Offences"]])
            tot[(period, rel)] = tot.get((period, rel), 0.0) + n
            if "fraud" in row[hdr["Offence Group"]].lower():
                fraud[period] = fraud.get(period, 0.0) + n
    periods = sorted({p for p, _ in tot})
    dup = [p for p in periods if sum(1 for q, _ in tot if q == p) > 1]
    rows = [{"period": p, "value": sum(v for (q, _r), v in tot.items() if q == p),
             "source_note": "; ".join(r.split("/")[-1] for (q, r) in tot if q == p)} for p in periods]
    CHECKS["safety_backup"] = {"force_names_matched": sorted(names), "periods_in_more_than_one_file": dup,
                               "fraud_offences_by_quarter_2011-Q2_to_2013-Q4": {
                                   p: fraud.get(p, 0.0) for p in periods if "2011-Q2" <= p <= "2013-Q4"}}
    return pd.DataFrame(rows)


# ---- housing ---------------------------------------------------------------

def build_housing_main():
    import pandas as pd
    p = pd.read_excel(RAW / "ons/pipr_monthly_price_statistics_21october2026.xlsx", sheet_name="Table 1", header=2)
    p = p[p["Area code"] == "E12000007"]
    pipr = {pd.Timestamp(t).strftime("%Y-%m"): float(v) for t, v in zip(p["Time period"], p["Index"])}
    i = pd.read_excel(RAW / "ons/iphrp_reference_table_january2024.xlsx", sheet_name="Table 1", header=None)
    hdr = [str(x).strip() for x in i.iloc[2].tolist()]
    codes = [str(x).strip() for x in i.iloc[3].tolist()]
    col = codes.index("E12000007")
    assert hdr[col] == "London"
    iphrp = {}
    for _, r in i.iloc[4:].iterrows():
        try:
            t = pd.Timestamp(r.iloc[0])
            iphrp[t.strftime("%Y-%m")] = float(r.iloc[col])
        except (ValueError, TypeError):
            continue
    join = "2015-01"
    factor = pipr[join] / iphrp[join]
    rows = []
    for ym in sorted(iphrp):
        if ym < join:
            rows.append({"period": ym, "value": iphrp[ym] * factor,
                         "source_note": f"IPHRP London (Jan 2015=100) x {factor:.8f}"})
    for ym in sorted(pipr):
        rows.append({"period": ym, "value": pipr[ym], "source_note": "PIPR London as published"})
    # how the two indices compare where both exist: 12-month growth, in points
    diffs = []
    for ym in sorted(set(pipr) & set(iphrp)):
        b = ym_add(ym, -12)
        if b in pipr and b in iphrp:
            diffs.append((ym, 100 * (pipr[ym] / pipr[b] - 1) - 100 * (iphrp[ym] / iphrp[b] - 1)))
    CHECKS["housing_main"] = {
        "join_month": join, "pipr_at_join": pipr[join], "iphrp_at_join": iphrp[join], "scale_factor": factor,
        "iphrp_first": min(iphrp), "iphrp_last": max(iphrp), "pipr_first": min(pipr), "pipr_last": max(pipr),
        "overlap_12m_growth_months": len(diffs),
        "overlap_12m_growth_pipr_minus_iphrp_mean_points": round(sum(d for _, d in diffs) / len(diffs), 3),
        "overlap_12m_growth_pipr_minus_iphrp_max_abs_points": round(max(abs(d) for _, d in diffs), 3),
    }
    return pd.DataFrame(rows)


def _ta1_rows(path: Path):
    """Rows of the TA1 sheet of a detailed local authority workbook (.ods or .xlsx)."""
    if path.suffix.lower() == ".ods":
        for sheet, row in ods_rows(path):
            if re.fullmatch(r"TA1_?", (sheet or "").strip(), re.I):
                yield [str(c).strip() for c in row]
    else:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        name = [n for n in wb.sheetnames if re.fullmatch(r"TA1_?", n.strip(), re.I)][0]
        for row in wb[name].iter_rows(values_only=True):
            yield ["" if c is None else str(c).strip() for c in row]
        wb.close()


def _ta1_totals(path: Path):
    """(England total, London total) of households in temporary accommodation at the end of the quarter."""
    col, eng, lon, seen = None, None, None, []
    for row in _ta1_rows(path):
        if eng is None:
            seen.append(row)
        if len(row) > 1 and row[0] == "E92000001" and row[1].upper() == "ENGLAND":
            # the total is the first column whose header names households in temporary accommodation
            for hdr in reversed(seen[:-1]):
                for k, c in enumerate(hdr):
                    if re.search(r"households in (TA|temporary accommodation)", c, re.I) and "per" not in c.lower():
                        col = k
                        break
                if col is not None:
                    break
            if col is None:
                raise ValueError(f"no temporary accommodation total column found in {path.name}")
            eng = float(row[col])
        elif eng is not None and len(row) > 1 and row[0] == "E12000007" and row[1] == "London":
            lon = float(row[col])
            break
    return eng, lon


def build_housing_backup():
    import pandas as pd
    df = pd.read_excel(RAW / "mhclg/Temporary_accommodation2018Q1.xlsx", sheet_name="775_London", header=None)
    rows, year = [], None
    for _, r in df.iterrows():
        y, q, v = r.iloc[0], str(r.iloc[1]).strip(), r.iloc[3]
        if re.fullmatch(r"\d{4}(\.0)?", str(y).strip()):
            year = int(float(y))
        mq = re.fullmatch(r"(Q[1-4])\d*", q)  # the last four quarters carry a footnote digit, e.g. "Q28"
        if year and mq:
            mark = str(r.iloc[2]).strip()
            try:
                rows.append({"period": f"{year}-{mq.group(1)}", "value": float(v),
                             "source_note": "MHCLG live table 775 (London), P1E returns"
                                            + (", marked revised" if mark == "R" else "")})
            except (ValueError, TypeError):
                continue
    old = pd.DataFrame(rows)
    old_last = old.period.max()
    # England totals from the national time series, to cross-check the column picked in each workbook
    eng_ts, eng_status = {}, {}
    ts = RAW / TA_TS_REL
    if ts.exists():
        for sheet, row in ods_rows(ts):
            if sheet == "TA1" and len(row) > 3 and re.fullmatch(r"\d{6}(\.0)?", str(row[1])):
                code = str(row[1])[:6]
                eng_ts[f"{code[:4]}-Q{int(code[4:6]) // 3}"] = float(row[3])
                eng_status[f"{code[:4]}-Q{int(code[4:6]) // 3}"] = str(row[2]).strip()
    new, mismatch, missing_files = [], {}, []
    for q, (url, title) in ta_quarter_files().items():
        path = RAW / "mhclg/detailed_la" / url.rsplit("/", 1)[-1]
        if not path.exists():
            missing_files.append(q)
            continue
        eng, lon = _ta1_totals(path)
        if eng is None or lon is None:
            raise ValueError(f"no England or London row found in table TA1 of {path.name}")
        if q in eng_ts and abs(eng - eng_ts[q]) > 0.5:
            mismatch[q] = [eng, eng_ts[q]]
        if q > old_last and lon is not None:
            new.append({"period": q, "value": lon, "provisional": 1 if eng_status.get(q) == "[p]" else 0,
                        "source_note": f"MHCLG detailed local authority tables, TA1 London row ({path.name}), H-CLIC"})
    CHECKS["housing_backup"] = {
        "table_775_first": old.period.min(), "table_775_last": old_last, "kept_from": "2004-Q1",
        "hclic_quarters_built": len(new), "hclic_first": new[0]["period"] if new else None,
        "hclic_last": new[-1]["period"] if new else None, "quarters_listed_but_file_not_saved": missing_files,
        "england_total_in_workbook_vs_national_time_series_mismatches": mismatch,
        "england_totals_cross_checked": len([q for q in ta_quarter_files() if q in eng_ts]),
    }
    out = pd.concat([old[old.period >= "2004-Q1"], pd.DataFrame(new)], ignore_index=True)
    return out


# ---- transport -------------------------------------------------------------

LONDON_FORCES = [1, 48]  # Metropolitan Police, City of London


def build_transport_main():
    import numpy as np
    import pandas as pd
    parts = []
    for ch in pd.read_csv(RAW / "dft/collision_1979_latest.csv",
                          usecols=["collision_index", "collision_year", "police_force", "date"],
                          dtype={"collision_index": str, "date": str}, chunksize=2_000_000):
        parts.append(ch[(ch.collision_year >= 2004) & (ch.police_force.isin(LONDON_FORCES))])
    col = pd.concat(parts)
    keys = set(col.collision_index)
    parts = []
    for ch in pd.read_csv(RAW / "dft/casualty_1979_latest.csv",
                          usecols=["collision_index", "collision_year", "casualty_severity",
                                   "casualty_adjusted_severity_serious"],
                          dtype={"collision_index": str}, chunksize=2_000_000):
        ch = ch[ch.collision_year >= 2004]
        parts.append(ch[ch.collision_index.isin(keys)])
    cas = pd.concat(parts).merge(col[["collision_index", "date"]], on="collision_index", how="left")
    cas["period"] = pd.to_datetime(cas["date"], format="%d/%m/%Y").dt.strftime("%Y-%m")
    cas["fatal"] = (cas.casualty_severity == 1).astype(float)
    cas["serious_unadj"] = (cas.casualty_severity == 2).astype(float)
    adj = cas.casualty_adjusted_severity_serious
    cas["serious_adj"] = np.where(cas.casualty_severity == 1, 0.0, adj)
    g = cas.groupby("period").agg(fatal=("fatal", "sum"), serious_adj=("serious_adj", "sum"),
                                  serious_unadj=("serious_unadj", "sum"), n=("fatal", "size")).reset_index()
    g["value"] = g.fatal + g.serious_adj
    yr = cas.assign(y=cas.period.str[:4]).groupby("y").agg(
        fatal=("fatal", "sum"), serious_unadj=("serious_unadj", "sum"), serious_adj=("serious_adj", "sum"))
    CHECKS["transport_main"] = {
        "london_collisions_2004_on": int(len(col)), "london_casualties_2004_on": int(len(cas)),
        "casualties_without_a_matching_collision": int(cas["date"].isna().sum()),
        "adjusted_serious_missing_or_negative": int(((adj < 0) | adj.isna()).sum()),
        "yearly_fatal_unadjusted_serious_adjusted_ksi": {
            y: [int(r.fatal), int(r.serious_unadj), round(float(r.fatal + r.serious_adj), 1)]
            for y, r in yr.iterrows()},
    }
    g["source_note"] = "fatal + sum of adjusted serious probabilities"
    return g[["period", "value", "source_note"]]


def build_transport_backup():
    import pandas as pd
    k = pd.read_excel(RAW / "tfl/tfl-tube-performance.xlsx", sheet_name="Key trends", header=None)
    hdr = [str(x).strip() for x in k.iloc[0].tolist()]
    c_days, c_end, c_month, c_lch = (hdr.index("Days in period"), hdr.index("Period ending"),
                                     hdr.index("Month"), hdr.index("Number of Lost Customer Hours"))
    recs, skipped = [], []
    for _, r in k.iloc[1:].iterrows():
        label = str(r.iloc[0]).strip()
        if not re.fullmatch(r"\d{2}_\d{2}/\d{2}", label):
            continue
        try:
            lch = float(r.iloc[c_lch])
        except (ValueError, TypeError):
            skipped.append(f"{label}: {str(r.iloc[c_lch])[:60]}")
            lch = None
        # the workbook is inconsistent about which of two date columns holds the period end;
        # the later of the two is the end in every row (checked below against days in period)
        end = max(pd.Timestamp(r.iloc[c_end]), pd.Timestamp(r.iloc[c_month]))
        days = int(r.iloc[c_days])
        recs.append({"label": label, "end": end, "days": days, "lch": lch})
    bad = [recs[i]["label"] for i in range(1, len(recs))
           if (recs[i]["end"] - recs[i - 1]["end"]).days != recs[i]["days"]]
    agg: dict = {}
    for r in recs:
        if r["lch"] is None:
            continue
        mid = r["end"] - pd.Timedelta(days=(r["days"] - 1) / 2)
        ym = mid.strftime("%Y-%m")
        a = agg.setdefault(ym, {"lch": 0.0, "days": 0, "labels": []})
        a["lch"] += r["lch"]
        a["days"] += r["days"]
        a["labels"].append(r["label"])
    rows = [{"period": ym, "value": a["lch"] / a["days"],
             "source_note": "periods " + "+".join(a["labels"])} for ym, a in sorted(agg.items())]
    CHECKS["transport_backup"] = {
        "periods_read": len(recs), "periods_without_a_valid_value": skipped,
        "periods_where_end_date_minus_previous_end_differs_from_days_in_period": bad,
        "months_holding_two_periods": [ym for ym, a in sorted(agg.items()) if len(a["labels"]) > 1],
    }
    return pd.DataFrame(rows)


# ---- environment -----------------------------------------------------------

AIR_MIN_CAPTURE = 0.5


def air_monthly(site: str, sp: str) -> dict:
    """Monthly mean of hourly readings for one site, with the share of hours that have a reading."""
    hours: dict = {}
    for f in sorted((RAW / "air").glob(f"{site}_{sp}_*.json")):
        d = json.loads(f.read_text())["RawAQData"]
        assert d["@SiteCode"] == site and d["@SpeciesCode"] == sp
        data = d.get("Data") or []
        if isinstance(data, dict):
            data = [data]
        for x in data:
            t, v = x["@MeasurementDateGMT"], x["@Value"]
            if v not in ("", None):
                hours[t] = float(v)
    acc: dict = {}
    for t, v in hours.items():
        a = acc.setdefault(t[:7], [0.0, 0])
        a[0] += v
        a[1] += 1
    out = {}
    for ym, (sm, n) in acc.items():
        total = calendar.monthrange(int(ym[:4]), int(ym[5:7]))[1] * 24
        out[ym] = {"mean": sm / n, "capture": n / total}
    return out


def all_months(first: str, last: str) -> list[str]:
    out, m = [], first
    while m <= last:
        out.append(m)
        m = ym_add(m, 1)
    return out


def _two_site_mean(a: dict, b: dict, name_a: str, name_b: str, first: str, last: str, key: str):
    import pandas as pd
    rows, miss = [], {"both": 0, name_a: 0, name_b: 0}
    low = []
    for ym in all_months(first, last):
        ok = {}
        for nm, d in ((name_a, a), (name_b, b)):
            x = d.get(ym)
            if x is None:
                ok[nm] = None
            elif x["capture"] < AIR_MIN_CAPTURE:
                ok[nm] = None
                low.append(f"{ym} {nm} {x['capture']:.2f}")
            else:
                ok[nm] = x
        if ok[name_a] and ok[name_b]:
            rows.append({"period": ym, "value": (ok[name_a]["mean"] + ok[name_b]["mean"]) / 2,
                         "source_note": f"{name_a} {ok[name_a]['mean']:.1f} ({ok[name_a]['capture']:.0%} of hours); "
                                        f"{name_b} {ok[name_b]['mean']:.1f} ({ok[name_b]['capture']:.0%} of hours)"})
        else:
            which = "both" if not ok[name_a] and not ok[name_b] else (name_a if not ok[name_a] else name_b)
            miss[which] += 1
            rows.append({"period": ym, "value": float("nan"),
                         "source_note": f"missing: {which} below {AIR_MIN_CAPTURE:.0%} of hours or no data"})
    df = pd.DataFrame(rows)
    have = df[df.value.notna()]
    df = df[(df.period >= have.period.min()) & (df.period <= have.period.max())].reset_index(drop=True)
    inside = df[df.value.isna()]
    CHECKS[key] = {"months_in_span": int(len(df)), "months_with_value": int(df.value.notna().sum()),
                   "months_missing_inside_span": int(len(inside)),
                   "missing_months_inside_span": inside.period.tolist(),
                   "site_months_below_capture_threshold": low}
    return df


def build_environment_main():
    return _two_site_mean(air_monthly("MY1", "NO2"), air_monthly("BL0", "NO2"), "MY1", "BL0",
                          "2004-01", LAST_FULL_MONTH, "environment_main")


def build_environment_backup():
    # Site code MY1 carries no PM2.5. Marylebone Road PM2.5 is published under the co-located
    # code MY7 (FDMS instrument, March 2009 to December 2021). MR8 (BAM instrument) is read only
    # to document why it is not joined on.
    my7, mr8 = air_monthly("MY7", "PM25"), air_monthly("MR8", "PM25")
    my1 = air_monthly("MY1", "PM25")
    df = _two_site_mean(my7, air_monthly("BL0", "PM25"), "MY7", "BL0",
                        "2004-01", LAST_FULL_MONTH, "environment_backup")
    ok7 = sorted(ym for ym, v in my7.items() if v["capture"] >= AIR_MIN_CAPTURE)
    ok8 = sorted(ym for ym, v in mr8.items() if v["capture"] >= AIR_MIN_CAPTURE)
    both = sorted(set(ok7) & set(ok8))
    ratios = [mr8[ym]["mean"] / my7[ym]["mean"] for ym in both]
    CHECKS["environment_backup"].update({
        "my1_pm25_months_with_any_reading": len(my1),
        "my7_months_passing_capture": [ok7[0], ok7[-1], len(ok7)] if ok7 else [],
        "mr8_months_passing_capture": [ok8[0], ok8[-1], len(ok8)] if ok8 else [],
        "mr8_months_passing_capture_after_2021-12": len([m for m in ok8 if m > "2021-12"]),
        "my7_mr8_months_both_passing": len(both),
        "mr8_over_my7_mean_ratio": round(sum(ratios) / len(ratios), 3) if ratios else None,
        "mr8_over_my7_ratio_range": [round(min(ratios), 3), round(max(ratios), 3)] if ratios else None,
    })
    return df


def write_air_sites() -> None:
    """Side file: each site's monthly mean and share of hours with a reading."""
    rows = []
    for site, sp in (("MY1", "NO2"), ("BL0", "NO2"), ("MY7", "PM25"), ("MR8", "PM25"), ("BL0", "PM25")):
        for ym, v in sorted(air_monthly(site, sp).items()):
            rows.append([site, sp, ym, repr(v["mean"]), round(v["capture"], 4),
                         int(v["capture"] >= AIR_MIN_CAPTURE)])
    with open(OUT / "london_environment_sites.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site_code", "species", "period", "monthly_mean", "share_of_hours_with_reading",
                    "passes_capture_rule"])
        w.writerows(rows)


# ---- education -------------------------------------------------------------

def _ks4_london(rel: str):
    import pandas as pd
    use = ["time_period", "geographic_level", "region_code", "version", "establishment_type_group",
           "breakdown_topic", "sex", "pupil_count", "attainment8_average"]
    parts = []
    for ch in pd.read_csv(RAW / rel, usecols=use, dtype=str, chunksize=200_000):
        parts.append(ch[(ch.geographic_level == "Regional") & (ch.region_code == "E12000007")
                        & (ch.breakdown_topic == "Total") & (ch.sex == "Total")])
    t = pd.concat(parts)
    assert t.time_period.is_unique and set(t.establishment_type_group) == {"All state-funded"}
    return {tp: (float(v), ver, pc) for tp, v, ver, pc in
            zip(t.time_period, t.attainment8_average, t.version, t.pupil_count)}


def _gla_attainment8() -> dict:
    """London Attainment 8 by school year from the GLA workbook (one sheet per year, named like 2015-16)."""
    import openpyxl
    out = {}
    wb = openpyxl.load_workbook(RAW / "lds/gcse_results_by_sex.xlsx", read_only=True, data_only=True)
    for ws in wb.worksheets:
        if not re.fullmatch(r"\d{4}-\d{2}", ws.title.strip()):
            continue
        col = None
        for row in ws.iter_rows(values_only=True):
            cells = ["" if c is None else str(c).strip() for c in row]
            if col is None:
                hits = [k for k, c in enumerate(cells) if c.startswith("Average Attainment 8 score")]
                if hits:
                    col = hits[0]  # the first block of columns is all pupils
                continue
            if cells and cells[0] == "E12000007":
                out[ws.title.strip().replace("-", "")] = float(cells[col])
                break
    wb.close()
    return out


def build_education_main():
    import pandas as pd
    named = _ks4_london(DFE_KS4_REL)            # the data set named in the methodology (2024/25 revised)
    newer = _ks4_london(DFE_KS4_NEW_REL) if (RAW / DFE_KS4_NEW_REL).exists() else {}
    gla = _gla_attainment8() if (RAW / "lds/gcse_results_by_sex.xlsx").exists() else {}
    rows = []
    for tp in sorted(set(named) | set(newer) | set(gla)):
        period = str(int(tp[:4]) + 1)
        label = f"school year {tp[:4]}/{tp[4:]}"
        if tp in named:
            v, ver, pc = named[tp]
            rows.append({"period": period, "value": v, "provisional": 0,
                         "source_note": f"{label}, DfE data set named in the methodology, {ver}, {pc} pupils"})
        elif tp in newer:
            v, ver, pc = newer[tp]
            rows.append({"period": period, "value": v, "provisional": 1 if ver == "Provisional" else 0,
                         "source_note": f"{label}, DfE 2025/26 release of the same data set, {ver}, {pc} pupils"})
        else:
            rows.append({"period": period, "value": gla[tp], "provisional": 0,
                         "source_note": f"{label}, London Datastore workbook of DfE figures (sheet {tp[:4]}-{tp[4:]})"})
    both_new = sorted(set(named) & set(newer))
    both_gla = sorted(set(named) & set(gla))
    CHECKS["education_main"] = {
        "years_in_named_dfe_file": sorted(named), "versions_in_named_dfe_file": {k: v[1] for k, v in named.items()},
        "years_only_in_2025_26_release": {k: [newer[k][0], newer[k][1]] for k in sorted(set(newer) - set(named))},
        "years_only_in_gla_workbook": {k: gla[k] for k in sorted(set(gla) - set(named) - set(newer))},
        "overlap_named_vs_2025_26_release_years": len(both_new),
        "overlap_named_vs_2025_26_release_differences": {k: [named[k][0], newer[k][0]] for k in both_new
                                                         if abs(named[k][0] - newer[k][0]) > 1e-9},
        "overlap_named_vs_gla_years": len(both_gla),
        "overlap_named_vs_gla_differences": {k: [named[k][0], gla[k]] for k in both_gla
                                             if abs(named[k][0] - gla[k]) > 1e-9},
    }
    return pd.DataFrame(rows)


def build_education_backup():
    import pandas as pd
    a = pd.read_csv(RAW / DFE_ABSENCE_REL, dtype=str)
    t = a[(a.geographic_level == "Regional") & (a.region_code == "E12000007")
          & (a.phase_type_grouping == "Total") & (a.attendance_status == "Absence")
          & (a.attendance_type == "Overall absence") & (a.attendance_reason == "Overall absence")]
    assert t.time_period.is_unique and len(t) > 0
    rows = [{"period": str(int(tp[:4]) + 1), "value": float(v),
             "source_note": f"school year {tp[:4]}/{tp[4:]}, {n} sessions missed"}
            for tp, v, n in zip(t.time_period, t.session_percent, t.session_count)]
    CHECKS["education_backup"] = {"school_years": sorted(t.time_period.tolist()),
                                  "time_identifier": sorted(t.time_identifier.unique().tolist())}
    return pd.DataFrame(rows)


# ---- registry --------------------------------------------------------------

ULEZ = [point_break("2019-04", "Ultra Low Emission Zone started in central London", "event"),
        point_break("2021-10", "Ultra Low Emission Zone expanded to the North and South Circular roads", "event"),
        point_break("2023-08", "Ultra Low Emission Zone expanded to all London boroughs", "event")]
CRIME_BREAKS = [
    point_break("2013-02", "fraud offences moved from police forces to Action Fraud; the source note says March "
                           "2013 and the counts fall in February 2013 (found tonight; not in the "
                           "methodology's breaks table)"),
    point_break("2019-03", "Metropolitan Police crime categories changed"),
    point_break("2024-02", "Metropolitan Police recording system changed (CONNECT)"),
]
NHS_PAGES = {
    "rtt": "https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/",
    "ae": "https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/",
}
CAT_ORDER = ["safety", "economy", "housing", "transport", "environment", "health", "education", "cost_of_living"]


def series_specs() -> list[dict]:
    S = []

    def add(category, role, **kw):
        kw.update(category=category, role=role, series_id=f"london_{category}_{role}")
        kw.setdefault("breaks", [])
        kw.setdefault("fallback_used", None)
        kw.setdefault("builder", None)
        S.append(kw)

    add("safety", "main",
        indicator_name="Recorded crime, all offences, Metropolitan Police",
        frequency="M", window_months=1, unit="offences per month", worse_when="higher", change_rule="pct_log",
        builder=build_safety_main, breaks=CRIME_BREAKS, release_lag_months=1,
        source_urls=["https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m"]
                    + [u for r, u, _ in SMALL_FILES if r.startswith("crime/mps_")],
        expected_first="2010-04", expected_last="2026-10",
        construction="Sum of every offence row (all categories, all boroughs, plus the airport and 'Unknown' rows) "
                     "in the Met's borough-level files on the London Datastore, by month. Three files are joined: "
                     "the historical file published 5 May 2026 (the last one carrying the full history) for April "
                     "2010 to October 2020, the historical file published 6 November 2026 for November 2020 to "
                     "October 2024, and the last-24-months file published the same day for November 2024 to "
                     "October 2026. Where the May and November vintages overlap they were compared month by month.",
        caveats="Starts April 2010, not 2008: no file with the older categories is on the Datastore now. Excludes "
                "the City of London. Counts are revised every month, so the join mixes a May 2026 vintage with a "
                "November 2026 vintage. Fraud offences left the count in 2013. Since June 2026 the historical file "
                "only keeps a rolling 48 months.")
    add("economy", "main",
        indicator_name="Unemployment rate, London, aged 16 and over, seasonally adjusted (ONS YCNI)",
        frequency="M", window_months=3, unit="percent", worse_when="higher", change_rule="points",
        builder=build_economy_main, release_lag_months=2,
        breaks=[point_break("2019-01", "Labour Force Survey reweighted"),
                span_break("2023-01", "2024-12", "Labour Force Survey response problems")],
        source_urls=[SMALL_FILES[0][1]], expected_first="1992-05", expected_last="2026-09",
        construction="Monthly rolling three-month observations of ONS series YCNI from the time series "
                     "generator. ONS labels each one with the middle month of the three, so the period here is "
                     "the label plus one month (the end month). The build checks that every quarterly value "
                     "equals the monthly value labelled with the quarter's middle month.",
        caveats="Regional Labour Force Survey estimates are noisy. Response problems in 2023 and 2024. "
                "Each value covers three months, so neighbouring values share two months of data.")
    add("housing", "main",
        indicator_name="Private rents index, London (ONS PIPR, with IPHRP joined on before 2015)",
        frequency="M", window_months=1, unit="index (PIPR reference scale)", worse_when="faster",
        change_rule="inflation_points", builder=build_housing_main, release_lag_months=1,
        breaks=[span_break("2015-01", "2016-12", "older rent index (IPHRP) joined to the current one (PIPR) at "
                           "January 2015; 24 months are flagged because the 12-month rent increase through "
                           "December 2015 mixes the two indices and its yearly change runs through December 2016")],
        source_urls=[SMALL_FILES[3][1], SMALL_FILES[4][1]], expected_first="2005-01", expected_last="2026-09",
        construction="January 2015 onward is the London index from the ONS Price Index of Private Rents, as "
                     "published. January 2005 to December 2014 is the London index from the discontinued ONS "
                     "Index of Private Housing Rental Prices, multiplied by one constant so the two indices are "
                     "equal in January 2015 (the first month both exist). The source_note column says which "
                     "index each month came from.",
        caveats="Two methods joined. The older index tracked the stock of rents more smoothly than the current "
                "one. Covers existing tenancies as well as new lets, so it lags the market for new lets.")
    add("transport", "main",
        indicator_name="Killed or seriously injured road casualties, London, severity-adjusted (DfT)",
        frequency="M", window_months=1, unit="casualties per month (adjusted)", worse_when="higher",
        change_rule="pct_log", builder=build_transport_main, release_lag_months=9,
        source_urls=[DFT_BASE + n for n in DFT_FILES.values()]
                    + ["https://www.gov.uk/government/statistics/road-safety-data"],
        expected_first="2004-01", expected_last="2025-12",
        construction="From the DfT open data casualty and collision files: casualties in collisions recorded by "
                     "the Metropolitan Police (force 1) or the City of London Police (force 48), counted in the "
                     "month of the collision date. The value is the number of fatal casualties plus the sum of "
                     "DfT's adjusted probability of being serious for every non-fatal casualty.",
        caveats="Starts 2004 because the adjusted figures do not exist before then (the methodology says 1979). "
                "Ends December 2025: DfT releases a full year once a year, so the lag runs from 9 to 20 months. "
                "The Met moved to injury-based reporting in November 2016; the adjustment is DfT's model of "
                "what earlier years would have shown, so it is an estimate made by DfT.")
    add("environment", "main",
        indicator_name="Nitrogen dioxide, mean of Marylebone Road and Bloomsbury (London Air Quality Network)",
        frequency="M", window_months=1, unit="micrograms per cubic metre", worse_when="higher",
        change_rule="pct_log", builder=build_environment_main, breaks=ULEZ, release_lag_months=0,
        source_urls=[AIR_API.format(site="MY1", sp="NO2", a="YYYY-01-01", b="YYYY-01-01"),
                     AIR_API.format(site="BL0", sp="NO2", a="YYYY-01-01", b="YYYY-01-01")],
        expected_first="2004-01", expected_last="2026-10",
        construction="Hourly readings for site codes MY1 and BL0 were fetched year by year. Each site's monthly "
                     "mean is the mean of its hours with a reading, kept only if at least half the hours in the "
                     "month have one. The value is the plain mean of the two site means. If either site fails "
                     "the test the month is left empty.",
        caveats="Two sites stand in for the city. Fetched from 2004 (the sites go back to 1997 and 1992). Recent "
                "months may not be ratified yet. The API's site list gives a wrong start date for Bloomsbury NO2.")
    add("health", "main",
        indicator_name="Waiting list: share waiting under 18 weeks, London region (NHS England RTT)",
        frequency="M", window_months=1, unit="percent", worse_when="lower", change_rule="points",
        release_lag_months=2, source_urls=[NHS_PAGES["rtt"]],
        fallback_used="None possible: the backup is published on the same site and is also missing.",
        expected_first="2007-08", expected_last="2026-09",
        construction="Not built. The plan was total incomplete pathways within 18 weeks divided by total "
                     "incomplete pathways for the London region row of each monthly commissioner workbook.",
        caveats="NHS England's statistics pages answer scripted requests with a browser challenge, so the "
                "collection stopped there. The backup comes from the same site, so London has no official "
                "Health series tonight.")
    add("education", "main",
        indicator_name="Attainment 8 average score, London region, state-funded schools (DfE)",
        frequency="A", window_months=12, unit="score points", worse_when="lower", change_rule="points",
        school_year=True, builder=build_education_main, release_lag_months=6,
        breaks=[span_break("2016-09", "2017-08", "GCSE grading changed (2017)"),
                span_break("2019-09", "2021-08", "teacher-assessed grades (2020 and 2021)"),
                span_break("2021-09", "2022-08", "exams returned: the 2022 comparison is against a "
                                                 "teacher-assessed year")],
        source_urls=["https://explore-education-statistics.service.gov.uk/data-catalogue/data-set/"
                     "9e761bdf-fe02-4e1e-9d3d-b32dac9fa6ef", DFE_KS4_URL, DFE_API + DFE_KS4_NEW_ID + "/csv",
                     "https://data.london.gov.uk/dataset/gcse-results-by-borough-20pd9"],
        expected_first="2016", expected_last="2026",
        fallback_used="School years 2015/16 to 2017/18 come from the Greater London Authority's London "
                      "Datastore workbook of DfE figures, because the DfE data set starts at 2018/19. "
                      "2025/26 comes from the newer release of the same DfE data set.",
        construction="2018/19 to 2024/25: the London regional row for all pupils (breakdown Total, sex Total, "
                     "all state-funded schools), column attainment8_average, in the DfE key stage 4 data set "
                     "named in the methodology. 2025/26: the same row in the 2025/26 release of that data set. "
                     "2015/16 to 2017/18: the London row of the 'Average Attainment 8 score' column for all "
                     "pupils in the London Datastore workbook, whose figures equal the DfE file in every year "
                     "both cover. The period is the year the school year ends.",
        caveats="Three sources stand behind ten or eleven points. 2025/26 is provisional. 2024/25 is the "
                "revised figure. The 2015/16 score was computed on the old A* to G point scale, so 2016 and "
                "2017 are not on the same footing. In the Datastore workbook the title cell of the older "
                "sheets wrongly reads 2023/24; the sheet names carry the year.")
    add("cost_of_living", "main",
        indicator_name="CPI 12-month rate, all items, UK (ONS D7G7)",
        frequency="M", window_months=1, unit="percent", worse_when="higher", change_rule="points",
        builder=build_cost_of_living_main, release_lag_months=1,
        source_urls=[SMALL_FILES[2][1]], expected_first="1989-01", expected_last="2026-09",
        construction="Monthly observations of ONS series D7G7 from the time series generator, as published. "
                     "It is already a 12-month rate, so the yearly change is taken in points.",
        caveats="UK-wide, not London: no London price index exists. Includes some rent. The October 2026 "
                "figure was due on 18 November 2026, after this run.")
    # ---- backups
    add("safety", "backup",
        indicator_name="Police recorded crime, all offences, Metropolitan Police force area (Home Office)",
        frequency="Q", window_months=3, unit="offences per quarter", worse_when="higher", change_rule="pct_log",
        builder=build_safety_backup, breaks=CRIME_BREAKS, release_lag_months=4,
        source_urls=["https://www.gov.uk/government/statistical-data-sets/"
                     "police-recorded-crime-and-outcomes-open-data-tables"]
                    + [u for r, u, _ in SMALL_FILES if r.startswith("homeoffice/prc")],
        expected_first="2002-Q2", expected_last="2026-Q2",
        construction="Sum of 'Number of Offences' over every offence code for the force 'Metropolitan Police' "
                     "in the three Home Office police force area open data workbooks, by financial quarter, "
                     "relabelled to calendar quarters (financial quarter 1 is April to June).",
        caveats="Includes fraud until it moved to Action Fraud. Quarters can be revised and can hold negative "
                "counts for single offence codes. The March 2019 category change belongs to the Met's own "
                "publication and is marked here only because the breaks table lists it under Safety. The "
                "Home Office notes say the 2024 system change closed dormant records and revised 2023/24.")
    add("economy", "backup",
        indicator_name="Claimant count, London, seasonally adjusted (ONS DPDK)",
        frequency="M", window_months=1, unit="thousand people", worse_when="higher", change_rule="pct_log",
        builder=build_economy_backup, release_lag_months=1,
        source_urls=[SMALL_FILES[1][1]], expected_first="1974-04", expected_last="2026-10",
        construction="Monthly observations of ONS series DPDK in dataset UNEM from the time series generator, "
                     "as published: claimant count, London, people, seasonally adjusted, in thousands.",
        caveats="An administrative count of people claiming unemployment-related benefits, not a survey. The "
                "move to Universal Credit widened who is counted; that is general knowledge about the series "
                "and was not checked against ONS documentation tonight, so no break is marked.")
    add("housing", "backup",
        indicator_name="Households in temporary accommodation, London, end of quarter (MHCLG)",
        frequency="Q", window_months=3, unit="households", worse_when="higher", change_rule="pct_log",
        builder=build_housing_backup, release_lag_months=5,
        breaks=[span_break("2018-04", "2020-06", "council returns (P1E) replaced by case-level records (H-CLIC) "
                           "from April 2018; found in the source tonight, not in the methodology's breaks table")],
        source_urls=["https://www.gov.uk/government/statistical-data-sets/live-tables-on-homelessness",
                     SMALL_FILES[14][1], TA_TS_URL],
        expected_first="2004-Q1", expected_last="2026-Q1",
        construction="To the first quarter of 2018: the London total in MHCLG live table 775 (households in "
                     "temporary accommodation at the end of each quarter), from the final edition of that table. "
                     "From the third quarter of 2019: the London row of table TA1 in each quarter's detailed "
                     "local authority workbook, taking the revised edition where one is listed. The England "
                     "total read from the same column is checked against MHCLG's national time series.",
        caveats="Five quarters are missing (April 2018 to June 2019): MHCLG lists no quarterly workbook with a "
                "London total for them. The two halves come from different collection systems. A snapshot at "
                "quarter end, not a flow. Totals include MHCLG's estimates for councils that did not report. "
                "The latest quarter is marked provisional by MHCLG.")
    add("transport", "backup",
        indicator_name="London Underground lost customer hours per day (TfL)",
        frequency="M", window_months=1, unit="lost customer hours per day", worse_when="higher",
        change_rule="pct_log", builder=build_transport_backup, release_lag_months=2,
        source_urls=["https://data.london.gov.uk/dataset/london-underground-performance-reports-em8qy",
                     SMALL_FILES[16][1]],
        expected_first="2011-05", expected_last="2020-02",
        construction="TfL reports lost customer hours for 13 four-week periods a year. Each period is assigned "
                     "to the calendar month that holds its midpoint, and the value is the period's lost "
                     "customer hours divided by its days. In the one month a year that holds two periods, both "
                     "are pooled (total hours over total days).",
        caveats="Four-week periods mapped to months, so a month's value can include days from the months "
                "either side. The file stops in March 2020 and TfL marks the last period as not valid. Not "
                "updated since. Figures are modelled by TfL from delays and passenger demand.")
    add("environment", "backup",
        indicator_name="PM2.5, mean of Marylebone Road and Bloomsbury (London Air Quality Network)",
        frequency="M", window_months=1, unit="micrograms per cubic metre", worse_when="higher",
        change_rule="pct_log", builder=build_environment_backup, release_lag_months=0, breaks=ULEZ,
        fallback_used="Marylebone Road PM2.5 is read from site code MY7, because MY1 carries no PM2.5.",
        source_urls=[AIR_API.format(site=x, sp="PM25", a="YYYY-01-01", b="YYYY-01-01")
                     for x in ("BL0", "MY7", "MR8", "MY1")],
        expected_first="2004-01", expected_last="2026-10",
        construction="Same construction as the NO2 series, with one change. Site code MY1 carries no PM2.5, "
                     "so Marylebone Road uses the co-located code MY7. Each site's monthly mean needs readings "
                     "for at least half the hours in the month; the value is the mean of the two sites, and "
                     "it is empty if either is missing.",
        caveats="Runs only from 2009 to 2021: MY7 started PM2.5 in March 2009 and closed in December 2021. "
                "The newer Marylebone Road code MR8 was not joined on: in the months both passed the capture "
                "rule it read about a third higher than MY7, and it has almost no readings after November "
                "2022. Instruments at Bloomsbury also changed over the years.")
    add("health", "backup",
        indicator_name="A&E four-hour performance, London region (NHS England)",
        frequency="M", window_months=1, unit="percent", worse_when="lower", change_rule="points",
        release_lag_months=1, source_urls=[NHS_PAGES["ae"]],
        expected_first="2015-06", expected_last="2026-10",
        construction="Not built. The plan was attendances seen within four hours divided by all attendances "
                     "for providers in the London region, from the monthly provider files.",
        caveats="Same site and same browser challenge as the main Health indicator.")
    add("education", "backup",
        indicator_name="Overall absence rate, London, state-funded primary, secondary and special schools (DfE)",
        frequency="A", window_months=12, unit="percent of possible sessions", worse_when="higher",
        change_rule="points", school_year=True, builder=build_education_backup, release_lag_months=7,
        source_urls=["https://explore-education-statistics.service.gov.uk/find-statistics/"
                     "pupil-absence-in-schools-in-england", DFE_API + DFE_ABSENCE_ID + "/csv"],
        expected_first="2007", expected_last="2025",
        construction="The London regional row of the DfE data set 'Absence sessions by reason' with school "
                     "type Total, attendance status Absence, attendance type Overall absence and reason Overall "
                     "absence, column session_percent. The period is the year the school year ends.",
        caveats="The data set has no 2019/20 school year, so that year is missing. How absence linked to "
                "COVID was recorded in 2020/21 and 2021/22 was not checked against DfE documentation tonight.")
    return S


def period_range(first: str, last: str, freq: str) -> list[str]:
    if freq == "M":
        return all_months(first, last)
    if freq == "A":
        return [str(y) for y in range(int(first), int(last) + 1)]
    out, (y, q) = [], (int(first[:4]), int(first[-1]))
    while f"{y}-Q{q}" <= last:
        out.append(f"{y}-Q{q}")
        y, q = (y, q + 1) if q < 4 else (y + 1, 1)
    return out


def plot_series(spec: dict, rows: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    x = pd.to_datetime([r["period_end_date"] for r in rows])
    y = [float(r["value"]) if r["value"] != "" else float("nan") for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=110)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    flagged = [r["break_flag"] == 1 for r in rows]
    start = None
    step = {"M": 31, "Q": 92, "A": 366}[spec["frequency"]]
    for i, f in enumerate(flagged + [False]):
        if f and start is None:
            start = i
        if not f and start is not None:
            ax.axvspan(x[start] - pd.Timedelta(days=step), x[i - 1], color="#52514e", alpha=0.12, lw=0)
            start = None
    marker = "o" if len(rows) < 60 else None
    ax.plot(x, y, color="#2a78d6", lw=1.6, marker=marker, ms=4)
    ax.set_title(f"{spec['series_id']}: {spec['indicator_name']}", fontsize=10, loc="left", color="#0b0b0b")
    ax.set_ylabel(spec["unit"], fontsize=9, color="#52514e")
    ax.grid(True, axis="y", color="#52514e", alpha=0.15, lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#52514e")
    ax.tick_params(colors="#52514e", labelsize=8)
    n = sum(1 for v in y if v == v)
    fig.text(0.01, 0.01, f"{rows[0]['period']} to {rows[-1]['period']}, {n} values. "
                         f"Grey bands: periods flagged for a marked break. Worse when {spec['worse_when']}.",
             fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(PLOTS / f"london_{spec['category']}_{spec['role']}.png")
    plt.close(fig)


def run_build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    all_rows, meta = [], []
    for spec in series_specs():
        sid = spec["series_id"]
        rows, status, problem = [], "missing", None
        if spec["builder"] is not None:
            try:
                df = spec["builder"]()
            except FileNotFoundError as e:
                df, problem = None, f"raw file not found: {e.filename}"
            if df is not None and len(df):
                df = df.sort_values("period").reset_index(drop=True)
                assert df.period.is_unique, f"{sid}: duplicate periods"
                # a period with no figure inside the span gets a row with an empty value, never a filled one
                got = set(df.period)
                holes = [p for p in period_range(df.period.min(), df.period.max(), spec["frequency"])
                         if p not in got]
                if holes:
                    import pandas as pd
                    df = pd.concat([df, pd.DataFrame([{"period": p, "value": float("nan"),
                                                       "source_note": "missing: no figure in the source files"}
                                                      for p in holes])], ignore_index=True)
                    df = df.sort_values("period").reset_index(drop=True)
                rows = tidy(spec, df)
        have = [r for r in rows if r["value"] != ""]
        if have:
            first, last = have[0]["period"], have[-1]["period"]
            got = {r["period"] for r in have}
            gaps = [p for p in period_range(first, last, spec["frequency"]) if p not in got]
            late_start = spec["expected_first"] is not None and first > spec["expected_first"]
            early_end = spec["expected_last"] is not None and last < spec["expected_last"]
            status = "partial" if (late_start or early_end or gaps) else "ok"
            CHECKS.setdefault(sid.replace("london_", ""), {}).update(
                {"first": first, "last": last, "n_obs": len(have), "periods_missing_inside_span": len(gaps),
                 "periods_missing_inside_span_list": gaps[:60],
                 "expected_first": spec["expected_first"], "expected_last": spec["expected_last"],
                 "min": min(float(r["value"]) for r in have), "max": max(float(r["value"]) for r in have),
                 "flagged_periods": sum(r["break_flag"] for r in rows)})
            plot_series(spec, rows)
        all_rows.extend(rows)
        meta.append({
            "series_id": sid, "category": spec["category"], "role": spec["role"],
            "indicator_name": spec["indicator_name"], "components": [],
            "frequency": spec["frequency"], "window_months": spec["window_months"], "unit": spec["unit"],
            "worse_when": spec["worse_when"], "change_rule": spec["change_rule"],
            "source_urls": spec["source_urls"],
            "first_period": have[0]["period"] if have else None,
            "last_period": have[-1]["period"] if have else None,
            "n_obs": len(have), "release_lag_months": spec["release_lag_months"],
            "status": status, "fallback_used": spec["fallback_used"],
            "construction": spec["construction"],
            "breaks": spec["breaks"] if have else [],
            "caveats": spec["caveats"] + (f" Build problem: {problem}." if problem else ""),
        })
        print(f"{sid:32s} {status:8s} {have[0]['period'] if have else '-':8s} "
              f"{have[-1]['period'] if have else '-':8s} n={len(have)}", flush=True)
    order = {c: i for i, c in enumerate(CAT_ORDER)}
    all_rows.sort(key=lambda r: (r["role"] != "main", order[r["category"]], r["period"]))
    with open(OUT / "london_official.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(all_rows)
    (OUT / "london_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_air_sites()
    (OUT / "london_build_checks.json").write_text(
        json.dumps(CHECKS, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(all_rows)} rows", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--air-pairs", default="")
    args = ap.parse_args()
    if args.download:
        for name, fn in DOWNLOADERS.items():
            if args.only and name not in args.only.split(","):
                continue
            if name == "air":
                fn(args.air_pairs)
            else:
                fn()
        return
    run_build()


if __name__ == "__main__":
    main()
