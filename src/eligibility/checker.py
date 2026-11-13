import json

import config

RULES = json.load(open(f"{config.PROCESSED_DIR}/scheme_rules.json", encoding="utf-8"))

# the order in which missing facts are asked (max 3 per turn)
FIELD_PRIORITY = [
    "state", "age", "family_income_rs", "owns_farmland", "daughter_order",
    "daughter_birth_date", "is_bpl_listed", "pays_income_tax",
    "is_practising_professional", "is_govt_employee_or_retired_officer",
]
# facts a user cannot answer from memory: send them to the official portal instead
CANNOT_ASK = {"secc_listed"}


def priority(field):
    return FIELD_PRIORITY.index(field) if field in FIELD_PRIORITY else len(FIELD_PRIORITY)


def derive(profile):
    p = dict(profile or {})
    lakh = p.get("family_income_lakh")
    if p.get("family_income_rs") is None and lakh is not None:
        p["family_income_rs"] = lakh * 100000
    # Vahli Dikri needs "born after 2 Aug 2019"; a birth year alone decides it unless it is 2019
    year = p.get("daughter_birth_year")
    if p.get("daughter_birth_date") is None and year is not None:
        if year > 2019:
            p["daughter_birth_date"] = "2020-01-01"
        elif year < 2019:
            p["daughter_birth_date"] = "2018-12-31"
    return p


def compare(actual, op, expected):
    """True / False, or None when the fact is unknown."""
    if actual is None:
        return None
    try:
        if isinstance(actual, str) and isinstance(expected, str) and op == "==":
            return actual.strip().lower() == expected.strip().lower()
        if op == "==":
            return actual == expected
        if op == ">=":
            return actual >= expected
        if op == "<=":
            return actual <= expected
        if op == ">":
            return actual > expected
        if op == "<":
            return actual < expected
    except TypeError:
        return None
    raise ValueError(f"unknown operator {op}")


def evaluate(scheme_id, profile):
    rule = RULES[scheme_id]
    f = derive(profile)
    required = rule["required_fields"]
    met, failed, caveats, unknown = [], [], [], set()

    def test(cond):
        return compare(f.get(cond["field"]), cond["op"], cond["value"])

    # 1) must-have conditions
    for c in rule["base_requirements"]:
        r = test(c)
        if r is True:
            met.append(c["reason"])
        elif r is False:
            failed.append(c["reason"])
        else:
            unknown.add(c["field"])

    # 2) exclusions: if one applies, the user is out
    for c in rule["exclusions"]:
        r = test(c)
        if r is True:
            failed.append(c["reason"])
        elif r is None:
            if c["field"] in required:
                unknown.add(c["field"])
            else:
                caveats.append(c["reason"])

    # 3) routes: the user needs at least ONE route to be fully true
    matched = None
    if rule["routes"]:
        unknown_routes = []
        for route in rule["routes"]:
            results = [test(c) for c in route["all_of"]]
            if all(x is True for x in results):
                matched = matched or route
            elif any(x is False for x in results):
                continue
            else:
                missing = [c["field"] for c, x in zip(route["all_of"], results) if x is None]
                unknown_routes.append((route, missing))
        if matched:
            met.append("Matches: " + matched["name"])
            met.extend(c["reason"] for c in matched["all_of"])
        else:
            for route, missing in unknown_routes:
                askable = [x for x in missing if x in required]
                if askable:
                    unknown.update(askable)
                else:
                    caveats.append("Could also be covered if: " + route["name"])

    # 4) decide
    missing_fields = []
    if failed:
        status = "not_eligible"
    else:
        birth_year_known = f.get("daughter_birth_year") is not None
        askable = {
            x for x in unknown
            if x not in CANNOT_ASK and not (x == "daughter_birth_date" and birth_year_known)
        }
        if askable:
            status = "need_info"
            missing_fields = sorted(askable, key=priority)
        elif unknown:
            status = "check_portal"
        elif rule["routes"] and not matched:
            status = "not_eligible"
            failed.append("None of the eligibility conditions match: " + "; ".join(r["name"] for r in rule["routes"]))
        else:
            status = "likely_eligible"

    return {
        "scheme_id": scheme_id,
        "name": rule["name"],
        "benefit": rule["benefit"],
        "status": status,
        "met": met,
        "failed": failed,
        "missing": missing_fields,
        "caveats": caveats,
        "assumptions": rule["assumptions"],
    }