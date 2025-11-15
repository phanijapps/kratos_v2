from __future__ import annotations

from typing import Any

from kratos.core.util.vault_middleware import ContextVaultMiddleware


class DummyRuntime:
    def __init__(self, state: dict[str, Any]):
        self.state = state


def create_middleware(tmp_path, **overrides) -> ContextVaultMiddleware:
    return ContextVaultMiddleware(
        workspace_dir=str(tmp_path),
        use_sqlite=False,
        enable_logging=False,
        **overrides,
    )


def get_tool(middleware: ContextVaultMiddleware, name: str):
    for tool in middleware.tools:
        if getattr(tool, "name", None) == name:
            return tool
    raise AssertionError(f"Tool named '{name}' was not registered")


def run_tool(tool, *args, **kwargs):
    if hasattr(tool, "func"):
        return tool.func(*args, **kwargs)
    if hasattr(tool, "invoke"):
        return tool.invoke(kwargs)
    return tool(*args, **kwargs)


def test_vault_middleware_tool_flow(tmp_path):
    middleware = create_middleware(tmp_path)
    state: dict[str, Any] = {}
    updates = middleware.before_agent(state, runtime=None)
    if updates:
        state.update(updates)
    runtime = DummyRuntime(state)

    write_tool = get_tool(middleware, "write_file")
    ls_tool = get_tool(middleware, "ls")
    read_tool = get_tool(middleware, "read_file")
    summary_tool = get_tool(middleware, "get_session_summary")
    glob_tool = get_tool(middleware, "glob_search")
    location_tool = get_tool(middleware, "get_vault_location")
    grep_tool = get_tool(middleware, "grep_search")

    write_result = run_tool(
        write_tool,
        file_path="/reports/summary.txt",
        content="hello world",
        runtime=runtime,
    )
    assert "Successfully wrote /reports/summary.txt" in write_result
    assert "Storage: session" in write_result

    ls_result = run_tool(ls_tool, runtime=runtime)
    assert "summary.txt" in ls_result

    read_result = run_tool(
        read_tool,
        file_path="/reports/summary.txt",
        runtime=runtime,
    )
    assert "hello world" in read_result

    summary_result = run_tool(summary_tool, runtime=runtime)
    assert "Session Summary" in summary_result
    assert "1 files" in summary_result

    glob_result = run_tool(glob_tool, pattern="*.txt", runtime=runtime)
    assert "summary.txt" in glob_result

    location_result = run_tool(
        location_tool,
        asset_type="reports",
        runtime=runtime,
    )
    assert location_result.endswith("reports")
    assert location_result.startswith(str(tmp_path))

    grep_result = run_tool(grep_tool, search_term="hello", runtime=runtime)
    assert "summary.txt" in grep_result
    assert "Line 1" in grep_result
