"""
Handlers for options data tools.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base import ToolExecutionError, ensure_symbol, format_response, get_ticker, download, ttl_cache


@ttl_cache(ttl=300, maxsize=256)
def _cached_option_chain(symbol: str, expiration: str) -> Dict[str, Any]:
    ticker = get_ticker(symbol)
    chain = ticker.option_chain(expiration)
    return {"calls": chain.calls, "puts": chain.puts}


def realtime_options(symbol: str, *, expiration: Optional[str] = None) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    ticker = get_ticker(symbol)
    try:
        expirations = ticker.options
    except Exception as exc:
        return format_response(
            "REALTIME_OPTIONS",
            symbol=symbol,
            error="options_unavailable",
            message=f"Unable to fetch option expirations for {symbol}: {exc}",
            suggestion="This symbol may not have options available, or there may be a temporary issue with the options data service."
        )
    
    if not expirations:
        return format_response(
            "REALTIME_OPTIONS",
            symbol=symbol,
            error="no_options",
            message=f"No option expirations available for {symbol}.",
            suggestion="This symbol may not have options trading, or options may not be available at this time."
        )
    
    target = expiration or expirations[0]
    if target not in expirations:
        return format_response(
            "REALTIME_OPTIONS",
            symbol=symbol,
            error="invalid_expiration",
            message=f"Expiration {target} is not available.",
            available_expirations=list(expirations),
            suggestion=f"Use one of the available expiration dates: {', '.join(expirations[:5])}{'...' if len(expirations) > 5 else ''}",
            recommended_expiration=expirations[0]  # Suggest the nearest expiration
        )
    
    try:
        chain_data = _cached_option_chain(symbol, target)
    except Exception as exc:
        return format_response(
            "REALTIME_OPTIONS",
            symbol=symbol,
            expiration=target,
            error="chain_fetch_failed",
            message=f"Failed to fetch option chain for {symbol} @ {target}: {exc}",
            available_expirations=list(expirations),
            suggestion="Try a different expiration date or retry later if this is a temporary issue."
        )
    
    return format_response("REALTIME_OPTIONS", symbol=symbol, expiration=target, calls=chain_data["calls"], puts=chain_data["puts"])


@ttl_cache(ttl=600, maxsize=256)
def _cached_option_history(contract_symbol: str, start: Optional[str], end: Optional[str], interval: str) -> Dict[str, Any]:
    data = download(
        [contract_symbol],
        start=start,
        end=end,
        period=None,
        interval=interval,
    )
    return {"data": data}


def historical_options(contract_symbol: str, *, start: Optional[str] = None, end: Optional[str] = None, interval: str = "1d") -> Dict[str, Any]:
    contract_symbol = ensure_symbol(contract_symbol)
    payload = _cached_option_history(contract_symbol, start, end, interval)
    return format_response(
        "HISTORICAL_OPTIONS",
        contract_symbol=contract_symbol,
        interval=interval,
        start=start,
        end=end,
        data=payload["data"],
    )


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "REALTIME_OPTIONS": lambda **kwargs: realtime_options(kwargs["symbol"], expiration=kwargs.get("expiration")),
    "HISTORICAL_OPTIONS": lambda **kwargs: historical_options(
        kwargs["contract_symbol"],
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        interval=kwargs.get("interval", "1d"),
    ),
}


__all__ = ["HANDLERS"]
