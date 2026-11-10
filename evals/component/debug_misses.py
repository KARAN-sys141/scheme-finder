import json
import re
import sys

import config
from src.retrieval.retriever import SchemeRetriever


def norm(s):
    s = s.lower().replace("₹", "").replace(",", "")
    s = re.sub(r"\b(rs\.?|inr)\s*", "", s)
    return re.sub(r"\s+", " ", s)


ids = sys.argv[1:] or ["G003", "G010", "G014", "G029", "G030"]
rows = {}
for line in open(config.GOLDEN_PATH, encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        rows[r["id"]] = r

ret = SchemeRetriever()
for rid in ids:
    row = rows[rid]
    kws = row["context_keywords"]
    gold = [
        c["chunk_id"]
        for c in ret.chunks
        if c["scheme_id"] in row["expected_scheme_ids"]
        and any(norm(k) in norm(c["text"].split("\n", 1)[1]) for k in kws)
    ]
    hits = ret.dense(row["question"], k=20)
    gold_set = set(gold)
    rank = next((i for i, h in enumerate(hits, 1) if h["chunk_id"] in gold_set), None)

    print("\n" + "=" * 80)
    print(rid, row["language"], "|", row["question"])
    print("keywords:", kws)
    print("chunks that contain the keywords:", gold or "NONE")
    print("rank of first such chunk in dense top 20:", rank or ">20")
    if not gold:
        print("DIAGNOSIS: no chunk has these keywords -> ingestion problem or keyword needs a Hindi/Gujarati form")
    elif rank is None or rank > 5:
        print("DIAGNOSIS: chunk exists but ranked too low -> retrieval problem (reranker should help)")
    else:
        print("DIAGNOSIS: retrieved fine at rank", rank)
    print("top 3 dense hits:")
    for h in hits[:3]:
        print("  -", h["chunk_id"])
        print("    ", h["text"].split("\n", 1)[1][:160].replace("\n", " "))