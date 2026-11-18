"""After the official second coder has been scored by the unattended chain, rewrite the first line of the
morning note's failure list so it says exactly what state the validation is in."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = json.load(open(os.path.join(ROOT, "data/public/validation_summary.json")))
p = os.path.join(ROOT, "logs/morning_failures.md")
lines = [l for l in open(p).read().split("\n") if l.strip() and "Validation is still provisional" not in l and "one allowed revision" not in l]
if s.get("status") == "final":
    failed = {c: b["failed_first_test"] for c, b in s["cities"].items() if b["failed_first_test"]}
    if failed and not os.path.exists(os.path.join(ROOT, "data/interim/validation/revision_result.json")):
        lines.insert(0, "- **The one allowed revision of category wording was not run.** The validation numbers are final, but the categories that failed the first test were dropped directly.")
else:
    lines.insert(0, "- **Validation is still provisional.** The blind second coder did not finish after its quota reset. The kappas come from the third AI pass. See `STATE.md` and `logs/final_validation.out`.")
open(p, "w").write("\n".join(lines) + "\n")
print("morning failure list updated; validation status:", s.get("status"))
