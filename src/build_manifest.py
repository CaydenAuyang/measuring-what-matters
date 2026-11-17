"""Merge the per-source download manifests into data/manifest.csv (every downloaded file: source address,
time retrieved, SHA-256, status)."""
import glob, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parts = []
for p in sorted(glob.glob(os.path.join(ROOT, "data/raw/**/manifest*.csv"), recursive=True)):
    d = pd.read_csv(p, dtype=str)
    d["manifest"] = os.path.relpath(p, ROOT)
    parts.append(d)
m = pd.concat(parts, ignore_index=True)
cols = ["path", "source_url", "retrieved_utc", "sha256", "status", "note", "manifest"]
for c in cols:
    if c not in m.columns: m[c] = ""
m[cols].to_csv(os.path.join(ROOT, "data/manifest.csv"), index=False)
print(len(m), "files in data/manifest.csv from", len(parts), "manifests;", m.status.value_counts().to_dict())
