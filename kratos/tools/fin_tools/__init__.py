"""
Legacy wrapper for financial tools.

The consolidated registry now lives in ``kratos.tools``. This module stays in
place so existing imports of ``kratos.tools.fin_tools`` continue to resolve
without duplicating the registry logic.
"""

from .base import ToolExecutionError

__all__ = ["ToolExecutionError"]
