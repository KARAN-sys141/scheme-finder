import json
import re
import time

from langchain_groq import ChatGroq

import config
from src.eligibility.questions import QUESTIONS

TYPES = {
    "state": str,
    "age": int,
    "family_income_lakh": float,
    "owns_farmland": bool,
    "pays_income_tax": bool,
    "is_practising_professional": bool,
    "is_govt_employee_or_retired_officer": bool,
    "monthly_pension_rs": float,
    "is_bpl_listed": bool,
    "secc_listed": bool,
    "daughter_order": int,
    "daughter_birth_year": int,
    "is_asha_worker": bool,
    "is_accredited_reporter": bool,
    "is_class3_4_fixed_pay_state_employee": bool,
    "is_institutional_landholder": bool,
    "holds_constitutional_post": bool,
    "is_nri": bool,
}

DESCRIPTIONS = {
    "state": "Indian state the user lives in, in English (e.g. Gujarat)",
    "age": "age in years of the person who would receive the benefit, only if a number is clearly stated",
    "family_income_lakh": "total yearly family income in lakh rupees (3.5 means Rs 3,50,000; 50,000 rupees is 0.5). If a monthly income is given, multiply by 12 first",
    "owns_farmland": "true if the family owns agricultural land, false if it clearly has none",
    "pays_income_tax": "true if anyone in the family pays income tax, false if clearly not",
    "is_practising_professional": "true if a family member is a practising doctor, engineer, lawyer, chartered accountant or architect",
    "is_govt_employee_or_retired_officer": "true if a family member is a government employee or retired government officer",
    "monthly_pension_rs": "monthly pension in rupees",
    "is_bpl_listed": "true if the family is in the BPL list or has a BPL card",
    "secc_listed": "true if the family is listed in SECC 2011",
    "daughter_order": "1 for first daughter, 2 for second, 3 for third or later",
    "daughter_birth_year": "four digit birth year of the daughter",
    "is_asha_worker": "true if a family member is an ASHA worker",
    "is_accredited_reporter": "true if a family member is an accredited reporter",
    "is_class3_4_fixed_pay_state_employee": "true if a family member is a Class-3 or Class-4 fixed-pay state government employee",
    "is_institutional_landholder": "true if the land belongs to an institution",
    "holds_constitutional_post": "true if a family member holds or held a constitutional post, minister, MP or MLA",
    "is_nri": "true if the family is a non-resident Indian family",
}

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=config.EXTRACT_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0,
            max_tokens=1500,
            reasoning_effort="low",
        )
    return _llm


def build_prompt(asked_fields):
    lines = [
        "You extract facts about a user from the user's message (English, Hindi, Gujarati or Hinglish).",
        "The user's message arrives in the next turn. Reply with ONLY a JSON object and nothing else.",
        "Include a key ONLY if the user clearly stated that fact or it is directly implied.",
        "Never guess. If a fact is not stated, leave the key out. Do not invent numbers.",
        "If no facts are stated, reply with {}.",
        "",
        "Allowed keys and meaning:",
    ]
    for k, d in DESCRIPTIONS.items():
        lines.append(f"- {k}: {d}")
    if asked_fields:
        lines += [
            "",
            "The assistant has just asked the user these questions, and the user's message may be a short reply "
            "(like yes, no, haan, nahi) to them. Apply the reply to the question it answers:",
        ]
        for i, f in enumerate(asked_fields, 1):
            if f in QUESTIONS:
                lines.append(f"{i}. [{f}] {QUESTIONS[f]['en']}")
    return "\n".join(lines)


def coerce(key, value):
    t = TYPES[key]
    if value is None:
        return None
    try:
        if t is bool:
            if isinstance(value, bool):
                return value
            s = str(value).strip().lower()
            return True if s in ("true", "yes") else False if s in ("false", "no") else None
        if isinstance(value, bool):
            return None
        if t is int:
            return int(float(value))
        if t is float:
            return float(value)
        s = str(value).strip()
        return s.title() if s else None
    except (ValueError, TypeError):
        return None


def parse_json(text):
    text = re.sub(r"```(?:json)?", "", text or "")
    spans, depth, start = [], 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                spans.append(text[start: i + 1])
    for s in reversed(spans):
        try:
            d = json.loads(s)
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    return None


def extract_profile(text, asked_fields=None):
    system = build_prompt(asked_fields or [])
    for attempt in range(6):
        try:
            out = get_llm().invoke([("system", system), ("human", "USER MESSAGE:\n" + text)]).content or ""
        except Exception as e:
            wait = 10 * (attempt + 1)
            print(f"[extract] retry {attempt + 1}: {str(e)[:100]} (sleep {wait}s)")
            time.sleep(wait)
            continue
        data = parse_json(out)
        if data is None:
            print(f"[extract] unreadable reply (attempt {attempt + 1}): {out[:200]!r}")
            continue
        clean = {}
        for k, v in data.items():
            if k in TYPES:
                c = coerce(k, v)
                if c is not None:
                    clean[k] = c
        return clean
    print("[extract] giving up, using empty profile")
    return {}