#!/usr/bin/env python
"""Official indicators for New York City (city code: nyc).

Usage
  python src/official/nyc.py --download   fetch raw files (skips files already saved)
  python src/official/nyc.py              rebuild all outputs from the saved raw files (offline)

Raw files are saved unchanged under data/raw/official/nyc/ and listed in
data/raw/official/nyc/manifest.csv. Nothing is estimated, interpolated or filled in.
"""
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

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "official" / "nyc"
OUT = ROOT / "data" / "interim" / "official"
PLOTS = OUT / "plots"
MANIFEST = RAW / "manifest.csv"
UA = "Mozilla/5.0 (research data fetch)"

NYC = "https://data.cityofnewyork.us/resource/"
NYS = "https://data.ny.gov/resource/"
CDC = "https://data.cdc.gov/resource/"
EPA = "https://aqs.epa.gov/aqsweb/airdata/"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
INFOHUB = "https://infohub.nyced.org/docs/default-source/default-document-library/"

EPA_FIRST_YEAR = 1999
EPA_LAST_YEAR = 2026
LAST_FULL_MONTH = "2026-10"  # fixed for this run (see STATE.md); later months are dropped as incomplete
NYC_COUNTIES = {"005": "Bronx", "047": "Kings", "061": "New York", "081": "Queens", "085": "Richmond"}

FELONY_Q = {
    "$select": "date_trunc_ym(rpt_dt) as month,count(*) as n",
    "$where": "law_cat_cd='FELONY'",
    "$group": "month",
    "$order": "month",
    "$limit": "50000",
}
SHOOT_Q = {
    "$select": "date_trunc_ym(occur_date) as month,count(*) as n_rows,count(distinct incident_key) as incidents",
    "$group": "month",
    "$order": "month",
    "$limit": "50000",
}
DHS_Q = {
    "$select": "date_trunc_ym(date_of_census) as month,avg(total_individuals_in_shelter) as avg_individuals,"
               "count(*) as n_rows,count(distinct date_of_census) as n_days,"
               "min(total_individuals_in_shelter) as min_individuals,max(total_individuals_in_shelter) as max_individuals",
    "$group": "month",
    "$order": "month",
    "$limit": "50000",
}
ATT_SELECT = ("schoolyear,sum(enrolled) as enrolled,sum(present) as present,sum(absent) as absent,"
              "sum(released) as released,count(*) as n_rows,count(distinct date) as n_dates")
ATT_SELECT_TEXT = ("schoolyear,sum(enrolled::number) as enrolled,sum(present::number) as present,"
                   "sum(absent::number) as absent,sum(released::number) as released,"
                   "count(*) as n_rows,count(distinct date) as n_dates")


def att_q(select):
    return {"$select": select, "$group": "schoolyear", "$order": "schoolyear", "$limit": "50000"}


# (relative path under RAW, url, params or None, note)
DOWNLOADS = [
    # ---- safety
    ("safety/nypd_complaints_historic_qgea-i56i_felony_by_report_month.json", NYC + "qgea-i56i.json", FELONY_Q,
     "NYPD Complaint Data Historic; server-side count of felony complaints by report month"),
    ("safety/nypd_complaints_ytd_5uac-w243_felony_by_report_month.json", NYC + "5uac-w243.json", FELONY_Q,
     "NYPD Complaint Data Current (Year To Date); server-side count of felony complaints by report month"),
    ("safety/nypd_shootings_archived_historic_833y-fsy8_by_month.json", NYC + "833y-fsy8.json", SHOOT_Q,
     "ARCHIVED NYPD Shooting Incident Data (Historic); rows are victims; incidents = distinct incident_key; by occurrence month"),
    ("safety/nypd_shootings_2006_present_5ucz-vwe8_by_month.json", NYC + "5ucz-vwe8.json", SHOOT_Q,
     "Shootings (2006-Present), formerly the year-to-date file; one row per incident; by occurrence month"),
    # ---- economy
    ("economy/nysdol_laus_sa_dh9m-5v4d_new_york_city.json", NYS + "dh9m-5v4d.json",
     {"$where": "area='New York City'", "$order": "year,month", "$limit": "50000"},
     "NYS DOL LAUS seasonally adjusted, area New York City, all rows"),
    ("economy/fred_SMS36935610000000001.csv", FRED + "SMS36935610000000001", None,
     "FRED: All Employees, Total Nonfarm, New York City, seasonally adjusted (BLS CES state and area)"),
    ("economy/fred_series_page_SMS36935610000000001.html", "https://fred.stlouisfed.org/series/SMS36935610000000001", None,
     "FRED series page, saved to document the series title, units and source"),
    # ---- housing
    ("housing/dhs_daily_report_historical_dwrg-kzni_monthly_avg.json", NYC + "dwrg-kzni.json", DHS_Q,
     "DHS Daily Report (Historical), 2013-08-21 to 2021-02-28; server-side monthly average of total individuals in shelter"),
    ("housing/dhs_daily_report_k46n-sa2m_monthly_avg.json", NYC + "k46n-sa2m.json", DHS_Q,
     "DHS Daily Report, from 2021-03-01; server-side monthly average of total individuals in shelter"),
    ("housing/coalition_for_the_homeless_shelter_population_worksheet_1983_present_202611.pdf",
     "https://www.coalitionforthehomeless.org/wp-content/uploads/2026/11/NYCHomelessShelterPopulationWorksheet1983Present_202611.pdf",
     None, "Coalition for the Homeless worksheet: NYC homeless municipal shelter population, monthly, 1983 to present"),
    ("housing/coalition_for_the_homeless_dhs_hpd_census_page.html", "https://www.coalitionforthehomeless.org/dhs-hpd-census/",
     None, "Page that links the worksheet; saved to document where the file came from"),
    ("housing/fred_CUURA101SEHA.csv", FRED + "CUURA101SEHA", None,
     "FRED: CPI-U rent of primary residence, New York-Newark-Jersey City, not seasonally adjusted"),
    # ---- transport
    ("transport/mta_kpi_2008_2021_cy9b-i9w9_subway_terminal_otp.json", NYS + "cy9b-i9w9.json",
     {"$where": "agency_name='NYC Transit' AND indicator_name='On-Time Performance (Terminal)'",
      "$order": "period", "$limit": "50000"},
     "MTA Key Performance Indicators 2008-2021: NYC Transit subway weekday terminal on-time performance, system-wide"),
    ("transport/mta_subway_terminal_otp_f6rf-2a3t_by_month_daytype.json", NYS + "f6rf-2a3t.json",
     {"$select": "month,day_type,sum(num_on_time_trips) as on_time_trips,sum(num_sched_trips) as sched_trips,count(*) as n_lines",
      "$group": "month,day_type", "$order": "month,day_type", "$limit": "50000"},
     "MTA Subway Terminal On-Time Performance: Beginning 2015; server-side sums of on-time and scheduled trips across lines"),
    ("transport/nypd_motor_vehicle_collisions_h9gi-nx95_by_month.json", NYC + "h9gi-nx95.json",
     {"$select": "date_trunc_ym(crash_date) as month,sum(number_of_persons_injured) as injured,"
                 "sum(number_of_persons_killed) as killed,count(*) as crashes",
      "$group": "month", "$order": "month", "$limit": "50000"},
     "NYPD Motor Vehicle Collisions - Crashes; server-side monthly sums of persons injured and killed"),
    # ---- health
    ("health/cdc_r8kw-7aab_new_york_city_by_month.json", CDC + "r8kw-7aab.json",
     {"$where": "state='New York City' AND `group`='By Month'", "$order": "start_date", "$limit": "50000"},
     "CDC NCHS Provisional COVID-19 Death Counts by Week Ending Date and State; New York City; By Month rows (total_deaths = all causes)"),
    ("health/cdc_vsrr_xkb8-kh2a_new_york_city.json", CDC + "xkb8-kh2a.json",
     {"$where": "state='YC' AND indicator in ('Number of Drug Overdose Deaths','Number of Deaths','Percent with drugs specified')",
      "$order": "indicator,year,month", "$limit": "50000"},
     "CDC VSRR Provisional Drug Overdose Death Counts; New York City (YC); 12 month-ending counts"),
    # ---- education
    ("education/nycdoe_2001-2011-graduation_rates_public_citywide.xlsx",
     INFOHUB + "2001-2011-graduation_rates_public_citywide.xlsx", None,
     "NYC DOE citywide graduation results, cohorts 2001 to 2011 (classes of 2005 to 2015)"),
    ("education/nycdoe_2025-graduation-rates-public-citywide.xlsx",
     INFOHUB + "2025-graduation-rates-public-citywide.xlsx", None,
     "NYC DOE citywide graduation results, latest file (through the class of 2025)"),
    ("education/nycdoe_graduation_results_page.html",
     "https://infohub.nyced.org/reports-and-policies/citywide-information-and-data/graduation-results", None,
     "InfoHub graduation results page; saved to document the file links"),
    ("education/nycdoe_daily_attendance_2006_2009_xwxx-rnki_by_schoolyear.json", NYC + "xwxx-rnki.json", att_q(ATT_SELECT),
     "2006-2009 Historical Daily Attendance By School; server-side sums by school year"),
    ("education/nycdoe_daily_attendance_2009_2012_wpqj-3buw_by_schoolyear.json", NYC + "wpqj-3buw.json", att_q(ATT_SELECT),
     "2009-2012 Historical Daily Attendance By School; server-side sums by school year"),
    ("education/nycdoe_daily_attendance_2012_2015_pffu-gbfi_by_schoolyear.json", NYC + "pffu-gbfi.json", att_q(ATT_SELECT),
     "2012-2015 Historical Daily Attendance By School; server-side sums by school year"),
    ("education/nycdoe_daily_attendance_2015_2018_3y5p-x48f_by_schoolyear.json", NYC + "3y5p-x48f.json", att_q(ATT_SELECT_TEXT),
     "2015-2018 Historical Daily Attendance By School; server-side sums by school year (text columns cast to number)"),
    ("education/nycdoe_daily_attendance_2018_2021_xc44-2jrh_by_schoolyear.json", NYC + "xc44-2jrh.json", att_q(ATT_SELECT),
     "2018-2021 Daily Attendance by School; server-side sums by school year"),
    ("education/nycdoe_attendance_results_2013_2019_mg8s-7r2b_citywide.json", NYC + "mg8s-7r2b.json",
     {"$where": "report_type='Citywide' AND grade='All Grades' AND demographic_variable='All Students'",
      "$order": "year", "$limit": "50000"},
     "Attendance Results 2013-2019, citywide all grades all students; used only as a cross-check"),
    # ---- cost of living
    ("cost_of_living/fred_CUURA101SA0L2.csv", FRED + "CUURA101SA0L2", None,
     "FRED: CPI-U all items less shelter, New York-Newark-Jersey City, not seasonally adjusted"),
    ("cost_of_living/fred_CUURA101SAF1.csv", FRED + "CUURA101SAF1", None,
     "FRED: CPI-U food, New York-Newark-Jersey City, not seasonally adjusted"),
]
# dataset descriptions as published by each portal (documentation only; no data values are taken from these)
for _dom, _ids in (("data.cityofnewyork.us", ["qgea-i56i", "5uac-w243", "833y-fsy8", "5ucz-vwe8", "dwrg-kzni", "k46n-sa2m",
                                              "h9gi-nx95", "xc44-2jrh"]),
                   ("data.ny.gov", ["dh9m-5v4d", "cy9b-i9w9", "f6rf-2a3t"]),
                   ("data.cdc.gov", ["r8kw-7aab", "xkb8-kh2a"])):
    for _id in _ids:
        DOWNLOADS.append((f"docs/{_id}_dataset_description.json", f"https://{_dom}/api/views/{_id}.json", None,
                          f"Portal metadata and description for dataset {_id} on {_dom}; documentation only"))
