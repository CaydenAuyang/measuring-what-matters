"""Production labeler: Claude through the Anthropic API. Batched, concurrent, resumable, cost-logged.

Usage: python src/labeler_claude.py --items <parquet> --out <jsonl> [--model claude-haiku-5-5] [--batch 50]
                                    [--workers 32] [--limit N] [--budget USD] [--task NAME] [--groups L0-hk,L1]
The system prompt is the frozen prompt in src/codebook.py, unchanged. Every request stays far below
100,000 tokens (the model's lower price tier). Rows already in --out are skipped, so the job can be restarted.
"""
import argparse, csv, datetime, json, os, re, sys, threading, time
import concurrent.futures as cf
import pandas as pd
import anthropic
sys.path.insert(0, os.path.dirname(__file__))
import codebook, envfile
from labeler import fmt_item

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# USD per 1M tokens (input, output including thinking) for prompts of 100K tokens or fewer.
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.00, 10.00)}
MAX_PROMPT_TOKENS = 100_000
lock = threading.Lock()
SYSTEM = codebook.SYSTEM_PROMPT      # the frozen prompt; --system swaps in a revised prompt file for the one allowed revision
usage = {"requests": 0, "in": 0, "out": 0, "cache_read": 0, "cache_write": 0, "fail": 0, "refusals": 0, "max_in": 0, "items": 0}

def cost(model):
    pi, po = PRICES[model]
    return (usage["in"] + 1.25 * usage["cache_write"] + 0.1 * usage["cache_read"]) / 1e6 * pi + usage["out"] / 1e6 * po

def parse_array(text):
    """Pull the JSON array of label strings out of the model's reply."""
    a, b = text.find("["), text.rfind("]")
    if a < 0 or b <= a:
        raise ValueError("no JSON array in reply")
    return json.loads(text[a:b + 1])

