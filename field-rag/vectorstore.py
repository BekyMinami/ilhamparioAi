"""Embedding + ChromaDB storage and search."""
import chromadb
import ollama

from config import CHROMA_PATH, COLLECTION_NAME, EMBED_BATCH_SIZE, EMBED_MODEL


def _get_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def _embed(texts: list[str]) -> list[list[float]]:
    """Turn a list of texts into embedding vectors via Ollama."""
    return ollama.embed(model=EMBED_MODEL, input=texts)["embeddings"]


def _clean_metadata(meta: dict) -> dict:
    """ChromaDB only accepts str/int/float/bool, so replace None/NaN with an empty string."""
    clean = {}
    for key, value in meta.items():
        if value is None or value != value:  # None or NaN
            clean[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean


def build_index(chunks: list[dict]) -> None:
    """Rebuild the index. Each chunk is {"text": str, "metadata": dict}."""
    client = _get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection did not exist yet
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[start:start + EMBED_BATCH_SIZE]
        texts = [c["text"] for c in batch]
        collection.add(
            ids=[f"chunk_{start + i}" for i in range(len(batch))],
            documents=texts,
            embeddings=_embed(texts),
            metadatas=[_clean_metadata(c["metadata"]) for c in batch],
        )


def search(query: str, k: int, where: dict | None = None) -> list[dict]:
    """Return the top-k chunks as {"text", "metadata", "distance"}."""
    collection = _get_client().get_collection(COLLECTION_NAME)
    result = collection.query(
        query_embeddings=_embed([query]), n_results=k, where=where
    )
    return [
        {"text": text, "metadata": meta, "distance": dist}
        for text, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]