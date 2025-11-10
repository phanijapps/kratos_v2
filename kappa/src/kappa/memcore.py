# memcore.py

import os
import json
import uuid
import networkx as nx
import chromadb
from typing import Optional, Dict, Any, Callable, List

# --- KEY CHANGE 1: Import the base class ---
from langchain.embeddings.base import Embeddings
# --- END KEY CHANGE 1 ---

from langchain_core.tools import tool

class Memcore:
    """
    A hybrid memory core that combines a vector store (for semantic search)
    and a knowledge graph (for episodic/process memory). It acts as a 
    factory for generating its own LangChain-compatible tools.
    """
    
    # --- KEY CHANGE 2: Modify the __init__ signature ---
    def __init__(self, store_path: str, namespace: str, embedding_function: Embeddings):
        """
        Initializes the memory core for a specific namespace.

        Args:
            store_path: The root directory to store memory files.
            namespace: The unique name for this memory (e.g., "semantic").
            embedding_function: An instantiated LangChain Embeddings object 
                              (e.g., HuggingFaceEmbeddings(), OpenAIEmbeddings()).
        """
    # --- END KEY CHANGE 2 ---
    
        self.namespace = namespace
        self.store_path = store_path

        # Ensure the store path exists
        os.makedirs(store_path, exist_ok=True)
        
        # --- KEY CHANGE 3: Assign the injected object ---
        self.embedding_function = embedding_function
        # --- END KEY CHANGE 3 ---

        # 2. Init Vector DB (Chroma)
        self.db_path = os.path.join(store_path, f"{namespace}_vectordb")
        self.vector_db_client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.vector_db_client.get_or_create_collection(
            name=f"{namespace}_collection",
            metadata={"hnsw:space": "cosine"},  # align distance metric with similarity calc
        )

        # 3. Init Graph DB (NetworkX)
        self.graph_path = os.path.join(store_path, f"{namespace}_graph.graphml")
        self.graph = self._load_graph()

    def _load_graph(self) -> nx.DiGraph:
        """Loads the NetworkX graph from its file path."""
        try:
            return nx.read_graphml(self.graph_path)
        except FileNotFoundError:
            return nx.DiGraph()

    def _save_graph(self):
        """Saves the graph to its file path."""
        nx.write_graphml(self.graph, self.graph_path)

    # --- CORE LOGIC METHODS (No changes needed) ---

    def create_or_update(self, task_description: str, solution_code: str, failure_trace: Optional[Dict[str, str]] = None) -> str:
        """
        The internal logic for saving or updating a memory.
        """
        memory_id = f"mem_{self.namespace}_" + str(uuid.uuid4())

        self.graph.add_node(memory_id,
                            type="Solution",
                            description=task_description,
                            solution_code=solution_code)
        
        if failure_trace:
            fail_id = f"fail_{memory_id}"
            self.graph.add_node(fail_id,
                                type="Failure",
                                failed_code=failure_trace.get('failed_code'),
                                error_message=failure_trace.get('error_message'))
            self.graph.add_edge(fail_id, memory_id, label="IS_FIXED_BY")
        
        self._save_graph()

        try:
            # This line works polymorphically with any embedding class
            task_embedding = self.embedding_function.embed_query(task_description)
            
            self.collection.add(
                ids=[memory_id],
                embeddings=[task_embedding],
                metadatas=[{"task_description": task_description, "source": self.namespace}]
            )
            return memory_id
        except Exception as e:
            return f"Error adding to vector store: {e}"


    def retrieve(self, new_task_description: str) -> Dict[str, Any]:
        """
        The internal logic for retrieving a memory.
        """
        try:
            # This line also works polymorphically
            query_embedding = self.embedding_function.embed_query(new_task_description)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1
            )
        except Exception as e:
            return {"error": f"Error querying vector store: {e}"}
        
        if not results or not results.get('ids') or not results['ids'][0]:
            return {}

        best_match_id = results['ids'][0][0]
        distance = results['distances'][0][0] if results.get('distances') else None
        similarity = None
        if distance is not None:
            # Chroma returns cosine distance in [0, 2]; convert back to [0,1] similarity
            similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
        
        try:
            memory_node = self.graph.nodes[best_match_id]
            fixed_error = None
            predecessors = list(self.graph.predecessors(best_match_id))
            if predecessors:
                fail_node_id = predecessors[0]
                if fail_node_id in self.graph.nodes:
                    fail_node = self.graph.nodes[fail_node_id]
                    fixed_error = fail_node.get('error_message')

            return {
                "retrieved_code": memory_node.get('solution_code'),
                "original_task": memory_node.get('description'),
                "fixed_error": fixed_error,
                "similarity_score": similarity
            }
            
        except KeyError:
            return {"error": "Graph node not found for retrieved vector. Memory may be out of sync."}
            
    # --- TOOL FACTORY (No changes needed) ---

    def get_tool(self, tool_type: str) -> Callable:
        """
        Factory method to generate and return a LangChain tool.
        """
        
        if tool_type == "retrieve":
            @tool(description=f"{self.namespace} retrieve a memory")
            def retrieve_tool(new_task_description: str) -> str:
                f"""
                Searches the {self.namespace} memory for a relevant 
                solution based on a new task description.
                """
                result = self.retrieve(new_task_description)
                return json.dumps(result)
            return retrieve_tool
        
        elif tool_type == "create_or_update":
            @tool(description=f"{self.namespace} create_or_update a memory")
            def create_or_update_tool(
                task_description: str,
                solution_code: str,
                failure_trace: Optional[Dict[str, str]] = None
            ) -> str:
                f"""
                Saves or updates a solution in the {self.namespace} 
                memory. Use this to record successful (or self-healed) 
                code executions.
                """
                memory_id = self.create_or_update(task_description, solution_code, failure_trace)
                return json.dumps({"status": "success", "memory_id": memory_id})
            return create_or_update_tool

        else:
            raise ValueError(f"Unknown tool_type: {tool_type}. Must be 'retrieve' or 'create_or_update'.")
