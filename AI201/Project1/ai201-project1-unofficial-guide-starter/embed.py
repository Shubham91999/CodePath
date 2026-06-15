"""
Milestone 4 — Embedding + Vector Store
Loads chunks from data/chunks.json, embeds each using nomic-embed-text via Ollama,
stores vectors + text + metadata in a local ChromaDB collection.
Run: python embed.py  (requires: ollama serve + ollama pull nomic-embed-text)
"""

import json
import sys
import chromadb
import ollama

CHUNKS_FILE = "data/chunks.json"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "asu_housing"
# EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_MODEL = "nomic-embed-text"
BATCH_SIZE = 50  # embed in batches to avoid memory spikes


def check_ollama():
    try:
        models = ollama.list()
        names = [m.model for m in models.models]
        if not any(EMBED_MODEL in n for n in names): # type: ignore
            print(f"[ERROR] '{EMBED_MODEL}' not found in Ollama.")
            print(f"  Run: ollama pull {EMBED_MODEL}")
            sys.exit(1)
    except Exception:
        print("[ERROR] Ollama is not running.")
        print("  Run: ollama serve")
        sys.exit(1)


def embed_batch(texts: list[str]) -> list[list[float]]:
    response = ollama.embed(model=EMBED_MODEL, input=texts)
    return response.embeddings # type: ignore


def main():
    check_ollama()

    with open(CHUNKS_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop and recreate collection for a clean run
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        ids = [c["id"] for c in batch]
        metadatas = [
            {
                "apartment": c["apartment"],
                "source": c["source"],
                "url": c["url"],
                "date": c["date"],
            }
            for c in batch
        ]

        embeddings = embed_batch(texts)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings, # type: ignore
            metadatas=metadatas, # type: ignore
        )

        print(f"  Embedded {min(i + BATCH_SIZE, total)}/{total} chunks")

    print(f"\nDone. Collection '{COLLECTION_NAME}' has {collection.count()} vectors.")
    print(f"Persisted to: {CHROMA_DIR}/")


if __name__ == "__main__":
    main()
