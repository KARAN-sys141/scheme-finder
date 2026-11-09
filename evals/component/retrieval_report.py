import json
import os
import re
from collections import defaultdict

import config
from src.retrieval.retriever import SchemeRetriever

K = 5


def norm(s):
    s = s.lower().replace("₹", "").replace(",", "")
    s = re.sub(r"\b(rs\.?|inr)\s*", "", s)
    return re.sub(r"\s+", " ", s)


rows = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["context_keywords"] and r["expected_scheme_ids"]]
print("rows evaluated:", len(rows))

ret = SchemeRetriever()

MODES = {
    "dense": lambda q, row: ret.dense(q, k=K),
    "sparse": lambda q, row: ret.sparse(q, k=K),
    "hybrid": lambda q, row: ret.hybrid(q, k=K),
    "hybrid+scheme_filter": lambda q, row: ret.hybrid(q, k=K, scheme_ids=row["expected_scheme_ids"]),
}


def kw_rank(hits, row):
    for i, h in enumerate(hits, 1):
        if h["scheme_id"] in row["expected_scheme_ids"]:
            body = norm(h["text"].split("\n", 1)[1])
            if any(norm(k) in body for k in row["context_keywords"]):
                return i
    return 0


results, misses = {}, defaultdict(list)
for mode, fn in MODES.items():
    stats = defaultdict(lambda: {"n": 0, "scheme": 0, "kw": 0, "mrr": 0.0})
    for row in rows:
        hits = fn(row["question"], row)
        scheme_ok = any(h["scheme_id"] in row["expected_scheme_ids"] for h in hits)
        rank = kw_rank(hits, row)
        for key in ("ALL", row["language"]):
            s = stats[key]
            s["n"] += 1
            s["scheme"] += scheme_ok
            s["kw"] += rank > 0
            s["mrr"] += (1 / rank) if rank else 0
        if rank == 0:
            misses[mode].append(f"{row['id']}({row['language']})")
    results[mode] = {
        k: {
            "n": v["n"],
            "scheme_hit": round(v["scheme"] / v["n"], 2),
            "kw_hit": round(v["kw"] / v["n"], 2),
            "mrr": round(v["mrr"] / v["n"], 2),
        }
        for k, v in stats.items()
    }

print(f"\n{'mode':<22}{'lang':<10}{'n':<4}{'scheme@5':<10}{'kw@5':<8}{'MRR'}")
for mode, per in results.items():
    for lang in ["ALL", "en", "hi", "gu", "hinglish"]:
        if lang in per:
            v = per[lang]
            print(f"{mode:<22}{lang:<10}{v['n']:<4}{v['scheme_hit']:<10}{v['kw_hit']:<8}{v['mrr']}")
    print()

for mode in ["hybrid", "hybrid+scheme_filter"]:
    print(f"MISSES [{mode}]:", misses[mode])

os.makedirs("evals/results", exist_ok=True)
json.dump(results, open("evals/results/retrieval_day3.json", "w"), indent=2)
print("\nsaved: evals/results/retrieval_day3.json")