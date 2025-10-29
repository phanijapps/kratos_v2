from pathlib import Path

from kratos.tools.repl_tools import SESSION_CODE_EXECUTOR


def run_tool(tool, **kwargs):
    if hasattr(tool, "func"):
        return tool.func(**kwargs)
    return tool(**kwargs)


def test_session_code_executor_runs_python_file(tmp_path):
    script = Path(tmp_path) / "demo.py"
    script.write_text(
        "print('hello from script')\nvalue = 21\nprint(value)",
        encoding="utf-8",
    )

    result = run_tool(
        SESSION_CODE_EXECUTOR,
        py_file_path=str(script),
        session_id="unit-session",
    )

    assert result.success is True
    assert "hello from script" in result.stdout
    assert "21" in result.stdout
    assert result.stderr == ""
    assert result.error_message is None


def test_session_code_executor_handles_missing_file(tmp_path):
    missing = Path(tmp_path) / "missing.py"

    result = run_tool(
        SESSION_CODE_EXECUTOR,
        py_file_path=str(missing),
        session_id="unit-session",
    )

    assert result.success is False
    assert "No such file or directory" in result.stderr
    assert str(missing) in result.stderr
