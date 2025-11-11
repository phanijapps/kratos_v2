from typing import Sequence
from deepagents.graph import SubAgent

from kratos.subagents.prompts import NUM_NERD, THINKER, REPORTER
from kratos.tools import SESSION_CODE_EXECUTOR, search_news, search_web
from kratos.tools.memory import semantic_memory_ingest, semantic_memory_retrieve, episodic_memory_ingest, episodic_memory_retrieve


SUBAGENTS = [
    {
        "name": "Nerd",
        "description": "A highly intelligent subagent who excels at complex problem-solving and analytical thinking using python code.",
        "prompt": NUM_NERD,
        "tools": [SESSION_CODE_EXECUTOR, semantic_memory_retrieve, episodic_memory_retrieve, episodic_memory_ingest],
        "output_format": {
            "type": "flexible",
            "options": [
                {
                    "format": "consolidated_report",
                    "description": "Technical analysis report with signals and trading recommendations"
                },
                {
                    "format": "report_with_instructions",
                    "description": "Technical analysis with instructions for multi-timeframe confirmation or divergence studies"
                },
                {
                    "format": "report_with_files",
                    "description": "Technical indicator data exported to files with instructions for codeact agent to perform backtesting, signal optimization, or custom indicator development (e.g., processing MACD, SMA, RSI files for strategy testing)"
                },
                {
                    "format": "report_with_files_and_instructions",
                    "description": "Complete technical analysis package with indicator data files and instructions for strategy backtesting, parameter optimization, or machine learning feature engineering"
                },
                {
                    "format": "episodic_memory_update_JSON",
                    "description": "List of episodes that include key learnings, code snippets, and observations to be stored in episodic memory for future reference"

                }
            ]
        }
    },
    {
        "name": "Thinker",
        "description": "A creative subagent who uses out-of-the-box thinking and performs financial analysis using output of number nerd subagent and tools available.",
        "prompt": THINKER,
        "tools": [search_web,search_news],
        "output_format": {
            "type": "flexible",
            "options": [
                {
                    "format": "consolidated_report",
                    "description": "Technical analysis report with signals and trading recommendations"
                },
                {
                    "format": "report_with_instructions",
                    "description": "Technical analysis with instructions for multi-timeframe confirmation or divergence studies"
                },
                {
                    "format": "report_with_files",
                    "description": "Technical indicator data exported to files with instructions for codeact agent to perform backtesting, signal optimization, or custom indicator development (e.g., processing MACD, SMA, RSI files for strategy testing)"
                },
                {
                    "format": "report_with_files_and_instructions",
                    "description": "Complete technical analysis package with indicator data files and instructions for strategy backtesting, parameter optimization, or machine learning feature engineering"
                }
            ]
        }
    },
    {
        "name": "Reporter",
        "description": "A detail-oriented subagent who specializes in gathering information, summarizing data, and generating comprehensive reports using all available tools and the output of other subagents.",
        "prompt": REPORTER,
        "tools": [episodic_memory_retrieve, episodic_memory_ingest],
        "output_format": {
            "type": "rigid",
            "options": [
                {
                    "format": "Final Report",
                    "description": "A single, consolidated HTML/Markdown report integrating all session artifacts (text summaries, table excerpts, chart embeds/references, key metrics) with novice-friendly explanations, logical justifications, and risk-aligned recommendations. Include absolute paths to all non-embedded files for reference."
                }
            ]
        }
    }
]




ADDITIONAL_INSTRUCTIONS = """
!!Important!!?: Run get_session_summary tool first and use appropriate relative locations to write_files.
Example: json files to /data. reports to /reports, python code to /code

For tools that return large result sets:
1. Offload results to filesystem immediately using write_file
2. Process results via subtask delegation to relevant subagents
3. Save processed summaries back to filesystem for context preservation
4. Use grep/glob to search through saved reports when synthesizing final analysis

When handling technical indicators (MACD, SMA, RSI, etc.):
- Delegate ONE indicator per subagent call to minimize context usage
- Example: task('technical_indicators', 'Calculate SMA for PTON and save to /reports/pton_sma.json')
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


def build_subagents(enabled: Sequence[str] | None = None) -> list[SubAgent]:
    """Build a list of financial subagents with enhanced prompts and tools.

    Args:
        enabled: Optional sequence of subagent names to include. Defaults to all.
    """
    subagents  = []
    for spec in SUBAGENTS:

        output_format = spec.get("output_format", {}) or {}
        enhanced_prompt = build_enhanced_system_prompt(
            base_prompt=spec.get("prompt", ""),
            output_format=output_format,
            additional_instructions=ADDITIONAL_INSTRUCTIONS,
        )

        subagents.append(
            SubAgent(
                name=spec.get("name", ""),
                description=spec.get("description", ""),
                system_prompt=enhanced_prompt,
                tools=spec.get("tools", []),
            )
        )

    return subagents


__all__ = [
    "build_subagents"
]
