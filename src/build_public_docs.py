"""Fill the dataset documents (README, data card, codebook) into data/public/."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import fill_template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "src/templates/public")
for name in ["README", "data_card", "codebook"]:
    text, missing = fill_template.fill(open(os.path.join(T, f"{name}.template.md")).read())
    open(os.path.join(ROOT, "data/public", f"{name}.md"), "w").write(text)
    print(f"data/public/{name}.md", "| not available:", sorted(set(missing)) if missing else "none")
