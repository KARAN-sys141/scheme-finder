import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import config
from api import sessions
from api.schemas import ChatRequest, ChatResponse, FeedbackRequest, Source
from src.pipeline import ask
from src.retrieval.search import get_retriever

log = logging.getLogger("schememitra")
BASE = Path(__file__).resolve().parent.parent
FEEDBACK_PATH = BASE / "logs" / "feedback.jsonl"

SCHEME_NAMES = {
    "pmkisan": "PM-KISAN",
    "pmjay": "Ayushman Bharat PM-JAY",
    "vahli_dikri": "Vahli Dikri Yojana",
    "ma_yojana": "MA Yojana",
}


@asynccontextmanager
async def lifespan(app):
    get_retriever()  # load embedding model + index once, so the first user does not wait
    yield


app = FastAPI(title="SchemeMitra", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE / "frontend")), name="static")


def build_sources(rec):
    ctx = rec["retrieval_context"]
    out = []
    for s in rec["sources"]:
        n = s["n"]
        text = ctx[n - 1] if 0 < n <= len(ctx) else ""
        body = text.split("\n", 1)[1] if "\n" in text else text
        out.append(
            Source(
                n=n,
                scheme_id=s["scheme_id"],
                scheme_name=SCHEME_NAMES.get(s["scheme_id"], s["scheme_id"]),
                section=s["section"],
                file=s["chunk_id"].split("::")[0],
                snippet=body.strip()[:240],
            )
        )
    return out


@app.get("/")
def index():
    return FileResponse(BASE / "frontend" / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "retrieval_mode": config.RETRIEVAL_MODE,
        "chunks": len(get_retriever().chunks),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    sid = req.session_id or sessions.new_id()
    state = sessions.get(sid)
    try:
        rec, new_state = ask(req.message, state)
    except Exception:
        log.exception("chat failed")
        raise HTTPException(status_code=503, detail="busy")  # never leak internal errors to the user
    sessions.put(sid, new_state)
    return ChatResponse(
        session_id=sid,
        reply=rec["reply"],
        kind=rec["kind"],
        route=rec["route"],
        language=rec["language"],
        sources=build_sources(rec),
        verdicts=rec["verdicts"],
        latency_s=rec["latency_s"],
    )


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": int(time.time()), **req.model_dump()}
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True}