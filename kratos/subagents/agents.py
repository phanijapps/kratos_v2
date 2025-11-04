from __future__ import annotations

from typing import Dict, List

from kratos.subagents.registry import SubAgentSpec, ToolBinding, registry
from kratos.subagents import specs  # noqa: F401  # ensure registration side-effects


def _binding_to_dict(binding: ToolBinding) -> Dict[str, str]:
    return {"tool": binding.id, "description": binding.description}


def _spec_to_legacy_payload(spec: SubAgentSpec) -> Dict[str, object]:
    return {
        "category": spec.name,
        "description": spec.description,
        "system_prompt": spec.prompt,
        "output_format": spec.output_format,
        "tools": [_binding_to_dict(binding) for binding in spec.tools],
    }


def get_registered_subagents() -> List[SubAgentSpec]:
    """Return all registered subagent specs."""
    return registry.list()


ALPHA_VANTAGE_SUBAGENTS: List[Dict[str, object]] = [
    _spec_to_legacy_payload(spec) for spec in get_registered_subagents()
]
