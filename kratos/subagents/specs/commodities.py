from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def commodities_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["commodities"]
    return SubAgentSpec(
        name="commodities",
        description="Global commodities pricing for energy, metals, and agricultural products",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("WTI", "West Texas Intermediate (WTI) crude oil prices"),
            ToolBinding("BRENT", "Brent crude oil prices"),
            ToolBinding("NATURAL_GAS", "Henry Hub natural gas spot prices"),
            ToolBinding("COPPER", "Global copper prices"),
            ToolBinding("ALUMINUM", "Global aluminum prices"),
            ToolBinding("WHEAT", "Global wheat prices"),
            ToolBinding("CORN", "Global corn prices"),
            ToolBinding("COTTON", "Global cotton prices"),
            ToolBinding("SUGAR", "Global sugar prices"),
            ToolBinding("COFFEE", "Global coffee prices"),
            ToolBinding("ALL_COMMODITIES", "All commodities prices"),
        ],
        group="market_data",
    )
