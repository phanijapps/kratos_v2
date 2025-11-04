from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def core_stock_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["core_stock_apis"]
    return SubAgentSpec(
        name="core_stock_apis",
        description="Provides comprehensive stock market data including real-time quotes, historical time series, and symbol search capabilities",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("TIME_SERIES_INTRADAY", "Current and 20+ years of historical intraday OHLCV data"),
            ToolBinding("TIME_SERIES_DAILY", "Daily time series (OHLCV) covering 20+ years"),
            ToolBinding("TIME_SERIES_DAILY_ADJUSTED", "Daily adjusted OHLCV with split/dividend events"),
            ToolBinding("TIME_SERIES_WEEKLY", "Weekly time series (last trading day of week)"),
            ToolBinding("TIME_SERIES_WEEKLY_ADJUSTED", "Weekly adjusted time series with dividends"),
            ToolBinding("TIME_SERIES_MONTHLY", "Monthly time series (last trading day of month)"),
            ToolBinding("TIME_SERIES_MONTHLY_ADJUSTED", "Monthly adjusted time series with dividends"),
            ToolBinding("GLOBAL_QUOTE", "Latest price and volume for a ticker"),
            ToolBinding("REALTIME_BULK_QUOTES", "Realtime quotes for up to 100 symbols"),
            ToolBinding("SYMBOL_SEARCH", "Search for symbols by keywords"),
            ToolBinding("MARKET_STATUS", "Current market status worldwide"),
        ],
        group="market_data",
    )
