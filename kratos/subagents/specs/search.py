from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def search_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["search_web"]
    return SubAgentSpec(
        name="search_web",
        description="Web search specialist for gathering market context, macro news, and corroborating data points.",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("search_web", "Used to run web search"),
            ToolBinding("search_news", "Used to run news-oriented search"),
        ],
        group="utilities",
    )
