import time

from src.eligibility.explain import compact
from src.eligibility.graph import chat_turn
from src.generation.chain import answer

# "Can I get / am I eligible / mil sakta hai" type questions go to the eligibility flow
ELIG_CUES = [
    "eligible", "eligibility", "qualify", "can i get", "do i get", "am i ",
    "पात्र", "पात्रता", "मिलेगा", "मिल सकता", "मिल सकती", "मिल सकते",
    "પાત્ર", "મળશે", "મળી શકે",
    "mil sakta", "mil sakti", "mil sakte", "milega", "milegi", "lag sakta",
]
# "how do I ..." questions are information questions even if they contain "eligibility"
HOW_CUES = ["how to", "how do i", "how can i", "कैसे", "kaise", "કેવી રીતે", "કેમ"]


def is_eligibility(message):
    t = message.lower()
    if any(h in t for h in HOW_CUES):
        return False
    return any(c in t for c in ELIG_CUES)


def ask(message, state=None):
    """One chat turn. Returns (record, new_state). Pass new_state back in for the next turn."""
    state = state or {}
    # keep only facts that should survive between turns (language is detected fresh every turn)
    carry = {k: state[k] for k in ("profile", "asked_fields", "schemes") if k in state}
    t0 = time.time()

    if carry.get("asked_fields") or is_eligibility(message):
        out = chat_turn(carry, message)
        results = out.get("results", [])
        rec = {
            "route": "graph",
            "kind": out["kind"],  # followup | verdict | no_scheme
            "language": out["language"],
            "schemes": out.get("schemes", []),
            "verdicts": {r["scheme_id"]: r["status"] for r in results},
            "reply": out["reply"],
            "cited": [],
            "sources": [],
            "retrieval_context": [compact(results)] if results else [],
        }
        new_state = {k: out[k] for k in ("profile", "asked_fields", "schemes") if k in out}
    else:
        r = answer(message)
        rec = {
            "route": "rag",
            "kind": "info",
            "language": r["language"],
            "schemes": [],
            "verdicts": {},
            "reply": r["answer"],
            "cited": r["cited"],
            "sources": r["sources"],
            "retrieval_context": r["retrieval_context"],
        }
        new_state = carry

    rec["latency_s"] = round(time.time() - t0, 2)
    return rec, new_state