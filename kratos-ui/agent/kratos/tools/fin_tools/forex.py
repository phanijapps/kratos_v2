"""
Handlers for foreign exchange tools.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base import ToolExecutionError, ensure_symbol, format_response, get_ticker, history, ttl_cache


def _fx_pair(from_symbol: str, to_symbol: str) -> str:
    return f"{ensure_symbol(from_symbol)}{ensure_symbol(to_symbol)}=X"


def fx_history(
    tool_name: str,
    *,
    from_symbol: str,
    to_symbol: str,
    interval: str,
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Dict[str, Any]:
    pair = _fx_pair(from_symbol, to_symbol)
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
        from_symbol=ensure_symbol(from_symbol),
        to_symbol=ensure_symbol(to_symbol),
        data=data,
    )


@ttl_cache(ttl=120, maxsize=256)
def _cached_fx_rate(pair: str) -> Dict[str, Any]:
    ticker = get_ticker(pair)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception:
        fast_info = {}
    recent = history(pair, interval="1d", period="5d", auto_adjust=False, include_actions=False)
    return {"rate": fast_info.get("last_price"), "recent": recent}


def currency_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    pair = _fx_pair(from_currency, to_currency)
    payload = _cached_fx_rate(pair)
    return format_response("CURRENCY_EXCHANGE_RATE", pair=pair, rate=payload["rate"], recent=payload["recent"])


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "FX_INTRADAY": lambda **kwargs: fx_history(
        "FX_INTRADAY",
        from_symbol=kwargs["from_symbol"],
        to_symbol=kwargs["to_symbol"],
        interval=kwargs.get("interval", "1h"),
        period=kwargs.get("period", "7d"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "FX_DAILY": lambda **kwargs: fx_history(
        "FX_DAILY",
        from_symbol=kwargs["from_symbol"],
        to_symbol=kwargs["to_symbol"],
        interval="1d",
        period=kwargs.get("period", "1y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "FX_WEEKLY": lambda **kwargs: fx_history(
        "FX_WEEKLY",
        from_symbol=kwargs["from_symbol"],
        to_symbol=kwargs["to_symbol"],
        interval="1wk",
        period=kwargs.get("period", "5y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "FX_MONTHLY": lambda **kwargs: fx_history(
        "FX_MONTHLY",
        from_symbol=kwargs["from_symbol"],
        to_symbol=kwargs["to_symbol"],
        interval="1mo",
        period=kwargs.get("period", "10y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
    ),
    "CURRENCY_EXCHANGE_RATE": lambda **kwargs: currency_exchange_rate(kwargs["from_currency"], kwargs["to_currency"]),
}


__all__ = ["HANDLERS"]
