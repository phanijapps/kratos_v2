from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def codeact_spec() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["codeact"]
    return SubAgentSpec(
        name="codeact",
        description="Codeact subagent to produce charts and analysis over tool results with filesystem-aware Python execution.",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
            ToolBinding(
                "session_code_executor",
                "Executes python files from disk given a file_path and optional working directory",
            ),
        ],
        group="utilities",
    )
