import config
from src.retrieval.retriever import SchemeRetriever

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = SchemeRetriever()
    return _retriever


def search(query, k=None, scheme_ids=None, language=None):
    r = get_retriever()
    kw = dict(k=k or config.TOP_K, scheme_ids=scheme_ids, language=language)
    mode = config.RETRIEVAL_MODE
    if mode == "dense":
        return r.dense(query, **kw)
    if mode == "hybrid_smart":
        return r.hybrid(query, **kw)
    if mode == "dense+rerank":
        return r.dense_rerank(query, **kw)
    return r.hybrid_rerank(query, **kw)