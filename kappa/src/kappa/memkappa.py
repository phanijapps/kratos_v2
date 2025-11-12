"""
Config-driven memory core (MemKappa).

This module provides a schema-based ingestion and retrieval system
for building a hybrid vector-graph memory. It is designed to be
used by an agent to create a self-improving, episodic memory.

The core components are:
1.  Vector Store (ChromaDB): For semantic search to find relevant memories.
2.  Graph Database (NetworkX): To store relationships between memories,
    code patterns, tools, and reflections.
3.  YAML Config: A schema that defines how to ingest data, what to
    index, and what graph structure to build.

The intended agent workflow is:
1.  [Retrieve]: Agent queries memory with a new task.
2.  [Lookup]: Agent uses IDs from retrieve to get specific code, insights, etc.
3.  [Act]: Agent performs the task.
4.  [Ingest]: Agent saves the outcome as a new memory, linking it to
    the tools and patterns it used.
"""

from __future__ import annotations

import json
import os
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

import chromadb
import networkx as nx
import yaml
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, create_model
from langchain_core.tools import tool


class MemKappa:
    """Hybrid memory core driven by YAML configs."""

    def __init__(
        self,
        store_path: str,
        namespace: str,
        embedding_function: Embeddings,
        config_path: str,
    ):
        """
        Initializes the hybrid memory store.

        Args:
            store_path: The directory to store all memory files (DBs, graph).
            namespace: A unique name for this memory (e.g., "episodic").
            embedding_function: The embedding model to use (from LangChain).
            config_path: Path to the YAML file defining the memory schema.
        """
        self.namespace = namespace
        self.store_path = store_path
        self.embedding_function = embedding_function
        self.config = self._load_config(config_path)
        self.ingestor_specs: Dict[str, Dict[str, Any]] = self.config.get("ingestors", {})
        if not self.ingestor_specs:
            raise ValueError(f"No ingestors defined in config: {config_path}")

        os.makedirs(store_path, exist_ok=True)

        # Initialize Vector DB (ChromaDB)
        collection_suffix = (
            self.config.get("vector_store", {}).get("collection_suffix") or namespace
        )
        self.db_path = os.path.join(store_path, f"{namespace}_vectordb")
        self.vector_db_client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.vector_db_client.get_or_create_collection(
            name=f"{namespace}_{collection_suffix}_collection",
            metadata={"hnsw:space": "cosine"}, # Use cosine similarity
        )

        # Initialize Graph DB (NetworkX)
        self.graph_path = os.path.join(store_path, f"{namespace}_graph.graphml")
        self.graph = self._load_graph()
        
        # Build dynamic Pydantic schemas for tools
        self._ingest_schema = self._build_ingest_schema()
        self.retrieve_doc = self.config.get("retrieve_doc", f"Retrieves {self.namespace} memory.")
        self.ingest_doc = self.config.get("ingestion_doc", f"Ingests {self.namespace} memory.")

    @staticmethod
    def _load_config(path: str) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def _build_ingest_schema(self) -> Optional[BaseModel]:
        """Dynamically builds a Pydantic model for the ingest tool."""
        if not self.ingestor_specs:
            return None
        # Create an Enum from the ingestor names
        enum_cls = Enum(
            f"{self.namespace.capitalize()}Ingestor",
            {name: name for name in self.ingestor_specs},
        )
        # Create a Pydantic model that uses the Enum
        model = create_model(
            f"{self.namespace.capitalize()}IngestInput",
            ingestor=(enum_cls, ...),
            payload=(Dict[str, Any], ...),
        )
        return model

    def ingest(self, ingestor: str, payload: Dict[str, Any]) -> str:
        """
        Ingests a new memory payload based on a defined ingestor schema.
        
        This method:
        1.  Builds a text blob and metadata for vector search.
        2.  Updates the graph with new nodes and edges.
        3.  Adds the memory to the vector collection.
        
        Args:
            ingestor: The name of the ingestor (must match YAML config).
            payload: The data payload to ingest.
            
        Returns:
            The unique ID of the newly created memory entry.
        """
        spec = self.ingestor_specs.get(ingestor)
        if not spec:
            raise ValueError(f"Ingestor '{ingestor}' is not defined for {self.namespace}")

        # 1. Prepare data for vector store
        vector_spec = spec.get("vector", {})
        text_blob = self._build_text(vector_spec.get("text_fields", []), payload)
        metadata = self._build_metadata(vector_spec.get("metadata", {}), payload)

        # 2. Update the graph
        graph_spec = spec.get("graph", {})
        graph_nodes = self._update_graph(graph_spec, payload)

        # 3. Add graph node IDs to metadata for retrieval
        metadata["graph_nodes"] = json.dumps(graph_nodes)
        memory_id = f"mem_{self.namespace}_{uuid.uuid4()}"
        
        if not text_blob:
            # If no text to index, this is a graph-only entry.
            # We can't add it to the vector store.
            print(f"Warning: Ingestor '{ingestor}' produced no text blob. Only graph was updated.")
            return f"graph_only_entry:{list(graph_nodes.values())[0] if graph_nodes else 'unknown'}"

        # 4. Add to vector collection
        embedding = self.embedding_function.embed_query(text_blob)
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            metadatas=[metadata],
        )
        return memory_id

    def retrieve(self, new_task_description: str, n_results: int = 1) -> Dict[str, Any]:
        """
        Retrieves relevant memories based on a semantic query.
        
        This method:
        1.  Queries the vector store for relevant memories.
        2.  Fetches the associated graph context (nodes + neighbors) for each memory.
        
        Args:
            new_task_description: The text query (e.g., a new task).
            n_results: The number of matching memories to return.
            
        Returns:
            A dictionary of matches, including graph context and similarity.
        """
        try:
            query_embedding = self.embedding_function.embed_query(new_task_description)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )
        except Exception as exc:  # pragma: no cover - protective catch
            return {"error": f"Error querying vector store: {exc}"}

        if not results or not results.get("ids"):
            return {}

        payloads = []
        for idx, memory_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][idx]
            distance = results.get("distances", [[None]])[0][idx]
            similarity = self._distance_to_similarity(distance)
            
            # Get the graph node IDs saved in metadata
            graph_nodes_raw = metadata.get("graph_nodes", {})
            if isinstance(graph_nodes_raw, str):
                try:
                    graph_nodes = json.loads(graph_nodes_raw)
                except json.JSONDecodeError:
                    graph_nodes = {}
            else:
                graph_nodes = graph_nodes_raw or {}
            
            # --- THIS IS THE KEY MODIFICATION ---
            # This function now builds the full graph context, including neighbors
            graph_context = self._build_graph_context(graph_nodes)
            
            payloads.append(
                {
                    "memory_id": memory_id,
                    "metadata": metadata,
                    "graph_context": graph_context,
                    "similarity_score": similarity,
                }
            )

        return {"matches": payloads}

    def _build_text(self, fields: List[str], payload: Dict[str, Any]) -> str:
        """Helper to concatenate text fields from a payload for vector indexing."""
        chunks = []
        for field in fields:
            value = self._extract_value(payload, field)
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                chunks.append(json.dumps(value, ensure_ascii=False))
            else:
                chunks.append(str(value))
        return "\n".join(chunks) if chunks else "" # Return empty string if no fields

    def _build_metadata(self, mapping: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to build a metadata dictionary from a payload."""
        metadata: Dict[str, Any] = {}
        for key, path in mapping.items():
            value = self._extract_value(payload, path)
            if value is not None:
                metadata[key] = value
        metadata["namespace"] = self.namespace
        return metadata

    # --- MODIFIED: _update_graph ---
    def _update_graph(self, graph_spec: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Updates the graph based on the spec, creating nodes and edges.
        This version supports linking new nodes to existing nodes.
        """
        # Tracks nodes created IN THIS PAYLOAD by their alias
        new_node_ids_by_alias: Dict[str, str] = {}
        
        # --- 1. Create New Nodes ---
        for node_spec in graph_spec.get("nodes", []):
            alias = node_spec.get("id")
            node_id = self._extract_value(payload, node_spec.get("key"))
            if not alias or not node_id:
                # This node wasn't in the payload, skip it
                continue
                
            attributes = {
                attr_name: self._extract_value(payload, attr_path)
                for attr_name, attr_path in (node_spec.get("attributes") or {}).items()
                # Only add attributes that are not None
                if self._extract_value(payload, attr_path) is not None
            }
            attributes["type"] = node_spec.get("type", alias)
            
            self.graph.add_node(node_id, **attributes)
            new_node_ids_by_alias[alias] = node_id

        # --- 2. Create Edges ---
        for edge_spec in graph_spec.get("edges", []):
            label = edge_spec.get("label", "RELATED_TO")
            
            # --- Find Source ID(s) ---
            source_ids_final = []
            if "source" in edge_spec:
                # Case 1: Source is an alias for a NEW node (from this payload)
                alias = edge_spec["source"]
                if alias in new_node_ids_by_alias:
                    source_ids_final.append(new_node_ids_by_alias[alias])
            elif "source_key" in edge_spec:
                # Case 2: Source is a path to ID(s) of EXISTING node(s)
                source_val = self._extract_value(payload, edge_spec["source_key"])
                if isinstance(source_val, list):
                    source_ids_final.extend([s for s in source_val if self.graph.has_node(s)])
                elif source_val and self.graph.has_node(source_val):
                    source_ids_final.append(source_val)

            # --- Find Target ID(s) ---
            target_ids_final = []
            if "target" in edge_spec:
                # Case 1: Target is an alias for a NEW node (from this payload)
                alias = edge_spec["target"]
                if alias in new_node_ids_by_alias:
                    target_ids_final.append(new_node_ids_by_alias[alias])
            elif "target_key" in edge_spec:
                # Case 2: Target is a path to ID(s) of EXISTING node(s)
                target_val = self._extract_value(payload, edge_spec["target_key"])
                if isinstance(target_val, list):
                    target_ids_final.extend([t for t in target_val if self.graph.has_node(t)])
                elif target_val and self.graph.has_node(target_val):
                    target_ids_final.append(target_val)
            
            # --- Create all (Source, Target) combinations ---
            if not source_ids_final or not target_ids_final:
                # If a required part of the edge is missing, skip
                continue

            for s_id in source_ids_final:
                for t_id in target_ids_final:
                    if s_id and t_id: # Final safety check
                        self.graph.add_edge(s_id, t_id, label=label)

        self._save_graph()
        return new_node_ids_by_alias
    # --- END MODIFIED ---

    # --- MODIFIED: _build_graph_context ---
    def _build_graph_context(self, node_refs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Builds a context blob from the graph, including node attributes
        and their immediate neighbors (incoming/outgoing edges).
        
        Args:
            node_refs: A dict of {alias: node_id} from the vector metadata.
            
        Returns:
            A dictionary of {alias: {node_data_and_neighbors}}.
        """
        context: Dict[str, Dict[str, Any]] = {}
        for alias, node_id in node_refs.items():
            if node_id in self.graph.nodes:
                # 1. Get node attributes
                node_data = dict(self.graph.nodes[node_id])
                
                # 2. Get neighbors
                outgoing = []
                # G.adj[node] returns a dict of {neighbor: edge_data}
                for target, edge_data in self.graph.adj[node_id].items():
                    outgoing.append({
                        "label": edge_data.get("label"),
                        "target_id": target,
                        "target_type": self.graph.nodes[target].get("type", "Unknown")
                    })
                
                incoming = []
                # G.pred[node] returns a dict of {neighbor: edge_data}
                for source, edge_data in self.graph.pred[node_id].items():
                    incoming.append({
                        "label": edge_data.get("label"),
                        "source_id": source,
                        "source_type": self.graph.nodes[source].get("type", "Unknown")
                    })

                node_data["neighbors"] = {"outgoing": outgoing, "incoming": incoming}
                context[alias] = node_data
        return context
    # --- END MODIFIED ---

    # --- MODIFIED: get_tool ---
    def get_tool(self, tool_type: str, name: str | None = None):
        """
        Factory method to generate LangChain-compatible tools.
        
        Args:
            tool_type: The type of tool to get ('retrieve', 'ingest', 'lookup_node').
            name: An optional name override for the tool.
            
        Returns:
            A LangChain @tool object.
        """
        tool_name = name or f"{self.namespace}_{tool_type}"
        
        # --- Tool 1: retrieve ---
        if tool_type == "retrieve":
            retrieve_schema = create_model(
                f"{self.namespace.capitalize()}RetrieveInput",
                new_task_description=(str, ...),
            )

            @tool(
                tool_name,
                description=f"{self.retrieve_doc}",
                args_schema=retrieve_schema,
            )
            def retrieve_tool(new_task_description: str) -> str:
                """
                Searches the configured memory namespace for relevant entries.
                """
                result = self.retrieve(new_task_description)
                return json.dumps(result)

            return retrieve_tool

        # --- Tool 2: ingest ---
        if tool_type == "ingest":
            if not self._ingest_schema:
                raise ValueError(f"No ingestors available for namespace {self.namespace}")

            schema = self._ingest_schema

            @tool(
                tool_name,
                description=f"{self.ingest_doc}",
                args_schema=schema,
            )
            def ingest_tool(ingestor, payload: Dict[str, Any]) -> str:  # type: ignore[valid-type]
                """
                Adds structured content to the namespace using the selected ingestor.
                """
                # Enum values arrive as Enum instances; get the raw value.
                ingestor_name = getattr(ingestor, "value", ingestor)
                memory_id = self.ingest(str(ingestor_name), payload)
                return json.dumps({"status": "success", "memory_id": memory_id})

            return ingest_tool

        # --- Tool 3: lookup_node (NEW) ---
        if tool_type == "lookup_node":
            lookup_schema = create_model(
                f"{self.namespace.capitalize()}LookupInput",
                node_id=(str, ...),
            )

            @tool(
                tool_name,
                description=f"Retrieves all attributes and neighbors for a *specific* node ID from the {self.namespace} graph. Use this to get the details (like code) for an ID found via 'retrieve'.",
                args_schema=lookup_schema,
            )
            def lookup_node_tool(node_id: str) -> str:
                """
                Fetches a specific node's data and its graph connections.
                """
                if not self.graph.has_node(node_id):
                    return json.dumps({"error": "Node not found", "node_id": node_id})

                # 1. Get the node's attributes
                node_data = dict(self.graph.nodes[node_id])
                
                # 2. Get all outgoing edges
                outgoing = []
                for target_id, edge_data in self.graph.adj[node_id].items():
                    outgoing.append({
                        "label": edge_data.get("label"),
                        "target_id": target_id,
                        "target_type": self.graph.nodes[target_id].get("type", "Unknown")
                    })
                
                # 3. Get all incoming edges
                incoming = []
                for source_id, edge_data in self.graph.pred[node_id].items():
                    incoming.append({
                        "label": edge_data.get("label"),
                        "source_id": source_id,
                        "source_type": self.graph.nodes[source_id].get("type", "Unknown")
                    })

                node_data["neighbors"] = {"outgoing": outgoing, "incoming": incoming}
                return json.dumps(node_data)

            return lookup_node_tool
        # --- END NEW TOOL ---

        raise ValueError(f"Unknown tool_type: {tool_type}. Expected 'retrieve', 'ingest', or 'lookup_node'.")
    # --- END MODIFIED ---

    def _extract_value(self, payload: Dict[str, Any], path: Optional[str]) -> Any:
        """
        Safely extracts a value from a nested dictionary using dot notation.
        
        Example: _extract_value(payload, "session.user.id")
        """
        if not path:
            return None
        current: Any = payload
        try:
            for part in path.split("."):
                if current is None:
                    return None
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return current
        except Exception:
            return None

    def _distance_to_similarity(self, distance: Optional[float]) -> Optional[float]:
        """Converts Chroma's cosine distance to a 0.0-1.0 similarity score."""
        if distance is None:
            return None
        # Chroma's cosine distance is 0 (identical) to 2 (opposite).
        # We convert this to a similarity score from 1.0 (identical) to 0.0 (unrelated).
        return max(0.0, min(1.0, 1.0 - (distance / 2.0)))

    def _load_graph(self) -> nx.DiGraph:
        """Loads the graph from the .graphml file, or creates a new one."""
        try:
            return nx.read_graphml(self.graph_path)
        except FileNotFoundError:
            return nx.DiGraph()

    def _save_graph(self) -> None:
        """Saves the graph to the .graphml file."""
        nx.write_graphml(self.graph, self.graph_path)


__all__ = ["MemKappa"]
