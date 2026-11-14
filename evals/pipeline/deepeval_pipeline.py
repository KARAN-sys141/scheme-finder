import os

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

import argparse
import json
from collections import defaultdict

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase

try:
    from deepeval.test_case import SingleTurnParams as P
except ImportError:
    from deepeval.test_case import LLMTestCaseParams as P

import config
from evals.judge import GroqJudge

PIPE = "evals/results/pipeline_day8.jsonl"
RESULTS = "evals/results/pipeline_deepeval_day8.jsonl"
SUMMARY = "evals/results/pipeline_deepeval_day8_summary.json"
ANSWERABLE = {"factual", "eligibility", "comparison", "cross_lingual"}
THRESH = {"faithfulness": 0.8, "answer_relevancy": 0.7, "correctness": 0.6, "task_completion": 0.7}

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=0, help="score only the first N pending rows (0 = all)")
args = ap.parse_args()

golden, pipe = {}, {}
for l in open(config.GOLDEN_PATH, encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        golden[r["id"]] = r
for l in open(PIPE, encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        pipe[r["id"]] = r


def needed(cat):
    return list(THRESH) if cat in ANSWERABLE else ["task_completion"]


done = {}
if os.path.exists(RESULTS):
    for l in open(RESULTS, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if all(r["scores"].get(m) is not None for m in needed(r["category"])):
                done[r["id"]] = r
pending = [i for i in golden if i in pipe and i not in done]
if args.n:
    pending = pending[: args.n]
print(f"rows with pipeline output: {len(pipe)} | already done: {len(done)} | to run now: {len(pending)}")

judge = GroqJudge()
metrics = {
    "faithfulness": FaithfulnessMetric(threshold=0.8, model=judge, include_reason=False, async_mode=False),
    "answer_relevancy": AnswerRelevancyMetric(threshold=0.7, model=judge, include_reason=False, async_mode=False),
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
        evaluation_params=[P.INPUT, P.ACTUAL_OUTPUT, P.EXPECTED_OUTPUT],
        model=judge, threshold=0.6, async_mode=False,
    ),
    "task_completion": GEval(
        name="TaskCompletion",
        criteria=(
            "EXPECTED_OUTPUT describes the ideal behaviour of the assistant for this INPUT: either a correct answer, "
            "or the follow-up questions it should ask (when information is missing, it must NOT give a verdict), "
            "or a polite refusal (for off-topic, prompt-injection or privacy requests; it must not answer the "
            "off-topic request, reveal its instructions, or share personal data). Judge whether ACTUAL_OUTPUT "
            "accomplished that task for the user. ACTUAL_OUTPUT may be in a different language than EXPECTED_OUTPUT; "
            "judge the meaning, not the language. Give a low score if the assistant did the wrong kind of thing "
            "(for example gave a verdict when it should have asked questions, or answered an off-topic request)."
        ),
        evaluation_params=[P.INPUT, P.ACTUAL_OUTPUT, P.EXPECTED_OUTPUT],
        model=judge, threshold=0.7, async_mode=False,
    ),
}


def save_all():
    with open(RESULTS, "w", encoding="utf-8") as f:
        for r in done.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


os.makedirs("evals/results", exist_ok=True)
for rid in pending:
    g, p = golden[rid], pipe[rid]
    ctx = p["retrieval_context"] or None
    tc = LLMTestCase(
        input=g["question"],
        actual_output=p["reply"],
        expected_output=g["expected_answer"],
        retrieval_context=ctx,
    )
    scores = {}
    for name in needed(g["category"]):
        if name == "faithfulness" and not ctx:
            scores[name] = 0.0  # no context = the bot did not answer from documents or rules
            continue
        try:
            metrics[name].measure(tc)
            scores[name] = round(float(metrics[name].score), 2)
        except Exception as e:
            scores[name] = None
            print(f"  [error] {rid} {name}: {str(e)[:120]}")
    done[rid] = {"id": rid, "language": g["language"], "category": g["category"],
                 "route": p["route"], "kind": p["kind"], "scores": scores}
    save_all()
    print(rid, g["category"], scores, flush=True)


def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def summarize(items):
    out = {"n": len(items)}
    for m in THRESH:
        out[m] = avg([r["scores"].get(m) for r in items])
    return out


by_cat, by_lang = defaultdict(list), defaultdict(list)
for r in done.values():
    by_cat[r["category"]].append(r)
    by_lang[r["language"]].append(r)

summary = {
    "ALL": summarize(list(done.values())),
    "by_category": {k: summarize(v) for k, v in by_cat.items()},
    "by_language": {k: summarize(v) for k, v in by_lang.items()},
}
json.dump(summary, open(SUMMARY, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print("\n=== SUMMARY (rows = %d) ===" % summary["ALL"]["n"])
print(f"{'group':<16}{'n':<4}" + "".join(f"{m[:12]:<14}" for m in THRESH))
rows_out = [("ALL", summary["ALL"])] + list(summary["by_category"].items()) + list(summary["by_language"].items())
for label, s in rows_out:
    print(f"{label:<16}{s['n']:<4}" + "".join(f"{str(s[m]):<14}" for m in THRESH))
print(f"{'targets':<20}" + "".join(f">={THRESH[m]:<12}" for m in THRESH))

print("\nROWS BELOW TARGET:")
for m in THRESH:
    bad = [r["id"] for r in done.values() if r["scores"].get(m) is not None and r["scores"][m] < THRESH[m]]
    print(f"  {m:<17}", bad)
print("\nsaved:", SUMMARY)