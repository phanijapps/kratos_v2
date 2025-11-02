import asyncio
from types import SimpleNamespace

from kratos.core.middleware.vault_middleware import ContextVaultMiddleware


class DummyRuntime:
    def __init__(self, state):
        self.state = state


def create_middleware(tmp_path, **overrides):
    return ContextVaultMiddleware(
        workspace_dir=str(tmp_path),
        use_sqlite=False,
        enable_logging=False,
        **overrides,
    )


def test_before_agent_initializes_missing_state(tmp_path):
    middleware = create_middleware(tmp_path)
    state = {}

    updates = middleware.before_agent(state, runtime=None)

    assert updates is not None
    assert updates["namespace"] == middleware.default_namespace
    assert isinstance(updates["session_id"], str)
    assert updates["files_created"] == 0
    assert updates["files_read"] == 0
    assert updates["total_bytes_written"] == 0


def test_before_agent_returns_none_when_state_populated(tmp_path):
    middleware = create_middleware(tmp_path)
    state = {
        "namespace": "custom",
        "session_id": "abc",
        "files_created": 1,
        "files_read": 2,
        "total_bytes_written": 10,
    }

    updates = middleware.before_agent(state, runtime=None)

    assert updates is None


def test_wrap_model_call_appends_system_prompt(tmp_path):
    middleware = create_middleware(tmp_path)
    request = SimpleNamespace(system_prompt="Base prompt")

    captured = {}

    def handler(req):
        captured["prompt"] = req.system_prompt
        return "handled"

    result = middleware.wrap_model_call(request, handler)

    assert result == "handled"
    assert captured["prompt"].startswith("Base prompt")
    assert "FileVault" in captured["prompt"]


def test_awrap_model_call_injects_prompt(tmp_path):
    middleware = create_middleware(tmp_path)
    request = SimpleNamespace(system_prompt=None)

    async def handler(req):
        return req.system_prompt

    result = asyncio.run(middleware.awrap_model_call(request, handler))

    assert isinstance(result, str)
    assert result.startswith("## FileVault")
