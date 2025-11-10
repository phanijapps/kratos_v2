"""
Config-driven memory core (MemKappa).

This module keeps the existing Memcore untouched while providing a safer
playground for schema-based ingestion. Each namespace loads a YAML config
that describes the available ingestors, the text/metadata to index, and
the graph nodes/edges to persist.

Example episodic ingestion payload (matches ``kappa/config/episodic.yml``):

.. code-block:: python

    payload = {
        "episode": {
            "id": "session-001",
            "task": "Fix flaky unit test",
            "context": "Test intermittently fails on CI",
            "resolution": "Added deterministic seed and retries",
            "reflection": "Need shared helper for deterministic data",
            "outcome": "success",
        }
    }
    mem.ingest("learning_episode", payload)
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
        self.namespace = namespace
        self.store_path = store_path
        self.embedding_function = embedding_function
        self.config = self._load_config(config_path)
        self.ingestor_specs: Dict[str, Dict[str, Any]] = self.config.get("ingestors", {})
        if not self.ingestor_specs:
            raise ValueError(f"No ingestors defined in config: {config_path}")

        os.makedirs(store_path, exist_ok=True)

        collection_suffix = (
            self.config.get("vector_store", {}).get("collection_suffix") or namespace
        )
        self.db_path = os.path.join(store_path, f"{namespace}_vectordb")
        self.vector_db_client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.vector_db_client.get_or_create_collection(
            name=f"{namespace}_{collection_suffix}_collection",
            metadata={"hnsw:space": "cosine"},
        )

        self.graph_path = os.path.join(store_path, f"{namespace}_graph.graphml")
        self.graph = self._load_graph()
        self._ingest_schema = self._build_ingest_schema()

    @staticmethod
    def _load_config(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def _build_ingest_schema(self) -> Optional[BaseModel]:
        if not self.ingestor_specs:
            return None
        enum_cls = Enum(
            f"{self.namespace.capitalize()}Ingestor",
            {name: name for name in self.ingestor_specs},
        )
        model = create_model(
            f"{self.namespace.capitalize()}IngestInput",
            ingestor=(enum_cls, ...),
            payload=(Dict[str, Any], ...),
        )
        return model

    def ingest(self, ingestor: str, payload: Dict[str, Any]) -> str:
        spec = self.ingestor_specs.get(ingestor)
        if not spec:
            raise ValueError(f"Ingestor '{ingestor}' is not defined for {self.namespace}")

        vector_spec = spec.get("vector", {})
        text_blob = self._build_text(vector_spec.get("text_fields", []), payload)
        metadata = self._build_metadata(vector_spec.get("metadata", {}), payload)

        graph_spec = spec.get("graph", {})
        graph_nodes = self._update_graph(graph_spec, payload)

        metadata["graph_nodes"] = json.dumps(graph_nodes)
        memory_id = f"mem_{self.namespace}_{uuid.uuid4()}"
        embedding = self.embedding_function.embed_query(text_blob)

        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            metadatas=[metadata],
        )
        return memory_id

    def retrieve(self, new_task_description: str, n_results: int = 1) -> Dict[str, Any]:
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
            graph_nodes_raw = metadata.get("graph_nodes", {})
            if isinstance(graph_nodes_raw, str):
                try:
                    graph_nodes = json.loads(graph_nodes_raw)
                except json.JSONDecodeError:
                    graph_nodes = {}
            else:
                graph_nodes = graph_nodes_raw or {}
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
        chunks = []
        for field in fields:
            value = self._extract_value(payload, field)
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                chunks.append(json.dumps(value, ensure_ascii=False))
            else:
                chunks.append(str(value))
        return "\n".join(chunks) if chunks else json.dumps(payload, ensure_ascii=False)

    def _build_metadata(self, mapping: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        for key, path in mapping.items():
            metadata[key] = self._extract_value(payload, path)
        metadata["namespace"] = self.namespace
        return metadata

    def _update_graph(self, graph_spec: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, str]:
        node_ids: Dict[str, str] = {}
        for node in graph_spec.get("nodes", []):
            alias = node.get("id")
            node_id = self._extract_value(payload, node.get("key"))
            if not alias or not node_id:
                continue
            attributes = {
                attr_name: self._extract_value(payload, attr_path)
                for attr_name, attr_path in (node.get("attributes") or {}).items()
            }
            attributes["type"] = node.get("type", alias)
            self.graph.add_node(node_id, **attributes)
            node_ids[alias] = node_id

        for edge in graph_spec.get("edges", []):
            source_id = node_ids.get(edge.get("source"))
            target_id = node_ids.get(edge.get("target"))
            if not source_id or not target_id:
                continue
            self.graph.add_edge(source_id, target_id, label=edge.get("label", "RELATED_TO"))

        self._save_graph()
        return node_ids

    def _build_graph_context(self, node_refs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        context: Dict[str, Dict[str, Any]] = {}
        for alias, node_id in node_refs.items():
            if node_id in self.graph.nodes:
                context[alias] = dict(self.graph.nodes[node_id])
        return context

    def get_tool(self, tool_type: str, *, name: str | None = None):
        tool_name = name or f"{self.namespace}_{tool_type}"
        if tool_type == "retrieve":
            retrieve_schema = create_model(
                f"{self.namespace.capitalize()}RetrieveInput",
                new_task_description=(str, ...),
            )

            @tool(
                tool_name,
                description=f"Used to retrieve {self.namespace}  memory entries relevant to the task description.",
                args_schema=retrieve_schema,
            )
            def retrieve_tool(new_task_description: str) -> str:
                """
                Searches the configured memory namespace for relevant entries.
                """
                result = self.retrieve(new_task_description)
                return json.dumps(result)

            return retrieve_tool

        if tool_type == "ingest":
            if not self._ingest_schema:
                raise ValueError(f"No ingestors available for namespace {self.namespace}")

            schema = self._ingest_schema

            @tool(
                tool_name,
                description=f"Save {self.namespace} memory for domain specific purposes.",
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

        raise ValueError(f"Unknown tool_type: {tool_type}. Expected 'retrieve' or 'ingest'.")

    def _extract_value(self, payload: Dict[str, Any], path: Optional[str]) -> Any:
        if not path:
            return None
        current: Any = payload
        for part in path.split("."):
            if current is None:
                return None
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _distance_to_similarity(self, distance: Optional[float]) -> Optional[float]:
        if distance is None:
            return None
        return max(0.0, min(1.0, 1.0 - (distance / 2.0)))

    def _load_graph(self) -> nx.DiGraph:
        try:
            return nx.read_graphml(self.graph_path)
        except FileNotFoundError:
            return nx.DiGraph()

    def _save_graph(self) -> None:
        nx.write_graphml(self.graph, self.graph_path)


__all__ = ["MemKappa"]
