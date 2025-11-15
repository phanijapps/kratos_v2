from __future__ import annotations

from pathlib import Path
from typing import Any

from kratos.core.util.vault_middleware import ContextVaultMiddleware
from kratos.tools.repl_tools import SESSION_CODE_EXECUTOR


class DummyRuntime:
    def __init__(self, state: dict[str, Any]):
        self.state = state


def create_middleware(tmp_path) -> ContextVaultMiddleware:
    return ContextVaultMiddleware(
        workspace_dir=str(tmp_path),
        use_sqlite=False,
        enable_logging=False,
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


def test_session_code_executor_uses_vault_location(tmp_path):
    middleware = create_middleware(tmp_path)
    state: dict[str, Any] = {}
    updates = middleware.before_agent(state, runtime=None)
    if updates:
        state.update(updates)
    runtime = DummyRuntime(state)

    location_tool = get_tool(middleware, "get_vault_location")
    write_tool = get_tool(middleware, "write_file")

    code_dir = run_tool(
        location_tool,
        asset_type="code",
        runtime=runtime,
    )
    code_dir_path = Path(code_dir)
    assert code_dir_path.name == "code"
    assert runtime.state["session_id"] in code_dir
    assert str(tmp_path) in code_dir

    script_content = f"""from pathlib import Path

target_dir = Path(r\"{code_dir}\")
output_file = target_dir / \"analysis.txt\"
output_file.write_text(\"analysis generated\", encoding=\"utf-8\")
print(\"analysis saved:\", output_file)
"""

    run_tool(
        write_tool,
        file_path="/code/analysis.py",
        content=script_content,
        runtime=runtime,
    )

    script_path = code_dir_path / "analysis.py"
    assert script_path.exists()

    exec_result = run_tool(
        SESSION_CODE_EXECUTOR,
        py_file_path=str(code_dir_path / "analysis.py"),
        session_id=runtime.state["session_id"],
    )

    assert exec_result.success is True
    assert "analysis saved" in exec_result.stdout
    output_path = code_dir_path / "analysis.txt"
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "analysis generated"
