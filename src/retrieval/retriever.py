import re

from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

import config
from src.retrieval.index import get_embeddings, load_chunks

RERANK_MODEL = "BAAI/bge-reranker-v2-m3"

# Split on spaces and punctuation only. (\w would break Hindi/Gujarati words at matras.)
TOKEN = re.compile(r"[^\s\.,;:!?()\[\]{}\"'|/\\\-–—•]+")
INDIC = re.compile(r"[\u0900-\u097F\u0A80-\u0AFF]")  # Devanagari + Gujarati


def tokenize(text):
    return TOKEN.findall(text.lower())


def chroma_filter(scheme_ids, language):
    conds = []
    if scheme_ids:
        conds.append({"scheme_id": {"$in": list(scheme_ids)}})
    if language:
        conds.append({"language": language})
    if not conds:
        return None
    return conds[0] if len(conds) == 1 else {"$and": conds}


class SchemeRetriever:
    def __init__(self):
        self.chunks = load_chunks()
        self.by_id = {c["chunk_id"]: c for c in self.chunks}
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in self.chunks])
        self.db = Chroma(
            collection_name="schemes",
            embedding_function=get_embeddings(),
            persist_directory=config.CHROMA_DIR,
        )
        self._reranker = None

    def _hit(self, chunk_id, score):
        c = self.by_id[chunk_id]
        return {
            "chunk_id": chunk_id,
            "scheme_id": c["scheme_id"],
            "language": c["language"],
            "section": c["section"],
            "text": c["text"],
            "score": float(score),
        }

    def dense(self, query, k=5, scheme_ids=None, language=None):
        res = self.db.similarity_search_with_score(
            query, k=k, filter=chroma_filter(scheme_ids, language)
        )
        # score is cosine distance: lower = closer
        return [self._hit(doc.metadata["chunk_id"], 1 - dist) for doc, dist in res]

    def sparse(self, query, k=5, scheme_ids=None, language=None):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(self.chunks)), key=lambda i: -scores[i])
        out = []
        for i in ranked:
            c = self.chunks[i]
            if scores[i] <= 0:
                break
            if scheme_ids and c["scheme_id"] not in scheme_ids:
                continue
            if language and c["language"] != language:
                continue
            out.append(self._hit(c["chunk_id"], scores[i]))
            if len(out) == k:
                break
        return out

    def hybrid(self, query, k=5, scheme_ids=None, language=None, pool=20, w_sparse=None):
        # script-aware: BM25 helps Latin-script queries (English/Hinglish),
        # but only adds noise for Hindi/Gujarati script queries
        if w_sparse is None:
            w_sparse = 0.0 if INDIC.search(query) else 1.0

        fused = {}
        for rank, h in enumerate(self.dense(query, pool, scheme_ids, language), 1):
            fused[h["chunk_id"]] = 1 / (60 + rank)
        if w_sparse > 0:
            for rank, h in enumerate(self.sparse(query, pool, scheme_ids, language), 1):
                fused[h["chunk_id"]] = fused.get(h["chunk_id"], 0) + w_sparse / (60 + rank)

        top = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [self._hit(cid, score) for cid, score in top]

    def rerank(self, query, hits, k=5):
        if self._reranker is None:
            self._reranker = CrossEncoder(RERANK_MODEL, max_length=512)
        scores = self._reranker.predict([(query, h["text"]) for h in hits])
        order = sorted(range(len(hits)), key=lambda i: -scores[i])[:k]
        return [{**hits[i], "score": float(scores[i])} for i in order]

    def dense_rerank(self, query, k=5, scheme_ids=None, language=None, pool=20):
        return self.rerank(query, self.dense(query, pool, scheme_ids, language), k)

    def hybrid_rerank(self, query, k=5, scheme_ids=None, language=None, pool=20):
        return self.rerank(query, self.hybrid(query, pool, scheme_ids, language, pool=pool), k)