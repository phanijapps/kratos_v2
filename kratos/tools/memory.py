from kappa.memkappa import MemKappa


# --- 1. Initialize Embedding Model ---
from langchain_ollama import OllamaEmbeddings
my_embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")


semantic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="semantic",
    embedding_function=my_embedding_model,  # Pass the object
    config_path="kappa/config/semantic.yml"
)

episodic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="episodic",
    embedding_function=my_embedding_model,  # Pass the same object
    config_path="kappa/config/episodic.yml"
)


semantic_memory_retrieve = semantic_mem.get_tool("retrieve", name="semantic_memory_retrieve")
semantic_memory_ingest = semantic_mem.get_tool("ingest", name="semantic_memory_ingest")

episodic_memory_retrieve = episodic_mem.get_tool("retrieve", name="episodic_memory_retrieve")
episodic_memory_ingest = episodic_mem.get_tool("ingest", name="episodic_memory_ingest")