from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def forex_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["forex"]
    return SubAgentSpec(
        name="forex",
        description="Foreign exchange rates across multiple timeframes",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("FX_INTRADAY", "Intraday foreign exchange rates"),
            ToolBinding("FX_DAILY", "Daily foreign exchange rates"),
            ToolBinding("FX_WEEKLY", "Weekly foreign exchange rates"),
            ToolBinding("FX_MONTHLY", "Monthly foreign exchange rates"),
        ],
        group="market_data",
    )
