"""Render the markdown tables and short phrases that the paper, brief and other documents reuse.

Called by analysis.py after results.json is built. Adds results["tables"] (markdown strings) and
results["text"] (short phrases), so every document is filled from one file and no number is retyped.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import outlets

CN = outlets.CITY_NAMES; KN = outlets.CATEGORY_NAMES
SN = {"news": "News", "search": "Search"}

def f2(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"

def pct(x):
    return "n/a" if x is None else f"{x * 100:.0f}%"

def join_names(keys, empty="none"):
    names = [KN[k] for k in keys]
    if not names: return empty
    if len(names) == 1: return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]

def ci(d):
    return f"{f2(d['est'])} ({f2(d['ci_low'])} to {f2(d['ci_high'])})"

def render(R):
    T, X = {}, {}
    V = R.get("validation") or {}
    # ---------------- main models
    rows = ["| Source | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |",
            "| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |"]
    for s in ["news", "search"]:
        m = (R.get("main") or {}).get(s)
        if not m: rows.append(f"| {SN[s]} | not available | | | | | | | |"); continue
        h1, h2 = m["h1"], m["h2"]
        rows.append(f"| {SN[s]} | {ci(h1)} | {f2(h1['p_boot'], 3)} | {h1['n_pairs']} | {h1['n_obs']:,} | {h1['n_eff_years']:.0f} | {ci(h2['worse'])} | {ci(h2['better'])} | {ci(h2['diff'])} |")
    T["main"] = "\n".join(rows)
    # ---------------- by category
    rows = ["| Category | News slope (95% interval) | Cities | Search slope (95% interval) | Cities |", "| :-- | :-- | --: | :-- | --: |"]
    for k in outlets.COMPARED:
        cells = []
        for s in ["news", "search"]:
            d = ((R.get("h1_by_category") or {}).get(s) or {}).get(k)
            cells += [ci(d), str(d["n_pairs"])] if d else ["not tested", "0"]
        rows.append(f"| {KN[k]} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    T["h1_by_category"] = "\n".join(rows)
    rows = ["| City | News slope (95% interval) | Pairs | Search slope (95% interval) | Pairs |", "| :-- | :-- | --: | :-- | --: |"]
    for c in outlets.CITIES:
        cells = []
        for s in ["news", "search"]:
            d = ((R.get("h1_by_city") or {}).get(s) or {}).get(c)
            cells += [ci(d), str(d["n_pairs"])] if d else ["not tested", "0"]
        rows.append(f"| {CN[c]} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    T["h1_by_city"] = "\n".join(rows)
    # ---------------- checks
    rows = ["| Check | News H1 slope (95% interval) | News pairs | News worse minus better | Search H1 slope (95% interval) | Search pairs | Search worse minus better |",
            "| :-- | :-- | --: | :-- | :-- | --: | :-- |"]
    m = R.get("main") or {}
    def cell(mm):
        return (ci(mm["h1"]), str(mm["h1"]["n_pairs"]), ci(mm["h2"]["diff"])) if mm else ("not run", "", "")
    n_, s_ = cell(m.get("news")), cell(m.get("search"))
    rows.append(f"| Main model | {n_[0]} | {n_[1]} | {n_[2]} | {s_[0]} | {s_[1]} | {s_[2]} |")
    for name, c in (R.get("checks") or {}).items():
        n_, s_ = cell(c.get("news")), cell(c.get("search"))
        rows.append(f"| {c.get('label', name)} | {n_[0]} | {n_[1]} | {n_[2]} | {s_[0]} | {s_[1]} | {s_[2]} |")
    T["checks"] = "\n".join(rows)
    # ---------------- pair level
    rows = ["| City | Category | Source | Official indicator | Frequency | Periods | r (95% interval) | p | Adjusted p | Opposite directions |",
            "| :-- | :-- | :-- | :-- | :-- | --: | :-- | --: | --: | --: |"]
    n_sig = 0; n_tested = 0
    for p in R.get("pair_level") or []:
        if p.get("excluded"):
            rows.append(f"| {CN[p['city']]} | {KN[p['category']]} | {SN[p['source']]} | {p.get('indicator') or ''} | | | not tested: {p['excluded']} | | | |"); continue
        n_tested += 1; n_sig += (p.get("p_bh") is not None and p["p_bh"] < 0.05)
        rows.append(f"| {CN[p['city']]} | {KN[p['category']]} | {SN[p['source']]} | {p.get('indicator') or ''} | {p.get('freq')} | {p.get('n')} | {f2(p.get('r'))} ({f2(p.get('r_ci_low'))} to {f2(p.get('r_ci_high'))}) | {f2(p.get('p'), 3)} | {f2(p.get('p_bh'), 3)} | {pct(p.get('opposite_share'))} |")
    T["pair_level"] = "\n".join(rows)
    X["pairs_tested"] = str(n_tested); X["pairs_adjusted_p_below_05"] = str(n_sig)
    X["pairs_not_tested"] = str(len(R.get("pair_level") or []) - n_tested)
    # ---------------- H3
    for s in ["news", "search"]:
        tab = ((R.get("h3") or {}).get("opposite_share") or {}).get(s) or {}
        rows = ["| Category | " + " | ".join(CN[c] for c in outlets.CITIES) + " |", "| :-- |" + " --: |" * 3]
        for k in outlets.COMPARED:
            cells = []
            for c in outlets.CITIES:
                d = (tab.get(c) or {}).get(k)
                cells.append(f"{pct(d['share'])} ({d['n']} {'months' if d['freq'] == 'M' else ('quarters' if d['freq'] == 'Q' else 'years')})" if d else "not tested")
            rows.append(f"| {KN[k]} | " + " | ".join(cells) + " |")
        T[f"h3_{s}"] = "\n".join(rows)
    runs = (R.get("h3") or {}).get("runs") or []
    rows = ["| City | Category | Source | From | To | Months | Official measure | Attention | Proposed cause (by AI, for Cayden to confirm) | Evidence |",
            "| :-- | :-- | :-- | :-- | :-- | --: | :-- | :-- | :-- | :-- |"]
    for r in runs[:20]:
        rows.append(f"| {CN[r['city']]} | {KN[r['category']]} | {SN[r['source']]} | {r['start']} | {r['end']} | {r['months']} | {r['official_direction']} | {r['attention_direction']} | {r['proposed_cause']} | {r['evidence']} |")
    T["runs_top20"] = "\n".join(rows)
    X["runs_total"] = str(len(runs)); X["runs_news"] = str(sum(r["source"] == "news" for r in runs)); X["runs_search"] = str(sum(r["source"] == "search" for r in runs))
    causes = {}
    for r in runs: causes[r["proposed_cause"]] = causes.get(r["proposed_cause"], 0) + 1
    T["runs_by_cause"] = "\n".join(["| Proposed cause (by AI, for Cayden to confirm) | Disconnections of six months or more |", "| :-- | --: |"] +
                                   [f"| {k} | {v} |" for k, v in sorted(causes.items(), key=lambda kv: -kv[1])])
    # ---------------- lead / lag
    ll = R.get("leadlag") or {}
    rows = ["| Category | News: lag with the largest mean r | Mean r | Search: lag with the largest mean r | Mean r |", "| :-- | --: | --: | --: | --: |"]
    for k in outlets.COMPARED:
        cells = []
        for s in ["news", "search"]:
            d = ((ll.get("by_category") or {}).get(s) or {}).get(k)
            cells += [f"{d['best_lag_months']:+d} months", f2(d["best_mean_r"])] if d else ["not tested", ""]
        rows.append(f"| {KN[k]} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    T["leadlag_by_category"] = "\n".join(rows)
    bp = ll.get("by_pair") or []
    X["leadlag_pairs"] = str(len(bp)); X["leadlag_pairs_p_below_05"] = str(sum(1 for b in bp if b.get("p_perm") is not None and b["p_perm"] < 0.05))
    ns = ll.get("news_vs_search") or {}
    rows = ["| Category | Lag with the largest mean r | Mean r at that lag | Mean r at lag 0 | Cities |", "| :-- | --: | --: | --: | --: |"]
    for k in outlets.CATEGORIES:
        d = ns.get(k)
        if d and "mean_r_by_lag" in d:
            rows.append(f"| {KN[k]} | {d['best_lag_months']:+d} months | {f2(d['best_mean_r'])} | {f2(d['r_at_lag0'])} | {d['n_cities']} |")
    T["news_vs_search"] = "\n".join(rows)
    # ---------------- ranking
    for c in outlets.CITIES:
        rk = (R.get("ranking") or {}).get(c)
        if not rk: continue
        rows = ["| Category | Official: distance from its 2015 to 2019 average (SD, worse is positive) | Official rank | News share, latest 12 months | Attention rank |", "| :-- | --: | --: | --: | --: |"]
        for r in sorted(rk["rows"], key=lambda r: (r["official_rank"] or 99)):
            rows.append(f"| {KN[r['category']]} | {f2(r['official_z_vs_2015_2019'])} | {r['official_rank'] or 'n/a'} | {f2(r['news_share_pct_latest_12m'], 1)}% | {r['attention_rank'] or 'n/a'} |"
                        if r["news_share_pct_latest_12m"] is not None else f"| {KN[r['category']]} | {f2(r['official_z_vs_2015_2019'])} | {r['official_rank'] or 'n/a'} | n/a | n/a |")
        T[f"ranking_{c}"] = "\n".join(rows)
        X[f"ranking_rho_{c}"] = f2(rk.get("spearman_rank_correlation"))
    # ---------------- signal-only categories
    so = (R.get("signal_only") or {}).get("news") or {}
    rows = ["| City | Category | Agreement check | Mean share 2015 to 2019 | Mean share 2023 to 2026 | Peak month | Share in peak month | What the peak month's coverage was about (named by AI from a seeded sample, for Cayden to confirm) |",
            "| :-- | :-- | :-- | --: | --: | :-- | --: | :-- |"]
    vcit = (R.get("validation") or {}).get("cities") or {}
    for c in outlets.CITIES:
        for k in outlets.SIGNAL_ONLY:
            d = (so.get(c) or {}).get(k)
            if not d: continue
            status = "not scored" if c not in vcit else ("kept" if k in vcit[c].get("kept", []) else "dropped: shown for completeness only")
            rows.append(f"| {CN[c]} | {KN[k]} | {status} | {f2(d['mean_2015_2019'], 1)}% | {f2(d['mean_2023_2026'], 1)}% | {d['peak_month']} | {f2(d['peak_share_pct'], 1)}% | {d.get('peak_event') or ''} |")
    T["signal_only_news"] = "\n".join(rows)
    # ---------------- validation
    vc = V.get("cities") or {}
    if vc:
        rows = ["| Category | " + " | ".join(CN[c] for c in outlets.CITIES if c in vc) + " |", "| :-- |" + " --: |" * len([c for c in outlets.CITIES if c in vc])]
        for k in outlets.CATEGORIES + ["not_civic"]:
            cells = []
            for c in outlets.CITIES:
                if c not in vc: continue
                d = vc[c]["categories"][k]
                mark = "" if k == "not_civic" else (" kept" if k in vc[c]["kept"] else " dropped")
                cells.append(f"{f2(d['kappa'])}{mark}")
            rows.append(f"| {KN[k]} | " + " | ".join(cells) + " |")
        rows.append("| **Overall** | " + " | ".join(f"**{f2(vc[c]['overall_kappa'])}**" for c in outlets.CITIES if c in vc) + " |")
        rows.append("| Items | " + " | ".join(str(vc[c]["n_items"]) for c in outlets.CITIES if c in vc) + " |")
        rows.append("| Not about the city (weighted) | " + " | ".join(pct(vc[c]["not_about_city_share"]) for c in outlets.CITIES if c in vc) + " |")
        T["validation_kappa"] = "\n".join(rows)
        for c in outlets.CITIES:
            if c in vc:
                X[f"kept_{c}"] = join_names(vc[c]["kept"]); X[f"dropped_{c}"] = join_names(vc[c]["dropped"])
                X[f"dropped_compared_{c}"] = join_names([k for k in vc[c]["dropped"] if k in outlets.COMPARED])
                X[f"n_kept_compared_{c}"] = str(len([k for k in vc[c]["kept"] if k in outlets.COMPARED]))
        X["validation_status"] = V.get("status", "not available")
    # ---------------- counts
    C = R.get("counts") or {}
    rows = ["| What | Count |", "| :-- | --: |",
            f"| Cities | {C.get('cities')} |",
            f"| Outlets in the main panels | {C.get('outlets_main_panel_total')} |",
            f"| Outlets on the full lists | {C.get('outlets_listed_total')} |",
            f"| GDELT records pulled for the listed outlets | {C.get('gdelt_rows_listed_outlets'):,} |",
            f"| Articles left after the city filters and duplicate removal | {C.get('articles_after_city_filter'):,} |",
            f"| Articles labeled, main panels | {C.get('articles_labeled_main_panel_total'):,} |",
            f"| Articles labeled, main panels and check lists | {C.get('articles_labeled_all') or 0:,} |",
            f"| Months of news | {C.get('news_months')} ({C.get('news_first_month')} to {C.get('news_last_month')}) |",
            f"| Official series (main and backup) | {C.get('official_series_total')} |",
            f"| Official values | {C.get('official_values'):,} |",
            f"| Months of search data | {C.get('search_months')} ({C.get('search_first_month')} to {C.get('search_last_month')}) |",
            f"| Search downloads per request | {C.get('search_downloads_per_request')} |"]
    T["counts"] = "\n".join(rows)
    cs = R.get("case_study")
    if cs:
        X["case_city"] = CN[cs["city"]]; X["case_category"] = KN[cs["category"]]; X["case_source"] = SN[cs["source"]].lower()
    return T, X

if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(ROOT, "data/public/results.json")
    R = json.load(open(p))
    R["tables"], R["text"] = render(R)
    json.dump(R, open(p, "w"), indent=1)
    print("tables:", list(R["tables"].keys())); print("text:", R["text"])
