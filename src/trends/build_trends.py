#!/usr/bin/env python3
"""Build the Google Trends attention shares from every downloaded CSV.

Run:
    .venv/bin/python -I src/trends/build_trends.py

Reads every file data/raw/trends/<city>_<request>_<YYYYMMDDTHHMMSSZ>.csv (all rounds).
Writes, in data/interim/trends/:
    trends_raw_long.csv   one row per city x request x download x month x category
    trends_shares.csv     one row per city x month x category
    trends_meta.json      zero months, sparse flags, Google note dates, Safety A-vs-C check
    plots/<city>_shares.png

The math is Appendix B of spec/methodology.md:
  1. "<1" is recorded as 0.5.
  2. Inside each downloaded request, every set is divided by the Economy set in the same
     month. Economy's own ratio is 1. If Economy reads 0, the ratio is undefined and is left
     missing. Those months are counted, never patched.
  3. Each ratio is averaged across the downloads of the same request (round 1, round 2, ...).
  4. For each city and month, share = ratio / sum of the twelve ratios. If any of the twelve
     ratios is missing, all twelve shares are missing for that month.
  5. A set that reads zero in more than 10% of months is flagged sparse. It stays in the
     denominator. No set is ever dropped or replaced.
Safety is taken from request A. Request C's Safety is used only for the consistency check.
No value is invented or filled in. Every number comes from a downloaded CSV.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "trends"
OUT = ROOT / "data" / "interim" / "trends"
PLOTS = OUT / "plots"
LOGS = OUT / "round_logs"
CFG = json.loads((ROOT / "src" / "trends" / "term_sets.json").read_text(encoding="utf-8"))

CITIES = ["hk", "nyc", "london"]
CATEGORIES = [
    "safety", "economy", "housing", "transport", "environment", "health",
    "education", "cost_of_living", "governance", "culture", "technology", "community",
]
# which request each category's share comes from (Economy is in all three)
SOURCE_REQUEST = {}
for _req in ["A", "B", "C"]:
    for _cat in CFG["requests"][_req]:
        if _cat != "economy" and _cat not in SOURCE_REQUEST:
            SOURCE_REQUEST[_cat] = _req  # safety -> A (first seen); C's safety is the check only
SPARSE_THRESHOLD = 0.10
FILE_RE = re.compile(r"^(hk|nyc|london)_([ABC])_(\d{8}T\d{6}Z)\.csv$")


def expected_months() -> list[str]:
    a, b = CFG["date"].split(" ")
    y, m = int(a[:4]), int(a[5:7])
    y2, m2 = int(b[:4]), int(b[5:7])
    out = []
    while (y, m) <= (y2, m2):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def read_manifest() -> dict[str, dict]:
    p = RAW / "manifest.csv"
    out = {}
    if p.exists():
        with p.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                out[Path(row["path"]).name] = row
    return out


def parse_download(path: Path, city: str, request: str) -> tuple[list[dict], dict]:
    """Return long rows and facts about one downloaded file. Raises if the file is not
    the request it claims to be. Nothing is filled in."""
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    rows = list(csv.reader(text.splitlines()))
    hdr_i = next((i for i, r in enumerate(rows) if r and r[0].strip() in ("Month", "Time")), None)
    if hdr_i is None:
        raise ValueError(f"{path.name}: no header row starting with Month")
    header = rows[hdr_i]
    cats = CFG["requests"][request]
    if len(header) != 1 + len(cats):
        raise ValueError(f"{path.name}: {len(header) - 1} data columns, expected {len(cats)}")
    geo_label = CFG["geo_labels"][city]
    for cell, cat in zip(header[1:], cats):
        m = re.match(r"^(.*): \((.*)\)$", cell.strip())
        if not m:
            raise ValueError(f"{path.name}: cannot read column name {cell!r}")
        item, geo = norm(m.group(1)), m.group(2).strip()
        want = norm(CFG["sets"][city][cat])
        if item != want:
            raise ValueError(f"{path.name}: column {item!r} is not the {cat} set {want!r}")
        if geo != geo_label:
            raise ValueError(f"{path.name}: geography {geo!r}, expected {geo_label!r}")
    category_line = next((norm(",".join(r)) for r in rows[:hdr_i] if r and r[0].startswith("Category")), "")
    long_rows = []
    unparsed = 0
    months = []
    for r in rows[hdr_i + 1:]:
        if not r or not re.match(r"^\d{4}-\d{2}$", r[0].strip()):
            continue
        month = r[0].strip()
        months.append(month)
        for cell, cat in zip(r[1:], cats):
            cell = cell.strip()
            lt1 = 0
            if cell == "<1":
                val, lt1 = 0.5, 1
            else:
                try:
                    val = float(cell)
                except ValueError:
                    val = math.nan
                    unparsed += 1
            long_rows.append({"month": month, "category": cat, "raw_value": val, "was_lt1": lt1})
    facts = {
        "file": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "n_months": len(months),
        "first_month": months[0] if months else None,
        "last_month": months[-1] if months else None,
        "category_line": category_line,
        "unparsed_cells": unparsed,
    }
    return long_rows, facts


def note_dates() -> dict:
    """Google's "Note" markers, as read off the chart by the download script."""
    seen: dict[str, dict] = {}
    n_logs = 0
    if LOGS.exists():
        for p in sorted(LOGS.glob("*.json")):
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if j.get("status") != "ok":
                continue
            n_logs += 1
            for n in j.get("notes", []):
                t = (n.get("text") or "").strip()
                if not t:
                    continue
                d = seen.setdefault(t, {"text": t, "date": None, "seen_in_downloads": []})
                m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})\.?$", t)
                if m:
                    mo, da, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    yr = yr + 2000 if yr < 100 else yr
                    d["date"] = f"{yr:04d}-{mo:02d}-{da:02d}"
                d["seen_in_downloads"].append(f"{j.get('city')}_{j.get('request')}_{j.get('download_id')}")
    notes = sorted(seen.values(), key=lambda x: x["date"] or "")
    for n in notes:
        n["n_downloads_showing_it"] = len(n["seen_in_downloads"])
    return {
        "source": "tooltips of the Note markers on the Trends chart, read by src/trends/download_round.mjs (data/interim/trends/round_logs/*.json)",
        "n_download_logs_read": n_logs,
        "notes": notes,
    }


