from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def economics_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["economic_indicators"]
    return SubAgentSpec(
        name="economic_indicators",
        description="Macroeconomic indicators including GDP, inflation, unemployment, and interest rates",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding("REAL_GDP", "Real Gross Domestic Product"),
            ToolBinding("REAL_GDP_PER_CAPITA", "Real GDP per capita"),
            ToolBinding("TREASURY_YIELD", "Daily treasury yield rates"),
            ToolBinding("FEDERAL_FUNDS_RATE", "Federal funds rate (interest rates)"),
            ToolBinding("CPI", "Consumer Price Index"),
            ToolBinding("INFLATION", "Inflation rates"),
            ToolBinding("RETAIL_SALES", "Retail sales data"),
            ToolBinding("DURABLES", "Durable goods orders"),
            ToolBinding("UNEMPLOYMENT", "Unemployment rate"),
            ToolBinding("NONFARM_PAYROLL", "Non-farm payroll data"),
        ],
        group="macro",
    )
