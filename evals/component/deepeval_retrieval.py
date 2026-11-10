import os

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

import argparse
import json
from collections import defaultdict

from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

import config
from evals.judge import GroqJudge
from src.retrieval.retriever import SchemeRetriever

ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="hybrid_smart+rerank")
ap.add_argument("--per_lang", type=int, default=1)
ap.add_argument("--fast", action="store_true", help="skip the slowest metric (relevancy)")
args = ap.parse_args()

rows = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["context_keywords"] and r["expected_scheme_ids"] and not r["expected_refusal"]]

pick, count = [], defaultdict(int)
for r in rows:
    if count[r["language"]] < args.per_lang:
        pick.append(r)
        count[r["language"]] += 1
print(f"mode={args.mode} | rows={len(pick)} | fast={args.fast}")

ret = SchemeRetriever()
FN = {
    "dense": lambda q: ret.dense(q, k=5),
    "hybrid_smart": lambda q: ret.hybrid(q, k=5),
    "dense+rerank": lambda q: ret.dense_rerank(q, k=5),
    "hybrid_smart+rerank": lambda q: ret.hybrid_rerank(q, k=5),
}

judge = GroqJudge()
metrics = {
    "precision": ContextualPrecisionMetric(threshold=0.5, model=judge, include_reason=False, async_mode=False),
    "recall": ContextualRecallMetric(threshold=0.5, model=judge, include_reason=False, async_mode=False),
}
if not args.fast:
    metrics["relevancy"] = ContextualRelevancyMetric(
        threshold=0.5, model=judge, include_reason=False, async_mode=False
    )

records = []
for row in pick:
    hits = FN[args.mode](row["question"])
    tc = LLMTestCase(
        input=row["question"],
        actual_output=row["expected_answer"],  # placeholder: no generator yet (Day 5)
        expected_output=row["expected_answer"],
        retrieval_context=[h["text"] for h in hits],
    )
    scores = {}
    for name, m in metrics.items():
        try:
            m.measure(tc)
            scores[name] = round(m.score, 2)
        except Exception as e:
            scores[name] = None
            print(f"  [error] {row['id']} {name}: {str(e)[:100]}")
    records.append({"id": row["id"], "language": row["language"], **scores})
    print(row["id"], row["language"], scores)

summary = defaultdict(lambda: defaultdict(list))
for rec in records:
    for name in metrics:
        if rec[name] is not None:
            summary["ALL"][name].append(rec[name])
            summary[rec["language"]][name].append(rec[name])

print("\n--- AVERAGES ---")
out = {}
for lang, per in summary.items():
    out[lang] = {n: round(sum(v) / len(v), 2) for n, v in per.items()}
    print(lang, out[lang])

os.makedirs("evals/results", exist_ok=True)
path = f"evals/results/deepeval_retrieval_{args.mode.replace('+', '_')}.json"
json.dump({"records": records, "summary": out}, open(path, "w"), indent=2)
print("saved:", path)