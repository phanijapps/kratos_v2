from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RenderRMarkdownArgs(BaseModel):
    """Input schema for rendering RMarkdown documents into PDF reports."""

    rmd_file_name: str = Field(
        description="RMarkdown file to render. Example: 'analysis.Rmd'"
    )
    code_path: str = Field(
        description="Absolute path to the folder containing the RMarkdown file. "
        "Example: '.vault/sessions/343432.34324/code'"
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional output directory for the generated PDF. "
        "Defaults to the provided code_path.",
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Optional output filename (with .pdf extension). Defaults to the "
        "RMarkdown filename with a .pdf suffix.",
    )


@dataclass
class RMarkdownExecutionResponse:
    """Result container for RMarkdown render executions."""

    success: bool
    stdout: str
    stderr: str
    return_value: Any = None
    charts: List[Dict[str, str]] = dataclass_field(default_factory=list)
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    duration_seconds: float = 0.0


def _as_r_string(value: str) -> str:
    """Return a string literal safe for use within an R expression."""
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


@tool(
    description="Render RMarkdown documents to PDF using the system Rscript executable.",
    args_schema=RenderRMarkdownArgs,
    return_direct=False,
)
def rmarkdown_pdf_executor(
    rmd_file_name: str,
    code_path: str,
    output_dir: Optional[str] = None,
    output_file: Optional[str] = None,
) -> RMarkdownExecutionResponse:
    """Render an RMarkdown document to a PDF file using ``rmarkdown::render``.

    The tool invokes the system ``Rscript`` binary with a short expression that
    loads and renders the supplied RMarkdown document. Outputs and errors from
    the R process are captured and returned alongside metadata describing the
    run.
    """

    start_time = time.time()

    input_dir = os.path.abspath(code_path)
    input_path = os.path.join(input_dir, rmd_file_name)

    if not os.path.isfile(input_path):
        duration = time.time() - start_time
        message = f"RMarkdown file not found: {input_path}"
        return RMarkdownExecutionResponse(
            success=False,
            stdout="",
            stderr=message,
            error_message=message,
            traceback=message,
            duration_seconds=duration,
        )

    resolved_output_dir = os.path.abspath(output_dir) if output_dir else input_dir
    Path(resolved_output_dir).mkdir(parents=True, exist_ok=True)

    default_output_name = Path(rmd_file_name).with_suffix(".pdf").name
    output_name = output_file or default_output_name

    output_path = os.path.join(resolved_output_dir, output_name)

    render_expression = (
        "rmarkdown::render("
        f"input = {_as_r_string(input_path)}, "
        f"output_file = {_as_r_string(output_name)}, "
        f"output_dir = {_as_r_string(resolved_output_dir)}, "
        "output_format = 'pdf_document', "
        "clean = TRUE"
        ")"
    )

    try:
        result = subprocess.run(
            ["Rscript", "-e", render_expression],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            cwd=input_dir,
        )

        duration = time.time() - start_time
        success = result.returncode == 0 and os.path.exists(output_path)

        error_message = None
        traceback = None
        if not success:
            default_error = "RMarkdown rendering failed. Check stderr for details."
            error_message = default_error
            traceback = result.stderr or default_error

        return RMarkdownExecutionResponse(
            success=success,
            stdout=result.stdout,
            stderr=result.stderr,
            output_path=output_path if success else None,
            error_message=error_message,
            traceback=traceback,
            duration_seconds=duration,
        )

    except subprocess.TimeoutExpired as exc:
        duration = time.time() - start_time
        stderr_output = getattr(exc, "stderr", "") or ""
        stdout_output = getattr(exc, "stdout", "") or ""
        return RMarkdownExecutionResponse(
            success=False,
            stdout=stdout_output,
            stderr=stderr_output,
            error_message="RMarkdown rendering timed out after 120 seconds.",
            traceback=str(exc),
            duration_seconds=duration,
        )

    except FileNotFoundError:
        duration = time.time() - start_time
        message = (
            "Rscript executable not found. Ensure R is installed and Rscript is "
            "available on the system PATH."
        )
        return RMarkdownExecutionResponse(
            success=False,
            stdout="",
            stderr=message,
            error_message=message,
            traceback=message,
            duration_seconds=duration,
        )

    except Exception as exc:  # pragma: no cover - defensive
        duration = time.time() - start_time
        message = f"Unexpected failure during RMarkdown rendering: {exc}"
        return RMarkdownExecutionResponse(
            success=False,
            stdout="",
            stderr=message,
            error_message=message,
            traceback=str(exc),
            duration_seconds=duration,
        )


RMARKDOWN_PDF_EXECUTOR = rmarkdown_pdf_executor

TOOLS = [rmarkdown_pdf_executor]
