import json
import os
import time

import config
from src.generation.chain import answer


def main():
    rows = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]
    os.makedirs(os.path.dirname(config.ANSWERS_PATH), exist_ok=True)

    done = set()
    if os.path.exists(config.ANSWERS_PATH):
        done = {json.loads(l)["id"] for l in open(config.ANSWERS_PATH, encoding="utf-8") if l.strip()}

    with open(config.ANSWERS_PATH, "a", encoding="utf-8") as f:
        for row in rows:
            if row["id"] in done:
                continue
            r = answer(row["question"])
            rec = {
                "id": row["id"],
                "category": row["category"],
                "language": row["language"],
                "detected_language": r["language"],
                "question": row["question"],
                "answer": r["answer"],
                "cited": r["cited"],
                "sources": r["sources"],
                "retrieval_context": r["retrieval_context"],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(row["id"], row["language"], "cited:", r["cited"])
            time.sleep(3)


if __name__ == "__main__":
    main()