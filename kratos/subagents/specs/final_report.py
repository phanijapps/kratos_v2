from kratos.subagents.registry import SubAgentSpec, ToolBinding, register_subagent
from kratos.subagents.system_prompts import SYSTEM_PROMPTS


@register_subagent
def final_report() -> SubAgentSpec:
    prompt_def = SYSTEM_PROMPTS["final_report"]
    return SubAgentSpec(
        name="final_report",
        description="Final Consolidated Report of all the generated artifacts",
        prompt=prompt_def["prompt"],
        output_format=prompt_def["output_format"],
        tools=[
          
        ],
        group="utilities",
    )
