import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_MODEL = "openai/gpt-oss-120b"
GEMINI_MODEL = "gemini-3.8-flash"

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
GOLDEN_PATH = "data/golden/golden_dataset.jsonl"
EMBED_MODEL = "BAAI/bge-m3"
CHROMA_DIR = "chroma_db"
RETRIEVAL_MODE = "hybrid_smart"  # dense | hybrid_smart | dense+rerank | hybrid_smart+rerank
TOP_K = 5
ANSWERS_PATH = "evals/results/answers_day5.jsonl"
JUDGE_MODEL = "openai/gpt-oss-20b"
EXTRACT_MODEL = JUDGE_MODEL