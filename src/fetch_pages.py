"""Fetch the real headline and opening lines of an article: live page first, then the Internet Archive.

Usage: python src/fetch_pages.py --in <csv with item_id,url,pdate> --out <jsonl> [--workers 6]
Output rows: item_id, source ('live' | 'archive' | 'none'), title, opening (first ~90 words), fetched_url, status.
Resumable: item_ids already in --out are skipped. Nothing is invented: a page that cannot be read is 'none'.
"""
import argparse, json, os, re, sys, time, threading, random
import concurrent.futures as cf
import pandas as pd, requests, trafilatura
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6"}
ia_lock = threading.Lock(); ia_next = [0.0]
BAD_TITLE = re.compile(r"(404|not found|page unavailable|access denied|just a moment|attention required|error|找不到|無法|subscribe to read|are you a robot)", re.I)

def ia_wait(gap=0.7):
    with ia_lock:
        now = time.time(); slot = max(now, ia_next[0]); ia_next[0] = slot + gap
    time.sleep(max(0, slot - time.time()))

def decode(resp):
    raw = resp.content
    enc = None
    m = re.search(rb"charset=[\"']?([A-Za-z0-9_\-]+)", raw[:3000])
    if m: enc = m.group(1).decode("ascii", "ignore")
    for e in [enc, resp.encoding if resp.encoding and resp.encoding.lower() != "iso-8859-1" else None, "utf-8", "big5hkscs", "gb18030"]:
        if not e: continue
        try: return raw.decode(e)
        except Exception: continue
    return raw.decode("utf-8", "ignore")

def extract(html, url):
    """Return (title, opening) from page HTML, or ('','')."""
    title, text = "", ""
    try:
        soup = BeautifulSoup(html, "lxml")
        og = soup.find("meta", property="og:title")
        if og and og.get("content"): title = og["content"].strip()
        if not title and soup.find("h1"): title = soup.find("h1").get_text(" ", strip=True)
        if not title and soup.title: title = soup.title.get_text(" ", strip=True)
        desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        desc = desc["content"].strip() if desc and desc.get("content") else ""
    except Exception:
        desc = ""
    try:
        text = trafilatura.extract(html, url=url, include_comments=False, include_tables=False, favor_precision=True) or ""
    except Exception:
        text = ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 80 and desc:
        text = (desc + " " + text).strip()
    # opening lines: first ~90 words, or ~220 characters for Chinese
    if re.search(r"[一-鿿]", text[:200] or title):
        opening = text[:260]
    else:
        opening = " ".join(text.split()[:90])
    title = re.sub(r"\s+", " ", title)[:300]
    return title, opening

def html_desc(resp):
    """The page's own summary line (og:description or meta description), if it has one."""
    try:
        soup = BeautifulSoup(decode(resp), "lxml")
        d = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        return d["content"].strip() if d and d.get("content") else ""
    except Exception:
        return ""

def _d(x):
    return re.sub(r"\s+", " ", x or "")[:400]

def good(title, opening):
    if not title or BAD_TITLE.search(title[:80]): return False
    return len(opening) >= 60

def try_live(url):
    try:
        r = requests.get(url, headers=UA, timeout=(6, 12), allow_redirects=True)
        if r.status_code != 200 or len(r.content) < 1500: return None
        # a redirect to the site front page is not the article
        if r.url.rstrip("/").count("/") <= 2 and url.rstrip("/").count("/") > 2: return None
        t, o = extract(decode(r), r.url)
        if good(t, o): return dict(source="live", title=t, opening=o, fetched_url=r.url, desc=_d(html_desc(r)))
    except Exception:
        return None
    return None

# Sites that answered automated requests with a challenge page. The run stops using such a site and does
# not look for its pages elsewhere. Its items are recorded as "blocked" and replaced by other items.
BLOCKED_SITES = ("scmp.com",)

def try_archive(url, pdate):
    """Closest Internet Archive copy to the article's date, for pages that are gone from the live site."""
    ts = (pdate or "2020-01-01").replace("-", "")[:8]
    for attempt in range(3):
        try:
            ia_wait(2.5)
            r = requests.get(f"https://web.archive.org/web/{ts}id_/{url}", headers=UA, timeout=(8, 30), allow_redirects=True)
            if r.status_code == 429 or r.status_code >= 500:      # the Archive asks clients to slow down: wait, then try again
                time.sleep(60 + 30 * attempt); continue
            if r.status_code != 200 or len(r.content) < 1500: return None
            t, o = extract(decode(r), url)
            if good(t, o):
                m = re.search(r"/web/(\d{14})", r.url)
                return dict(source="archive", title=t, opening=o, fetched_url=r.url, desc=_d(html_desc(r)), snapshot=m.group(1) if m else "")
            return None
        except Exception:
            time.sleep(5)
    return None

def fetch_one(row):
    if any(d in row["url"] for d in BLOCKED_SITES):
        res = dict(source="blocked", title="", opening="", fetched_url="", desc="")
    else:
        res = try_live(row["url"]) or try_archive(row["url"], row.get("pdate"))
    if not res: res = dict(source="none", title="", opening="", fetched_url="", desc="")
    res["item_id"] = row["item_id"]
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    df = pd.read_csv(a.inp, dtype=str)
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try: done.add(json.loads(line)["item_id"])
            except Exception: pass
    df = df[~df.item_id.isin(done)]
    if a.limit: df = df.head(a.limit)
    rows = df.to_dict("records")
    n = 0; cnt = {"live": 0, "archive": 0, "none": 0, "blocked": 0}
    with open(a.out, "a") as f, cf.ThreadPoolExecutor(a.workers) as ex:
        for res in ex.map(fetch_one, rows):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            cnt[res["source"]] += 1; n += 1
            if n % 50 == 0: print(n, cnt, flush=True)
    print("DONE", n, cnt, flush=True)
