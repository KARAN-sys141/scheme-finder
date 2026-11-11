import json
import os
import re

import pytest

import config
from src.generation.language import detect_language

DEVA = re.compile(r"[\u0900-\u097F]")
GUJ = re.compile(r"[\u0A80-\u0AFF]")
LETTER = re.compile(r"[A-Za-z\u0900-\u097F\u0A80-\u0AFF]")


def load_golden():
    return [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]


def test_language_detection_on_golden():
    wrong = []
    for r in load_golden():
        got = detect_language(r["question"])
        if got != r["language"]:
            wrong.append((r["id"], r["language"], got))
    assert not wrong, f"wrong detections (id, expected, got): {wrong}"

ANSWERS = config.ANSWERS_PATH


def load_answers():
    return [json.loads(l) for l in open(ANSWERS, encoding="utf-8") if l.strip()]


@pytest.mark.skipif(not os.path.exists(ANSWERS), reason="run batch_generate first")
def test_answer_script_matches_language():
    bad = []
    for r in load_answers():
        a = r["answer"].replace("।", ".").replace("॥", ".")
        d, g = len(DEVA.findall(a)), len(GUJ.findall(a))
        letters = max(len(LETTER.findall(a)), 1)
        lang = r["detected_language"]
        ok = (
            (lang == "hi" and d >= 0.4 * letters)
            or (lang == "gu" and g >= 0.4 * letters)
            or (lang in ("en", "hinglish") and d + g == 0)
        )
        if not ok:
            bad.append((r["id"], lang))
    assert not bad, f"answer language/script mismatch: {bad}"


@pytest.mark.skipif(not os.path.exists(ANSWERS), reason="run batch_generate first")
def test_answerable_questions_have_citations():
    skip = {"missing_info", "out_of_scope", "adversarial"}
    rows = [r for r in load_answers() if r["category"] not in skip]
    missing = [r["id"] for r in rows if not r["cited"]]
    assert len(missing) <= max(1, int(0.15 * len(rows))), f"no citation in: {missing}"


@pytest.mark.skipif(not os.path.exists(ANSWERS), reason="run batch_generate first")
def test_out_of_scope_has_no_citations():
    rows = [r for r in load_answers() if r["category"] == "out_of_scope"]
    cited = [r["id"] for r in rows if r["cited"]]
    assert not cited, f"out-of-scope answers should not cite scheme documents: {cited}"