def label_batch(client, rows, model, depth=0):
    text = "ITEMS\n" + "\n".join(fmt_item(i + 1, r) for i, r in enumerate(rows))
    last = ""
    for attempt in range(3):
        try:
            msg = client.messages.create(
                model=model, max_tokens=16000, system=SYSTEM,
                messages=[{"role": "user", "content": text}],
            )
        except anthropic.BadRequestError as e:          # not retryable as sent
            last = f"bad request: {e.message}"[:200]; break
        except anthropic.RateLimitError as e:
            last = "rate limited"; time.sleep(float(e.response.headers.get("retry-after", "10")) + 1); continue
        except anthropic.APIStatusError as e:
            last = f"status {e.status_code}"; time.sleep(3 + 3 * attempt); continue
        except anthropic.APIConnectionError:
            last = "connection error"; time.sleep(3 + 3 * attempt); continue
        u = msg.usage
        with lock:
            usage["requests"] += 1; usage["in"] += u.input_tokens; usage["out"] += u.output_tokens
            usage["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
            usage["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
            usage["max_in"] = max(usage["max_in"], u.input_tokens)
        if msg.stop_reason == "refusal":
            with lock: usage["refusals"] += 1
            last = "refusal"; break                      # split below, so one item cannot block a whole request
        if msg.stop_reason == "max_tokens":
            last = "hit max_tokens"; break
        reply = "".join(b.text for b in msg.content if b.type == "text")
        try:
            arr = parse_array(reply)
        except Exception as e:
            last = f"unparseable reply: {e}"[:120]
            print(f"retry ({len(rows)} items): {last}", file=sys.stderr, flush=True); continue
        got = {}
        for o in arr:
            try:
                n, cat, tone = codebook.parse_label(o)
            except Exception:
                continue
            if 1 <= n <= len(rows) and n not in got:
                got[n] = (cat, tone)
        if len(got) >= 0.9 * len(rows):
            with lock:
                usage["fail"] += len(rows) - len(got); usage["items"] += len(got)
            return [dict(item_id=r["item_id"], category=got[i + 1][0], tone=got[i + 1][1], model_version=msg.model)
                    for i, r in enumerate(rows) if i + 1 in got]
        last = f"bad shape: {len(got)} of {len(rows)}"
        print(f"retry ({len(rows)} items): {last}", file=sys.stderr, flush=True)
    if len(rows) > 1 and depth < 6:
        print(f"split ({len(rows)} items): {last}", file=sys.stderr, flush=True)
        h = len(rows) // 2
        return label_batch(client, rows[:h], model, depth + 1) + label_batch(client, rows[h:], model, depth + 1)
    with lock: usage["fail"] += len(rows)
    print(f"FAILED {len(rows)} item(s): {last}", file=sys.stderr, flush=True)
    return []

def log_cost(task, model):
    with open(os.path.join(ROOT, "logs", "api_costs.csv"), "a") as f:
        csv.writer(f).writerow([datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), task, model,
                                usage["requests"], usage["in"], usage["out"], round(cost(model), 4)])

def make_batches(df, batch):
    cols = ["item_id", "city", "outlet", "headline", "themes"] + (["grp"] if "grp" in df.columns else [])
    recs = df[cols].to_dict("records")
    batches, cur = [], []
    for r in recs:      # keep the given order; a batch never mixes rounds or cities
        if cur and (len(cur) >= batch or (r.get("grp"), r["city"]) != (cur[0].get("grp"), cur[0]["city"])):
            batches.append(cur); cur = []
        cur.append(r)
    if cur: batches.append(cur)
    return batches

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="claude-haiku-5-5"); ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--workers", type=int, default=32); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--budget", type=float, default=100.0); ap.add_argument("--task", default="label")
    ap.add_argument("--groups", default=""); ap.add_argument("--stats", default=""); ap.add_argument("--system", default="")
    a = ap.parse_args()
    global SYSTEM
    if a.system:
        SYSTEM = open(a.system).read()
    envfile.load_env()
    client = anthropic.Anthropic(max_retries=4, timeout=300.0)
    df = pd.read_parquet(a.items) if a.items.endswith(".parquet") else pd.read_csv(a.items)
    if a.groups:
        df = df[df.grp.isin(a.groups.split(","))]
    done = set()
    if os.path.exists(a.out):
        with open(a.out) as f:
            for line in f:
                try: done.add(json.loads(line)["item_id"])
                except Exception: pass
    df = df[~df.item_id.isin(done)]
    if a.limit: df = df.head(a.limit)
    batches = make_batches(df, a.batch)
    print(f"{len(done)} already labeled, {len(df)} to do in {len(batches)} requests, model {a.model}", flush=True)
    t0 = time.time(); n_done = 0; stopped = False
    with open(a.out, "a") as fout, cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(label_batch, client, b, a.model) for b in batches]
        for fu in cf.as_completed(futs):
            for o in fu.result():
                fout.write(json.dumps(o) + "\n")
            n_done += 1
            if n_done % 100 == 0:
                fout.flush(); el = time.time() - t0
                print(f"{n_done}/{len(batches)} requests, {el:.0f}s, {usage['items'] / el * 60:.0f} items/min, ${cost(a.model):.2f}, unlabeled {usage['fail']}, refusals {usage['refusals']}", flush=True)
            if cost(a.model) > a.budget and not stopped:
                stopped = True
                print("BUDGET REACHED, stopping", flush=True)
                for f2 in futs: f2.cancel()
    assert usage["max_in"] < MAX_PROMPT_TOKENS, usage["max_in"]
    log_cost(a.task, a.model)
    el = time.time() - t0
    stats = dict(task=a.task, model=a.model, requests=usage["requests"], items_labeled=usage["items"], items_unlabeled=usage["fail"],
                 input_tokens=usage["in"], output_tokens=usage["out"], cost_usd=round(cost(a.model), 4),
                 cost_per_item_usd=round(cost(a.model) / max(1, usage["items"]), 8), largest_request_input_tokens=usage["max_in"],
                 refusals=usage["refusals"], seconds=round(el, 1), batch=a.batch)
    if a.stats:
        json.dump(stats, open(a.stats, "w"), indent=1)
    print("DONE", json.dumps(stats), flush=True)

if __name__ == "__main__":
    main()
