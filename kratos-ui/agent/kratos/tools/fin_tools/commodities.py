"""
Handlers for commodity market tools.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .base import format_response, history

_COMMODITY_SYMBOLS = {
    "WTI": "CL=F",
    "BRENT": "BZ=F",
    "NATURAL_GAS": "NG=F",
    "COPPER": "HG=F",
    "ALUMINUM": "ALI=F",
    "WHEAT": "ZW=F",
    "CORN": "ZC=F",
    "COTTON": "CT=F",
    "SUGAR": "SB=F",
    "COFFEE": "KC=F",
    "ALL_COMMODITIES": "PALLFNFINDEXM",
}


def commodity(tool_name: str, *, period: str = "6mo", interval: str = "1d") -> Dict[str, Any]:
    symbol = _COMMODITY_SYMBOLS[tool_name]
    data = history(
        symbol,
        interval=interval,
        period=period,
        auto_adjust=False,
        include_actions=False,
    )
    return format_response(tool_name, symbol=symbol, data=data)


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    name: (lambda tool=name: (lambda **kwargs: commodity(tool, period=kwargs.get("period", "6mo"), interval=kwargs.get("interval", "1d"))))()
    for name in _COMMODITY_SYMBOLS
}


__all__ = ["HANDLERS"]
