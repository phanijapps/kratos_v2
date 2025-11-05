from deepagents import SubAgent
from langchain.tools import tool
import datetime

from kratos.core.graph import create_deep_agent
from kratos.subagents import build_subagents


from kratos.llm_factory import ModelProvider, LLMFactory
from kratos.prompts import KAI_RAJA_KAI_PROMPT

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
    #LLMFactory.get_llm_model(model_provider=ModelProvider.OPENROUTER, model_name="google/gemini-2.5-flash")
    #LLMFactory.get_llm_model(model_provider=ModelProvider.DEEPSEEK)
    #
    #
    #
    
    subagents = build_subagents()
    return create_deep_agent(
        system_prompt=KAI_RAJA_KAI_PROMPT,
        tools=[get_current_date_time],
        model=model, 
        subagents=subagents, 
        use_longterm_memory=True
    )

kai = get_fin_graph()
