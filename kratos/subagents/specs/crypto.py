from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def crypto_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["cryptocurrencies"]
    return SubAgentSpec(
        name="cryptocurrencies",
        description="Digital and cryptocurrency market data with exchange rates and historical time series",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("CURRENCY_EXCHANGE_RATE", "Exchange rate between digital/crypto currencies"),
            ToolBinding("DIGITAL_CURRENCY_INTRADAY", "Intraday time series for digital currencies"),
            ToolBinding("DIGITAL_CURRENCY_DAILY", "Daily time series for digital currencies"),
            ToolBinding("DIGITAL_CURRENCY_WEEKLY", "Weekly time series for digital currencies"),
            ToolBinding("DIGITAL_CURRENCY_MONTHLY", "Monthly time series for digital currencies"),
        ],
        group="market_data",
    )
