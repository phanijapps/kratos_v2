from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def alpha_intelligence_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["alpha_intelligence"]
    return SubAgentSpec(
        name="alpha_intelligence",
        description="Advanced market intelligence including sentiment analysis, earnings transcripts, market movers, and insider trading",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("NEWS_SENTIMENT", "Live and historical market news & sentiment"),
            ToolBinding("TOP_GAINERS_LOSERS", "Top 20 gainers, losers, and most active"),
            ToolBinding("INSIDER_TRANSACTIONS", "Latest and historical insider transactions"),
            ToolBinding("ANALYTICS_FIXED_WINDOW", "Advanced analytics over fixed windows"),
            ToolBinding("ANALYTICS_SLIDING_WINDOW", "Advanced analytics over sliding windows"),
        ],
        group="market_data",
    )
