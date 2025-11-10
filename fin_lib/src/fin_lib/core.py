"""
Core stock market data tools.

This module provides essential stock market data functionality including:
- Real-time quotes and bulk quotes
- Historical price data (intraday, daily, weekly, monthly)
- Symbol search and market status
- Professional charting capabilities
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, Iterable, List, Optional, Union

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_json,
    get_ticker,
    history,
    ttl_cache,
    create_candlestick_chart,
    create_line_chart,
)


def get_quote(symbol: str) -> Dict[str, Any]:
    """
    Get real-time quote for a single symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        Dictionary containing quote data with current price, changes, and metadata
        
    Example:
        >>> quote = get_quote("AAPL")
        >>> print(f"Current price: ${quote['quote']['price']}")
    """
    try:
        symbol = ensure_symbol(symbol)
        payload = _cached_quote(symbol)
        return format_response("GLOBAL_QUOTE", quote=payload["quote"], data=payload["latest"])
    except ToolExecutionError as e:
        return format_response(
            "GLOBAL_QUOTE",
            error="symbol_not_found",
            message=str(e),
            suggestion="Please verify the symbol is correct and try again. Use search_symbols() to find valid symbols.",
            symbol=symbol if 'symbol' in locals() else None
        )


def get_historical_data(
    symbol: str,
    *,
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "1d",
    adjusted: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get historical price data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        adjusted: Whether to use adjusted prices
        include_chart: Whether to include a candlestick chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing historical data and optional chart
        
    Example:
        >>> data = get_historical_data("AAPL", period="1y", include_chart=True)
        >>> print(f"Retrieved {len(data['data'])} data points")
    """
    data = history(
        symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=adjusted,
        include_actions=True,
    )
    
    result = format_response(
        "TIME_SERIES_DAILY",
        symbol=ensure_symbol(symbol),
        interval=interval,
        period=period,
        start=start,
        end=end,
        adjusted=adjusted,
        data=data,
    )
    
    if include_chart and not data.empty:
        try:
            chart = create_candlestick_chart(
                data, symbol, 
                title=f"{symbol} Historical Prices",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_bulk_quotes(symbols: Iterable[str]) -> Dict[str, Any]:
    """
    Get real-time quotes for multiple symbols.
    
    Args:
        symbols: List of ticker symbols
        
    Returns:
        Dictionary containing quotes for all symbols
        
    Example:
        >>> quotes = get_bulk_quotes(["AAPL", "MSFT", "GOOGL"])
        >>> for quote in quotes['quotes']:
        ...     print(f"{quote['symbol']}: ${quote['price']}")
    """
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


def search_symbols(
    keywords: str, 
    *, 
    region: str = "US", 
    quotes_count: int = 10
) -> Dict[str, Any]:
    """
    Search for stock symbols by keywords.
    
    Args:
        keywords: Search terms (company name, symbol, etc.)
        region: Market region (US, CA, GB, etc.)
        quotes_count: Maximum number of results
        
    Returns:
        Dictionary containing search results
        
    Example:
        >>> results = search_symbols("apple")
        >>> for result in results['results']:
        ...     print(f"{result['symbol']}: {result['shortname']}")
    """
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


def get_market_status(region: str = "US") -> Dict[str, Any]:
    """
    Get current market status for a region.
    
    Args:
        region: Market region (US, CA, GB, etc.)
        
    Returns:
        Dictionary containing market status information
        
    Example:
        >>> status = get_market_status("US")
        >>> print(f"Market is {'open' if status['status']['is_open'] else 'closed'}")
    """
    region = region.upper()
    now_utc = _dt.datetime.now(_dt.timezone.utc)
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


def get_intraday_data(
    symbol: str,
    *,
    interval: str = "1h",
    period: str = "7d",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get intraday price data with optional charting.
    
    Args:
        symbol: Stock ticker symbol
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h)
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        include_chart: Whether to include a candlestick chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing intraday data and optional chart
    """
    data = history(
        symbol,
        interval=interval,
        period=period,
        auto_adjust=True,
        include_actions=True,
    )
    
    result = format_response(
        "TIME_SERIES_INTRADAY",
        symbol=ensure_symbol(symbol),
        interval=interval,
        period=period,
        data=data,
    )
    
    if include_chart and not data.empty:
        try:
            chart = create_candlestick_chart(
                data, symbol,
                title=f"{symbol} Intraday Prices ({interval})",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def compare_symbols(
    symbols: List[str],
    period: str = "1y",
    normalize: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Compare multiple symbols over a time period.
    
    Args:
        symbols: List of ticker symbols to compare
        period: Time period for comparison
        normalize: Whether to normalize prices to percentage changes
        include_chart: Whether to include a comparison chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing comparison data and optional chart
    """
    if len(symbols) < 2:
        raise ToolExecutionError("At least 2 symbols required for comparison.")
    
    comparison_data = {}
    for symbol in symbols:
        try:
            data = history(symbol, interval="1d", period=period)
            if normalize:
                # Normalize to percentage change from first value
                data = (data / data.iloc[0] - 1) * 100
            comparison_data[symbol] = data['Close']
        except Exception as e:
            comparison_data[symbol] = f"Error: {str(e)}"
    
    result = format_response(
        "SYMBOL_COMPARISON",
        symbols=symbols,
        period=period,
        normalized=normalize,
        data=comparison_data
    )
    
    if include_chart and comparison_data:
        try:
            import pandas as pd
            chart_data = pd.DataFrame({k: v for k, v in comparison_data.items() 
                                     if not isinstance(v, str)})
            if not chart_data.empty:
                title = f"Symbol Comparison ({period})"
                if normalize:
                    title += " - Normalized % Change"
                chart = create_line_chart(
                    chart_data, title,
                    y_label="Price" if not normalize else "% Change",
                    style=chart_style
                )
                result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


# Internal helper functions
@ttl_cache(ttl=60, maxsize=256)
def _cached_quote(symbol: str) -> Dict[str, Any]:
    """Get cached quote data for a symbol."""
    ticker = get_ticker(symbol)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception as exc:
        print(f"[get_quote] fast_info unavailable for {symbol}: {exc}")
        fast_info = {}

    def _fast(field: str, *aliases: str) -> Any:
        """Lookup helper that tries multiple key variants in fast_info."""
        for key in (field, *aliases):
            if key in fast_info:
                return fast_info[key]
        return None

    latest = history(symbol, interval="1d", period="5d", auto_adjust=False)
    latest_close = None
    if not latest.empty:
        try:
            latest_close = float(latest["Close"].iloc[-1])
        except Exception:
            latest_close = None

    quote = {
        "symbol": symbol,
        "price": _fast("last_price", "lastPrice", "regularMarketPrice") or latest_close,
        "currency": _fast("currency"),
        "previous_close": _fast("previous_close", "previousClose", "regularMarketPreviousClose"),
        "open": _fast("open"),
        "day_high": _fast("day_high", "dayHigh"),
        "day_low": _fast("day_low", "dayLow"),
        "last_volume": _fast("last_volume", "lastVolume"),
        "ten_day_average_volume": _fast("ten_day_average_volume", "tenDayAverageVolume"),
        "three_month_average_volume": _fast("three_month_average_volume", "threeMonthAverageVolume"),
        "market_cap": _fast("market_cap", "marketCap"),
        "shares": _fast("shares"),
        "fifty_day_average": _fast("fifty_day_average", "fiftyDayAverage"),
        "two_hundred_day_average": _fast("two_hundred_day_average", "twoHundredDayAverage"),
        "year_high": _fast("year_high", "yearHigh"),
        "year_low": _fast("year_low", "yearLow"),
        "year_change": _fast("year_change", "yearChange"),
        "timezone": _fast("timezone"),
    }
    return {"quote": quote, "latest": latest.tail(1)}


@ttl_cache(ttl=1800, maxsize=64)
def _cached_symbol_search(keywords: str, region: str, quotes_count: int) -> Dict[str, Any]:
    """Cached symbol search."""
    url = (
        f"https://query2.finance.yahoo.com/v1/finance/search?"
        f"q={keywords}&quotesCount={quotes_count}&newsCount=0&region={region}"
    )
    return get_json(url)


# Export main functions
__all__ = [
    "get_quote",
    "get_historical_data",
    "get_bulk_quotes", 
    "search_symbols",
    "get_market_status",
    "get_intraday_data",
    "compare_symbols",
]
