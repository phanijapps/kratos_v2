from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def options_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["options_data_apis"]
    return SubAgentSpec(
        name="options_data_apis",
        description="Delivers real-time and historical options market data with Greeks calculations",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("REALTIME_OPTIONS", "Realtime US options data with Greeks"),
            ToolBinding("HISTORICAL_OPTIONS", "Historical options chain for 15+ years"),
        ],
        group="market_data",
    )
