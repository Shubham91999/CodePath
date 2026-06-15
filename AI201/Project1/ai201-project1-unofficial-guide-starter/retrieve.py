"""
Milestone 4 — Retrieval
Embeds a user query with nomic-embed-text, searches ChromaDB for top-k
most similar chunks, returns results with text + metadata.
"""

import sys
import chromadb
import ollama

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "asu_housing"
EMBED_MODEL = "nomic-embed-text"
TOP_K = 5
MIN_SCORE = 0.30  # chunks below this threshold are too dissimilar to be useful


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        print(f"[ERROR] Collection '{COLLECTION_NAME}' not found.")
        print("  Run: python embed.py")
        sys.exit(1)


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    response = ollama.embed(model=EMBED_MODEL, input=[query])
    query_embedding = response.embeddings[0]

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0], # type: ignore
        results["metadatas"][0], # type: ignore
        results["distances"][0], # type: ignore
    ):
        chunks.append(
            {
                "text": text,
                "apartment": meta.get("apartment", "Unknown"),
                "source": meta.get("source", "Unknown"),
                "url": meta.get("url", ""),
                "date": meta.get("date", "Unknown"),
                "score": round(1 - dist, 4),  # cosine similarity (higher = more relevant)
            }
        )

    # Filter out chunks below the minimum similarity threshold.
    # ChromaDB always returns k results even when nothing is relevant —
    # without this filter, low-score chunks pollute the LLM context.
    return [c for c in chunks if c["score"] >= MIN_SCORE]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Which apartments are close to ASU campus?"
    print(f"Query: {query}\n")

    results = retrieve(query)
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['apartment']} — {r['source']} (score: {r['score']})")
        print(f"    {r['text'][:200]}...")
        print()
