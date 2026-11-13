import json
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import config
from src.generation.prompts import LANG_INSTRUCTION

SYSTEM = """You are SchemeMitra. A rule checker has already decided the eligibility result for each scheme. Explain it to the user.
Rules:
1. Use ONLY the RESULTS JSON below. Never add facts, amounts or rules that are not in it.
2. status meanings: likely_eligible = tell the user they are likely eligible. not_eligible = explain simply why not, using the 'failed' reasons. check_portal = say you cannot confirm this from the chat and the user should check on the official portal.
3. Never say definitely eligible. Say likely.
4. If 'caveats' is not empty, add ONE short sentence saying this holds only if none of those apply, and name them briefly.
5. If a scheme is likely_eligible, mention its benefit in one short sentence.
6. {language_instruction}
7. At most 6 short sentences or bullet points. End with one line asking the user to confirm on the official portal or at the nearest government office.
8. Keep scheme names and numbers exactly as written in RESULTS."""

HUMAN = "RESULTS:\n{results}\n\nUSER QUESTION: {question}"

_chain = None


def get_chain():
    global _chain
    if _chain is None:
        llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0,
            max_tokens=2000,
            reasoning_effort="low",
        )
        _chain = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)]) | llm | StrOutputParser()
    return _chain


def compact(results):
    out = []
    for r in results:
        item = {"scheme": r["name"], "status": r["status"], "failed": r["failed"], "caveats": r["caveats"][:4]}
        if r["status"] == "likely_eligible":
            item["benefit"] = r["benefit"]
            item["met"] = r["met"]
        if r["status"] == "check_portal":
            item["note"] = r["assumptions"]
        out.append(item)
    return json.dumps(out, ensure_ascii=False, indent=1)


def explain(results, lang, question):
    inputs = {
        "language_instruction": LANG_INSTRUCTION[lang],
        "results": compact(results),
        "question": question,
    }
    for attempt in range(6):
        try:
            text = get_chain().invoke(inputs)
            if text and text.strip():
                return text.strip()
            raise ValueError("empty answer")
        except Exception as e:
            wait = 8 * (attempt + 1)
            print(f"[explain] retry {attempt + 1}: {str(e)[:100]} (sleep {wait}s)")
            time.sleep(wait)
    raise RuntimeError("explain failed after 6 retries")