from typing import TypedDict

from langgraph.graph import END, StateGraph

from src.eligibility.checker import evaluate, priority
from src.eligibility.explain import explain
from src.eligibility.extract import extract_profile
from src.eligibility.questions import NO_SCHEME, build_followup
from src.eligibility.router import detect_schemes
from src.generation.language import detect_language


class State(TypedDict, total=False):
    message: str
    language: str
    schemes: list
    profile: dict
    asked_fields: list
    results: list
    reply: str
    kind: str  # followup | verdict | no_scheme


def n_detect(s):
    lang = s.get("language") or detect_language(s["message"])
    found = detect_schemes(s["message"])
    return {"language": lang, "schemes": found or s.get("schemes", [])}


def n_extract(s):
    new = extract_profile(s["message"], s.get("asked_fields"))
    profile = dict(s.get("profile") or {})
    profile.update({k: v for k, v in new.items() if v is not None})
    return {"profile": profile}


def n_check(s):
    return {"results": [evaluate(sid, s["profile"]) for sid in s["schemes"]]}


def route(s):
    if not s["schemes"]:
        return "no_scheme"
    if any(r["status"] == "need_info" for r in s["results"]):
        return "ask"
    return "explain"


def n_ask(s):
    missing = []
    for r in s["results"]:
        for f in r["missing"]:
            if f not in missing:
                missing.append(f)
    missing.sort(key=priority)
    fields = missing[:3]
    return {"asked_fields": fields, "reply": build_followup(fields, s["language"]), "kind": "followup"}


def n_explain(s):
    return {
        "reply": explain(s["results"], s["language"], s["message"]),
        "kind": "verdict",
        "asked_fields": [],
    }


def n_no_scheme(s):
    return {"reply": NO_SCHEME[s["language"]], "kind": "no_scheme", "asked_fields": []}


def build_graph():
    g = StateGraph(State)
    g.add_node("detect", n_detect)
    g.add_node("extract", n_extract)
    g.add_node("check", n_check)
    g.add_node("ask", n_ask)
    g.add_node("explain", n_explain)
    g.add_node("no_scheme", n_no_scheme)
    g.set_entry_point("detect")
    g.add_edge("detect", "extract")
    g.add_edge("extract", "check")
    g.add_conditional_edges("check", route, {"ask": "ask", "explain": "explain", "no_scheme": "no_scheme"})
    g.add_edge("ask", END)
    g.add_edge("explain", END)
    g.add_edge("no_scheme", END)
    return g.compile()


GRAPH = build_graph()


def chat_turn(state, message):
    """state = what the previous turn returned ({} for the first turn)."""
    return GRAPH.invoke({**state, "message": message})