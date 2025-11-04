from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional


@dataclass(frozen=True, slots=True)
class ToolBinding:
    """Tool identifier plus a human readable description."""

    id: str
    description: str


@dataclass(frozen=True, slots=True)
class SubAgentSpec:
    """Immutable definition describing a DeepAgents subagent."""

    name: str
    description: str
    prompt: str
    tools: List[ToolBinding]
    output_format: Optional[Mapping[str, Any]] = None
    group: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class SubAgentRegistry:
    """Central registry for subagent specifications."""

    def __init__(self) -> None:
        self._specs: Dict[str, SubAgentSpec] = {}

    def register(self, spec: SubAgentSpec) -> SubAgentSpec:
        """Register a new subagent specification."""
        if spec.name in self._specs:
            raise ValueError(f"Subagent '{spec.name}' already registered.")
        self._specs[spec.name] = spec
        return spec

    def register_from_factory(
        self, factory: Callable[[], SubAgentSpec]
    ) -> SubAgentSpec:
        """Decorator/helper to register via a factory callable."""
        spec = factory()
        return self.register(spec)

    def get(self, name: str) -> SubAgentSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Unknown subagent '{name}'.") from exc

    def list(self, names: Optional[Iterable[str]] = None) -> List[SubAgentSpec]:
        if names is None:
            return list(self._specs.values())
        selected: List[SubAgentSpec] = []
        for name in names:
            selected.append(self.get(name))
        return selected

    def groups(self) -> Dict[str, List[SubAgentSpec]]:
        grouped: Dict[str, List[SubAgentSpec]] = {}
        for spec in self._specs.values():
            key = spec.group or "default"
            grouped.setdefault(key, []).append(spec)
        return grouped


registry = SubAgentRegistry()


def register_subagent(factory: Callable[[], SubAgentSpec]) -> Callable[[], SubAgentSpec]:
    """Decorator for modules to register their subagent spec."""

    registry.register_from_factory(factory)
    return factory


__all__ = [
    "ToolBinding",
    "SubAgentSpec",
    "SubAgentRegistry",
    "registry",
    "register_subagent",
]
