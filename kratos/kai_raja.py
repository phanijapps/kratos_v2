from deepagents import SubAgent
from langchain.tools import tool
import datetime

from kratos.core.graph import create_deep_agent
from kratos.subagents import build_subagents


from kratos.llm_factory import ModelProvider, LLMFactory
from kratos.prompts import KAI_RAJA_KAI_PROMPT
from kratos.tools.memory import semantic_memory_ingest, semantic_memory_lookup

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
    model = LLMFactory.get_llm_model(model_provider=ModelProvider.OPENROUTER, model_name="anthropic/claude-sonnet-4.5")
    #LLMFactory.get_llm_model(model_provider=ModelProvider.OPENROUTER, model_name="openai/gpt-5-mini")
    #LLMFactory.get_llm_model(model_provider=ModelProvider.DEEPSEEK)
    #
    #
    #
    
    subagents = build_subagents()
    return create_deep_agent(
        system_prompt=KAI_RAJA_KAI_PROMPT,
        tools=[get_current_date_time, semantic_memory_ingest, semantic_memory_lookup],
        model=model, 
        subagents=subagents, 
        use_longterm_memory=True
    )

kai = get_fin_graph()