def main() -> int:
    # Optional folders, used only to test the script on copies. The real run takes no arguments.
    import argparse
    global RAW, OUT, PLOTS, LOGS
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", default=str(RAW))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--logs", default=None)
    args = ap.parse_args()
    RAW, OUT = Path(args.raw).resolve(), Path(args.out).resolve()
    PLOTS = OUT / "plots"
    LOGS = Path(args.logs).resolve() if args.logs else (OUT / "round_logs")
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    months_expected = expected_months()
    manifest = read_manifest()

    files = []
    skipped = []
    for p in sorted(RAW.glob("*.csv")):
        if p.name == "manifest.csv":
            continue
        m = FILE_RE.match(p.name)
        if not m:
            skipped.append(p.name)
            continue
        files.append((p, m.group(1), m.group(2), m.group(3)))
    if not files:
        print("No Trends downloads found in data/raw/trends/. Nothing built.")
        return 1

    long_parts = []
    inputs = []
    for p, city, request, dl in files:
        rows, facts = parse_download(p, city, request)
        man = manifest.get(p.name)
        facts["in_manifest"] = man is not None
        if man is not None and man.get("sha256") and man["sha256"] != facts["sha256"]:
            raise SystemExit(f"{p.name}: file bytes do not match the sha256 in the manifest. Stopping.")
        facts.update({"city": city, "request": request, "download_id": dl})
        missing = [m_ for m_ in months_expected if m_ not in {r["month"] for r in rows}]
        facts["months_missing_from_file"] = missing
        inputs.append(facts)
        for r in rows:
            r.update({"city": city, "request": request, "download_id": dl})
        long_parts.extend(rows)

    raw = pd.DataFrame(long_parts)[["city", "request", "download_id", "month", "category", "raw_value", "was_lt1"]]
    raw["_c"] = raw["city"].map({c: i for i, c in enumerate(CITIES)})
    raw = raw.sort_values(["_c", "request", "download_id", "month", "category"], kind="stable").drop(columns="_c")
    raw.to_csv(OUT / "trends_raw_long.csv", index=False)

    # ---- ratios to Economy, inside each download ----
    econ = raw[raw["category"] == "economy"][["city", "request", "download_id", "month", "raw_value"]].rename(
        columns={"raw_value": "economy_value"})
    r = raw.merge(econ, on=["city", "request", "download_id", "month"], how="left")
    r["ratio"] = np.where(r["economy_value"] > 0, r["raw_value"] / r["economy_value"].where(r["economy_value"] > 0), np.nan)
    r["is_zero"] = (r["raw_value"] == 0).astype(int)

    meta = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "Appendix B of spec/methodology.md. '<1' = 0.5. ratio = set / Economy in the same request, download and month. "
                  "Ratios averaged across downloads of the same request. share = ratio / sum of the twelve ratios. "
                  "A month where Economy reads 0 in any request has no shares (left missing).",
        "definitions": {
            "zero": "the cell in the CSV is 0. A cell shown as '<1' is 0.5 and is not a zero.",
            "lt1_share": "share of months where the cell was '<1'. Reported for information. It is not part of the sparse rule.",
            "sparse": f"mean across downloads of the share of months reading zero is above {SPARSE_THRESHOLD:.0%}. "
                      "For Economy, which is in all three requests, the worst of the three requests is used.",
            "n_downloads": "how many downloads of the category's source request give a defined ratio in that month. "
                           "For Economy: the smallest such count across requests A, B and C.",
            "zero_month_flag": "1 if the set read zero in that month in at least one download used.",
            "safety_source": "request A. Request C's Safety is only the consistency check.",
        },
        "months_expected": {"first": months_expected[0], "last": months_expected[-1], "n": len(months_expected)},
        "sparse_threshold": SPARSE_THRESHOLD,
        "inputs": inputs,
        "files_skipped_not_matching_name_pattern": skipped,
        "google_notes": note_dates(),
        "cities": {},
    }

    share_rows = []
    for city in CITIES:
        rc = r[r["city"] == city]
        cmeta: dict = {"geo": CFG["geos"][city], "geo_label": CFG["geo_labels"][city]}
        if rc.empty:
            cmeta["status"] = "missing: no downloads for this city"
            meta["cities"][city] = cmeta
            continue
        dls = {req: sorted(rc[rc["request"] == req]["download_id"].unique()) for req in ["A", "B", "C"]}
        cmeta["downloads_by_request"] = dls
        cmeta["n_downloads_by_request"] = {k: len(v) for k, v in dls.items()}
        cmeta["requests_missing"] = [k for k, v in dls.items() if not v]

        # Economy in each request and download
        econ_info = {}
        for req in ["A", "B", "C"]:
            for dl in dls[req]:
                e = rc[(rc["request"] == req) & (rc["download_id"] == dl) & (rc["category"] == "economy")]
                zero_months = sorted(e[e["raw_value"] == 0]["month"])
                econ_info[f"{req}_{dl}"] = {
                    "request": req, "download_id": dl,
                    "n_months": int(len(e)),
                    "n_months_economy_zero": len(zero_months),
                    "months_economy_zero": zero_months,
                    "n_months_economy_lt1": int(e["was_lt1"].sum()),
                    "economy_min": float(e["raw_value"].min()),
                    "economy_median": float(e["raw_value"].median()),
                    "economy_max": float(e["raw_value"].max()),
                }
        cmeta["economy_by_download"] = econ_info

        # mean ratio across downloads of the same request
        g = rc.groupby(["request", "category", "month"])
        avg = g.agg(ratio=("ratio", "mean"), n_downloads=("ratio", "count"),
                    n_zero_downloads=("is_zero", "sum"), n_files=("ratio", "size")).reset_index()

        # wide table of the twelve ratios
        per_cat = {}
        for cat in CATEGORIES:
            if cat == "economy":
                e = avg[avg["category"] == "economy"]
                n_by_req = e.pivot(index="month", columns="request", values="n_downloads").reindex(
                    index=months_expected, columns=["A", "B", "C"]).fillna(0)
                z_by_req = e.pivot(index="month", columns="request", values="n_zero_downloads").reindex(
                    index=months_expected, columns=["A", "B", "C"]).fillna(0)
                n = n_by_req.min(axis=1).astype(int)
                d = pd.DataFrame({"month": months_expected, "ratio": np.where(n.values >= 1, 1.0, np.nan),
                                  "n_downloads": n.values, "n_zero_downloads": z_by_req.sum(axis=1).astype(int).values})
                d["source_request"] = "A+B+C"
            else:
                req = SOURCE_REQUEST[cat]
                e = avg[(avg["category"] == cat) & (avg["request"] == req)].set_index("month").reindex(months_expected)
                d = pd.DataFrame({"month": months_expected, "ratio": e["ratio"].values,
                                  "n_downloads": e["n_downloads"].fillna(0).astype(int).values,
                                  "n_zero_downloads": e["n_zero_downloads"].fillna(0).astype(int).values})
                d["source_request"] = req
            d["category"] = cat
            per_cat[cat] = d
        wide = pd.DataFrame({cat: per_cat[cat]["ratio"].values for cat in CATEGORIES}, index=months_expected)
        defined = wide.notna().all(axis=1)
        total = wide.sum(axis=1).where(defined)
        shares = wide.div(total, axis=0)

        # zero months and the sparse flag
        cats_meta = {}
        for cat in CATEGORIES:
            reqs = ["A", "B", "C"] if cat == "economy" else [SOURCE_REQUEST[cat]]
            by_dl = {}
            by_req_mean = {}
            lt1_vals = []
            for req in reqs:
                vals = []
                for dl in dls[req]:
                    e = rc[(rc["request"] == req) & (rc["download_id"] == dl) & (rc["category"] == cat)]
                    zs = float((e["raw_value"] == 0).mean()) if len(e) else math.nan
                    ls = float(e["was_lt1"].mean()) if len(e) else math.nan
                    by_dl[f"{req}_{dl}"] = {"share_of_months_zero": zs, "n_months_zero": int((e["raw_value"] == 0).sum()),
                                           "share_of_months_lt1": ls, "n_months_lt1": int(e["was_lt1"].sum()),
                                           "n_months": int(len(e)),
                                           "max_value": float(e["raw_value"].max()) if len(e) else None,
                                           "median_value": float(e["raw_value"].median()) if len(e) else None}
                    vals.append(zs)
                    lt1_vals.append(ls)
                if vals:
                    by_req_mean[req] = float(np.mean(vals))
            if by_req_mean:
                zero_mean = max(by_req_mean.values()) if cat == "economy" else by_req_mean[reqs[0]]
                sparse = bool(zero_mean > SPARSE_THRESHOLD)
            else:
                zero_mean, sparse = None, None
            # where the zero months fall (first download of the first source request), for information
            zero_periods = None
            if dls[reqs[0]]:
                e0 = rc[(rc["request"] == reqs[0]) & (rc["download_id"] == dls[reqs[0]][0]) & (rc["category"] == cat)]
                zm = sorted(e0[e0["raw_value"] == 0]["month"])
                zero_periods = {
                    "download": f"{reqs[0]}_{dls[reqs[0]][0]}",
                    "2004-2010": sum(m_ < "2011-01" for m_ in zm),
                    "2011-2015": sum("2011-01" <= m_ < "2016-01" for m_ in zm),
                    "2016-2021": sum("2016-01" <= m_ < "2022-01" for m_ in zm),
                    "2022-2026": sum(m_ >= "2022-01" for m_ in zm),
                    "last_zero_month": zm[-1] if zm else None,
                }
            entry = {
                "source_request": "A+B+C" if cat == "economy" else reqs[0],
                "n_downloads": min(len(dls[q]) for q in reqs),
                "zero_share_by_download": by_dl,
                "zero_share_mean_across_downloads": zero_mean,
                "sparse": sparse,
                # not part of the pre-registered rule: how often the set read "<1" (recorded as 0.5)
                "lt1_share_mean_across_downloads": float(np.mean(lt1_vals)) if lt1_vals else None,
                "zero_months_by_period": zero_periods,
                "mean_share": float(shares[cat].mean()) if defined.any() else None,
            }
            if cat == "economy":
                entry["zero_share_mean_by_request"] = by_req_mean
            cats_meta[cat] = entry
        cmeta["categories"] = cats_meta
        cmeta["sparse_sets"] = [c for c in CATEGORIES if cats_meta[c]["sparse"]]

        # months with no shares
        undefined_months = [m_ for m_, ok in zip(months_expected, defined.values) if not ok]
        econ_zero_any = sorted({m_ for v in econ_info.values() for m_ in v["months_economy_zero"]})
        cmeta["months_with_shares"] = int(defined.sum())
        cmeta["months_without_shares"] = {"n": len(undefined_months), "months": undefined_months}
        cmeta["months_economy_zero_in_any_download"] = {"n": len(econ_zero_any), "months": econ_zero_any}
        sums = shares.sum(axis=1)[defined]
        cmeta["share_sum_check"] = {
            "months_checked": int(defined.sum()),
            "max_abs_deviation_from_1": float((sums - 1).abs().max()) if defined.any() else None,
            "all_sum_to_1": bool(((sums - 1).abs() < 1e-9).all()) if defined.any() else None,
        }

        # what happens at Google's note dates: 12 months before against 12 months after
        note_checks = {}
        for n in meta["google_notes"]["notes"]:
            if not n.get("date"):
                continue
            nm = n["date"][:7]
            if nm not in months_expected:
                continue
            i = months_expected.index(nm)
            before, after = months_expected[max(0, i - 12):i], months_expected[i:i + 12]
            per = {}
            for cat in CATEGORIES:
                sb = float(shares.loc[before, cat].mean()) if before else math.nan
                sa = float(shares.loc[after, cat].mean()) if after else math.nan
                zb = int(per_cat[cat].set_index("month").loc[before, "n_zero_downloads"].gt(0).sum())
                za = int(per_cat[cat].set_index("month").loc[after, "n_zero_downloads"].gt(0).sum())
                per[cat] = {"mean_share_12m_before": sb, "mean_share_12m_after": sa,
                            "after_over_before": (sa / sb) if sb and not math.isnan(sb) else None,
                            "zero_months_12m_before": zb, "zero_months_12m_after": za}
            note_checks[n["date"]] = per
        cmeta["note_date_checks"] = {
            "what": "mean share and count of zero months in the 12 months before and the 12 months from each Google note date. "
                    "A change here can be a real event or Google's change. It is listed, not corrected.",
            "by_note_date": note_checks,
        }

        # Safety / Economy from request A against request C
        a = avg[(avg["category"] == "safety") & (avg["request"] == "A")].set_index("month")["ratio"]
        c = avg[(avg["category"] == "safety") & (avg["request"] == "C")].set_index("month")["ratio"]
        both = pd.concat([a.rename("A"), c.rename("C")], axis=1).dropna()
        if len(both) >= 3 and both["A"].std() > 0 and both["C"].std() > 0:
            cmeta["safety_consistency_A_vs_C"] = {
                "what": "Safety / Economy from request A against the same ratio from request C, months where both are defined",
                "n_months": int(len(both)),
                "pearson_r": float(both["A"].corr(both["C"])),
                "mean_abs_difference": float((both["A"] - both["C"]).abs().mean()),
                "mean_ratio_A": float(both["A"].mean()),
                "mean_ratio_C": float(both["C"].mean()),
                "mean_abs_difference_over_mean_ratio_A": float((both["A"] - both["C"]).abs().mean() / both["A"].mean()) if both["A"].mean() else None,
                "n_downloads_A": len(dls["A"]), "n_downloads_C": len(dls["C"]),
            }
        else:
            cmeta["safety_consistency_A_vs_C"] = {"status": "missing: needs request A and request C for this city", "n_months": int(len(both))}
        meta["cities"][city] = cmeta

        for cat in CATEGORIES:
            d = per_cat[cat]
            for i, month in enumerate(months_expected):
                ratio = d["ratio"].iloc[i]
                share = shares[cat].iloc[i]
                share_rows.append({
                    "city": city, "month": month, "category": cat,
                    "ratio_to_economy": ratio, "share": share,
                    "n_downloads": int(d["n_downloads"].iloc[i]),
                    "sparse_flag": "" if cats_meta[cat]["sparse"] is None else int(cats_meta[cat]["sparse"]),
                    "zero_month_flag": int(d["n_zero_downloads"].iloc[i] >= 1),
                    "n_zero_downloads": int(d["n_zero_downloads"].iloc[i]),
                    "source_request": d["source_request"].iloc[i],
                    "shares_defined": int(bool(defined.iloc[i])),
                })

    sh = pd.DataFrame(share_rows)
    sh.to_csv(OUT / "trends_shares.csv", index=False)
    (OUT / "trends_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    make_plots(sh, meta)
    print_summary(meta)
    return 0


def make_plots(sh: pd.DataFrame, meta: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    SURFACE, TEXT, TEXT2, MUTED, GRID, AXIS, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#2a78d6"
    names = {"safety": "Safety", "economy": "Economy", "housing": "Housing", "transport": "Transport",
             "environment": "Environment", "health": "Health", "education": "Education",
             "cost_of_living": "Cost of Living", "governance": "Governance", "culture": "Culture",
             "technology": "Technology", "community": "Community"}
    city_names = {"hk": "Hong Kong", "nyc": "New York media market", "london": "England (for London)"}
    notes = [pd.Timestamp(n["date"]) for n in meta["google_notes"]["notes"] if n.get("date")]
    for city in CITIES:
        cm = meta["cities"].get(city, {})
        d = sh[sh["city"] == city]
        if d.empty or "categories" not in cm:
            continue
        fig, axes = plt.subplots(4, 3, figsize=(13, 11), sharex=True)
        fig.patch.set_facecolor(SURFACE)
        for ax, cat in zip(axes.ravel(), CATEGORIES):
            e = d[d["category"] == cat]
            x = pd.to_datetime(e["month"] + "-01")
            y = e["share"].astype(float) * 100
            ax.set_facecolor(SURFACE)
            for nd in notes:
                ax.axvline(nd, color=AXIS, linewidth=0.8, linestyle=(0, (3, 3)), zorder=1)
            ax.plot(x, y, color=BLUE, linewidth=1.4, zorder=3, solid_joinstyle="round")
            top = float(np.nanmax(y)) if np.isfinite(y).any() else 1.0
            ax.set_ylim(0, top * 1.12 if top > 0 else 1)
            c = cm["categories"][cat]
            tag = "  (sparse)" if c["sparse"] else ""
            ax.text(0.0, 1.13, f"{names[cat]}{tag}", transform=ax.transAxes, ha="left", va="bottom",
                    fontsize=11, color=TEXT, fontweight="bold")
            zs = c["zero_share_mean_across_downloads"]
            l1 = c["lt1_share_mean_across_downloads"]
            lab = "" if zs is None else f"reads zero in {zs:.0%} of months" + (f', "<1" in {l1:.0%}' if l1 else "")
            ax.text(0.0, 1.03, lab, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, color=MUTED)
            ax.grid(axis="y", color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            for s in ["top", "right", "left"]:
                ax.spines[s].set_visible(False)
            ax.spines["bottom"].set_color(AXIS)
            ax.tick_params(colors=MUTED, labelsize=8, length=0)
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}%"))
            ax.xaxis.set_major_locator(mdates.YearLocator(4))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
            ax.set_xlim(pd.Timestamp("2004-01-01"), pd.Timestamp("2026-10-01"))
        sc = cm["share_sum_check"]
        nd = cm["n_downloads_by_request"]
        sub = (f"Share of the twelve search sets, by month, January 2004 to October 2026. Each panel has its own vertical scale. "
               f"Downloads per request: A {nd['A']}, B {nd['B']}, C {nd['C']}.\n"
               f"The twelve shares sum to 100% in {sc['months_checked']} of {meta['months_expected']['n']} months"
               f" (largest gap {sc['max_abs_deviation_from_1']:.1e}). "
               f"Months with no shares because Economy read zero: {cm['months_without_shares']['n']}.\n"
               f"Dashed lines: dates Google changed its data ({', '.join(n.strftime('%-d %b %Y') for n in notes) or 'none read'}). "
               f"A set marked sparse reads zero in more than 10% of months.")
        fig.suptitle(f"Google Trends attention shares: {city_names[city]}", x=0.02, y=0.988, ha="left",
                     fontsize=15, color=TEXT, fontweight="bold")
        fig.text(0.02, 0.962, sub, ha="left", va="top", fontsize=9, color=TEXT2, linespacing=1.5)
        fig.tight_layout(rect=(0, 0, 1, 0.905), h_pad=2.4, w_pad=1.6)
        fig.savefig(PLOTS / f"{city}_shares.png", dpi=140, facecolor=SURFACE)
        plt.close(fig)


def print_summary(meta: dict) -> None:
    print(f"inputs: {len(meta['inputs'])} files")
    print("google notes:", [(n["date"], n["n_downloads_showing_it"]) for n in meta["google_notes"]["notes"]])
    for city, cm in meta["cities"].items():
        if "categories" not in cm:
            print(city, cm.get("status"))
            continue
        print(f"\n== {city}  downloads per request {cm['n_downloads_by_request']}")
        print("  sparse sets:", cm["sparse_sets"] or "none")
        for cat, c in cm["categories"].items():
            z = c["zero_share_mean_across_downloads"]
            ms = c["mean_share"]
            l1 = c["lt1_share_mean_across_downloads"]
            print(f"    {cat:15s} zero {z:6.1%}  '<1' {l1:6.1%}  sparse {str(c['sparse']):5s}  mean share {ms if ms is None else round(ms, 4)}")
        for k, v in cm["economy_by_download"].items():
            print(f"  economy in {k}: zero months {v['n_months_economy_zero']}, <1 months {v['n_months_economy_lt1']}, "
                  f"min {v['economy_min']}, median {v['economy_median']}, max {v['economy_max']}")
        print(f"  months without shares: {cm['months_without_shares']['n']}  {cm['months_without_shares']['months'][:12]}")
        print(f"  share sum check: {cm['share_sum_check']}")
        print(f"  safety A vs C: {cm['safety_consistency_A_vs_C']}")


if __name__ == "__main__":
    sys.exit(main())
