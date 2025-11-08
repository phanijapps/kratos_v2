"""
Foreign exchange (forex) trading tools.

This module provides comprehensive forex functionality including:
- Currency exchange rates and historical data
- Major, minor, and exotic currency pairs
- Forex market analysis and charting
- Currency conversion utilities
- Professional charting capabilities
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_ticker,
    history,
    ttl_cache,
    create_line_chart,
    create_candlestick_chart,
)


def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    *,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get current exchange rate between two currencies.
    
    Args:
        from_currency: Base currency code (e.g., 'USD', 'EUR')
        to_currency: Quote currency code (e.g., 'JPY', 'GBP')
        include_chart: Whether to include recent rate chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing exchange rate and optional chart
        
    Example:
        >>> rate = get_exchange_rate("USD", "EUR", include_chart=True)
        >>> print(f"1 USD = {rate['rate']} EUR")
    """
    pair = _fx_pair(from_currency, to_currency)
    payload = _cached_fx_rate(pair)
    
    result = format_response(
        "CURRENCY_EXCHANGE_RATE",
        from_currency=ensure_symbol(from_currency),
        to_currency=ensure_symbol(to_currency),
        pair=pair,
        rate=payload["rate"],
        recent=payload["recent"]
    )
    
    if include_chart and not payload["recent"].empty:
        try:
            chart = create_line_chart(
                payload["recent"]["Close"],
                title=f"{from_currency}/{to_currency} Exchange Rate",
                y_label="Exchange Rate",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_forex_history(
    from_currency: str,
    to_currency: str,
    *,
    period: str = "1y",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get historical forex data for a currency pair.
    
    Args:
        from_currency: Base currency code
        to_currency: Quote currency code
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        include_chart: Whether to include forex chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing historical forex data and optional chart
        
    Example:
        >>> data = get_forex_history("EUR", "USD", period="6mo", include_chart=True)
        >>> print(f"Retrieved {len(data['data'])} data points")
    """
    pair = _fx_pair(from_currency, to_currency)
    data = history(
        pair,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=False,
        include_actions=False,
    )
    
    result = format_response(
        "FX_HISTORICAL",
        from_currency=ensure_symbol(from_currency),
        to_currency=ensure_symbol(to_currency),
        pair=pair,
        interval=interval,
        period=period,
        start=start,
        end=end,
        data=data,
    )
    
    if include_chart and not data.empty:
        try:
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                # Use candlestick for intraday data
                chart = create_candlestick_chart(
                    data, f"{from_currency}/{to_currency}",
                    title=f"{from_currency}/{to_currency} Forex Chart",
                    show_volume=False,
                    style=chart_style
                )
            else:
                # Use line chart for daily+ data
                chart = create_line_chart(
                    data["Close"],
                    title=f"{from_currency}/{to_currency} Exchange Rate",
                    y_label="Exchange Rate",
                    style=chart_style
                )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_major_pairs(
    *,
    include_rates: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get data for major forex pairs.
    
    Args:
        include_rates: Whether to include current rates
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing major pairs data and optional chart
        
    Example:
        >>> majors = get_major_pairs(include_chart=True)
        >>> for pair in majors['pairs']:
        ...     print(f"{pair['pair']}: {pair['rate']}")
    """
    major_pairs = [
        ("EUR", "USD"),  # Euro/US Dollar
        ("GBP", "USD"),  # British Pound/US Dollar
        ("USD", "JPY"),  # US Dollar/Japanese Yen
        ("USD", "CHF"),  # US Dollar/Swiss Franc
        ("AUD", "USD"),  # Australian Dollar/US Dollar
        ("USD", "CAD"),  # US Dollar/Canadian Dollar
        ("NZD", "USD"),  # New Zealand Dollar/US Dollar
    ]
    
    pairs_data = []
    chart_data = {}
    
    for from_curr, to_curr in major_pairs:
        try:
            if include_rates:
                rate_data = get_exchange_rate(from_curr, to_curr)
                pairs_data.append({
                    "pair": f"{from_curr}/{to_curr}",
                    "from_currency": from_curr,
                    "to_currency": to_curr,
                    "rate": rate_data.get("rate"),
                    "symbol": _fx_pair(from_curr, to_curr)
                })
            
            if include_chart:
                # Get recent data for chart
                recent_data = get_forex_history(from_curr, to_curr, period="1mo")
                if "data" in recent_data and recent_data["data"]:
                    chart_data[f"{from_curr}/{to_curr}"] = pd.Series(
                        [item["Close"] for item in recent_data["data"]],
                        index=[item["timestamp"] for item in recent_data["data"]]
                    )
        except Exception as e:
            pairs_data.append({
                "pair": f"{from_curr}/{to_curr}",
                "error": str(e)
            })
    
    result = format_response(
        "MAJOR_FOREX_PAIRS",
        pairs=pairs_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            chart = create_line_chart(
                chart_df,
                title="Major Forex Pairs - 1 Month",
                y_label="Exchange Rate",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> Dict[str, Any]:
    """
    Convert amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Dictionary containing conversion result
        
    Example:
        >>> result = convert_currency(100, "USD", "EUR")
        >>> print(f"100 USD = {result['converted_amount']} EUR")
    """
    if amount <= 0:
        raise ToolExecutionError("Amount must be positive.")
    
    rate_data = get_exchange_rate(from_currency, to_currency)
    rate = rate_data.get("rate")
    
    if rate is None:
        raise ToolExecutionError(f"Could not get exchange rate for {from_currency}/{to_currency}")
    
    converted_amount = amount * rate
    
    return format_response(
        "CURRENCY_CONVERSION",
        original_amount=amount,
        from_currency=ensure_symbol(from_currency),
        to_currency=ensure_symbol(to_currency),
        exchange_rate=rate,
        converted_amount=converted_amount,
        conversion_string=f"{amount} {from_currency} = {converted_amount:.4f} {to_currency}"
    )


def compare_currencies(
    base_currency: str,
    target_currencies: List[str],
    *,
    period: str = "1y",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Compare a base currency against multiple target currencies.
    
    Args:
        base_currency: Base currency code
        target_currencies: List of target currency codes
        period: Time period for comparison
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing currency comparison data and optional chart
    """
    if len(target_currencies) < 1:
        raise ToolExecutionError("At least one target currency required.")
    
    comparison_data = {}
    chart_data = {}
    
    for target in target_currencies:
        try:
            # Get current rate
            rate_data = get_exchange_rate(base_currency, target)
            comparison_data[f"{base_currency}/{target}"] = {
                "current_rate": rate_data.get("rate"),
                "target_currency": target
            }
            
            if include_chart:
                # Get historical data for chart
                hist_data = get_forex_history(base_currency, target, period=period)
                if "data" in hist_data and hist_data["data"]:
                    chart_data[f"{base_currency}/{target}"] = pd.Series(
                        [item["Close"] for item in hist_data["data"]],
                        index=[item["timestamp"] for item in hist_data["data"]]
                    )
        except Exception as e:
            comparison_data[f"{base_currency}/{target}"] = {"error": str(e)}
    
    result = format_response(
        "CURRENCY_COMPARISON",
        base_currency=base_currency,
        target_currencies=target_currencies,
        period=period,
        data=comparison_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            chart = create_line_chart(
                chart_df,
                title=f"{base_currency} vs Multiple Currencies ({period})",
                y_label="Exchange Rate",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_forex_volatility(
    from_currency: str,
    to_currency: str,
    *,
    period: str = "1y",
    window: int = 30
) -> Dict[str, Any]:
    """
    Calculate forex pair volatility.
    
    Args:
        from_currency: Base currency code
        to_currency: Quote currency code
        period: Time period for analysis
        window: Rolling window for volatility calculation
        
    Returns:
        Dictionary containing volatility metrics
    """
    pair = _fx_pair(from_currency, to_currency)
    data = history(
        pair,
        interval="1d",
        period=period,
        auto_adjust=False,
        include_actions=False,
    )
    
    if len(data) < window:
        raise ToolExecutionError(f"Insufficient data for volatility calculation. Need at least {window} days.")
    
    # Calculate daily returns
    returns = data["Close"].pct_change().dropna()
    
    # Calculate volatility metrics
    volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
    rolling_vol = returns.rolling(window=window).std() * (252 ** 0.5)
    
    return format_response(
        "FOREX_VOLATILITY",
        from_currency=ensure_symbol(from_currency),
        to_currency=ensure_symbol(to_currency),
        pair=pair,
        period=period,
        annualized_volatility=volatility,
        rolling_volatility=rolling_vol,
        average_daily_return=returns.mean(),
        volatility_window=window
    )


# Internal helper functions
def _fx_pair(from_symbol: str, to_symbol: str) -> str:
    """Create forex pair symbol for yfinance."""
    return f"{ensure_symbol(from_symbol)}{ensure_symbol(to_symbol)}=X"


@ttl_cache(ttl=120, maxsize=256)
def _cached_fx_rate(pair: str) -> Dict[str, Any]:
    """Get cached forex rate data."""
    ticker = get_ticker(pair)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception:
        fast_info = {}
    
    recent = history(pair, interval="1d", period="5d", auto_adjust=False, include_actions=False)
    
    # Try to get rate from fast_info first, then fall back to latest Close price
    rate = fast_info.get("last_price")
    if rate is None and not recent.empty:
        rate = float(recent["Close"].iloc[-1])
    
    return {"rate": rate, "recent": recent}


# Export main functions
__all__ = [
    "get_exchange_rate",
    "get_forex_history",
    "get_major_pairs",
    "convert_currency",
    "compare_currencies",
    "get_forex_volatility",
]
