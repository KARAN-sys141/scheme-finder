import json
import os
import re

import pytest

import config

PATH = "evals/results/pipeline_day8.jsonl"
pytestmark = pytest.mark.skipif(not os.path.exists(PATH), reason="run run_pipeline first")

DEVA = re.compile(r"[\u0900-\u097F]")
GUJ = re.compile(r"[\u0A80-\u0AFF]")

REC, GOLD = {}, {}
if os.path.exists(PATH):
    for l in open(PATH, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            REC[r["id"]] = r
    for l in open(config.GOLDEN_PATH, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            GOLD[r["id"]] = r

EXPECTED_VERDICT = {
    "G009": ("pmkisan", "likely_eligible"),
    "G010": ("pmkisan", "not_eligible"),
    "G011": ("pmkisan", "not_eligible"),
    "G012": ("pmjay", "likely_eligible"),
    "G013": ("vahli_dikri", "likely_eligible"),
    "G014": ("vahli_dikri", "not_eligible"),
    "G015": ("ma_yojana", "likely_eligible"),
    "G016": ("ma_yojana", "likely_eligible"),
}


def ids(category):
    return [i for i, g in GOLD.items() if g["category"] == category]


def test_all_30_rows_present():
    assert len(REC) == 30, f"only {len(REC)} rows in pipeline_day8.jsonl"


@pytest.mark.parametrize("rid", ids("eligibility"))
def test_eligibility_rows_give_verdict(rid):
    assert REC[rid]["kind"] == "verdict", (rid, REC[rid]["kind"], REC[rid]["reply"][:120])


@pytest.mark.parametrize("rid", ids("missing_info"))
def test_missing_info_rows_ask_followup(rid):
    assert REC[rid]["kind"] == "followup", (rid, REC[rid]["kind"], REC[rid]["reply"][:120])


@pytest.mark.parametrize("rid", ids("factual") + ids("comparison") + ids("cross_lingual"))
def test_information_rows_use_rag(rid):
    assert REC[rid]["route"] == "rag", (rid, REC[rid]["route"], REC[rid]["kind"])


@pytest.mark.parametrize("rid", ids("out_of_scope") + ids("adversarial"))
def test_refusal_rows_do_not_cite_scheme_documents(rid):
    assert REC[rid]["route"] == "rag" and REC[rid]["cited"] == [], (rid, REC[rid]["reply"][:150])


@pytest.mark.parametrize("rid,expect", list(EXPECTED_VERDICT.items()))
def test_verdict_exact_match(rid, expect):
    scheme, status = expect
    assert REC[rid]["verdicts"].get(scheme) == status, (rid, REC[rid]["verdicts"])


def test_information_rows_have_citations():
    rows = [REC[i] for i in ids("factual") + ids("comparison") + ids("cross_lingual")]
    missing = [r["id"] for r in rows if not r["cited"]]
    assert len(missing) <= max(1, int(0.15 * len(rows))), f"no citation in: {missing}"


@pytest.mark.parametrize("rid", ids("missing_info"))
def test_followup_in_right_script(rid):
    lang, text = GOLD[rid]["language"], REC[rid]["reply"]
    d, g = len(DEVA.findall(text)), len(GUJ.findall(text))
    ok = (lang == "hi" and d > 0) or (lang == "gu" and g > 0) or (lang in ("en", "hinglish") and d + g == 0)
    assert ok, (rid, lang)