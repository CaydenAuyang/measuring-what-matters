"""Bulk labeling with a language model: batched, concurrent, resumable, cost-logged.

Usage: python src/labeler.py --items <parquet|csv with item_id, city, outlet, headline, themes> --out <jsonl>
                             [--model M] [--batch 25] [--workers 16] [--limit N] [--budget USD] [--task NAME]
Rows already present in --out are skipped, so the job can be stopped and restarted.
"""
import argparse, csv, datetime, json, os, random, sys, threading, time
import concurrent.futures as cf
import pandas as pd, requests
sys.path.insert(0, os.path.dirname(__file__))
import codebook, outlets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
PRICES = {  # USD per 1M tokens (input, output incl. thinking), from ai.google.dev pricing page on 2026-11-17
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-3.8-flash": (0.75, 4.50),
}
MAX_THEMES = 30
lock = threading.Lock()
usage = {"requests": 0, "in": 0, "out": 0, "fail": 0}

def fmt_item(n, row):
    name = outlets.BY_KEY[row["outlet"]]["name"] if row["outlet"] in outlets.BY_KEY else row["outlet"]
    themes = [t for t in str(row.get("themes") or "").split(";") if t][:MAX_THEMES]
    return f'[{n}] city: {outlets.CITY_NAMES.get(row["city"], row["city"])} | outlet: {name} | headline: {row.get("headline") or ""} | themes: {"; ".join(themes)}'

RPM = 15.0            # free-tier limit found in the throughput test: 15 requests a minute per model
_next_slot = [0.0]
STOP = {"daily": False}

def wait_slot():
    with lock:
        now = time.time()
        slot = max(now, _next_slot[0])
        _next_slot[0] = slot + 60.0 / RPM + 0.05
    time.sleep(max(0.0, slot - time.time()))

class Quota(Exception):
    def __init__(self, quota_id, delay, msg):
        super().__init__(msg); self.quota_id = quota_id; self.delay = delay

def call(model, system, text, key, thinking_field):
    gen = {"temperature": 0, "responseMimeType": "application/json", "responseSchema": codebook.RESPONSE_SCHEMA}
    if thinking_field:
        gen["thinkingConfig"] = thinking_field
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}], "generationConfig": gen}
    wait_slot()
    r = requests.post(API.format(model=model), headers={"x-goog-api-key": key}, json=body, timeout=180)
    if r.status_code == 429:
        qid, delay = "", 20.0
        try:
            for det in r.json()["error"].get("details", []):
                if det.get("@type", "").endswith("QuotaFailure"):
                    qid = ";".join(v.get("quotaId", "") for v in det.get("violations", []))
                if det.get("@type", "").endswith("RetryInfo"):
                    delay = float(det.get("retryDelay", "20s").rstrip("s"))
        except Exception:
            pass
        raise Quota(qid, delay, f"HTTP 429 {qid}")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    d = r.json()
    um = d.get("usageMetadata", {})
    txt = d["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(txt), um, d.get("modelVersion", "")

def label_batch(rows, model, system, key, thinking_field, depth=0):
    text = "ITEMS\n" + "\n".join(fmt_item(i + 1, r) for i, r in enumerate(rows))
    last = None
    for attempt in range(6):
        try:
            arr, um, mv = call(model, system, text, key, thinking_field)
            with lock:
                usage["requests"] += 1
                usage["in"] += um.get("promptTokenCount", 0)
                usage["out"] += um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)
            got = {}
            for o in arr:
                try:
                    n, cat, tone = codebook.parse_label(o)
                except Exception:
                    continue
                if 1 <= n <= len(rows) and n not in got:
                    got[n] = (cat, tone)
            # keep every validly labeled item; items the model skipped stay unlabeled and are picked up on a later pass
            if len(got) >= 0.9 * len(rows):
                with lock:
                    usage["fail"] += len(rows) - len(got)
                return [dict(item_id=r["item_id"], category=got[i + 1][0], tone=got[i + 1][1], model_version=mv)
                        for i, r in enumerate(rows) if i + 1 in got]
            last = f"bad shape: got {len(got)} of {len(rows)}"
        except Quota as q:
            last = str(q)
            print(f"quota: {q.quota_id} retry in {q.delay:.0f}s", file=sys.stderr, flush=True)
            if "PerDay" in q.quota_id:
                STOP["daily"] = True
                return []
            time.sleep(q.delay + 1 + random.random() * 2)
        except Exception as e:  # noqa
            last = str(e)[:200]
            time.sleep(3 + 3 * attempt)
        if STOP["daily"]:
            return []
    if len(rows) > 1 and depth < 4:   # split and retry halves
        h = len(rows) // 2
        return label_batch(rows[:h], model, system, key, thinking_field, depth + 1) + \
               label_batch(rows[h:], model, system, key, thinking_field, depth + 1)
    with lock:
        usage["fail"] += len(rows)
    print(f"FAILED {len(rows)} item(s): {last}", file=sys.stderr, flush=True)
    return []

