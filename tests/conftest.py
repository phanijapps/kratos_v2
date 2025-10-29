import sys
import types


def _ensure_module(name: str) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        sys.modules[name] = module
    return module


try:  # pragma: no cover - only exercised when dependency exists
    import langchain_core.tools  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    langchain_core = _ensure_module("langchain_core")

    class _SimpleTool:
        def __init__(self, func, name: str | None = None):
            self.func = func
            self.name = name or getattr(func, "__name__", "tool")

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def invoke(self, input_data):
            if isinstance(input_data, dict):
                return self.func(**input_data)
            return self.func(input_data)

        def run(self, *args, **kwargs):
            if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
                return self.invoke(args[0])
            return self.func(*args, **kwargs)

    def tool(func=None, *, name: str | None = None, args_schema=None, return_direct=None):
        def decorator(fn):
            return _SimpleTool(fn, name=name)

        if func is None:
            return decorator
        return decorator(func)

    class InjectedToolArg:  # Minimal placeholder used only for typing
        def __init__(self, *_, **__):
            pass

    tools_mod = types.ModuleType("langchain_core.tools")
    tools_mod.tool = tool
    tools_mod.InjectedToolArg = InjectedToolArg
    sys.modules["langchain_core.tools"] = tools_mod
    setattr(langchain_core, "tools", tools_mod)

try:  # pragma: no cover
    import langchain_core.messages  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    messages_mod = types.ModuleType("langchain_core.messages")

    class ToolMessage:  # noqa: D401 - simple placeholder
        """Placeholder for langchain_core.messages.ToolMessage."""

    messages_mod.ToolMessage = ToolMessage
    sys.modules["langchain_core.messages"] = messages_mod

try:  # pragma: no cover
    import langchain.agents.middleware.types  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    langchain_mod = _ensure_module("langchain")
    agents_mod = _ensure_module("langchain.agents")
    middleware_mod = _ensure_module("langchain.agents.middleware")
    types_mod = types.ModuleType("langchain.agents.middleware.types")

    class AgentState(dict):
        """Lightweight AgentState stub used in tests."""

    class AgentMiddleware:  # noqa: D401
        """Placeholder AgentMiddleware base class."""

    class ModelRequest:
        def __init__(self, system_prompt: str | None = None):
            self.system_prompt = system_prompt

    class ModelResponse(dict):
        """Simple dictionary-backed response."""

    types_mod.AgentState = AgentState
    types_mod.AgentMiddleware = AgentMiddleware
    types_mod.ModelRequest = ModelRequest
    types_mod.ModelResponse = ModelResponse
    sys.modules["langchain.agents.middleware.types"] = types_mod
    setattr(middleware_mod, "types", types_mod)
    setattr(agents_mod, "middleware", middleware_mod)
    setattr(langchain_mod, "agents", agents_mod)

try:  # pragma: no cover
    import langchain.tools  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    langchain_tools_mod = types.ModuleType("langchain.tools")

    class ToolRuntime:  # noqa: D401
        """Placeholder ToolRuntime."""

    langchain_tools_mod.ToolRuntime = ToolRuntime
    sys.modules["langchain.tools"] = langchain_tools_mod

try:  # pragma: no cover
    import langchain.tools.tool_node  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    tool_node_mod = types.ModuleType("langchain.tools.tool_node")

    class ToolCallRequest:  # noqa: D401
        """Placeholder ToolCallRequest."""

    tool_node_mod.ToolCallRequest = ToolCallRequest
    sys.modules["langchain.tools.tool_node"] = tool_node_mod

try:  # pragma: no cover
    import langgraph.types  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    langgraph_mod = _ensure_module("langgraph")
    types_mod = types.ModuleType("langgraph.types")

    class Command:  # noqa: D401
        """Placeholder Command type."""

    types_mod.Command = Command
    sys.modules["langgraph.types"] = types_mod
    setattr(langgraph_mod, "types", types_mod)
