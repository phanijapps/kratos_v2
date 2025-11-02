"""
Handlers for economic indicator tools backed by FRED series on Yahoo Finance.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .base import format_response, history

_ECONOMIC_TICKERS = {
    "REAL_GDP": "GDPC1",
    "REAL_GDP_PER_CAPITA": "A939RX0Q048SBEA",
    "TREASURY_YIELD": "^TNX",
    "FEDERAL_FUNDS_RATE": "FEDFUNDS",
    "CPI": "CPIAUCSL",
    "INFLATION": "T10YIE",
    "RETAIL_SALES": "RSAFS",
    "DURABLES": "DGORDER",
    "UNEMPLOYMENT": "UNRATE",
    "NONFARM_PAYROLL": "PAYEMS",
}


def economic_indicator(tool_name: str, *, period: str = "10y", interval: str = "1mo") -> Dict[str, Any]:
    symbol = _ECONOMIC_TICKERS[tool_name]
    data = history(
        symbol,
        interval=interval,
        period=period,
        auto_adjust=False,
        include_actions=False,
    )
    return format_response(tool_name, symbol=symbol, data=data)


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    name: (lambda tool=name: (lambda **kwargs: economic_indicator(tool, period=kwargs.get("period", "10y"), interval=kwargs.get("interval", "1mo"))))()
    for name in _ECONOMIC_TICKERS
}


__all__ = ["HANDLERS"]

