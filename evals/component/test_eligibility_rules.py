import json

import pytest

import config
from src.eligibility.checker import evaluate
from src.eligibility.router import detect_schemes

GOLDEN = {}
for line in open(config.GOLDEN_PATH, encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        GOLDEN[r["id"]] = r


def profile_from_golden(up):
    p = {}
    for k in ("state", "age", "pays_income_tax", "owns_farmland", "daughter_order"):
        if k in up:
            p[k] = up[k]
    if "family_income_lakh" in up:
        p["family_income_lakh"] = up["family_income_lakh"]
    if "birth_year" in up:
        p["daughter_birth_year"] = up["birth_year"]
    if "land_hectares" in up:
        p["owns_farmland"] = up["land_hectares"] > 0
    if "doctor" in up.get("occupation", "").lower():
        p["is_practising_professional"] = True
    return p


def verdicts(row):
    p = profile_from_golden(row["user_profile"])
    return {s: evaluate(s, p)["status"] for s in detect_schemes(row["question"])}


def test_router_on_golden():
    for rid in ["G009", "G010", "G011", "G012", "G013", "G014", "G015", "G016",
                "G017", "G018", "G019", "G020"]:
        row = GOLDEN[rid]
        found = set(detect_schemes(row["question"]))
        assert found and found <= set(row["expected_scheme_ids"]), (rid, found)


@pytest.mark.parametrize("rid,scheme,expected", [
    ("G009", "pmkisan", "likely_eligible"),
    ("G010", "pmkisan", "not_eligible"),
    ("G011", "pmkisan", "not_eligible"),
    ("G012", "pmjay", "likely_eligible"),
    ("G013", "vahli_dikri", "likely_eligible"),
    ("G014", "vahli_dikri", "not_eligible"),
    ("G015", "ma_yojana", "likely_eligible"),
    ("G016", "ma_yojana", "likely_eligible"),
])
def test_eligibility_verdicts(rid, scheme, expected):
    assert verdicts(GOLDEN[rid]).get(scheme) == expected


@pytest.mark.parametrize("rid", ["G017", "G018", "G019", "G020"])
def test_missing_info_rows_need_followup(rid):
    v = verdicts(GOLDEN[rid])
    assert v and "need_info" in v.values(), (rid, v)


def test_pmjay_age_boundary():
    assert evaluate("pmjay", {"age": 70})["status"] == "likely_eligible"
    assert evaluate("pmjay", {"age": 69})["status"] == "check_portal"


def test_vahli_birth_year_2019_needs_portal():
    p = {"state": "Gujarat", "family_income_rs": 100000, "daughter_order": 1, "daughter_birth_year": 2019}
    assert evaluate("vahli_dikri", p)["status"] == "check_portal"


def test_ma_not_eligible_lists_other_routes():
    p = {"state": "Gujarat", "family_income_rs": 450000, "age": 30, "is_bpl_listed": False}
    r = evaluate("ma_yojana", p)
    assert r["status"] == "not_eligible" and r["caveats"]


def test_ma_senior_with_income_up_to_6_lakh():
    p = {"state": "Gujarat", "family_income_rs": 450000, "age": 65, "is_bpl_listed": False}
    assert evaluate("ma_yojana", p)["status"] == "likely_eligible"


def test_ma_asks_bpl_when_unknown():
    p = {"state": "Gujarat", "family_income_rs": 450000, "age": 30}
    r = evaluate("ma_yojana", p)
    assert r["status"] == "need_info" and "is_bpl_listed" in r["missing"]


def test_pmkisan_rules_ask_only_two_things():
    r = evaluate("pmkisan", {})
    assert r["status"] == "need_info" and set(r["missing"]) == {"owns_farmland", "pays_income_tax"}