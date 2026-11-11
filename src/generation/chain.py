import re
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import config
from src.generation.language import detect_language
from src.generation.prompts import HUMAN, LANG_INSTRUCTION, SYSTEM
from src.retrieval.search import search


def get_llm():
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=0,
        max_tokens=2000,
        reasoning_effort="low",
    )


prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])
chain = prompt | get_llm() | StrOutputParser()


def format_context(hits):
    parts = []
    for i, h in enumerate(hits, 1):
        body = h["text"].split("\n", 1)[1]
        source = h["chunk_id"].split("::")[0]
        parts.append(f"[{i}] {h['scheme_id']} | {h['section']} | {source}\n{body}")
    return "\n\n".join(parts)


def run_chain(inputs):
    for attempt in range(6):
        try:
            out = chain.invoke(inputs)
            if out and out.strip():
                return out.strip()
            raise ValueError("empty answer (try a bigger max_tokens in get_llm)")
        except Exception as e:
            wait = 8 * (attempt + 1)
            print(f"[llm] retry {attempt + 1}: {str(e)[:110]} (sleep {wait}s)")
            time.sleep(wait)
    raise RuntimeError("LLM failed after 6 retries")

CITE = re.compile(r"[\[【]\s*(\d+(?:\s*[,;]\s*\d+)*)\s*[\]】]")


def extract_cited(text, n):
    nums = set()
    for m in CITE.findall(text):
        for x in re.split(r"[,;]", m):
            x = x.strip()
            if x.isdigit() and 1 <= int(x) <= n:
                nums.add(int(x))
    return sorted(nums)


def answer(question, scheme_ids=None):
    lang = detect_language(question)
    hits = search(question, scheme_ids=scheme_ids)
    text = run_chain(
        {
            "language_instruction": LANG_INSTRUCTION[lang],
            "context": format_context(hits),
            "question": question,
        }
    )
    cited = extract_cited(text, len(hits))
    return {
        "question": question,
        "language": lang,
        "answer": text,
        "cited": cited,
        "sources": [
            {
                "n": n,
                "scheme_id": hits[n - 1]["scheme_id"],
                "section": hits[n - 1]["section"],
                "chunk_id": hits[n - 1]["chunk_id"],
            }
            for n in cited
        ],
        "retrieval_context": [h["text"] for h in hits],
    }