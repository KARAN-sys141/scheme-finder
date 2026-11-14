import json
import os
import time

import config
from src.pipeline import ask

OUT = "evals/results/pipeline_day8.jsonl"

rows = [json.loads(l) for l in open(config.GOLDEN_PATH, encoding="utf-8") if l.strip()]
os.makedirs("evals/results", exist_ok=True)

done = set()
if os.path.exists(OUT):
    done = {json.loads(l)["id"] for l in open(OUT, encoding="utf-8") if l.strip()}

with open(OUT, "a", encoding="utf-8") as f:
    for row in rows:
        if row["id"] in done:
            continue
        rec, _ = ask(row["question"])
        f.write(json.dumps({"id": row["id"], "category": row["category"],
                            "golden_language": row["language"], **rec}, ensure_ascii=False) + "\n")
        f.flush()
        print(row["id"], f"[{rec['route']}/{rec['kind']}]", rec["verdicts"], f"{rec['latency_s']}s", flush=True)
        time.sleep(3)

lat = sorted(json.loads(l)["latency_s"] for l in open(OUT, encoding="utf-8") if l.strip())
if lat:
    print(f"\nrows: {len(lat)} | latency p50 = {lat[len(lat) // 2]}s | p95 = {lat[int(len(lat) * 0.95) - 1]}s | max = {lat[-1]}s")