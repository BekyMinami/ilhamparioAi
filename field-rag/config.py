"""Central configuration. Constants only."""

# Chunking (measured in characters)
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 256

# Retrieval
TOP_K = 5

# LLM
LLM_MODEL = "qwen2.5-coder:7b"
TEMPERATURE = 0.1

# Embeddings
EMBED_MODEL = "bge-m3"

# Vector store
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "tickets"
EMBED_BATCH_SIZE = 32