"""
Handlers for core stock market data tools.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Callable, Dict, Iterable, Optional

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_json,
    get_ticker,
    history,
    ttl_cache,
)


def _time_series(
    tool_name: str,
    *,
    symbol: str,
    interval: str,
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    adjusted: bool = True,
) -> Dict[str, Any]:
    data = history(
        symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=adjusted,
        include_actions=True,
    )
    return format_response(
        tool_name,
        symbol=ensure_symbol(symbol),
        interval=interval,
        period=period,
        start=start,
        end=end,
        adjusted=adjusted,
        data=data,
    )


@ttl_cache(ttl=60, maxsize=256)
def _cached_quote(symbol: str) -> Dict[str, Any]:
    ticker = get_ticker(symbol)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception:
        fast_info = {}
    latest = history(symbol, interval="1d", period="5d", auto_adjust=False)
    quote = {
        "symbol": symbol,
        "price": fast_info.get("last_price"),
        "currency": fast_info.get("currency"),
        "previous_close": fast_info.get("previous_close"),
        "regular_market_change": fast_info.get("regular_market_change"),
        "regular_market_change_percent": fast_info.get("regular_market_change_percent"),
        "regular_market_time": fast_info.get("regular_market_time"),
    }
    return {"quote": quote, "latest": latest.tail(1)}


def global_quote(symbol: str) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    payload = _cached_quote(symbol)
    return format_response("GLOBAL_QUOTE", quote=payload["quote"], data=payload["latest"])


def realtime_bulk_quotes(symbols: Iterable[str]) -> Dict[str, Any]:
    symbols = list(symbols)
    if not symbols:
        raise ToolExecutionError("Provide at least one symbol for bulk quotes.")
    results = []
    for raw in symbols:
        symbol = ensure_symbol(raw)
        ticker = get_ticker(symbol)
        try:
            fast_info = dict(ticker.fast_info)
        except Exception:
            fast_info = {}
        results.append(
            {
                "symbol": symbol,
                "price": fast_info.get("last_price"),
                "currency": fast_info.get("currency"),
                "regular_market_change": fast_info.get("regular_market_change"),
                "regular_market_change_percent": fast_info.get("regular_market_change_percent"),
                "regular_market_time": fast_info.get("regular_market_time"),
            }
        )
    return format_response("REALTIME_BULK_QUOTES", quotes=results)


@ttl_cache(ttl=1800, maxsize=64)
def _cached_symbol_search(keywords: str, region: str, quotes_count: int) -> Dict[str, Any]:
    url = (
        f"https://query2.finance.yahoo.com/v1/finance/search?"
        f"q={keywords}&quotesCount={quotes_count}&newsCount=0&region={region}"
    )
    return get_json(url)


def symbol_search(keywords: str, *, region: str = "US", quotes_count: int = 10) -> Dict[str, Any]:
    query = keywords.strip()
    if not query:
        raise ToolExecutionError("A search query is required.")
    
    data = _cached_symbol_search(query, region.upper(), quotes_count)
    
    # Check if the response contains an error
    if isinstance(data, dict) and data.get("error"):
        return format_response(
            "SYMBOL_SEARCH",
            query=query,
            region=region.upper(),
            error=data.get("error"),
            message=data.get("message", "Symbol search temporarily unavailable"),
            suggestion="Try searching for a more specific symbol or company name, or try again later."
        )
    
    return format_response("SYMBOL_SEARCH", query=query, region=region.upper(), results=data.get("quotes", []))


def market_status(region: str = "US") -> Dict[str, Any]:
    region = region.upper()
    now_utc = _dt.datetime.utcnow()
    weekday = now_utc.weekday()
    is_weekend = weekday >= 5
    exchange_open = False
    if region == "US":
        eastern = _dt.timezone(_dt.timedelta(hours=-5))
        now_eastern = now_utc.astimezone(eastern)
        open_time = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
        close_time = now_eastern.replace(hour=16, minute=0, second=0, microsecond=0)
        exchange_open = open_time <= now_eastern <= close_time and not is_weekend
        hours = {"open": "09:30", "close": "16:00", "timezone": "America/New_York"}
    else:
        hours = {"open": None, "close": None, "timezone": "UTC"}
    status = {
        "region": region,
        "timestamp_utc": now_utc.isoformat(),
        "is_weekend": is_weekend,
        "is_open": exchange_open,
        "hours": hours,
        "note": "Status approximated using standard exchange hours; holidays not accounted for.",
    }
    return format_response("MARKET_STATUS", status=status)


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "TIME_SERIES_INTRADAY": lambda **kwargs: _time_series(
        "TIME_SERIES_INTRADAY",
        interval=kwargs.get("interval", "1h"),
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "7d"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=kwargs.get("adjusted", True),
    ),
    "TIME_SERIES_DAILY": lambda **kwargs: _time_series(
        "TIME_SERIES_DAILY",
        interval="1d",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "1y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=kwargs.get("adjusted", True),
    ),
    "TIME_SERIES_DAILY_ADJUSTED": lambda **kwargs: _time_series(
        "TIME_SERIES_DAILY_ADJUSTED",
        interval="1d",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "1y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=True,
    ),
    "TIME_SERIES_WEEKLY": lambda **kwargs: _time_series(
        "TIME_SERIES_WEEKLY",
        interval="1wk",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "5y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=kwargs.get("adjusted", True),
    ),
    "TIME_SERIES_WEEKLY_ADJUSTED": lambda **kwargs: _time_series(
        "TIME_SERIES_WEEKLY_ADJUSTED",
        interval="1wk",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "5y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=True,
    ),
    "TIME_SERIES_MONTHLY": lambda **kwargs: _time_series(
        "TIME_SERIES_MONTHLY",
        interval="1mo",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "10y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=kwargs.get("adjusted", True),
    ),
    "TIME_SERIES_MONTHLY_ADJUSTED": lambda **kwargs: _time_series(
        "TIME_SERIES_MONTHLY_ADJUSTED",
        interval="1mo",
        symbol=kwargs["symbol"],
        period=kwargs.get("period", "10y"),
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        adjusted=True,
    ),
    "GLOBAL_QUOTE": lambda **kwargs: global_quote(kwargs["symbol"]),
    "REALTIME_BULK_QUOTES": lambda **kwargs: realtime_bulk_quotes(kwargs.get("symbols", [])),
    "SYMBOL_SEARCH": lambda **kwargs: symbol_search(
        kwargs["keywords"],
        region=kwargs.get("region", "US"),
        quotes_count=kwargs.get("quotes_count", 10),
    ),
    "MARKET_STATUS": lambda **kwargs: market_status(kwargs.get("region", "US")),
}


__all__ = ["HANDLERS"]