DOWNLOADS.append(("docs/cdc_nchs_covid19_provisional_counts_technical_notes.html",
                  "https://www.cdc.gov/nchs/nvss/vsrr/covid19/tech_notes.htm", None,
                  "CDC NCHS technical notes: provisional death counts are tabulated by the jurisdiction where the death occurred"))
DOWNLOADS.append(("docs/cdc_nchs_vsrr_drug_overdose_page.html",
                  "https://www.cdc.gov/nchs/nvss/vsrr/drug-overdose-data.htm", None,
                  "CDC NCHS VSRR drug overdose page: 12-month-ending counts, reported by jurisdiction of occurrence"))
for _y in range(EPA_FIRST_YEAR, EPA_LAST_YEAR + 1):
    DOWNLOADS.append((f"environment/daily_88101_{_y}.zip", f"{EPA}daily_88101_{_y}.zip", None,
                      f"EPA AirData daily PM2.5 FRM/FEM mass (parameter 88101), all US monitors, {_y}"))
for _y in range(EPA_FIRST_YEAR, EPA_LAST_YEAR + 1):
    DOWNLOADS.append((f"environment/daily_aqi_by_county_{_y}.zip", f"{EPA}daily_aqi_by_county_{_y}.zip", None,
                      f"EPA AirData daily AQI by county, all US counties, {_y}"))


# --------------------------------------------------------------------------- download

def read_manifest():
    rows = {}
    if MANIFEST.exists():
        with open(MANIFEST, newline="") as f:
            for r in csv.DictReader(f):
                rows[r["path"]] = r
    return rows


def write_manifest(rows):
    RAW.mkdir(parents=True, exist_ok=True)
    cols = ["path", "source_url", "retrieved_utc", "sha256", "status", "note"]
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k].get(c, "") for c in cols})


def download(only=None):
    import requests

    man = read_manifest()
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA})
    n_new = n_fail = 0
    for rel, url, params, note in DOWNLOADS:
        if only and not rel.startswith(only):
            continue
        path = RAW / rel
        key = str(path.relative_to(ROOT))
        if path.exists() and path.stat().st_size > 0 and man.get(key, {}).get("status") == "ok":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        status, final_url, content = "failed", url, None
        for attempt in (1, 2):
            try:
                r = sess.get(url, params=params, timeout=300)
                final_url = r.url
                if r.status_code == 200 and len(r.content) > 0:
                    content, status = r.content, "ok"
                    break
                status = f"failed_http_{r.status_code}"
            except Exception as e:  # noqa: BLE001
                status = f"failed_{type(e).__name__}"
            time.sleep(5)
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if content is not None:
            path.write_bytes(content)
            sha = hashlib.sha256(content).hexdigest()
            n_new += 1
        else:
            sha = ""
            n_fail += 1
        man[key] = {"path": key, "source_url": final_url, "retrieved_utc": now, "sha256": sha,
                    "status": status, "note": note}
        write_manifest(man)
        print(f"[{status}] {rel} ({len(content) if content else 0} bytes)", flush=True)
        time.sleep(1.5)  # be polite
    print(f"download done: {n_new} new, {n_fail} failed")


# --------------------------------------------------------------------------- helpers

COLS = ["city", "category", "role", "series_id", "component", "indicator_name", "frequency", "period",
        "period_end_date", "window_months", "value", "unit", "worse_when", "change_rule", "break_flag",
        "break_note", "provisional"]
CHECKS = {}   # numbers quoted in the notes are written to nyc_checks.json from here


def jload(rel):
    return json.loads((RAW / rel).read_text())


def ym(s):
    """'2006-01-01T00:00:00.000' -> '2006-01'"""
    return str(s)[:7]


def period_end(period, freq):
    if freq == "M":
        y, m = int(period[:4]), int(period[5:7])
        return f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"
    if freq == "A":
        return f"{int(period):04d}-12-31"
    raise ValueError(freq)


