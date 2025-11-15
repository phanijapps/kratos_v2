import logging
from langchain.tools import tool
import datetime
from pathlib import Path
from typing import Any, Optional

from kratos.core.graph import create_deep_agent
from kratos.subagents import build_subagents
from kratos.core.utils import LoggingMiddleware
from kratos.core.middleware import KratosCompositeBackend
from langchain.agents import  AgentState

from kratos.llm_factory import ModelProvider, LLMFactory
from kratos.prompts import KAI_RAJA_KAI_PROMPT
from kratos.tools.memory import semantic_memory_ingest, semantic_memory_lookup
from deepagents.backends import StateBackend, FilesystemBackend

class KratosState(AgentState):
    ticker: Optional[str]
    workspace_dir: Optional[str]
    sessions: Any

@tool(description="Gets Current System Date Time")
def get_current_date_time() -> str:
    """
    Gets current system date/time.

    Returns:
    String format of date time.
    """
    return str(datetime.datetime.now())



def get_fin_graph():
    """
    Factory function that builds and returns the financial deep agent graph.
    """
    model = LLMFactory.get_llm_model(model_provider=ModelProvider.DEEPSEEK)
    #LLMFactory.get_llm_model(model_provider=ModelProvider.OPENROUTER, model_name="google/gemini-2.5-flash-preview-09-2025")
    #LLMFactory.get_llm_model(model_provider=ModelProvider.DEEPSEEK)
  
    vault_path = Path("./.vault").resolve()
    print(f"Vault path = {vault_path}")
    backend = KratosCompositeBackend(
            default=FilesystemBackend(root_dir=str(vault_path), virtual_mode = True),
            routes={
                
            }
    )
    

    return create_deep_agent(
        system_prompt = KAI_RAJA_KAI_PROMPT,
        tools = [get_current_date_time, semantic_memory_ingest, semantic_memory_lookup],
        model = model,
        backend = backend,
        state_schmea=KratosState,
        subagents = build_subagents(),
        middleware = [LoggingMiddleware(log_level=logging.INFO, agent_name="kai_raja_agent")],
    )

kai = get_fin_graph()
