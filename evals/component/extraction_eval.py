import json

import config
from src.eligibility.extract import extract_profile

MAP = {
    "state": "state",
    "age": "age",
    "family_income_lakh": "family_income_lakh",
    "pays_income_tax": "pays_income_tax",
    "owns_farmland": "owns_farmland",
    "daughter_order": "daughter_order",
    "birth_year": "daughter_birth_year",
}

rows = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["category"] == "eligibility"]

total = correct = 0
bad = []
for r in rows:
    got = extract_profile(r["question"])
    for gk, pk in MAP.items():
        if gk in r["user_profile"]:
            total += 1
            want = r["user_profile"][gk]
            val = got.get(pk)
            ok = val is not None and (
                abs(val - want) < 0.01 if isinstance(want, (int, float)) and not isinstance(want, bool) else val == want
            )
            correct += ok
            if not ok:
                bad.append((r["id"], pk, "want", want, "got", val))
    print(r["id"], r["language"], got, flush=True)

print(f"\nfield accuracy: {correct}/{total} = {correct / total:.2f}")
print("target >= 0.85")
for b in bad:
    print("MISMATCH:", b)