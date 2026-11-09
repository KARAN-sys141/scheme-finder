import json, os, glob, random
from collections import Counter

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from src.ingestion.clean import clean_text

SCHEMES = {
    "pmkisan": "PM-KISAN",
    "pmjay": "Ayushman Bharat PM-JAY",
    "vahli_dikri": "Vahli Dikri Yojana",
    "ma_yojana": "Mukhyamantri Amrutum (MA) Yojana",
}

# heading text (lowercase) -> section label
HEADING_MAP = {
    "introduction": "overview", "objective": "overview", "details": "overview",
    "benefits": "benefits", "benefit": "benefits",
    "benefits and eligibility conditions": "benefits_eligibility",
    "eligibility": "eligibility", "eligibility criteria": "eligibility",
    "exclusion categories": "exclusions", "exclusions": "exclusions",
    "documents": "documents", "documents required": "documents",
    "process to apply": "how_to_apply", "how to apply": "how_to_apply",
    "application process": "how_to_apply",
    # Hindi
    "परिचय": "overview", "लाभ": "benefits", "पात्रता": "eligibility",
    "दस्तावेज": "documents", "आवश्यक दस्तावेज": "documents",
    "आवेदन प्रक्रिया": "how_to_apply", "आवेदन कैसे करें": "how_to_apply",
    # Gujarati
    "પરિચય": "overview", "લાભો": "benefits", "પાત્રતા": "eligibility",
    "દસ્તાવેજો": "documents", "જરૂરી દસ્તાવેજો": "documents",
    "અરજી પ્રક્રિયા": "how_to_apply",
}


def parse_filename(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    language = stem.split("_")[-1]
    scheme_id = next((s for s in SCHEMES if stem.startswith(s)), None)
    return stem, scheme_id, language


def split_sections(text):
    sections, current, buf = [], "general", []
    for line in text.split("\n"):
        key = line.strip().strip(":").strip().lower()
        if key in HEADING_MAP and len(line.strip()) < 45:
            if "".join(buf).strip():
                sections.append((current, "\n".join(buf).strip()))
            current, buf = HEADING_MAP[key], []
        else:
            buf.append(line)
    if "".join(buf).strip():
        sections.append((current, "\n".join(buf).strip()))
    return sections


splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100,
    separators=["\n\n", "\n", "।", ". ", " ", ""],
)

chunks = []
for path in sorted(glob.glob(f"{config.RAW_DIR}/*.txt")):
    stem, scheme_id, language = parse_filename(path)
    if scheme_id is None:
        print("SKIP (unknown scheme):", stem)
        continue
    text = clean_text(open(path, encoding="utf-8").read())
    n = 0
    for section, body in split_sections(text):
        for piece in splitter.split_text(body):
            piece = piece.strip()
            if len(piece) < 40:
                continue
            n += 1
            header = f"[{SCHEMES[scheme_id]} | {section}]"
            chunks.append({
                "chunk_id": f"{stem}::{section}::{n}",
                "scheme_id": scheme_id,
                "scheme_name": SCHEMES[scheme_id],
                "language": language,
                "source_file": os.path.basename(path),
                "section": section,
                "text": header + "\n" + piece,
            })
    print(f"{stem}: {n} chunks")

os.makedirs(config.PROCESSED_DIR, exist_ok=True)
with open(f"{config.PROCESSED_DIR}/chunks.jsonl", "w", encoding="utf-8") as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

lengths = [len(c["text"]) for c in chunks]
print("\nTOTAL chunks:", len(chunks))
print("by scheme  :", dict(Counter(c["scheme_id"] for c in chunks)))
print("by language:", dict(Counter(c["language"] for c in chunks)))
print("by section :", dict(Counter(c["section"] for c in chunks)))
if lengths:
    print("length min/avg/max:", min(lengths), sum(lengths) // len(lengths), max(lengths))

print("\n--- 4 RANDOM CHUNKS (read them) ---")
for c in random.sample(chunks, min(4, len(chunks))):
    print("\n#", c["chunk_id"])
    print(c["text"])