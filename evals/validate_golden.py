import json, glob, re
from collections import Counter

REQUIRED = ["id", "language", "category", "question", "user_profile", "expected_answer",
            "expected_scheme_ids", "context_keywords", "must_ask_followup", "expected_refusal"]
LANGS = {"en", "hi", "gu", "hinglish"}

def norm(s):
    s = s.lower().replace("₹", "").replace(",", "")
    s = re.sub(r"\b(rs\.?|inr)\s*", "", s)
    return re.sub(r"\s+", " ", s)

raw = ""
for f in glob.glob("data/raw/*.txt"):
    raw += " " + open(f, encoding="utf-8").read()
raw = norm(raw)

rows, errors, ids = [], [], set()
for n, line in enumerate(open("data/golden/golden_dataset.jsonl", encoding="utf-8"), 1):
    if not line.strip():
        continue
    try:
        r = json.loads(line)
    except Exception as e:
        errors.append(f"line {n}: invalid JSON ({e})")
        continue
    rows.append(r)
    for k in REQUIRED:
        if k not in r:
            errors.append(f"{r.get('id', n)}: missing key {k}")
    if r.get("language") not in LANGS:
        errors.append(f"{r.get('id')}: bad language")
    if r.get("id") in ids:
        errors.append(f"{r.get('id')}: duplicate id")
    ids.add(r.get("id"))
    kws = r.get("context_keywords", [])
    if kws and not any(norm(k) in raw for k in kws):
        errors.append(f"{r['id']}: none of {kws} found in data/raw -> check your source files")

print("rows:", len(rows))
print("by category:", dict(Counter(r["category"] for r in rows)))
print("by language:", dict(Counter(r["language"] for r in rows)))
print("ERRORS:" if errors else "ALL GOOD")
for e in errors:
    print(" -", e)