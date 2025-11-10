"""
Cryptocurrency trading and analysis tools.

This module provides comprehensive cryptocurrency functionality including:
- Real-time crypto prices and historical data
- Major cryptocurrencies and altcoins
- Crypto market analysis and charting
- Portfolio tracking utilities
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


def get_crypto_price(
    symbol: str,
    *,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get current cryptocurrency price.
    
    Args:
        symbol: Crypto symbol (e.g., 'BTC-USD', 'ETH-USD')
        include_chart: Whether to include recent price chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing crypto price and optional chart
        
    Example:
        >>> price = get_crypto_price("BTC-USD", include_chart=True)
        >>> print(f"Bitcoin price: ${price['quote']['price']}")
    """
    crypto_symbol = _ensure_crypto_symbol(symbol)
    payload = _cached_crypto_quote(crypto_symbol)
    
    result = format_response(
        "CRYPTO_QUOTE",
        symbol=crypto_symbol,
        quote=payload["quote"],
        recent=payload["recent"]
    )
    
    if include_chart and not payload["recent"].empty:
        try:
            chart = create_line_chart(
                payload["recent"]["Close"],
                title=f"{symbol} Price Chart",
                y_label="Price (USD)",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_crypto_history(
    symbol: str,
    *,
    period: str = "1y",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get historical cryptocurrency data.
    
    Args:
        symbol: Crypto symbol (e.g., 'BTC-USD', 'ETH-USD')
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
        include_chart: Whether to include crypto chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing historical crypto data and optional chart
        
    Example:
        >>> data = get_crypto_history("ETH-USD", period="6mo", include_chart=True)
        >>> print(f"Retrieved {len(data['data'])} data points")
    """
    crypto_symbol = _ensure_crypto_symbol(symbol)
    data = history(
        crypto_symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=False,
        include_actions=False,
    )
    
    result = format_response(
        "CRYPTO_HISTORICAL",
        symbol=crypto_symbol,
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
                    data, symbol,
                    title=f"{symbol} Crypto Chart",
                    show_volume=True,
                    style=chart_style
                )
            else:
                # Use line chart for daily+ data
                chart = create_line_chart(
                    data["Close"],
                    title=f"{symbol} Price History",
                    y_label="Price (USD)",
                    style=chart_style
                )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_major_cryptos(
    *,
    include_prices: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get data for major cryptocurrencies.
    
    Args:
        include_prices: Whether to include current prices
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing major crypto data and optional chart
        
    Example:
        >>> majors = get_major_cryptos(include_chart=True)
        >>> for crypto in majors['cryptos']:
        ...     print(f"{crypto['symbol']}: ${crypto['price']}")
    """
    major_cryptos = [
        "BTC-USD",   # Bitcoin
        "ETH-USD",   # Ethereum
        "BNB-USD",   # Binance Coin
        "XRP-USD",   # Ripple
        "ADA-USD",   # Cardano
        "SOL-USD",   # Solana
        "DOGE-USD",  # Dogecoin
        "DOT-USD",   # Polkadot
        "AVAX-USD",  # Avalanche
        "MATIC-USD", # Polygon
    ]
    
    cryptos_data = []
    chart_data = {}
    
    for symbol in major_cryptos:
        try:
            if include_prices:
                price_data = get_crypto_price(symbol)
                cryptos_data.append({
                    "symbol": symbol,
                    "name": _get_crypto_name(symbol),
                    "price": price_data.get("quote", {}).get("price"),
                    "change": price_data.get("quote", {}).get("regular_market_change"),
                    "change_percent": price_data.get("quote", {}).get("regular_market_change_percent")
                })
            
            if include_chart:
                # Get recent data for chart
                recent_data = get_crypto_history(symbol, period="1mo")
                if "data" in recent_data and recent_data["data"]:
                    chart_data[symbol] = pd.Series(
                        [item["Close"] for item in recent_data["data"]],
                        index=[item["timestamp"] for item in recent_data["data"]]
                    )
        except Exception as e:
            cryptos_data.append({
                "symbol": symbol,
                "error": str(e)
            })
    
    result = format_response(
        "MAJOR_CRYPTOCURRENCIES",
        cryptos=cryptos_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            # Normalize prices to percentage change for comparison
            normalized_df = (chart_df / chart_df.iloc[0] - 1) * 100
            chart = create_line_chart(
                normalized_df,
                title="Major Cryptocurrencies - 1 Month (% Change)",
                y_label="% Change",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def compare_cryptos(
    symbols: List[str],
    *,
    period: str = "1y",
    normalize: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Compare multiple cryptocurrencies.
    
    Args:
        symbols: List of crypto symbols
        period: Time period for comparison
        normalize: Whether to normalize to percentage changes
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing crypto comparison data and optional chart
    """
    if len(symbols) < 2:
        raise ToolExecutionError("At least 2 symbols required for comparison.")
    
    comparison_data = {}
    chart_data = {}
    
    for symbol in symbols:
        try:
            crypto_symbol = _ensure_crypto_symbol(symbol)
            
            # Get current price
            price_data = get_crypto_price(crypto_symbol)
            comparison_data[crypto_symbol] = {
                "current_price": price_data.get("quote", {}).get("price"),
                "name": _get_crypto_name(crypto_symbol)
            }
            
            if include_chart:
                # Get historical data for chart
                hist_data = get_crypto_history(crypto_symbol, period=period)
                if "data" in hist_data and hist_data["data"]:
                    prices = pd.Series(
                        [item["Close"] for item in hist_data["data"]],
                        index=[item["timestamp"] for item in hist_data["data"]]
                    )
                    
                    if normalize:
                        # Normalize to percentage change from first value
                        prices = (prices / prices.iloc[0] - 1) * 100
                    
                    chart_data[crypto_symbol] = prices
        except Exception as e:
            comparison_data[symbol] = {"error": str(e)}
    
    result = format_response(
        "CRYPTO_COMPARISON",
        symbols=symbols,
        period=period,
        normalized=normalize,
        data=comparison_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            title = f"Cryptocurrency Comparison ({period})"
            if normalize:
                title += " - Normalized % Change"
            chart = create_line_chart(
                chart_df,
                title=title,
                y_label="Price" if not normalize else "% Change",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_crypto_volatility(
    symbol: str,
    *,
    period: str = "1y",
    window: int = 30
) -> Dict[str, Any]:
    """
    Calculate cryptocurrency volatility.
    
    Args:
        symbol: Crypto symbol
        period: Time period for analysis
        window: Rolling window for volatility calculation
        
    Returns:
        Dictionary containing volatility metrics
    """
    crypto_symbol = _ensure_crypto_symbol(symbol)
    data = history(
        crypto_symbol,
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
    volatility = returns.std() * (365 ** 0.5)  # Annualized volatility (crypto trades 365 days)
    rolling_vol = returns.rolling(window=window).std() * (365 ** 0.5)
    
    return format_response(
        "CRYPTO_VOLATILITY",
        symbol=crypto_symbol,
        period=period,
        annualized_volatility=volatility,
        rolling_volatility=rolling_vol,
        average_daily_return=returns.mean(),
        volatility_window=window,
        max_daily_return=returns.max(),
        min_daily_return=returns.min()
    )


def calculate_crypto_returns(
    symbol: str,
    *,
    period: str = "1y"
) -> Dict[str, Any]:
    """
    Calculate cryptocurrency returns over a period.
    
    Args:
        symbol: Crypto symbol
        period: Time period for calculation
        
    Returns:
        Dictionary containing return metrics
    """
    crypto_symbol = _ensure_crypto_symbol(symbol)
    data = history(
        crypto_symbol,
        interval="1d",
        period=period,
        auto_adjust=False,
        include_actions=False,
    )
    
    if len(data) < 2:
        raise ToolExecutionError("Insufficient data for return calculation.")
    
    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]
    total_return = (end_price / start_price - 1) * 100
    
    # Calculate daily returns
    daily_returns = data["Close"].pct_change().dropna()
    
    return format_response(
        "CRYPTO_RETURNS",
        symbol=crypto_symbol,
        period=period,
        start_price=start_price,
        end_price=end_price,
        total_return_percent=total_return,
        average_daily_return=daily_returns.mean() * 100,
        best_day_return=daily_returns.max() * 100,
        worst_day_return=daily_returns.min() * 100,
        positive_days=len(daily_returns[daily_returns > 0]),
        negative_days=len(daily_returns[daily_returns < 0]),
        total_days=len(daily_returns)
    )


# Internal helper functions
def _ensure_crypto_symbol(symbol: str) -> str:
    """Ensure crypto symbol has proper format for yfinance."""
    symbol = ensure_symbol(symbol)
    if not symbol.endswith("-USD") and not symbol.endswith("=X"):
        # Add -USD suffix if not present
        symbol = f"{symbol}-USD"
    return symbol


def _get_crypto_name(symbol: str) -> str:
    """Get friendly name for crypto symbol."""
    names = {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "BNB-USD": "Binance Coin",
        "XRP-USD": "Ripple",
        "ADA-USD": "Cardano",
        "SOL-USD": "Solana",
        "DOGE-USD": "Dogecoin",
        "DOT-USD": "Polkadot",
        "AVAX-USD": "Avalanche",
        "MATIC-USD": "Polygon",
        "LINK-USD": "Chainlink",
        "UNI-USD": "Uniswap",
        "LTC-USD": "Litecoin",
        "BCH-USD": "Bitcoin Cash",
        "ALGO-USD": "Algorand",
    }
    return names.get(symbol, symbol.replace("-USD", ""))


@ttl_cache(ttl=60, maxsize=256)
def _cached_crypto_quote(symbol: str) -> Dict[str, Any]:
    """Get cached crypto quote data."""
    ticker = get_ticker(symbol)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception:
        fast_info = {}
    
    recent = history(symbol, interval="1d", period="5d", auto_adjust=False, include_actions=False)
    recent_close = None
    if not recent.empty:
        try:
            recent_close = float(recent["Close"].iloc[-1])
        except Exception:
            recent_close = None

    def _fast(field: str, *aliases: str):
        for key in (field, *aliases):
            if key in fast_info:
                return fast_info[key]
        return None

    quote = {
        "symbol": symbol,
        "price": _fast("last_price", "lastPrice", "regularMarketPrice") or recent_close,
        "currency": _fast("currency") or "USD",
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
    return {"quote": quote, "recent": recent}


# Export main functions
__all__ = [
    "get_crypto_price",
    "get_crypto_history",
    "get_major_cryptos",
    "compare_cryptos",
    "get_crypto_volatility",
    "calculate_crypto_returns",
]
