import json
from kappa import MemKappa
from langchain_ollama import OllamaEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings

# --- 1. Initialize Embedding Function ---
print("Initializing embedding function...")
my_embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")

# --- 2. Initialize Memory Cores ---
# Make sure 'semantic.yml' is the updated version that
# checks for 'parent_tool' using 'source_key'.
print("Initializing semantic memory...")
semantic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="semantic",
    embedding_function=my_embedding_model,
    config_path="kappa/config/semantic.yml" 
)

print("Initializing episodic memory...")
episodic_mem = MemKappa(
    store_path="./.vault/memory", 
    namespace="episodic",
    embedding_function=my_embedding_model,
    config_path="kappa/config/episodic.yml"
)

# --- 3. Generate Tools ---
print("Generating tools...")
semantic_tools = [
    semantic_mem.get_tool("retrieve", name="semantic_retrieve"),
    semantic_mem.get_tool("ingest", name="semantic_ingest"),
    semantic_mem.get_tool("lookup_node", name="semantic_lookup_node")
]

episodic_tools = [
    episodic_mem.get_tool("retrieve", name="episodic_retrieve"),
    episodic_mem.get_tool("ingest", "episodic_ingest"),
    episodic_mem.get_tool("lookup_node", "episodic_lookup_node")
]

tools = semantic_tools + episodic_tools
print("\nGenerated Tools:")
for t in tools:
    print(f"- {t.name}: {t.description.splitlines()[0].strip()}")

# --- 4. Pass Tools to Agent ---
print("\nAgent executor can now be built with these tools.")

# --- 5. Populate Semantic Memory (NEW SIMPLIFIED LOGIC) ---
print("\nPopulating semantic memory with processed API docs...")
try:
    # Load the new, pre-processed JSON file
    with open('fin_lib/docs/api_ref.json', 'r') as f:
        api_docs = json.load(f)

    ingest_count = 0
    # No more special logic! Just loop and ingest.
    for section in api_docs.get("sections", []):
        for endpoint in section.get("endpoints", []):
            
            # The payload maps directly from the JSON
            payload = {
                "section": {
                    "name": section.get("name"),
                    "description": section.get("description"),
                },
                "endpoint": endpoint,
                # This is the key: pass the 'parent_tool' field if it exists
                # The 'semantic.yml' schema will use this to build the graph
                "parent_tool": endpoint.get("parent_tool") 
            }
            semantic_mem.ingest("api_doc", payload)
            ingest_count += 1
            
    print(f"Semantic memory populated with {ingest_count} total endpoints (real and virtual).")

    # --- Example Retrieval ---
    print("\n--- Testing Retrieval for 'RSI' ---")
    resp_json = semantic_tools[0].invoke({"new_task_description": "How do I calculate RSI?"})
    print(resp_json)
    
    # This shows the agent *how* to use the tool it found
    print("\n--- Testing Lookup for 'RSI' node ---")
    resp_lookup = semantic_tools[2].invoke({"node_id": "RSI"})
    print(resp_lookup)
    
    print("\n--- Testing Lookup for 'technical_analysis' parent node ---")
    resp_parent_lookup = semantic_tools[2].invoke({"node_id": "technical_analysis"})
    print(resp_parent_lookup)


except FileNotFoundError:
    print("ERROR: 'api_docs_processed.json' not found. Make sure it is in the same directory.")
except Exception as e:
    print(f"Error populating semantic memory: {e}")