def fred_csv(rel):
    df = pd.read_csv(RAW / rel, dtype=str)
    df.columns = ["date", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    n_blank = int(df["value"].isna().sum())
    df = df.dropna(subset=["value"]).copy()          # blanks are dropped, never filled
    df["period"] = df["date"].str[:7]
    return df[["period", "value"]].reset_index(drop=True), n_blank


def in_break(period, freq, b):
    if freq == "A":
        return b["start"][:4] <= period <= b["end"][:4]
    return b["start"] <= period <= b["end"]


def month_gaps(periods):
    """months missing between the first and last period"""
    if not periods:
        return []
    idx = pd.period_range(min(periods), max(periods), freq="M").strftime("%Y-%m")
    have = set(periods)
    return [p for p in idx if p not in have]


SERIES = []   # list of (meta dict, dataframe)


def add_series(meta, df):
    """df needs: period, value; optional: provisional, src_note"""
    df = df.copy()
    freq = meta["frequency"]
    df = df.sort_values("period").reset_index(drop=True)
    assert not df["period"].duplicated().any(), meta["series_id"] + " duplicate periods"
    assert df["value"].notna().all(), meta["series_id"] + " missing values"
    if freq == "M":
        df = df[df["period"] <= LAST_FULL_MONTH].reset_index(drop=True)
    if "provisional" not in df:
        df["provisional"] = 0
    if "src_note" not in df:
        df["src_note"] = ""
    flags, notes = [], []
    for _, r in df.iterrows():
        hit = [b for b in meta["breaks"] if in_break(r["period"], freq, b)]
        txt = [f"{b['kind']}: {b['note']}" for b in hit]
        if r["src_note"]:
            txt = [f"source: {r['src_note']}"] + txt
        flags.append(1 if hit else 0)
        notes.append(" | ".join(txt))
    out = pd.DataFrame({
        "city": "nyc", "category": meta["category"], "role": meta["role"], "series_id": meta["series_id"],
        "component": "", "indicator_name": meta["indicator_name"], "frequency": freq,
        "period": df["period"],
        "period_end_date": [f"{int(p):04d}-08-31" if meta["category"] == "education" else period_end(p, freq)
                            for p in df["period"]],
        "window_months": meta["window_months"], "value": df["value"].astype(float).round(6),
        "unit": meta["unit"], "worse_when": meta["worse_when"], "change_rule": meta["change_rule"],
        "break_flag": flags, "break_note": notes, "provisional": df["provisional"].astype(int),
    })[COLS]
    m = dict(meta)
    m["components"] = []
    m["first_period"] = out["period"].iloc[0] if len(out) else None
    m["last_period"] = out["period"].iloc[-1] if len(out) else None
    m["n_obs"] = int(len(out))
    if freq == "M" and len(out):
        gaps = month_gaps(list(out["period"]))
        m["missing_months_inside_range"] = gaps if len(gaps) <= 60 else f"{len(gaps)} months (see notes)"
    SERIES.append((m, out))
    return out


def meta(series_id, category, role, name, freq, window, unit, worse, rule, urls, lag, status, fallback,
         construction, breaks, caveats):
    return {"series_id": series_id, "category": category, "role": role, "indicator_name": name,
            "frequency": freq, "window_months": window, "unit": unit, "worse_when": worse, "change_rule": rule,
            "source_urls": urls, "release_lag_months": lag, "status": status, "fallback_used": fallback,
            "construction": construction, "breaks": breaks, "caveats": caveats}


CPI_BREAK = {"start": "2018-01", "end": "2018-12", "kind": "method",
             "note": "BLS redrew CPI area boundaries in January 2018 (New York-Newark-Jersey City area). "
                     "Flagged for the 12 months whose 12-month rate straddles the change; the yearly change in "
                     "that rate straddles it through 2019-12."}


# --------------------------------------------------------------------------- safety

def build_safety():
    hist = pd.DataFrame(jload("safety/nypd_complaints_historic_qgea-i56i_felony_by_report_month.json"))
    cur = pd.DataFrame(jload("safety/nypd_complaints_ytd_5uac-w243_felony_by_report_month.json"))
    for d in (hist, cur):
        d["period"] = d["month"].map(ym)
        d["value"] = d["n"].astype(float)
    n_null = int(hist["month"].isna().sum())
    hist = hist.dropna(subset=["month"])
    pre = hist[hist["period"] < "2006-01"]
    CHECKS["safety_main"] = {
        "historic_first": hist["period"].min(), "historic_last": hist["period"].max(),
        "current_first": cur["period"].min(), "current_last": cur["period"].max(),
        "historic_rows_before_2006_dropped": int(len(pre)), "historic_null_month_rows": n_null,
        "overlap_months": sorted(set(hist["period"]) & set(cur["period"])),
    }
    hist = hist[hist["period"] >= "2006-01"]
    cur = cur[~cur["period"].isin(set(hist["period"]))]
    hist["provisional"], cur["provisional"] = 0, 1
    hist["src_note"], cur["src_note"] = "", ""
    df = pd.concat([hist, cur])[["period", "value", "provisional", "src_note"]]
    add_series(meta(
        "nyc_safety_main", "safety", "main", "Felony complaints, NYPD, by report month", "M", 1, "complaints",
        "higher", "pct_log",
        [NYC + "qgea-i56i.json", NYC + "5uac-w243.json"], 3, "ok", None,
        "Count of NYPD complaint records with law_cat_cd = FELONY, grouped by the month of the report date "
        "(rpt_dt). The count was done on the NYC Open Data server. Months through the end of last year come "
        "from the historic file and this year's months from the current-year file.",
        [],
        "Reported crime only. All felony complaints, not only the seven major felonies, so the level is higher "
        "than CompStat's index-crime totals. The current-year file holds complete quarters only and is "
        "preliminary; those months are marked provisional. The two files are joined each January."), df)

    arch = pd.DataFrame(jload("safety/nypd_shootings_archived_historic_833y-fsy8_by_month.json"))
    now = pd.DataFrame(jload("safety/nypd_shootings_2006_present_5ucz-vwe8_by_month.json"))
    for d in (arch, now):
        d["period"] = d["month"].map(ym)
        d["value"] = d["incidents"].astype(float)
    both = arch.merge(now, on="period", suffixes=("_arch", "_now"))
    diff = (both["value_now"] - both["value_arch"])
    CHECKS["safety_backup"] = {
        "archived_first": arch["period"].min(), "archived_last": arch["period"].max(),
        "current_first": now["period"].min(), "current_last": now["period"].max(),
        "overlap_months": int(len(both)), "overlap_months_with_any_difference": int((diff != 0).sum()),
        "overlap_max_abs_difference_incidents": float(diff.abs().max()),
        "overlap_sum_archived": float(both["value_arch"].sum()), "overlap_sum_current": float(both["value_now"].sum()),
    }
    last_arch = arch["period"].max()
    a = arch[["period", "value"]].copy()
    b = now[now["period"] > last_arch][["period", "value"]].copy()
    a["provisional"] = 0
    b["provisional"] = (b["period"] >= "2026-01").astype(int)
    df = pd.concat([a, b])
    brk = []
    rel_gap = abs(both["value_now"].sum() - both["value_arch"].sum()) / both["value_arch"].sum()
    CHECKS["safety_backup"]["overlap_total_relative_gap"] = float(rel_gap)
    if rel_gap > 0.005:   # the join is flagged as a break only when the two files disagree by more than 0.5 percent
        y, m = int(last_arch[:4]), int(last_arch[5:7])
        start = f"{y + 1}-01" if m == 12 else f"{y}-{m + 1:02d}"
        end = (pd.Period(start, freq="M") + 11).strftime("%Y-%m")
        brk = [{"start": start, "end": end, "kind": "method",
                "note": "archived historic shooting file joined to the restructured 2006-present file; the two "
                        "differ in some overlapping months"}]
    add_series(meta(
        "nyc_safety_backup", "safety", "backup", "Shooting incidents, NYPD, by occurrence month", "M", 1,
        "incidents", "higher", "pct_log",
        [NYC + "833y-fsy8.json", NYC + "5ucz-vwe8.json"], 3, "ok", None,
        "Count of distinct shooting incidents (incident_key) by the month the shooting happened, counted on the "
        "NYC Open Data server. Months through the last month of the archived historic file come from that file "
        "and later months from the 2006-present file, which replaced the year-to-date file.",
        brk,
        "Incidents, not victims: one shooting with three victims counts once. NYPD restructured this data in "
        "2025 into shootings, victims and offenders; the dataset id the methodology names as year-to-date now "
        "holds every year. Current-year months are marked provisional."), df)


# --------------------------------------------------------------------------- economy

def build_economy():
    d = pd.DataFrame(jload("economy/nysdol_laus_sa_dh9m-5v4d_new_york_city.json"))
    assert set(d["area"]) == {"New York City"}
    d["period"] = d["year"].astype(int).map("{:04d}".format) + "-" + d["month"].astype(int).map("{:02d}".format)
    d["value"] = d["unemployment_rate"].astype(float)
    d = d.sort_values("period")
    d["provisional"] = 0
    d.loc[d["period"] == d["period"].max(), "provisional"] = 1
    add_series(meta(
        "nyc_economy_main", "economy", "main", "Unemployment rate, seasonally adjusted, New York City", "M", 1,
        "percent", "higher", "points",
        [NYS + "dh9m-5v4d.json"], 1, "ok", None,
        "The unemployment_rate field for the area New York City in the NYS Department of Labor file of "
        "seasonally adjusted Local Area Unemployment Statistics. Used as published.",
        [],
        "Model-based estimate for the five counties, revised every year, so old months change between "
        "vintages. The newest month is preliminary and marked provisional. The file has no row for October "
        "2025, so that month is missing and is not filled in."), d[["period", "value", "provisional"]])

    f, n_blank = fred_csv("economy/fred_SMS36935610000000001.csv")
    f["provisional"] = 0
    f.loc[f["period"] == f["period"].max(), "provisional"] = 1
    CHECKS["economy_backup"] = {"fred_blank_rows_dropped": n_blank}
    add_series(meta(
        "nyc_economy_backup", "economy", "backup", "Total nonfarm jobs, seasonally adjusted, New York City", "M", 1,
        "thousand jobs", "lower", "pct_log",
        [FRED + "SMS36935610000000001", "https://fred.stlouisfed.org/series/SMS36935610000000001"], 1, "ok",
        "FRED copy of the BLS state and area series starts in 1990; the methodology lists 1950.",
        "FRED series SMS36935610000000001, All Employees: Total Nonfarm in New York City, NY, seasonally "
        "adjusted, from the BLS Current Employment Statistics state and area program. Used as published, in "
        "thousands of jobs.",
        [],
        "Better when higher. Starts 1990, not 1950. Benchmarked every March, so recent months get revised. "
        "The newest month is preliminary and marked provisional."), f)


# --------------------------------------------------------------------------- housing

MONTHS3 = {m.upper(): i for i, m in enumerate(calendar.month_abbr) if m}


def parse_coalition_pdf(rel):
    import pdfplumber

    def num(words):
        t = "".join(w["text"] for w in sorted(words, key=lambda w: w["x0"])).replace(",", "")
        return float(t) if re.fullmatch(r"\d+", t) else None

    rows = []
    with pdfplumber.open(RAW / rel) as pdf:
        for page in pdf.pages:
            lines = {}
            for w in page.extract_words(x_tolerance=1.5):
                lines.setdefault(round(w["top"]), []).append(w)
            for top in sorted(lines):
                ws = sorted(lines[top], key=lambda w: w["x0"])
                mon3 = ws[0]["text"][:3]   # the worksheet also writes SEPT, JUNE and JULY
                if len(ws) < 3 or mon3 not in MONTHS3 or not re.fullmatch(r"(19|20)\d\d", ws[1]["text"]):
                    continue
                cols = {"total": [], "fam_persons": [], "single_adults": []}
                for w in ws[2:]:
                    x1 = w["x1"]
                    if 100 < x1 <= 165:
                        cols["total"].append(w)
                    elif 210 < x1 <= 257:
                        cols["fam_persons"].append(w)
                    elif 350 < x1 <= 395:
                        cols["single_adults"].append(w)
                rows.append({"period": f"{ws[1]['text']}-{MONTHS3[mon3]:02d}",
                             "total": num(cols["total"]) if cols["total"] else None,
                             "fam_persons": num(cols["fam_persons"]) if cols["fam_persons"] else None,
                             "single_adults": num(cols["single_adults"]) if cols["single_adults"] else None})
    return pd.DataFrame(rows)


def build_housing():
    c = parse_coalition_pdf("housing/coalition_for_the_homeless_shelter_population_worksheet_1983_present_202611.pdf")
    assert not c["period"].duplicated().any()
    full = c.dropna(subset=["total", "fam_persons", "single_adults"])
    ident = (full["total"] - full["fam_persons"] - full["single_adults"]).abs()
    co = c.dropna(subset=["total"]).copy()
    frames = []
    for rel in ("housing/dhs_daily_report_historical_dwrg-kzni_monthly_avg.json",
                "housing/dhs_daily_report_k46n-sa2m_monthly_avg.json"):
        d = pd.DataFrame(jload(rel))
        d["file"] = rel
        frames.append(d)
    d = pd.concat(frames)
    d["period"] = d["month"].map(ym)
    for k in ("avg_individuals", "n_rows", "n_days", "min_individuals", "max_individuals"):
        d[k] = d[k].astype(float)
    assert not d["period"].duplicated().any()
    d["days_in_month"] = [calendar.monthrange(int(p[:4]), int(p[5:7]))[1] for p in d["period"]]
    d = d.sort_values("period").reset_index(drop=True)
    d["spread_pct"] = 100 * (d["max_individuals"] - d["min_individuals"]) / d["avg_individuals"]
    d[["period", "avg_individuals", "n_days", "days_in_month", "min_individuals", "max_individuals", "spread_pct", "file"]] \
        .round(3).to_csv(OUT / "nyc_housing_main_coverage.csv", index=False)
    incomplete = d[d["n_days"] < d["days_in_month"]]
    # a month is used when more than half of its days have a census figure; the day count is kept in the coverage file
    keep = d[d["n_days"] > 0.5 * d["days_in_month"]].copy()
    first_dhs = keep["period"].min()
    ov = keep.merge(co, on="period")
    ov["diff"] = ov["total"] - ov["avg_individuals"]
    ov["diff_pct"] = 100 * ov["diff"] / ov["avg_individuals"]
    first12 = ov[ov["period"] < (pd.Period(first_dhs, freq="M") + 12).strftime("%Y-%m")]
    by_year = ov.assign(year=ov["period"].str[:4]).groupby("year")["diff_pct"].mean().round(2).to_dict()
    CHECKS["housing_main"] = {
        "coalition_rows_parsed": int(len(c)), "coalition_rows_with_total": int(len(co)),
        "coalition_first_with_total": co["period"].min(), "coalition_last": co["period"].max(),
        "coalition_rows_checked_total_equals_families_plus_single_adults": int(len(full)),
        "coalition_rows_failing_that_identity": int((ident > 1).sum()),
        "coalition_months_without_total_before_join": [p for p in month_gaps(list(co["period"])) if p < first_dhs],
        "dhs_first_day_month": d["period"].min(), "dhs_first_month_used": first_dhs,
        "dhs_months_where_rows_differ_from_distinct_days": sorted(d[d["n_rows"] != d["n_days"]]["period"]),
        "dhs_months_with_missing_days": {r["period"]: f"{int(r['n_days'])}/{int(r['days_in_month'])}"
                                         for _, r in incomplete.iterrows()},
        "dhs_months_dropped_half_or_fewer_days": sorted(set(d["period"]) - set(keep["period"])),
        "dhs_max_within_month_spread_pct": float(d["spread_pct"].max()),
        "dhs_month_of_max_spread": d.loc[d["spread_pct"].idxmax(), "period"],
        "overlap_months": int(len(ov)),
        "overlap_first_12_months_mean_coalition_minus_dhs": float(first12["diff"].mean()),
        "overlap_first_12_months_mean_pct": float(first12["diff_pct"].mean()),
        "overlap_mean_pct_by_year": by_year,
    }
    a = co[co["period"] < first_dhs][["period", "total"]].rename(columns={"total": "value"})
    a["src_note"] = "Coalition for the Homeless worksheet (total municipal shelter population)"
    b = keep[["period", "avg_individuals", "file"]].rename(columns={"avg_individuals": "value"})
    b["src_note"] = np.where(b["file"].str.contains("dwrg-kzni"),
                             "DHS Daily Report (Historical) dwrg-kzni, mean of daily census",
                             "DHS Daily Report k46n-sa2m, mean of daily census")
    df = pd.concat([a, b[["period", "value", "src_note"]]])
    join_end = (pd.Period(first_dhs, freq="M") + 11).strftime("%Y-%m")
    breaks = [
        {"start": "2011-10", "end": "2012-09", "kind": "method",
         "note": "Coalition worksheet: family figures are end-of-month counts through September 2011 and "
                 "average daily counts after (found in the worksheet's own note)"},
        {"start": first_dhs, "end": join_end, "kind": "method",
         "note": "join: Coalition for the Homeless worksheet before this month, NYC Open Data DHS Daily Report "
                 "from this month; the Coalition total covers more shelter systems than the DHS report"},
        {"start": "2022-04", "end": "2024-12", "kind": "event",
         "note": "asylum-seeker arrivals raise the shelter count"},
    ]
    add_series(meta(
        "nyc_housing_main", "housing", "main", "People in DHS shelters, monthly average of the daily census", "M", 1,
        "people", "higher", "pct_log",
        [NYC + "dwrg-kzni.json", NYC + "k46n-sa2m.json",
         "https://www.coalitionforthehomeless.org/wp-content/uploads/2026/11/NYCHomelessShelterPopulationWorksheet1983Present_202611.pdf"],
        1, "ok", None,
        "From the first full month of the DHS Daily Report on NYC Open Data, the value is the mean of the daily "
        "figure total_individuals_in_shelter over the days of the month, computed on the server from the "
        "historical file (to February 2021) and the current file (from March 2021). Before that month the value "
        "is the Total Population column of the Coalition for the Homeless worksheet, read from the PDF. Months "
        "where the worksheet has no total are left out.",
        breaks,
        "Three files joined. The Coalition total is a different, wider count than the DHS Daily Report (see "
        "notes for the measured gap), so the join is a level break. Early Coalition years have months with no "
        "total. DHS system only after the join: it leaves out people in shelters run by other agencies."), df)

    f, n_blank = fred_csv("housing/fred_CUURA101SEHA.csv")
    CHECKS["housing_backup"] = {"fred_blank_rows_dropped": n_blank}
    add_series(meta(
        "nyc_housing_backup", "housing", "backup", "CPI rent of primary residence, New York metro area", "M", 1,
        "index 1982-84=100", "faster", "inflation_points",
        [FRED + "CUURA101SEHA"], 1, "ok", None,
        "FRED series CUURA101SEHA, the BLS Consumer Price Index for All Urban Consumers, rent of primary "
        "residence, New York-Newark-Jersey City, not seasonally adjusted. Index level as published.",
        [CPI_BREAK],
        "Metro area, not the five boroughs. Rents of sitting tenants move slowly, so the index lags market "
        "rents. Months FRED lists with no value are left out: every other month before 1978, and October 2025, "
        "which has no published value."), f)


# --------------------------------------------------------------------------- transport

def build_transport():
    k = pd.DataFrame(jload("transport/mta_kpi_2008_2021_cy9b-i9w9_subway_terminal_otp.json"))
    assert set(k["indicator_name"]) == {"On-Time Performance (Terminal)"} and set(k["agency_name"]) == {"NYC Transit"}
    k["period"] = k["period"].str[:7]
    k["value"] = pd.to_numeric(k["monthly_actual"], errors="coerce")
    n_k_null = int(k["value"].isna().sum())
    k = k.dropna(subset=["value"])
    assert not k["period"].duplicated().any()
    f = pd.DataFrame(jload("transport/mta_subway_terminal_otp_f6rf-2a3t_by_month_daytype.json"))
    f["period"] = f["month"].map(ym)
    for c in ("on_time_trips", "sched_trips", "n_lines"):
        f[c] = f[c].astype(float)
    wk = f[f["day_type"] == "1"].copy()
    wk["value"] = 100 * wk["on_time_trips"] / wk["sched_trips"]
    allday = f.groupby("period")[["on_time_trips", "sched_trips"]].sum()
    allday["all_days"] = 100 * allday["on_time_trips"] / allday["sched_trips"]
    ov = k.merge(wk, on="period", suffixes=("_kpi", "_new"))
    d = ov["value_new"] - ov["value_kpi"]
    y2015 = ov[ov["period"].str[:4] == "2015"]
    wkend = f[f["day_type"] == "2"]
    CHECKS["transport_main"] = {
        "kpi_first": k["period"].min(), "kpi_last": k["period"].max(), "kpi_rows_without_value": n_k_null,
        "kpi_missing_months": month_gaps(list(k["period"])),
        "new_file_first": wk["period"].min(), "new_file_last": wk["period"].max(),
        "new_file_weekend_rows_first": wkend["period"].min() if len(wkend) else None,
        "overlap_months": int(len(ov)), "overlap_first": ov["period"].min(), "overlap_last": ov["period"].max(),
        "overlap_mean_new_minus_kpi_points": float(d.mean()), "overlap_mean_abs_difference_points": float(d.abs().mean()),
        "overlap_max_abs_difference_points": float(d.abs().max()),
        "overlap_2015_mean_abs_difference_points": float((y2015["value_new"] - y2015["value_kpi"]).abs().mean()),
        "overlap_correlation": float(np.corrcoef(ov["value_new"], ov["value_kpi"])[0, 1]),
    }
    a = k[k["period"] < "2015-01"][["period", "value"]].copy()
    a["src_note"] = "MTA Key Performance Indicators 2008-2021 (cy9b-i9w9), published weekday terminal OTP"
    b = wk[["period", "value"]].copy()
    b["src_note"] = "MTA Subway Terminal On-Time Performance: Beginning 2015 (f6rf-2a3t), weekday trips summed over lines"
    add_series(meta(
        "nyc_transport_main", "transport", "main", "Subway weekday terminal on-time performance, system-wide", "M", 1,
        "percent of trains", "lower", "points",
        [NYS + "cy9b-i9w9.json", NYS + "f6rf-2a3t.json"], 1, "ok",
        "The file the methodology links starts in 2015; months from June 2009 to December 2014 come from the "
        "MTA Key Performance Indicators 2008-2021 file. No open file has months before June 2009.",
        "Through December 2014 the value is the published monthly figure for NYC Transit On-Time Performance "
        "(Terminal), a weekday measure, from the MTA Key Performance Indicators file. From January 2015 the value "
        "is 100 times weekday on-time trips divided by weekday scheduled trips, summed over all lines on the "
        "server, from the MTA Subway Terminal On-Time Performance file. Weekday only in both, because the new "
        "file has weekend rows only from 2019.",
        [{"start": "2015-01", "end": "2015-12", "kind": "method",
          "note": "subway performance files joined at January 2015 (archive KPI file before, line-level file "
                  f"after); in the {len(ov)} overlapping months the two differ by {d.abs().mean():.3f} points on "
                  f"average and {d.abs().max():.3f} at most, so the join does not move the level"}],
        "Better when higher. Weekday trains only. Schedule changes move the measure. The archive file has no "
        "figures before June 2009 and skips a few months."), pd.concat([a, b]))

    c = pd.DataFrame(jload("transport/nypd_motor_vehicle_collisions_h9gi-nx95_by_month.json"))
    c["period"] = c["month"].map(ym)
    for x in ("injured", "killed", "crashes"):
        c[x] = pd.to_numeric(c[x], errors="coerce")
    assert c[["injured", "killed"]].notna().all().all()
    c["value"] = c["injured"] + c["killed"]
    dropped = sorted(c[c["period"] > LAST_FULL_MONTH]["period"])
    c["provisional"] = (c["period"] >= (pd.Period(LAST_FULL_MONTH, freq="M") - 1).strftime("%Y-%m")).astype(int)
    CHECKS["transport_backup"] = {"first": c["period"].min(), "months_dropped_as_incomplete": dropped,
                                  "crashes_per_month_2015": float(c[c["period"].str[:4] == "2015"]["crashes"].mean()),
                                  "crashes_per_month_2017": float(c[c["period"].str[:4] == "2017"]["crashes"].mean()),
                                  "crashes_per_month_2025": float(c[c["period"].str[:4] == "2025"]["crashes"].mean())}
    add_series(meta(
        "nyc_transport_backup", "transport", "backup", "People killed or injured in motor-vehicle crashes, NYPD", "M", 1,
        "people", "higher", "pct_log",
        [NYC + "h9gi-nx95.json"], 1, "ok", None,
        "Sum of number_of_persons_injured and number_of_persons_killed over all police-reported crashes, grouped "
        "by the month of the crash date, computed on the NYC Open Data server.",
        [{"start": "2016-03", "end": "2017-02", "kind": "method",
          "note": "NYPD crash recording system changed in March 2016"}],
        "Police-reported crashes only. Injury counts depend on what officers record. The number of crash "
        "records in the file falls from about 18,000 a month in 2015 to about 7,000 in 2025 while the injured "
        "and killed counts do not fall the same way, which points to a change in which crashes get a report; "
        "that is why this series counts people hurt, not crashes. The portal says the data are preliminary and "
        "change when reports are amended, so the two newest months are marked provisional."),
        c[["period", "value", "provisional"]])


# --------------------------------------------------------------------------- environment

def read_epa_pm25():
    use = ["State Code", "County Code", "Site Num", "POC", "Sample Duration", "Pollutant Standard", "Date Local",
           "Event Type", "Arithmetic Mean", "Units of Measure"]
    parts = []
    for y in range(EPA_FIRST_YEAR, EPA_LAST_YEAR + 1):
        with zipfile.ZipFile(RAW / f"environment/daily_88101_{y}.zip") as z:
            with z.open(z.namelist()[0]) as fh:
                for ch in pd.read_csv(fh, usecols=use, dtype=str, chunksize=400000):
                    ch = ch[(ch["State Code"] == "36") & (ch["County Code"].isin(NYC_COUNTIES))]
                    if len(ch):
                        parts.append(ch)
    d = pd.concat(parts, ignore_index=True)
    d["value"] = d["Arithmetic Mean"].astype(float)
    d["Event Type"] = d["Event Type"].fillna("None")
    return d


def build_environment():
    raw = read_epa_pm25()
    info = {"nyc_rows_read": int(len(raw)),
            "units": raw["Units of Measure"].value_counts().to_dict(),
            "sample_durations": raw["Sample Duration"].value_counts().to_dict(),
            "event_types": raw["Event Type"].value_counts().to_dict(),
            "pollutant_standards": raw["Pollutant Standard"].value_counts().to_dict()}
    # one reading per monitor (site, POC, sample duration) per day: where EPA lists a day twice because of an
    # exceptional event, keep the reading that includes the event; then collapse the repeated pollutant standards
    key = ["County Code", "Site Num", "POC", "Date Local"]
    d = raw.copy()
    # continuous monitors appear twice per day (1 HOUR summary and 24-HR BLK AVG); keep the 24-hour form when present
    d["dur_rank"] = (d["Sample Duration"] == "1 HOUR").astype(int)
    best = d.groupby(key)["dur_rank"].transform("min")
    info["rows_dropped_1hour_duplicate_of_24hour"] = int((d["dur_rank"] > best).sum())
    d = d[d["dur_rank"] == best]
    info["monitor_days_with_only_1hour_form"] = int(d.loc[d["dur_rank"] == 1, key].drop_duplicates().shape[0])
    incl = d.loc[d["Event Type"] == "Included", key].drop_duplicates().assign(has_incl=True)
    d = d.merge(incl, on=key, how="left")
    d = d[~((d["Event Type"] == "Excluded") & d["has_incl"].eq(True))]
    mon = d.groupby(key)["value"].agg(["mean", "min", "max"]).reset_index()
    info["monitor_days"] = int(len(mon))
    info["monitor_days_where_standards_disagree"] = int(((mon["max"] - mon["min"]).abs() > 1e-9).sum())
    site = mon.groupby(["County Code", "Site Num", "Date Local"], as_index=False)["mean"].mean()
    county = site.groupby(["County Code", "Date Local"], as_index=False)["mean"].mean()
    daily = county.groupby("Date Local").agg(value=("mean", "mean"), n_counties=("mean", "size")).reset_index()
    daily["period"] = daily["Date Local"].str[:7]
    m = daily.groupby("period").agg(value=("value", "mean"), n_days=("value", "size"),
                                    mean_counties=("n_counties", "mean"), min_counties=("n_counties", "min")).reset_index()
    m["days_in_month"] = [calendar.monthrange(int(p[:4]), int(p[5:7]))[1] for p in m["period"]]
    n_sites = (site.assign(period=site["Date Local"].str[:7])[["period", "County Code", "Site Num"]]
               .drop_duplicates().groupby("period").size())
    m["n_sites"] = m["period"].map(n_sites)
    m.round(4).to_csv(OUT / "nyc_environment_main_coverage.csv", index=False)
    # a month is kept when at least 75 percent of its days have a city value; trailing thin months are dropped
    thin = m[m["n_days"] < 0.75 * m["days_in_month"]]
    keep = m[m["n_days"] >= 0.75 * m["days_in_month"]].copy()
    info.update({"first_month_in_files": m["period"].min(), "last_month_in_files": m["period"].max(),
                 "months_dropped_under_75pct_days": {r["period"]: f"{int(r['n_days'])}/{int(r['days_in_month'])}"
                                                     for _, r in thin.iterrows()},
                 "mean_counties_per_day_by_year": daily.assign(y=daily["Date Local"].str[:4]).groupby("y")["n_counties"]
                 .mean().round(2).to_dict(),
                 "days_with_data_by_year": daily.assign(y=daily["Date Local"].str[:4]).groupby("y").size().to_dict(),
                 "days_with_data_by_county_by_year": {
                     NYC_COUNTIES[k]: g.assign(y=g["Date Local"].str[:4]).groupby("y").size().to_dict()
                     for k, g in county.groupby("County Code")},
                 "june_2023_value": float(m.loc[m["period"] == "2023-06", "value"].iloc[0])})
    CHECKS["environment_main"] = info
    keep["provisional"] = (keep["period"] >= "2026-01").astype(int)
    smoke = [{"start": "2023-06", "end": "2023-06", "kind": "event",
              "note": "June 2023 Canadian wildfire smoke; a real spike"},
             {"start": "2024-06", "end": "2024-06", "kind": "event",
              "note": "base effect: this month's yearly change is measured against the June 2023 wildfire smoke month"}]
    network = [{"start": "2025-01", "end": "2025-12", "kind": "method",
                "note": "found in the data: from January 2025 all five counties have a reading every day; before, "
                        "most days rest on two or three counties, so the mix of boroughs behind the city value changes"}]
    add_series(meta(
        "nyc_environment_main", "environment", "main",
        "PM2.5, monthly mean of daily readings across the five boroughs", "M", 1, "micrograms per cubic meter",
        "higher", "pct_log",
        [EPA + "download_files.html", EPA + "daily_88101_YYYY.zip"], 6, "ok", None,
        "From the EPA AirData daily files for parameter 88101 (PM2.5 by federal reference or equivalent "
        "methods), rows for Bronx, Kings, New York, Queens and Richmond counties. Each monitor's daily means are "
        "averaged to a site value, sites to a county value, and the counties that reported that day to one city "
        "value. The monthly value is the mean of the daily city values. Days flagged as exceptional events are "
        "kept in.",
        smoke + network,
        "Monitors open, close and change method over time, and filter monitors sample every third or sixth "
        "day, so the number of counties behind a day varies (see nyc_environment_main_coverage.csv). Months "
        "with a city value on fewer than 75 percent of days are left out. Data for 2026 are not yet certified "
        "and are marked provisional. Non-reference monitors (parameter 88502) are not used."),
        keep[["period", "value", "provisional"]])

    parts = []
    for y in range(EPA_FIRST_YEAR, EPA_LAST_YEAR + 1):
        with zipfile.ZipFile(RAW / f"environment/daily_aqi_by_county_{y}.zip") as z:
            with z.open(z.namelist()[0]) as fh:
                a = pd.read_csv(fh, dtype=str)
        a["State Code"] = a["State Code"].str.zfill(2)
        a["County Code"] = a["County Code"].str.zfill(3)
        a = a[(a["State Code"] == "36") & (a["County Code"].isin(NYC_COUNTIES))]
        parts.append(a)
    a = pd.concat(parts, ignore_index=True)
    a["AQI"] = a["AQI"].astype(float)
    assert not a.duplicated(["County Code", "Date"]).any()
    dly = a.groupby("Date").agg(value=("AQI", "mean"), n_counties=("AQI", "size")).reset_index()
    dly["period"] = dly["Date"].str[:7]
    am = dly.groupby("period").agg(value=("value", "mean"), n_days=("value", "size"),
                                   mean_counties=("n_counties", "mean"), min_counties=("n_counties", "min")).reset_index()
    am["days_in_month"] = [calendar.monthrange(int(p[:4]), int(p[5:7]))[1] for p in am["period"]]
    am.round(4).to_csv(OUT / "nyc_environment_backup_coverage.csv", index=False)
    thin = am[am["n_days"] < 0.75 * am["days_in_month"]]
    keep = am[am["n_days"] >= 0.75 * am["days_in_month"]].copy()
    keep["provisional"] = (keep["period"] >= "2026-01").astype(int)
    CHECKS["environment_backup"] = {
        "first_month_in_files": am["period"].min(), "last_month_in_files": am["period"].max(),
        "months_dropped_under_75pct_days": {r["period"]: f"{int(r['n_days'])}/{int(r['days_in_month'])}"
                                            for _, r in thin.iterrows()},
        "mean_counties_per_day_by_year": dly.assign(y=dly["Date"].str[:4]).groupby("y")["n_counties"].mean().round(2).to_dict(),
        "defining_parameter_share": a["Defining Parameter"].value_counts(normalize=True).round(3).to_dict()}
    add_series(meta(
        "nyc_environment_backup", "environment", "backup",
        "Air quality index, monthly mean of daily county values across the five boroughs", "M", 1, "AQI",
        "higher", "pct_log",
        [EPA + "download_files.html", EPA + "daily_aqi_by_county_YYYY.zip"], 6, "ok",
        "Built from 1999, not 1989, so the whole series sits inside the years with PM2.5 monitoring.",
        "From the EPA AirData daily AQI by county files, rows for the five New York City counties. The daily city "
        "value is the mean of the counties that have an AQI that day, and the monthly value is the mean of the "
        "daily city values.",
        smoke + [{"start": "1999-07", "end": "2000-06", "kind": "method",
                  "note": "found in the data: PM2.5 monitoring starts in July 1999, so AQI values before then "
                          "leave out fine particles"}],
        "The AQI is the highest of several pollutant sub-indices, so it mixes ozone in summer with particles in "
        "winter, and EPA recomputes it when breakpoints change. Data for 2026 are not yet certified and are "
        "marked provisional."), keep[["period", "value", "provisional"]])


# --------------------------------------------------------------------------- health

def build_health():
    d = pd.DataFrame(jload("health/cdc_r8kw-7aab_new_york_city_by_month.json"))
    assert set(d["state"]) == {"New York City"} and set(d["group"]) == {"By Month"}
    d["period"] = d["year"].astype(int).map("{:04d}".format) + "-" + d["month"].astype(int).map("{:02d}".format)
    d["value"] = pd.to_numeric(d.get("total_deaths"), errors="coerce")
    as_of = d["data_as_of"].max()[:10]
    d["end"] = d["end_date"].str[:10]
    d["full_month"] = [e == period_end(p, "M") for e, p in zip(d["end"], d["period"])]
    partial = sorted(d[~d["full_month"]]["period"])
    n_null = int(d["value"].isna().sum())
    d = d[d["full_month"]].dropna(subset=["value"]).copy()
    lag_days = (pd.Timestamp(as_of) - pd.to_datetime(d["end"])).dt.days
    d["provisional"] = (lag_days < 180).astype(int)
    CHECKS["health_main"] = {"data_as_of": as_of, "first": d["period"].min(), "last_full_month": d["period"].max(),
                             "partial_months_dropped": partial, "rows_without_total_deaths": n_null,
                             "months_marked_provisional": sorted(d[d["provisional"] == 1]["period"])}
    add_series(meta(
        "nyc_health_main", "health", "main", "Deaths from all causes occurring in New York City, by month", "M", 1,
        "deaths", "higher", "pct_log",
        [CDC + "r8kw-7aab.json"], 2, "partial",
        "CDC WONDER needs a data-use agreement form, which this run may not accept. The open CDC file that lists "
        "New York City by month starts in January 2020 and counts deaths by place of occurrence, not residence.",
        "The total_deaths field (all causes) for the jurisdiction New York City in the By Month rows of the CDC "
        "NCHS file Provisional COVID-19 Death Counts by Week Ending Date and State. Used as published. The "
        "unfinished current month is dropped.",
        [],
        "Starts 2020, not 1999, so the first yearly changes are for 2021 and sit inside the COVID period. Deaths "
        "are counted where they happened, not where the person lived. Provisional death-certificate counts: "
        "recent months are incomplete and rise as certificates arrive; months ending less than 180 days before "
        "the file date are marked provisional."), d[["period", "value", "provisional"]])

    v = pd.DataFrame(jload("health/cdc_vsrr_xkb8-kh2a_new_york_city.json"))
    assert set(v["state"]) == {"YC"} and set(v["period"]) == {"12 month-ending"}
    v = v.drop(columns=["period"])
    mnum = {m: i for i, m in enumerate(calendar.month_name) if m}
    v["p"] = v["year"].astype(int).map("{:04d}".format) + "-" + v["month"].map(mnum).map("{:02d}".format)
    v["value"] = pd.to_numeric(v["data_value"], errors="coerce")
    v["pc"] = pd.to_numeric(v.get("percent_complete"), errors="coerce")
    if "footnote_symbol" not in v:
        v["footnote_symbol"] = ""
    v["footnote_symbol"] = v["footnote_symbol"].fillna("")
    od = v[v["indicator"] == "Number of Drug Overdose Deaths"].copy()
    n_null = int(od["value"].isna().sum())
    od = od.dropna(subset=["value"])
    od["footnote"] = od["footnote"].fillna("") if "footnote" in od else ""
    od["provisional"] = (od["footnote"].str.contains("Underreported") | (od["pc"] < 100)).astype(int)
    od["pred"] = pd.to_numeric(od.get("predicted_value"), errors="coerce")
    last12 = od.sort_values("p").tail(12)
    CHECKS["health_backup"] = {
        "first": od["p"].min(), "last": od["p"].max(), "rows_without_value": n_null,
        "months_marked_provisional": sorted(od[od["provisional"] == 1]["p"]),
        "footnotes": od["footnote"].value_counts().to_dict(),
        "last_12_months_mean_pct_gap_predicted_vs_reported": float((100 * (last12["pred"] - last12["value"]) / last12["value"]).mean()),
    }
    add_series(meta(
        "nyc_health_backup", "health", "backup", "Drug overdose deaths, 12 months ending, New York City", "M", 12,
        "deaths", "higher", "pct_log",
        [CDC + "xkb8-kh2a.json"], 5, "ok", None,
        "The reported count (data_value) for the indicator Number of Drug Overdose Deaths, jurisdiction New York "
        "City, in the CDC VSRR Provisional Drug Overdose Death Counts file. Each value is the number of deaths "
        "in the 12 months ending in that month. The period is the end month.",
        [],
        "Each value covers 12 months, so neighboring months overlap. Reported counts, not CDC's predicted counts; "
        "recent months are underreported while investigations finish, and months CDC footnotes as incomplete "
        "are marked provisional. Deaths are counted where they happened."),
        od.rename(columns={"p": "period"})[["period", "value", "provisional"]])

    # extra, not one of the 16: all-cause deaths, 12 months ending, from the same VSRR file
    al = v[v["indicator"] == "Number of Deaths"].dropna(subset=["value"]).copy()
    al["provisional"] = (al["footnote"].fillna("").str.contains("Underreported") | (al["pc"] < 100)).astype(int)
    return al.rename(columns={"p": "period"})[["period", "value", "provisional"]]


# --------------------------------------------------------------------------- education

def read_grad(rel):
    g = pd.read_excel(RAW / rel, sheet_name="All", dtype=str)
    g = g[g["Category"] == "All Students"].copy()
    g["cohort_year"] = g["Cohort Year"].astype(int)
    g["period"] = (g["cohort_year"] + 4).astype(str)
    g["value"] = pd.to_numeric(g["% Grads"], errors="coerce")
    g["n_cohort"] = pd.to_numeric(g["# Total Cohort"], errors="coerce")
    g["n_grads"] = pd.to_numeric(g["# Grads"], errors="coerce")
    return g[["Cohort", "cohort_year", "period", "value", "n_cohort", "n_grads"]]


def build_education():
    g = pd.concat([read_grad("education/nycdoe_2001-2011-graduation_rates_public_citywide.xlsx"),
                   read_grad("education/nycdoe_2025-graduation-rates-public-citywide.xlsx")])
    june = g[g["Cohort"] == "4 year June"].dropna(subset=["value"]).copy()
    aug = g[g["Cohort"] == "4 year August"].dropna(subset=["value"]).copy()
    assert not june["period"].duplicated().any() and not aug["period"].duplicated().any()
    recomputed = (100 * june["n_grads"] / june["n_cohort"] - june["value"]).abs().max()
    both = june.merge(aug, on="period", suffixes=("_june", "_aug"))
    CHECKS["education_main"] = {
        "june_classes": [june["period"].min(), june["period"].max(), int(len(june))],
        "august_classes": [aug["period"].min(), aug["period"].max(), int(len(aug))],
        "max_abs_gap_published_rate_vs_grads_over_cohort": float(recomputed),
        "august_minus_june_points_mean": float((both["value_aug"] - both["value_june"]).mean()),
        "august_minus_june_points_min": float((both["value_aug"] - both["value_june"]).min()),
        "august_minus_june_points_max": float((both["value_aug"] - both["value_june"]).max()),
    }
    waiver = [{"start": "2020-01", "end": "2022-12", "kind": "method",
               "note": "Regents exam waivers for the classes of 2020 to 2022 may have raised graduation rates; "
                       "the class of 2023 is then compared with a waiver year"}]
    add_series(meta(
        "nyc_education_main", "education", "main", "Four-year graduation rate as of June, NYC public schools", "A", 12,
        "percent of cohort", "lower", "points",
        [INFOHUB + "2001-2011-graduation_rates_public_citywide.xlsx", INFOHUB + "2025-graduation-rates-public-citywide.xlsx",
         "https://infohub.nyced.org/reports-and-policies/citywide-information-and-data/graduation-results"],
        6, "ok",
        "June rate used, not August: the August rate is not in the DOE file for the classes of 2005 to 2007.",
        "The published % Grads figure for All Students, cohort type 4 year June, from the All sheet of the two "
        "NYC DOE citywide graduation files (cohorts 2001 to 2011, and 2012 to 2021). The period is the "
        "graduation year, which is the cohort year plus four.",
        waiver,
        "Better when higher. State cohort method. The June rate leaves out August graduates, so it runs a few "
        "points under the August rate the city usually quotes; the August series is in nyc_official_extra.csv. "
        "The two DOE files meet between the classes of 2015 and 2016 with no overlapping year to compare. The DOE "
        "notes say most Regents exams from June 2020 to August 2021 were cancelled and waived, and that the "
        "classes of 2020, 2021 and 2023 were revised and will not match state figures. Charter schools are not "
        "included."),
        june[["period", "value"]])

    att = []
    for rel in ("education/nycdoe_daily_attendance_2006_2009_xwxx-rnki_by_schoolyear.json",
                "education/nycdoe_daily_attendance_2009_2012_wpqj-3buw_by_schoolyear.json",
                "education/nycdoe_daily_attendance_2012_2015_pffu-gbfi_by_schoolyear.json",
                "education/nycdoe_daily_attendance_2015_2018_3y5p-x48f_by_schoolyear.json",
                "education/nycdoe_daily_attendance_2018_2021_xc44-2jrh_by_schoolyear.json"):
        a = pd.DataFrame(jload(rel))
        a["file"] = rel.split("/")[-1]
        att.append(a)
    a = pd.concat(att, ignore_index=True)
    for c in ("enrolled", "present", "absent", "released", "n_rows", "n_dates"):
        a[c] = a[c].astype(float)
    assert a["schoolyear"].str.fullmatch(r"\d{8}").all() and not a["schoolyear"].duplicated().any()
    a["period"] = a["schoolyear"].str[4:8]
    a["value"] = 100 * a["present"] / (a["present"] + a["absent"])
    chk = pd.DataFrame(jload("education/nycdoe_attendance_results_2013_2019_mg8s-7r2b_citywide.json"))
    chk["period"] = "20" + chk["year"].str[-2:]
    chk["official"] = chk["attendance"].astype(float)
    cmp_ = a.merge(chk[["period", "official"]], on="period")
    CHECKS["education_backup"] = {
        "school_days_with_records_by_period": {r["period"]: int(r["n_dates"]) for _, r in a.iterrows()},
        "crosscheck_years": list(cmp_["period"]),
        "crosscheck_mean_built_minus_doe_published_points": float((cmp_["value"] - cmp_["official"]).mean()),
        "crosscheck_max_abs_points": float((cmp_["value"] - cmp_["official"]).abs().max()),
    }
    add_series(meta(
        "nyc_education_backup", "education", "backup", "Average daily attendance rate, NYC public schools, by school year",
        "A", 12, "percent of student days", "lower", "points",
        [NYC + "xwxx-rnki.json", NYC + "wpqj-3buw.json", NYC + "pffu-gbfi.json", NYC + "3y5p-x48f.json", NYC + "xc44-2jrh.json"],
        6, "ok", None,
        "From the five NYC DOE daily attendance by school files, the server summed students present and students "
        "absent over every school and school day in each school year. The value is 100 times present divided by "
        "present plus absent. The period is the year the school year ends.",
        [{"start": "2020-01", "end": "2021-12", "kind": "method",
          "note": "found in the data: the 2019-20 school year has attendance records for far fewer school days "
                  "(buildings closed in March 2020), and 2020-21 was a remote and blended year"}],
        "Better when higher. Built from school-day records, so it differs a little from the rate DOE prints in "
        "its end-of-year report (cross-check in notes). Series ends with school year 2020-21, as planned."),
        a[["period", "value"]])
    return aug[["period", "value"]]


# --------------------------------------------------------------------------- cost of living

def build_cost():
    for sid, role, fid, name in (("nyc_cost_of_living_main", "main", "CUURA101SA0L2", "CPI all items less shelter, New York metro area"),
                                 ("nyc_cost_of_living_backup", "backup", "CUURA101SAF1", "CPI food, New York metro area")):
        f, n_blank = fred_csv(f"cost_of_living/fred_{fid}.csv")
        CHECKS[sid] = {"fred_blank_rows_dropped": n_blank}
        add_series(meta(
            sid, "cost_of_living", role, name, "M", 1, "index 1982-84=100", "faster", "inflation_points",
            [FRED + fid], 1, "ok", None,
            f"FRED series {fid}, the BLS Consumer Price Index for All Urban Consumers for New York-Newark-Jersey "
            "City, not seasonally adjusted. Index level as published; months FRED lists with no value are left out.",
            [CPI_BREAK],
            "Metro area, not the five boroughs. Not seasonally adjusted, which is fine for 12-month rates. "
            "October 2025 has no published value, so 12-month rates for 2025-10 and 2026-10 cannot be computed. "
            "Before 1978 the index was not published every month."), f)


# --------------------------------------------------------------------------- plots and output

def make_plots():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS.mkdir(parents=True, exist_ok=True)
    for m, df in SERIES:
        fig, ax = plt.subplots(figsize=(10, 3.8))
        x = pd.to_datetime(df["period_end_date"])
        ax.plot(x, df["value"], color="#1f4e79", lw=1.1, marker="o" if m["frequency"] == "A" else None, ms=3)
        prov = df[df["provisional"] == 1]
        if len(prov):
            ax.plot(pd.to_datetime(prov["period_end_date"]), prov["value"], color="#c0504d", lw=0, marker="o", ms=2.5,
                    label="provisional")
        for b in m["breaks"]:
            s = pd.Timestamp(b["start"] + "-01")
            e = pd.Timestamp(b["end"] + "-01") + pd.offsets.MonthEnd(0)
            ax.axvspan(s, e, color="#f2c14e" if b["kind"] == "method" else "#9bbb59", alpha=0.35, lw=0)
        ax.set_title(f"{m['series_id']}: {m['indicator_name']}", fontsize=10)
        ax.set_ylabel(m["unit"], fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.25)
        ax.text(0.005, 0.02, f"{m['first_period']} to {m['last_period']}, n={m['n_obs']}; yellow = method break, "
                             f"green = event; worse when {m['worse_when']}", transform=ax.transAxes, fontsize=7)
        if len(prov):
            ax.legend(fontsize=7, loc="upper left")
        fig.tight_layout()
        fig.savefig(PLOTS / f"nyc_{m['category']}_{m['role']}.png", dpi=110)
        plt.close(fig)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    SERIES.clear()
    CHECKS.clear()
    build_safety()
    build_economy()
    build_housing()
    build_transport()
    build_environment()
    allcause12 = build_health()
    aug = build_education()
    build_cost()

    order = ["safety", "economy", "housing", "transport", "environment", "health", "education", "cost_of_living"]
    SERIES.sort(key=lambda s: (0 if s[0]["role"] == "main" else 1, order.index(s[0]["category"])))
    out = pd.concat([df for _, df in SERIES], ignore_index=True)
    assert not out.duplicated(["series_id", "component", "period"]).any()
    out.to_csv(OUT / "nyc_official.csv", index=False)
    (OUT / "nyc_meta.json").write_text(json.dumps([m for m, _ in SERIES], indent=2) + "\n")

    # extra series, same columns, NOT part of the 16 (alternatives the central pipeline may choose to use)
    main_n = len(SERIES)
    add_series(meta(
        "nyc_health_alt_allcause12", "health", "alt", "Deaths from all causes, 12 months ending, New York City", "M", 12,
        "deaths", "higher", "pct_log", [CDC + "xkb8-kh2a.json"], 5, "ok", None,
        "The indicator Number of Deaths for New York City in the CDC VSRR Provisional Drug Overdose Death Counts "
        "file: all deaths in the 12 months ending in that month. Starts January 2015.",
        [], "An alternative to the monthly deaths series with longer coverage. Each value covers 12 months. "
            "Counted by place of occurrence."), allcause12)
    add_series(meta(
        "nyc_education_alt_august", "education", "alt", "Four-year graduation rate as of August, NYC public schools",
        "A", 12, "percent of cohort", "lower", "points",
        [INFOHUB + "2001-2011-graduation_rates_public_citywide.xlsx", INFOHUB + "2025-graduation-rates-public-citywide.xlsx"],
        9, "ok", None,
        "The published % Grads figure for All Students, cohort type 4 year August, from the same two DOE files. "
        "The DOE file has no August rate for the classes of 2005 to 2007.",
        [{"start": "2020-01", "end": "2022-12", "kind": "method",
          "note": "Regents exam waivers for the classes of 2020 to 2022 may have raised graduation rates"}],
        "The rate the city usually quotes. Starts with the class of 2008."), aug)
    extra = SERIES[main_n:]
    pd.concat([df for _, df in extra], ignore_index=True).to_csv(OUT / "nyc_official_extra.csv", index=False)
    (OUT / "nyc_meta_extra.json").write_text(json.dumps([m for m, _ in extra], indent=2) + "\n")
    del SERIES[main_n:]

    make_plots()
    CHECKS["summary"] = [{k: m[k] for k in ("series_id", "status", "frequency", "first_period", "last_period", "n_obs")}
                         | {"n_break_flagged": int(df["break_flag"].sum()), "n_provisional": int(df["provisional"].sum()),
                            "min": float(df["value"].min()), "max": float(df["value"].max())}
                         for m, df in SERIES]
    (OUT / "nyc_checks.json").write_text(json.dumps(CHECKS, indent=2, default=str) + "\n")
    for row in CHECKS["summary"]:
        print(row)




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--only", default=None, help="with --download: only paths starting with this prefix")
    a = ap.parse_args()
    if a.download:
        download(a.only)
        return
    build()


if __name__ == "__main__":
    main()
