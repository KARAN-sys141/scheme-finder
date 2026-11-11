import os

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

import json

from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

import config
from evals.judge import GroqJudge

RESULTS = "evals/results/generator_day6.jsonl"

golden = {}
for l in open(config.GOLDEN_PATH, encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        golden[r["id"]] = r

answers = {}
for l in open(config.ANSWERS_PATH, encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        answers[r["id"]] = r

results = [json.loads(l) for l in open(RESULTS, encoding="utf-8") if l.strip()]

judge = GroqJudge()
metric = HallucinationMetric(threshold=0.3, model=judge, include_reason=False, async_mode=False)

for r in results:
    a, g = answers[r["id"]], golden[r["id"]]
    tc = LLMTestCase(
        input=g["question"],
        actual_output=a["answer"],
        context=["\n\n".join(a["retrieval_context"])],
    )
    try:
        metric.measure(tc)
        r["scores"]["hallucination"] = round(float(metric.score), 2)
    except Exception as e:
        print("  [error]", r["id"], str(e)[:120])
    print(r["id"], r["scores"]["hallucination"], flush=True)
    with open(RESULTS, "w", encoding="utf-8") as f:
        for x in results:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")