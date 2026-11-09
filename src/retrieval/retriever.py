import re

from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi

import config
from src.retrieval.index import get_embeddings, load_chunks

# Split on spaces and punctuation only. (\w would break Hindi/Gujarati words at matras.)
TOKEN = re.compile(r"[^\s\.,;:!?()\[\]{}\"'|/\\\-–—•]+")


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
        # score here is cosine distance: lower = closer
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

    def hybrid(self, query, k=5, scheme_ids=None, language=None, pool=20):
        dense_hits = self.dense(query, pool, scheme_ids, language)
        sparse_hits = self.sparse(query, pool, scheme_ids, language)
        fused = {}
        for rank, h in enumerate(dense_hits, 1):
            fused[h["chunk_id"]] = fused.get(h["chunk_id"], 0) + 1 / (60 + rank)
        for rank, h in enumerate(sparse_hits, 1):
            fused[h["chunk_id"]] = fused.get(h["chunk_id"], 0) + 1 / (60 + rank)
        top = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [self._hit(cid, score) for cid, score in top]