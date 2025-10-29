import pytest

try:
    from deepagents.graph import SubAgent  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency missing locally
    SubAgent = None  # type: ignore[misc]


@pytest.mark.skipif(SubAgent is None, reason="deepagents package not available")
def test_build_subagents_registers_expected_tools():
    from kratos.subagents import build_subagents

    subagents = build_subagents()

    assert subagents, "build_subagents() should return at least one SubAgent entry"

    by_name = {}
    for entry in subagents:
        if isinstance(entry, dict):
            name = entry.get("name")
            tools = entry.get("tools", [])
        else:
            name = getattr(entry, "name", None)
            tools = getattr(entry, "tools", [])
        if name:
            by_name[name] = tools

    print("Subagents discovered:", sorted(by_name))
    tool_summary = {}
    for name, tools in by_name.items():
        tool_summary[name] = sorted(
            tool_name
            for tool_name in (getattr(tool, "name", None) for tool in tools)
            if tool_name
        )
    print("Tool registry snapshot:", tool_summary)

    assert "codeact" in by_name, "codeact subagent missing from registry"
    codeact_tools = {getattr(tool, "name", None) for tool in by_name["codeact"]}
    assert "session_code_executor" in codeact_tools

    assert "search_web" in by_name, "search_web subagent missing from registry"
    search_tools = {getattr(tool, "name", None) for tool in by_name["search_web"]}
    assert {"search_web", "search_news"} <= search_tools
