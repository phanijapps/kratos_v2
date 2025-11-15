"""Middleware for providing filesystem tools to an agent."""
# ruff: noqa: E501
from typing import  TypedDict, Optional, Any
from pathlib import Path

from deepagents.backends import FilesystemBackend, CompositeBackend
from deepagents.backends.sandbox import SandboxBackendProtocol
from deepagents.middleware import FilesystemMiddleware
from langchain.messages import AIMessage

from kratos.core.get_ticker import get_ticker


def merge_if_not_exists(x: Optional[str], y: Optional[str]) -> Optional[str]:
    """Reducer for un: keeps existing if set, otherwise takes new."""
    if x is not None:
        return x
    return y

class KratosFileBackend(FilesystemBackend, SandboxBackendProtocol):

    def set_new_working_dir(self, root_dir):
        self.cwd = Path(root_dir).resolve() if root_dir else Path.cwd()


class KratosCompositeBackend(CompositeBackend):

    def __init__(self, *args, **kwargs):
        # Call parent constructor FIRST
        self.is_initialized = False
        super().__init__(*args, **kwargs)

    def add_routes(self, routes: dict[str, str] = None):
        if routes is None:
            return
        print(f"Adding Routes {self.default}")
        for key, value in routes.items():
            print(f"Key {key} Value {value}")
            self.routes[key] = FilesystemBackend(root_dir = value, virtual_mode=True)
    
    def set_backend_initialized(self):
        self.is_initialized = True

    def is_initialized(self):
        
        if self.is_initialized == None: 
            return False
        else:
            return self.is_initialized

    def set_default(self, default_path: str):
        self.default = FilesystemBackend(root_dir=default_path, virtual_mode=True)
            


class ContextPath(TypedDict):
    """Path configuration for Kratos context management."""
    relative_path: str
    absolute_path: str
    description: str


class KratosFilesystemMiddleware(FilesystemMiddleware):

    def __init__(self, *args, **kwargs):
        # Call parent constructor FIRST
        super().__init__(*args, **kwargs)
        # Your additional initialization (if any)
        self.ticker_found = False
    
    async def abefore_agent(self, state, runtime):
        # Implementation to create context locations based on the state and runtime
        # This is a placeholder for the actual logic
        updates: dict[str, Any] = {}


        workspace_dir_value = state.get("workspace_dir", "./.vault")
        workspace_dir = Path(workspace_dir_value).resolve()
        updates["workspace_dir"] = str(workspace_dir)

        if not self.backend.is_initialized(): 
            ## Need to get the first Human message
            prompt = state["messages"][0].content
            print(prompt)
            ticker = get_ticker(prompt)
            print(f"Ticker {ticker}")

            # Skip 
            if not ticker.found:
                return {
                    "messages": [AIMessage(ticker.reason)],
                    "jump_to": "end"
                }
            else:
                # set paths
                print(f"Ticker Found {ticker}")

                abs_workspace = workspace_dir / "sessions"/ ticker.ticker
                abs_workspace.mkdir(exist_ok=True)
                print(f"Absolute workspace {abs_workspace}")

                self.backend.set_default(str(abs_workspace))

                code_path = abs_workspace / "code"
                reports_path = abs_workspace / "reports"
                data_path = abs_workspace / "data"
                charts_path = abs_workspace / "charts"

                code_path.mkdir(exist_ok=True)
                reports_path.mkdir(exist_ok=True)
                data_path.mkdir(exist_ok=True)
                charts_path.mkdir(exist_ok=True)

                self.backend.set_backend_initialized()

                

                self.backend.add_routes(
                    routes ={
                       f"/sessions/{ticker.ticker}/code/" : str(code_path),
                       f"/sessions/{ticker.ticker}/reports/" : str(reports_path),
                       f"/sessions/{ticker.ticker}/data/" : str(data_path),
                       f"/sessions/{ticker.ticker}/charts/" : str(charts_path)
                    }
                )
                updates["ticker"] = ticker.ticker
                updates["abs_workspace"] = abs_workspace 
                updates["workspace"] = str(workspace_dir)
                # Set up Session Paths.


                updates["session"] = [
                    {"relative_path":f"/sessions/{ticker.ticker}/code/" , "absolute_path": str(code_path), "description": "Source code files"},
                    {"relative_path": f"/sessions/{ticker.ticker}/reports/", "absolute_path": str(reports_path), "description": "Generated reports"},
                    {"relative_path": f"/sessions/{ticker.ticker}/data/", "absolute_path": str(data_path), "description": "Data files"},
                    {
                        "relative_path": f"/sessions/{ticker.ticker}/charts/", "absolute_path": str(charts_path), "description": "Charts files"
                    }
                ]
                self.ticker_found = True

                return updates
        return None
