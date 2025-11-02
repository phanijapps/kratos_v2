"""
Handlers for digital currency tools.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base import ensure_symbol, format_response, history


def _crypto_pair(symbol: str, market: str) -> str:
    return f"{ensure_symbol(symbol)}-{ensure_symbol(market)}"


def digital_currency_history(
    tool_name: str,
    *,
    symbol: str,
    market: str = "USD",
    interval: str = "1d",
    period: Optional[str] = "90d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Dict[str, Any]:
    pair = _crypto_pair(symbol, market)
    data = history(
        pair,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=False,
        include_actions=False,
    )
    return format_response(
        tool_name,
        symbol=ensure_symbol(symbol),
        market=ensure_symbol(market),
        data=data,
    )


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "DIGITAL_CURRENCY_INTRADAY": lambda **kwargs: digital_currency_history(
        "DIGITAL_CURRENCY_INTRADAY",
        symbol=kwargs["symbol"],
        market=kwargs.get("market", "USD"),
        interval=kwargs.get("interval", "1h"),
        period=kwargs.get("period", "7d"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "DIGITAL_CURRENCY_DAILY": lambda **kwargs: digital_currency_history(
        "DIGITAL_CURRENCY_DAILY",
        symbol=kwargs["symbol"],
        market=kwargs.get("market", "USD"),
        interval="1d",
        period=kwargs.get("period", "180d"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "DIGITAL_CURRENCY_WEEKLY": lambda **kwargs: digital_currency_history(
        "DIGITAL_CURRENCY_WEEKLY",
        symbol=kwargs["symbol"],
        market=kwargs.get("market", "USD"),
        interval="1wk",
        period=kwargs.get("period", "2y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "DIGITAL_CURRENCY_MONTHLY": lambda **kwargs: digital_currency_history(
        "DIGITAL_CURRENCY_MONTHLY",
        symbol=kwargs["symbol"],
        market=kwargs.get("market", "USD"),
        interval="1mo",
        period=kwargs.get("period", "5y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
}


__all__ = ["HANDLERS"]
