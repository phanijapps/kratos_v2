from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def fundamentals_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["fundamental_data"]
    return SubAgentSpec(
        name="fundamental_data",
        description="Company financial statements, earnings data, and corporate event calendars",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("COMPANY_OVERVIEW", "Company information, financial ratios, and metrics"),
            ToolBinding("INCOME_STATEMENT", "Annual and quarterly income statements"),
            ToolBinding("BALANCE_SHEET", "Annual and quarterly balance sheets"),
            ToolBinding("CASH_FLOW", "Annual and quarterly cash flow statements"),
            ToolBinding("EARNINGS", "Annual and quarterly earnings data"),
            ToolBinding("LISTING_STATUS", "Listing and delisting data for equities"),
            ToolBinding("EARNINGS_CALENDAR", "Earnings calendar for upcoming earnings"),
            ToolBinding("IPO_CALENDAR", "Initial public offering calendar"),
        ],
        group="market_data",
    )
