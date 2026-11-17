"""Fill MORNING.md at the project root from its template."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import fill_template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
text, missing = fill_template.fill(open(os.path.join(ROOT, "src/templates/root/MORNING.template.md")).read())
open(os.path.join(ROOT, "MORNING.md"), "w").write(text)
print("MORNING.md | not available:", sorted(set(missing)) if missing else "none")
