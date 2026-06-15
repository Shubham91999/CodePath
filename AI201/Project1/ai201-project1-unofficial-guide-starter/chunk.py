"""
Milestone 3 — Chunking
Loads raw text from data/raw/, splits into chunks using RecursiveCharacterTextSplitter,
prepends a metadata header to each chunk, saves to data/chunks.json.
Run: python chunk.py
"""

import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

RAW_DIR = "data/raw"
OUTPUT_FILE = "data/chunks.json"

# 400 tokens * ~4 chars/token = 1600 chars; 50 tokens overlap = 200 chars
# Safe for nomic-embed-text (8192 token limit)
CHUNK_SIZE = 1600
CHUNK_OVERLAP = 200

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_metadata(name: str) -> dict:
    meta_path = os.path.join(RAW_DIR, f"{name}.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def format_chunk(text: str, meta: dict) -> str:
    header = f"Apartment: {meta.get('apartment', 'Unknown')} | Source: {meta.get('source', 'Unknown')} | Date: {meta.get('date', 'Unknown')}"
    return f"{header}\n{text}"


def main():
    os.makedirs("data", exist_ok=True)

    txt_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"No .txt files found in {RAW_DIR}/. Run ingest.py first.")
        return

    all_chunks = []

    for filename in sorted(txt_files):
        name = filename.replace(".txt", "")
        raw_path = os.path.join(RAW_DIR, filename)

        with open(raw_path, encoding="utf-8") as f:
            text = f.read()

        meta = load_metadata(name)
        splits = splitter.split_text(text)

        for i, split_text in enumerate(splits):
            chunk = {
                "id": f"{name}_{i}",
                "text": format_chunk(split_text, meta),
                "apartment": meta.get("apartment", "Unknown"),
                "source": meta.get("source", "Unknown"),
                "url": meta.get("url", ""),
                "date": meta.get("date", "Unknown"),
            }
            all_chunks.append(chunk)

        print(f"  {name}: {len(splits)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    sizes = [len(c["text"]) for c in all_chunks]
    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Chunk size — min: {min(sizes)}, max: {max(sizes)}, avg: {sum(sizes)//len(sizes)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
