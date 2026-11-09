import json
import os
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

import config


def load_chunks():
    path = f"{config.PROCESSED_DIR}/chunks.jsonl"
    return [json.loads(line) for line in open(path, encoding="utf-8")]


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=config.EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def build_index():
    chunks = load_chunks()
    if os.path.exists(config.CHROMA_DIR):
        shutil.rmtree(config.CHROMA_DIR)

    docs = [
        Document(
            page_content=c["text"],
            metadata={
                "chunk_id": c["chunk_id"],
                "scheme_id": c["scheme_id"],
                "language": c["language"],
                "section": c["section"],
                "source_file": c["source_file"],
            },
        )
        for c in chunks
    ]
    Chroma.from_documents(
        docs,
        get_embeddings(),
        ids=[c["chunk_id"] for c in chunks],
        collection_name="schemes",
        collection_metadata={"hnsw:space": "cosine"},
        persist_directory=config.CHROMA_DIR,
    )
    print(f"Indexed {len(docs)} chunks into {config.CHROMA_DIR}")


if __name__ == "__main__":
    build_index()