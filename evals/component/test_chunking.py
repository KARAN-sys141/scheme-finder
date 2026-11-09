import json, re
from collections import defaultdict

import pytest

import config

SCHEMES = ["pmkisan", "pmjay", "vahli_dikri", "ma_yojana"]


def norm(s):
    s = s.lower().replace("₹", "").replace(",", "")
    s = re.sub(r"\b(rs\.?|inr)\s*", "", s)
    return re.sub(r"\s+", " ", s)


CHUNKS = [json.loads(l) for l in open(f"{config.PROCESSED_DIR}/chunks.jsonl", encoding="utf-8")]
GOLDEN = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]

by_scheme = defaultdict(str)
for c in CHUNKS:
    by_scheme[c["scheme_id"]] += " " + norm(c["text"])


def test_chunk_sizes():
    bad = [c["chunk_id"] for c in CHUNKS if not (40 <= len(c["text"]) <= 1200)]
    assert not bad, f"chunks with bad length: {bad}"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_scheme_has_chunks(scheme):
    assert sum(1 for c in CHUNKS if c["scheme_id"] == scheme) >= 3


@pytest.mark.parametrize("lang", ["en", "hi", "gu"])
def test_language_present(lang):
    assert any(c["language"] == lang for c in CHUNKS), f"no {lang} chunks"


KW_ROWS = [r for r in GOLDEN if r["context_keywords"] and r["expected_scheme_ids"]]


@pytest.mark.parametrize("row", KW_ROWS, ids=[r["id"] for r in KW_ROWS])
def test_golden_keywords_in_chunks(row):
    text = " ".join(by_scheme[s] for s in row["expected_scheme_ids"])
    assert any(norm(k) in text for k in row["context_keywords"]), (
        f"{row['id']}: none of {row['context_keywords']} found in chunks of {row['expected_scheme_ids']}"
    )


def test_scheme_rules_file():
    rules = json.load(open(f"{config.PROCESSED_DIR}/scheme_rules.json", encoding="utf-8"))
    for s in SCHEMES:
        assert s in rules, f"missing scheme {s}"
        for key in ["name", "benefit", "base_requirements", "routes", "exclusions", "required_fields", "assumptions"]:
            assert key in rules[s], f"{s} missing {key}"