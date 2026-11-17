"""Second coder and third pass for the validation set: a Gemini model reads each article's real headline
and opening lines, blind to the first coder's labels.

Usage: python src/coder2_gemini.py --city hk --model gemini-3.5-flash-lite --role coder2 [--tag v1] [--batch 25] [--rpm 10]
       (input: data/interim/validation/<city>_coder2_input_<tag>.jsonl; output: <city>_<role>_labels_<tag>.csv)
The input file never contains the first coder's labels.
"""
import argparse, csv, datetime, json, os, sys, time
import pandas as pd, requests
sys.path.insert(0, os.path.dirname(__file__))
import codebook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "data/interim/validation")
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SYSTEM = open(os.path.join(ROOT, "src/coder2_prompt.md")).read()
ABOUT = ["yes", "no", "unclear"]

def fmt(n, r):
    return (f'[{n}] city: {r["city"]} | outlet: {r["outlet"]} | headline: {r["headline"]} | '
            f'summary: {r.get("summary_line") or ""} | opening: {r["opening_lines"]}')

def call(model, text, key):
    body = {"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "ARRAY", "items": {"type": "STRING"}},
                                 "thinkingConfig": {"thinkingLevel": "minimal"}}}
    r = requests.post(API.format(model=model), headers={"x-goog-api-key": key}, json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
    d = r.json()
    return json.loads(d["candidates"][0]["content"]["parts"][0]["text"]), d.get("usageMetadata", {}), d.get("modelVersion", "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True); ap.add_argument("--model", required=True); ap.add_argument("--role", default="coder2")
    ap.add_argument("--tag", default="v1"); ap.add_argument("--batch", type=int, default=25); ap.add_argument("--rpm", type=float, default=10)
    ap.add_argument("--input", default=""); ap.add_argument("--output", default="")
    a = ap.parse_args()
    key = os.environ["GEMINI_API_KEY"]
    inp = a.input or os.path.join(V, f"{a.city}_coder2_input_{a.tag}.jsonl")
    outp = a.output or os.path.join(V, f"{a.city}_{a.role}_labels_{a.tag}.csv")
    rows = [json.loads(l) for l in open(inp)]
    done = set(pd.read_csv(outp, dtype=str).vid) if os.path.exists(outp) else set()
    rows = [r for r in rows if r["vid"] not in done]
    new = not os.path.exists(outp)
    tin = tout = nreq = 0
    with open(outp, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["vid", "category", "tone", "about_city", "model_version"])
        for i in range(0, len(rows), a.batch):
            chunk = rows[i:i + a.batch]; pending = chunk
            for attempt in range(5):
                if not pending: break
                text = "ITEMS\n" + "\n".join(fmt(k + 1, r) for k, r in enumerate(pending))
                try:
                    arr, um, mv = call(a.model, text, key); nreq += 1
                    tin += um.get("promptTokenCount", 0); tout += um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)
                except Exception as e:
                    msg = str(e)
                    print("error:", msg[:200], flush=True)
                    if "PerDay" in msg:
                        print("DAILY QUOTA REACHED", flush=True); sys.exit(2)
                    time.sleep(20 + 10 * attempt); continue
                got = {}
                for s in arr:
                    try:
                        n, cat, tone, ab = [x.strip() for x in s.split(":")]
                        if cat in codebook.LABELS and tone in codebook.TONES and ab in ABOUT: got[int(n)] = (cat, tone, ab)
                    except Exception:
                        pass
                for k, r in enumerate(pending):
                    if k + 1 in got: w.writerow([r["vid"], *got[k + 1], mv])
                f.flush()
                pending = [r for k, r in enumerate(pending) if k + 1 not in got]
                time.sleep(60.0 / a.rpm)
            if pending: print("UNLABELED after retries:", [r["vid"] for r in pending], flush=True)
    with open(os.path.join(ROOT, "logs", "api_costs.csv"), "a") as f:
        csv.writer(f).writerow([datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), f"{a.role} {a.city} {a.tag}", a.model, nreq, tin, tout, 0.0])
    n_out = len(pd.read_csv(outp)) if os.path.exists(outp) else 0
    print(f"DONE {a.role} {a.city}: {n_out} rows in {outp}, {nreq} requests, tokens in {tin} out {tout}", flush=True)

if __name__ == "__main__":
    main()
