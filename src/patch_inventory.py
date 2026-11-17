"""Fill the "What this run found" cells of the source inventory that depend on facts known only late in the run
(page-fetch counts, the headline check, the number of Trends downloads, what was cut). Safe to run again."""
import glob, json, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "deliverables/source_inventory_v2.md")
V = os.path.join(ROOT, "data/interim/validation")

def fetch_counts():
    out = {}
    for c in ["hk", "nyc", "london"]:
        f = os.path.join(V, f"{c}_pages_v1.jsonl"); cand = os.path.join(V, f"{c}_candidates_v1.csv")
        d = pd.read_json(f, lines=True, dtype={"item_id": str}).drop_duplicates("item_id").merge(pd.read_csv(cand, dtype=str)[["item_id", "outlet"]], on="item_id")
        out[c] = d
    return out

def main():
    L = open(P).read().split("\n")
    fc = fetch_counts()
    tot = {k: sum(int((d.source == k).sum()) for d in fc.values()) for k in ["live", "archive", "none", "blocked", "gdelt_title"]}
    tried = sum(len(d) for d in fc.values())
    hk = fc["hk"]; hkcna = hk[hk.outlet == "hkcna"]
    hc = json.load(open(os.path.join(V, "headline_check_result.json")))
    n_dl = len([f for f in glob.glob(os.path.join(ROOT, "data/raw/trends/*.csv")) if "manifest" not in f]) // 9
    def per(c):
        d = fc[c]; real = d[~d.source.isin(["blocked", "gdelt_title"])]
        return f"{int((real.source == 'live').sum())} of {len(real)}"
    cut_social = "Not used in this run. The social media snapshot was cut. It needs API keys or logins that the run did not have, and LIHKG's terms on automated access were never confirmed. The proposal names this as the second item to cut."
    cut_archive = "Not used in this run. The pre-2015 news extension was cut. This archive needs an API key or a subscription that the run did not have. The proposal names the extension as the first item to cut."
    new = {
        "| [YouTube Data API v3]": cut_social, "| [X API]": cut_social, "| [Threads keyword search]": cut_social, "| [LIHKG]": cut_social,
        "| [Guardian Open Platform]": cut_archive, "| [New York Times Archive API]": cut_archive, "| [WiseNews (Wisers)]": cut_archive,
        "| [GDELT stored page titles]": (
            f"This run left the field out of the main extract and pulled it later for the headline-check days only (48.4 GB billed). The check used {hc['n_items']:,} articles from 2020 on. "
            f"Where the web address had headline words, the production labels agreed with labels made from the real stored headline at kappa {hc['cities']['hk']['with_headline_words']['kappa']:.2f} in Hong Kong, "
            f"{hc['cities']['nyc']['with_headline_words']['kappa']:.2f} in New York and {hc['cities']['london']['with_headline_words']['kappa']:.2f} in London. For Hong Kong items with theme tags alone the kappa was "
            f"{hc['cities']['hk']['theme_tags_only']['kappa']:.2f}, below 0.61, so the pre-registered rule left two outlets out of 2015 to 2019. The field also supplied the real headline for {tot['gdelt_title']} South China Morning Post validation candidates after that site challenged automated requests."),
    }
    ia_val = (f"For the first validation draw the run tried {tried - tot['blocked'] - tot['gdelt_title']:,} pages from live sites and, where a live page was gone, from the Archive. {tot['archive']} usable copies came from the Archive. "
              f"HK China News Agency article pages return 404 on the live site, and the Archive held a usable copy for {int((hkcna.source == 'archive').sum())} of {len(hkcna)} tried. "
              "The Archive refused requests that arrived too fast, so the run paced them 2.5 seconds apart.")
    live_val = (f"Live pages loaded for {per('nyc')} New York candidates, {per('london')} London candidates and {per('hk')} Hong Kong candidates outside the South China Morning Post. "
                f"scmp.com answered page requests with a challenge page (HTTP 403). The run stopped using that site and did not fetch its pages from anywhere else: {tot['blocked']} candidates before 2020 were replaced, and candidates from 2020 on used GDELT's stored headline.")
    seen_ia = 0
    for i, l in enumerate(L):
        if not l.startswith("|"): continue
        cells = l.split(" | ")
        for key, txt in new.items():
            if l.startswith(key):
                cells[-1] = txt + " |"; L[i] = " | ".join(cells)
        if l.startswith("| [Internet Archive Wayback Machine]"):
            seen_ia += 1
            if seen_ia == 1:
                cells[-1] = ia_val + " |"; L[i] = " | ".join(cells)
        if l.startswith("| Live outlet pages"):
            cells[-1] = live_val + " |"; L[i] = " | ".join(cells)
        if l.startswith("| [Google Trends]"):
            last = cells[-1]
            a = last.find("All nine requests downloaded")
            b = last.find("Requests made minutes apart")
            if a >= 0 and b > a:
                head = (f"All nine requests were downloaded {n_dl} time(s): on November 17 between 20:46 and 20:53 UTC" + (" and again after local midnight on November 18" if n_dl >= 2 else "") +
                        ", each with 274 monthly points from January 2004 to October 2026. ")
                cells[-1] = last[:a] + head + last[b:]; L[i] = " | ".join(cells)
    text = "\n".join(L)
    note = "\nThe hand-coded check named in this table is the plan's wording. In this run a second AI language model took the place of hand-coding. See `deliverables/deviations.md`.\n"
    if "The hand-coded check named in this table" not in text:
        k = text.find("| [Hammond and Weidmann (2014)]")
        e = text.find("\n", k)
        text = text[:e + 1] + note + text[e + 1:]
    open(P, "w").write(text)
    print("inventory patched; trends downloads:", n_dl, "| pages:", tot, "| tried", tried)

if __name__ == "__main__":
    main()
