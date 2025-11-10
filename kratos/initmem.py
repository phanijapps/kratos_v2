# main.py

import json
from kappa import MemKappa
from langchain_huggingface import HuggingFaceEmbeddings
# You could also import other embedding providers here
# from langchain_openai import OpenAIEmbeddings

# --- 1. Initialize Embedding Function FIRST ---
# This is the new step. You can swap this line to use
# any LangChain-compatible embedding class.
print("Initializing embedding function...")
#my_embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
from langchain_ollama import OllamaEmbeddings
my_embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")

# If you had an OpenAI API key, you could swap it:
# my_embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# --- 2. Initialize Memory Cores ---
# Pass the *instantiated* embedding object to the constructor.

print("Initializing semantic memory...")
semantic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="semantic",
    embedding_function=my_embedding_model,  # Pass the object
    config_path="kappa/config/semantic.yml"
)

print("Initializing episodic memory...")
episodic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="episodic",
    embedding_function=my_embedding_model,  # Pass the same object
    config_path="kappa/config/episodic.yml"
)

# --- 3. Generate Tools ---
# This part remains identical to before.
print("Generating tools...")
semantic_ret_tool = semantic_mem.get_tool("retrieve", name="semantic_memory_retrieve")
semantic_ingest_tool = semantic_mem.get_tool("ingest", name="semantic_memory_ingest")

episodic_ret_tool = episodic_mem.get_tool("retrieve", name="episodic_memory_retrieve")
episodic_ingest_tool = episodic_mem.get_tool("ingest", name="episodic_memory_ingest")

tools = [
    semantic_ret_tool,
    semantic_ingest_tool,
    episodic_ret_tool,
    episodic_ingest_tool
]

print("\nGenerated Tools:")
for t in tools:
    print(f"- {t.name}: {t.description.splitlines()[0].strip()}") # [0] to get the first line of the description

# --- 4. Pass Tools to DeepAgent ---
# (Your agent setup logic here)
print("\nAgent executor can now be built with these tools.")

# --- 5. Example: Populate Semantic Memory ---
# This logic is also unchanged, but it now uses the 
# 'semantic_cr_tool' which contains the injected 'my_embedding_model'.
print("\nPopulating semantic memory with API docs (one-time setup)...")
try:
    with open('.vault/docs/api_json.json', 'r') as f:
        api_docs = json.load(f)

    for section in api_docs.get("sections", []):
        for endpoint in section.get("endpoints", []):
            payload = {
                "section": {
                    "name": section.get("name"),
                    "description": section.get("description"),
                },
                "endpoint": endpoint,
            }
            semantic_mem.ingest("api_doc", payload)
            
    print("Semantic memory populated with API documentation.")
    resp = semantic_ret_tool.invoke({"new_task_description": "Help me with technical analysis finding RSI and Bollinger bands functions in the API."})
    print("Sample retrieval result:")
    print(resp)

except FileNotFoundError:
    print("api_json.json not found. Skipping semantic population.")
except Exception as e:
    print(f"Error populating semantic memory: {e}")

