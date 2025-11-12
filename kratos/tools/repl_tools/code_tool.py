from langchain_core.tools import tool

from pydantic import BaseModel, Field
from dataclasses import dataclass, field as dataclass_field
from typing import Any, List, Dict, Optional
import subprocess
import time
import sys


# Define Pydantic schema for tool arguments
class ExecuteFileArgs(BaseModel):
    """Input schema for executing Python files."""
    
    py_file_name: str = Field(
        description="Python analysis file to execute Example: 'script.py' or 'analysis.py'"
    )
    code_path: str = Field(
        description="Abosolute path of code location Example '.vault/sessions/343432.34324/code'"
    )


# Define response dataclass
@dataclass
class ExecutionResponse:
    """Result container for a sandboxed execution."""
    
    success: bool
    stdout: str
    stderr: str
    return_value: Any = None
    charts: List[Dict[str, str]] = dataclass_field(default_factory=list)
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    duration_seconds: float = 0.0


# Define the tool
@tool(
    description="Session Code excecutor is used to run python code that is generated as part of agent execution",
    args_schema=ExecuteFileArgs,
    return_direct=False,
)
def session_code_executor(py_file_name: str, 
                          code_path: str) -> ExecutionResponse:
    """Execute a Python file in an isolated subprocess and capture comprehensive execution results.
    
    This tool runs Python scripts safely by executing them in separate processes with timeout protection.
    It captures stdout, stderr, execution duration, and error information. Use this when you need to:
    - Run generated Python scripts from the current session
    - Execute data analysis or processing scripts
    - Test code in isolation without affecting the main process
    - Capture and analyze script output and errors
    
    Args:
        py_file_name: Name of the file to execute (e.g., 'generated_script.py')
        code_path: Path where code is generated (e.g. './vault/session/32234324/code)
    
    Returns:
        ExecutionResponse object containing success status, outputs, errors, and execution metrics
    
    Example:
        result = execute_file(
            py_file_path="data_analysis.py",
            session_id="./vault/session/32234324/code"
        )
        if result.success:
            print(f"Output: {result.stdout}")
        else:
            print(f"Error: {result.error_message}")
    """
    # Only save if payload is large AND session_id is available
    
    py_file_path = f"{code_path}/{py_file_name}"
    print(f"Trying to Execute {py_file_path}")
    print(f"Using Python interpreter: {sys.executable}")

    start_time = time.time()
    
    try:
        # Run the Python file as a subprocess with timeout
        result = subprocess.run(
            ['python', py_file_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        return ExecutionResponse(
            success=success,
            stdout=result.stdout,
            stderr=result.stderr,
            return_value=None,
            charts=[],
            error_message=result.stderr if not success else None,
            traceback=result.stderr if not success else None,
            duration_seconds=duration
        )
        
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start_time
        return ExecutionResponse(
            success=False,
            stdout=e.stdout.decode() if e.stdout else "",
            stderr=e.stderr.decode() if e.stderr else "",
            error_message="Execution timed out after 30 seconds",
            traceback=str(e),
            duration_seconds=duration
        )
        
    except FileNotFoundError as e:
        duration = time.time() - start_time
        return ExecutionResponse(
            success=False,
            stdout="",
            stderr=str(e),
            error_message=f"File not found: {py_file_path}",
            traceback=str(e),
            duration_seconds=duration
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return ExecutionResponse(
            success=False,
            stdout="",
            stderr=str(e),
            error_message=f"Execution failed: {str(e)}",
            traceback=str(e),
            duration_seconds=duration
        )

SESSION_CODE_EXECUTOR = session_code_executor

TOOLS = [session_code_executor]
