import os

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

import argparse
import json
import re
from collections import defaultdict

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, HallucinationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

import config
from evals.judge import GroqJudge

RESULTS = "evals/results/generator_day6.jsonl"
SUMMARY = "evals/results/generator_day6_summary.json"
ANSWERABLE = {"factual", "eligibility", "comparison", "cross_lingual"}
THRESH = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.7,
    "hallucination": 0.8,  # lower is better
    "correctness": 0.6,
    "language_match": 0.8,
    "simplicity": 0.6,
}

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=0, help="score only the first N pending rows (0 = all)")
ap.add_argument("--reasons", action="store_true", help="also save the judge's reason (slower)")
args = ap.parse_args()

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

rows = [i for i in golden if golden[i]["category"] in ANSWERABLE and i in answers]
print("answerable rows with saved answers:", len(rows))

done = {}
if os.path.exists(RESULTS):
    for l in open(RESULTS, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if all(r["scores"].get(m) is not None for m in THRESH):
                done[r["id"]] = r
pending = [i for i in rows if i not in done]
if args.n:
    pending = pending[: args.n]
print(f"already done: {len(done)} | to run now: {len(pending)}")

judge = GroqJudge()
R = args.reasons

metrics = {
    "faithfulness": FaithfulnessMetric(threshold=0.8, model=judge, include_reason=R, async_mode=False),
    "answer_relevancy": AnswerRelevancyMetric(threshold=0.7, model=judge, include_reason=R, async_mode=False),
    "hallucination": HallucinationMetric(threshold=0.8, model=judge, include_reason=R, async_mode=False),
    "correctness": GEval(
        name="Correctness",
        criteria=(
            "Compare ACTUAL_OUTPUT with EXPECTED_OUTPUT. Key facts (amounts, age and income limits, "
            "yes/no or eligible/not-eligible verdict, scheme names) must match. EXPECTED_OUTPUT is in English "
            "while ACTUAL_OUTPUT may be in Hindi, Gujarati or Hinglish: judge the meaning, not the language. "
            "Saying 'likely eligible' instead of 'yes' is acceptable. Penalise wrong or missing numbers or the "
            "opposite verdict. Do NOT penalise extra helpful detail, citation markers like [1], or a line asking "
            "the user to confirm on the official portal."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        model=judge, threshold=0.6, async_mode=False,
    ),
    "language_match": GEval(
        name="LanguageMatch",
        criteria=(
            "ACTUAL_OUTPUT must be in the same language and script as the user's question in INPUT. "
            "English question -> English. Hindi in Devanagari -> Hindi in Devanagari. Gujarati script -> "
            "Gujarati script. Hinglish (Hindi written in Roman letters) -> Hinglish in Roman letters only. "
            "Scheme names, numbers and citation markers like [1] are allowed in any script. "
            "Penalise a reply in a different language or with mixed scripts."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge, threshold=0.8, async_mode=False,
    ),
    "simplicity": GEval(
        name="Simplicity",
        criteria=(
            "ACTUAL_OUTPUT should be easy for a person with little education: short sentences, everyday words, "
            "no jargon, no long paragraphs, at most about 6 sentences or bullet points. "
            "Penalise long, complicated or heavy official-sounding text."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge, threshold=0.6, async_mode=False,
    ),
}


def save_all():
    with open(RESULTS, "w", encoding="utf-8") as f:
        for r in done.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


os.makedirs("evals/results", exist_ok=True)

for rid in pending:
    g, a = golden[rid], answers[rid]
    tc = LLMTestCase(
        input=g["question"],
        actual_output=a["answer"],
        expected_output=g["expected_answer"],
        retrieval_context=a["retrieval_context"],
        context=["\n\n".join(a["retrieval_context"])],
    )
    scores, reasons = {}, {}
    for name, m in metrics.items():
        try:
            m.measure(tc)
            scores[name] = round(float(m.score), 2)
            if R:
                reasons[name] = getattr(m, "reason", None)
        except Exception as e:
            scores[name] = None
            print(f"  [error] {rid} {name}: {str(e)[:120]}")
    done[rid] = {
        "id": rid, "language": g["language"], "category": g["category"],
        "scores": scores, "reasons": reasons,
    }
    save_all()
    print(rid, g["language"], scores, flush=True)


def passes(metric, value):
    return value >= THRESH[metric]


def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


groups = {"ALL": list(done.values())}
by_lang, by_cat = defaultdict(list), defaultdict(list)
for r in done.values():
    by_lang[r["language"]].append(r)
    by_cat[r["category"]].append(r)


def summarize(items):
    out = {"n": len(items)}
    for m in THRESH:
        out[m] = avg([r["scores"].get(m) for r in items])
    return out


summary = {
    "ALL": summarize(groups["ALL"]),
    "by_language": {k: summarize(v) for k, v in by_lang.items()},
    "by_category": {k: summarize(v) for k, v in by_cat.items()},
}

ans_rows = [answers[i] for i in done if i in answers]
words = [len(a["answer"].split()) for a in ans_rows]
summary["deterministic"] = {
    "avg_words": round(sum(words) / len(words)) if words else None,
    "with_citation_pct": round(100 * sum(1 for a in ans_rows if a["cited"]) / max(len(ans_rows), 1)),
}
json.dump(summary, open(SUMMARY, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print("\n=== SUMMARY (n = %d) ===" % summary["ALL"]["n"])
print(f"{'group':<16}" + "".join(f"{m[:11]:<13}" for m in THRESH))
for label, s in [("ALL", summary["ALL"])] + [(k, v) for k, v in summary["by_language"].items()]:
    print(f"{label:<16}" + "".join(f"{str(s[m]):<13}" for m in THRESH))
print("targets         " + "".join(f"{'>=' + str(THRESH[m]):<13}" for m in THRESH))
print("deterministic:", summary["deterministic"])

print("\nROWS BELOW TARGET:")
for m in THRESH:
    bad = [r["id"] for r in done.values() if r["scores"].get(m) is not None and not passes(m, r["scores"][m])]
    print(f"  {m:<17}", bad)
print("\nsaved:", SUMMARY)