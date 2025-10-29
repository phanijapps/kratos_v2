from typing import List

from deepagents.graph import SubAgent
from langchain.tools import BaseTool

from kratos.subagents.agents import ALPHA_VANTAGE_SUBAGENTS


ADDITIONAL_INSTRUCTIONS = """
For tools that return large result sets:
1. Offload results to filesystem immediately using write_file
2. Process results via subtask delegation to relevant subagents
3. Save processed summaries back to filesystem for context preservation
4. Use grep/glob to search through saved reports when synthesizing final analysis

When handling technical indicators (MACD, SMA, RSI, etc.):
- Delegate ONE indicator per subagent call to minimize context usage
- Example: task('technical_indicators', 'Calculate SMA for PTON and save to reports/pton_sma.json')
- Store each indicator result in separate files: {symbol}_{indicator}_report.txt
- Use ls to verify file creation, read_file to retrieve specific reports
"""


def build_enhanced_system_prompt(
    base_prompt: str,
    output_format: dict,
    additional_instructions: str,
) -> str:
    """
    Build an enhanced system prompt that includes output format instructions.

    Args:
        base_prompt: The original system prompt from system_prompts.py
        output_format: The output format specification dictionary
        additional_instructions: Additional instructions to append

    Returns:
        Enhanced system prompt with output format guidelines
    """
    output_format_instructions = """

## Output Format Guidelines

You can return your analysis in one of the following formats based on the complexity and requirements of the task:

"""

    # Add each output format option
    if output_format and "options" in output_format:
        for idx, option in enumerate(output_format["options"], 1):
            output_format_instructions += f"""
{idx}. **{option['format'].replace('_', ' ').title()}**
   - {option['description']}
"""

    output_format_instructions += """

**Selection Guidelines:**
- Use "consolidated_report" for straightforward queries requiring direct analysis
- Use "report_with_instructions" when the master agent needs to perform follow-up actions
- Use "report_with_files" when raw data needs to be processed by a codeact agent
- Use "report_with_files_and_instructions" for complex multi-stage analysis workflows

**File Export Format:**
When exporting files, use CSV or JSON format and clearly specify:
- Filename and location
- Data structure and field descriptions
- Processing instructions for the codeact agent
"""

    # Combine all parts
    enhanced_prompt = (
        base_prompt
        + output_format_instructions
        + "\n\n"
        + additional_instructions
    )

    return enhanced_prompt


def get_financial_tools() -> list[BaseTool]:
    """
    Gets financial tools from local yfinance-based fin_tools module
    """
    from kratos.tools import TOOLS
    return TOOLS


def build_subagents() -> list[SubAgent]:
    """Build a list of financial subagents with enhanced prompts and tools."""
    subagents = []
    tools = get_financial_tools()

    for sub_agent_config in ALPHA_VANTAGE_SUBAGENTS:
        sub_agent_tool_names = [tool["tool"] for tool in sub_agent_config["tools"]]

        # Extract output format and enhance system prompt
        output_format = sub_agent_config.get("output_format", {})
        enhanced_prompt = build_enhanced_system_prompt(
            base_prompt=sub_agent_config["system_prompt"],
            output_format=output_format,
            additional_instructions=ADDITIONAL_INSTRUCTIONS,
        )

        subagents.append(
            SubAgent(
                name=sub_agent_config["category"],
                description=sub_agent_config["description"],
                system_prompt=enhanced_prompt,
                tools=[tool for tool in tools if tool.name in sub_agent_tool_names],
            )
        )

    return subagents


__all__ = [
    "build_subagents",
]
