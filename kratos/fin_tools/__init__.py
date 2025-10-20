"""
Public export surface for the yfinance-backed financial tools.

The module assembles handlers from category-specific files and exposes them as
LangChain tools whose names mirror the original Alpha Vantage endpoints.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Annotated, Optional
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool, InjectedToolArg

from kratos.tools import ALPHA_VANTAGE_SUBAGENTS

from .alpha_intelligence import HANDLERS as ALPHA_INTELLIGENCE_HANDLERS
from .commodities import HANDLERS as COMMODITY_HANDLERS
from .core import HANDLERS as CORE_HANDLERS
from .crypto import HANDLERS as CRYPTO_HANDLERS
from .economics import HANDLERS as ECONOMIC_HANDLERS
from .forex import HANDLERS as FOREX_HANDLERS
from .fundamentals import HANDLERS as FUNDAMENTAL_HANDLERS
from .options import HANDLERS as OPTIONS_HANDLERS
from .technical import HANDLERS as TECHNICAL_HANDLERS
from .base import ToolExecutionError


import json

HANDLER_TABLE: Dict[str, Callable[..., Dict[str, Any]]] = {}
for handler_set in (
    CORE_HANDLERS,
    OPTIONS_HANDLERS,
    ALPHA_INTELLIGENCE_HANDLERS,
    FUNDAMENTAL_HANDLERS,
    FOREX_HANDLERS,
    CRYPTO_HANDLERS,
    COMMODITY_HANDLERS,
    ECONOMIC_HANDLERS,
    TECHNICAL_HANDLERS,
):
    HANDLER_TABLE.update(handler_set)


def _build_tool_map() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for category in ALPHA_VANTAGE_SUBAGENTS:
        for tool_meta in category["tools"]:
            mapping[tool_meta["tool"]] = tool_meta["description"]
    return mapping


TOOL_DESCRIPTIONS = _build_tool_map()

# Ensure we have handlers for every declared tool
missing = sorted(set(TOOL_DESCRIPTIONS) - set(HANDLER_TABLE))
if missing:
    raise RuntimeError(f"No handlers registered for tools: {missing}")


def _error_payload(tool_name: str, message: str) -> Dict[str, Any]:
    return {"tool": tool_name, "success": False, "error": message}

def _is_payload_large(result: Dict[str,Any]) -> bool:
    if isinstance(result, dict):
        result.setdefault("tool", tool_name)
        result.setdefault("success", True)
        
        # Check for large payload
        threshold = 10000  # tokens
        json_str = json.dumps(result)
        estimated_tokens = len(json_str) // 4  # Rough estimate; refine as needed
        
        if estimated_tokens > threshold:
            return True
            # Optionally, clear heavy fields here if you want to return a slim version
            # e.g., if "data" in result and isinstance(result["data"], (list, dict)):
            #     result["data"] = None  # or {"offloaded": True}
        else:
            return False
        
def _execute(tool_name: str, **kwargs: Any) -> Dict[str, Any]:
    handler = HANDLER_TABLE.get(tool_name)
    if handler is None:
        return _error_payload(tool_name, f"No handler registered for tool {tool_name}.")
    try:
        print(kwargs["runtime"])
        result = handler(**kwargs)
        if(_is_payload_large(result=result)):
            print("Payload is super large..offload it")
            
    except ToolExecutionError as exc:
        return _error_payload(tool_name, str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        return _error_payload(tool_name, f"{tool_name} failed: {exc}")

    if isinstance(result, dict):
        result.setdefault("tool", tool_name)
        result.setdefault("success", True)
        return result

    return {"tool": tool_name, "success": True, "data": result}


def _get_tool_input_schema(tool_name: str) -> BaseModel:
    """Create appropriate input schema for each tool based on its expected parameters."""

    class BaseInput(BaseModel):
        runtime: Annotated[Optional[Any], InjectedToolArg()]
    
    # Define common schemas
    class SymbolInput(BaseInput):
        symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, PTON, UBER)")
    
    class SymbolWithPeriodInput(BaseInput):
        symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, PTON, UBER)")
        period: str = Field(default="1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
        interval: str = Field(default="1d", description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
    
    class ForexInput(BaseInput):
        from_symbol: str = Field(description="From currency symbol (e.g., USD)")
        to_symbol: str = Field(description="To currency symbol (e.g., EUR)")
    
    class CryptoInput(BaseInput):
        symbol: str = Field(description="Cryptocurrency symbol (e.g., BTC)")
        market: str = Field(default="USD", description="Market currency (e.g., USD)")
    
    class KeywordsInput(BaseInput):
        keywords: str = Field(description="Search keywords")
    
    class BulkQuotesInput(BaseInput):
        symbols: List[str] = Field(description="List of stock symbols")
    
    class OptionsInput(BaseInput):
        symbol: str = Field(description="Stock ticker symbol for options (e.g., AAPL, PTON, UBER)")
        expiration: str = Field(default=None, description="Option expiration date (YYYY-MM-DD format)")
    
    class HistoricalOptionsInput(BaseInput):
        contract_symbol: str = Field(description="Option contract symbol (e.g., AAPL240119C00150000)")
        start: str = Field(default=None, description="Start date (YYYY-MM-DD)")
        end: str = Field(default=None, description="End date (YYYY-MM-DD)")
        interval: str = Field(default="1d", description="Data interval")
    
    class EmptyInput(BaseInput):
        pass
    
    # Map tools to their input schemas
    if tool_name in ["GLOBAL_QUOTE", "COMPANY_OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", 
                     "CASH_FLOW", "EARNINGS", "NEWS_SENTIMENT", "INSIDER_TRANSACTIONS", 
                     "ANALYTICS_FIXED_WINDOW", "ANALYTICS_SLIDING_WINDOW"]:
        return SymbolInput
    elif tool_name.startswith("TIME_SERIES_") or tool_name in ["SMA", "EMA", "RSI", "MACD", "BBANDS", "STOCH", "STOCHF", "STOCHRSI", "WILLR", "ADX", "ADXR", "APO", "PPO", "MOM", "BOP", "CCI", "CMO", "ROC", "ROCR", "AROON", "AROONOSC", "MFI", "TRIX", "ULTOSC", "DX", "MINUS_DI", "PLUS_DI", "MINUS_DM", "PLUS_DM", "MIDPOINT", "MIDPRICE", "SAR", "TRANGE", "ATR", "NATR", "AD", "ADOSC", "OBV", "WMA", "DEMA", "TEMA", "TRIMA", "KAMA", "MAMA", "VWAP", "T3", "MACDEXT"] or tool_name.startswith("HT_"):
        return SymbolWithPeriodInput
    elif tool_name.startswith("FX_"):
        return ForexInput
    elif tool_name.startswith("DIGITAL_CURRENCY_") or tool_name == "CURRENCY_EXCHANGE_RATE":
        return CryptoInput
    elif tool_name == "SYMBOL_SEARCH":
        return KeywordsInput
    elif tool_name == "REALTIME_BULK_QUOTES":
        return BulkQuotesInput
    elif tool_name == "REALTIME_OPTIONS":
        return OptionsInput
    elif tool_name == "HISTORICAL_OPTIONS":
        return HistoricalOptionsInput
    elif tool_name == "TOP_GAINERS_LOSERS":
        return EmptyInput
    else:
        return EmptyInput


def _build_tool(tool_name: str, description: str):
    """Build a StructuredTool with proper input schema."""
    input_schema = _get_tool_input_schema(tool_name)
    
    def _dynamic_tool(**kwargs: Any) -> Dict[str, Any]:
        """Dynamic tool wrapper."""
        return _execute(tool_name, **kwargs)
    
    return StructuredTool.from_function(
        func=_dynamic_tool,
        name=tool_name,
        description=description,
        args_schema=input_schema
    )


TOOLS: List[Any] = []
globals_dict = globals()
for tool_name, description in TOOL_DESCRIPTIONS.items():
    tool_obj = _build_tool(tool_name, description)
    globals_dict[tool_name] = tool_obj
    TOOLS.append(tool_obj)


__all__ = [tool.name for tool in TOOLS] + ["TOOLS", "ToolExecutionError"]
