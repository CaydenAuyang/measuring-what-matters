"""Load KEY=value pairs from the project's .env file into the environment (values are never printed)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env(path=None):
    path = path or os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.replace("export ", "").strip(); v = v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v
