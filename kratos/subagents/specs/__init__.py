"""
Module import side-effects register subagents with the global registry.
"""

from importlib import import_module

_MODULES = [
    "kratos.subagents.specs.core_stock",
    "kratos.subagents.specs.options",
    "kratos.subagents.specs.alpha_intelligence",
    "kratos.subagents.specs.fundamentals",
    "kratos.subagents.specs.forex",
    "kratos.subagents.specs.crypto",
    "kratos.subagents.specs.commodities",
    "kratos.subagents.specs.economics",
    "kratos.subagents.specs.technicals",
    "kratos.subagents.specs.codeact",
    "kratos.subagents.specs.search",
    "kratos.subagents.specs.final_report"
]


for module_path in _MODULES:
    import_module(module_path)


__all__ = ["_MODULES"]