def cost(model):
    pi, po = PRICES.get(model, (1.0, 5.0))
    return usage["in"] / 1e6 * pi + usage["out"] / 1e6 * po

def log_cost(task, model):
    path = os.path.join(ROOT, "logs", "api_costs.csv")
    with open(path, "a") as f:
        csv.writer(f).writerow([datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), task, model,
                                usage["requests"], usage["in"], usage["out"], round(cost(model), 4)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3.1-flash-lite"); ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--budget", type=float, default=60.0); ap.add_argument("--rpm", type=float, default=2.0); ap.add_argument("--task", default="label")
    ap.add_argument("--system", default=""); ap.add_argument("--thinking", default="minimal")
    a = ap.parse_args()
    key = os.environ["GEMINI_API_KEY"]
    global RPM
    RPM = a.rpm
    system = open(a.system).read() if a.system else codebook.SYSTEM_PROMPT
    thinking_field = {"budget0": {"thinkingBudget": 0}, "minimal": {"thinkingLevel": "minimal"}, "none": None}[a.thinking]
    df = pd.read_parquet(a.items) if a.items.endswith(".parquet") else pd.read_csv(a.items)
    done = set()
    if os.path.exists(a.out):
        with open(a.out) as f:
            for line in f:
                try: done.add(json.loads(line)["item_id"])
                except Exception: pass
    df = df[~df.item_id.isin(done)]
    if a.limit: df = df.head(a.limit)
    print(f"{len(done)} already labeled, {len(df)} to do, model {a.model}", flush=True)
    recs = df[["item_id", "city", "outlet", "headline", "themes"]].to_dict("records")
    # keep the given order (rows arrive sorted by priority group); a batch never mixes groups or cities
    cols = ["item_id", "city", "outlet", "headline", "themes"] + (["grp"] if "grp" in df.columns else [])
    recs = df[cols].to_dict("records")
    batches, cur = [], []
    for r in recs:
        if cur and (len(cur) >= a.batch or (r.get("grp"), r["city"]) != (cur[0].get("grp"), cur[0]["city"])):
            batches.append(cur); cur = []
        cur.append(r)
    if cur: batches.append(cur)
    t0 = time.time(); n_done = 0
    with open(a.out, "a") as fout, cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(label_batch, b, a.model, system, key, thinking_field) for b in batches]
        for k, fu in enumerate(cf.as_completed(futs)):
            for o in fu.result():
                fout.write(json.dumps(o) + "\n")
            n_done += 1
            if STOP["daily"]:
                print("DAILY QUOTA REACHED, stopping", flush=True)
                open(os.path.join(ROOT, "logs", "gemini_daily_quota.flag"), "w").write(datetime.datetime.now(datetime.UTC).isoformat())
                for f2 in futs: f2.cancel()
                break
            if n_done % 15 == 0:
                fout.flush()
                el = time.time() - t0
                print(f"{n_done}/{len(batches)} batches, {el:.0f}s, {n_done * a.batch / el * 60:.0f} items/min, list-price ${cost(a.model):.2f}, fails {usage['fail']}", flush=True)
            if cost(a.model) > a.budget:
                print("BUDGET REACHED, stopping", flush=True)
                for f2 in futs: f2.cancel()
                break
    log_cost(a.task, a.model)
    print(f"DONE {a.task}: requests {usage['requests']}, in {usage['in']}, out {usage['out']}, ${cost(a.model):.2f}, failed items {usage['fail']}, {time.time() - t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
