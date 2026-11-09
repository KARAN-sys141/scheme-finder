import os

folders = [
    "data/raw", "data/processed", "data/golden",
    "src/ingestion", "src/retrieval", "src/generation",
    "src/eligibility", "src/gateway", "src/guardrails", "src/monitoring",
    "api", "frontend",
    "evals/component", "evals/pipeline", "evals/application",
    "evals/safety", "evals/operations",
]
for f in folders:
    os.makedirs(f, exist_ok=True)
    if f.startswith(("src", "api", "evals")):
        open(os.path.join(f, "__init__.py"), "a").close()

for top in ["src", "evals"]:
    open(os.path.join(top, "__init__.py"), "a").close()

with open(".gitignore", "w") as g:
    g.write(".venv/\n.env\n__pycache__/\nchroma_db/\n*.log\n")

print("Structure ready")