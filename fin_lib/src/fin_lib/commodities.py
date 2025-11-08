"""
Commodities trading and analysis tools.

This module provides comprehensive commodities functionality including:
- Precious metals (gold, silver, platinum, palladium)
- Energy commodities (oil, natural gas)
- Agricultural commodities (wheat, corn, soybeans)
- Industrial metals (copper, aluminum)
- Professional charting capabilities
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

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


def get_commodity_price(
    symbol: str,
    *,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get current commodity price.
    
    Args:
        symbol: Commodity symbol (e.g., 'GC=F', 'CL=F', 'SI=F')
        include_chart: Whether to include recent price chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing commodity price and optional chart
        
    Example:
        >>> price = get_commodity_price("GC=F", include_chart=True)  # Gold
        >>> print(f"Gold price: ${price['quote']['price']}")
    """
    commodity_symbol = _ensure_commodity_symbol(symbol)
    payload = _cached_commodity_quote(commodity_symbol)
    
    result = format_response(
        "COMMODITY_QUOTE",
        symbol=commodity_symbol,
        name=_get_commodity_name(commodity_symbol),
        quote=payload["quote"],
        recent=payload["recent"]
    )
    
    if include_chart and not payload["recent"].empty:
        try:
            chart = create_line_chart(
                payload["recent"]["Close"],
                title=f"{_get_commodity_name(commodity_symbol)} Price Chart",
                y_label="Price",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_commodity_history(
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
    Get historical commodity data.
    
    Args:
        symbol: Commodity symbol
        period: Time period
        interval: Data interval
        start: Start date
        end: End date
        include_chart: Whether to include chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing historical commodity data and optional chart
    """
    commodity_symbol = _ensure_commodity_symbol(symbol)
    data = history(
        commodity_symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        auto_adjust=False,
        include_actions=False,
    )
    
    result = format_response(
        "COMMODITY_HISTORICAL",
        symbol=commodity_symbol,
        name=_get_commodity_name(commodity_symbol),
        interval=interval,
        period=period,
        data=data,
    )
    
    if include_chart and not data.empty:
        try:
            chart = create_line_chart(
                data["Close"],
                title=f"{_get_commodity_name(commodity_symbol)} Price History",
                y_label="Price",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_precious_metals(
    *,
    include_prices: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get data for precious metals.
    
    Args:
        include_prices: Whether to include current prices
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing precious metals data and optional chart
    """
    metals = [
        "GC=F",  # Gold
        "SI=F",  # Silver
        "PL=F",  # Platinum
        "PA=F",  # Palladium
    ]
    
    metals_data = []
    chart_data = {}
    
    for symbol in metals:
        try:
            if include_prices:
                price_data = get_commodity_price(symbol)
                metals_data.append({
                    "symbol": symbol,
                    "name": _get_commodity_name(symbol),
                    "price": price_data.get("quote", {}).get("price"),
                    "change": price_data.get("quote", {}).get("regular_market_change"),
                    "change_percent": price_data.get("quote", {}).get("regular_market_change_percent")
                })
            
            if include_chart:
                recent_data = get_commodity_history(symbol, period="1mo")
                if "data" in recent_data and recent_data["data"]:
                    chart_data[_get_commodity_name(symbol)] = pd.Series(
                        [item["Close"] for item in recent_data["data"]],
                        index=[item["timestamp"] for item in recent_data["data"]]
                    )
        except Exception as e:
            metals_data.append({
                "symbol": symbol,
                "name": _get_commodity_name(symbol),
                "error": str(e)
            })
    
    result = format_response(
        "PRECIOUS_METALS",
        metals=metals_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            # Normalize for comparison
            normalized_df = (chart_df / chart_df.iloc[0] - 1) * 100
            chart = create_line_chart(
                normalized_df,
                title="Precious Metals - 1 Month (% Change)",
                y_label="% Change",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_energy_commodities(
    *,
    include_prices: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """Get data for energy commodities."""
    energy = [
        "CL=F",  # Crude Oil
        "NG=F",  # Natural Gas
        "BZ=F",  # Brent Oil
        "RB=F",  # Gasoline
        "HO=F",  # Heating Oil
    ]
    
    energy_data = []
    chart_data = {}
    
    for symbol in energy:
        try:
            if include_prices:
                price_data = get_commodity_price(symbol)
                energy_data.append({
                    "symbol": symbol,
                    "name": _get_commodity_name(symbol),
                    "price": price_data.get("quote", {}).get("price"),
                    "change": price_data.get("quote", {}).get("regular_market_change"),
                    "change_percent": price_data.get("quote", {}).get("regular_market_change_percent")
                })
            
            if include_chart:
                recent_data = get_commodity_history(symbol, period="1mo")
                if "data" in recent_data and recent_data["data"]:
                    chart_data[_get_commodity_name(symbol)] = pd.Series(
                        [item["Close"] for item in recent_data["data"]],
                        index=[item["timestamp"] for item in recent_data["data"]]
                    )
        except Exception as e:
            energy_data.append({
                "symbol": symbol,
                "name": _get_commodity_name(symbol),
                "error": str(e)
            })
    
    result = format_response(
        "ENERGY_COMMODITIES",
        energy=energy_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            normalized_df = (chart_df / chart_df.iloc[0] - 1) * 100
            chart = create_line_chart(
                normalized_df,
                title="Energy Commodities - 1 Month (% Change)",
                y_label="% Change",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def compare_commodities(
    symbols: List[str],
    *,
    period: str = "1y",
    normalize: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """Compare multiple commodities."""
    if len(symbols) < 2:
        raise ToolExecutionError("At least 2 symbols required for comparison.")
    
    comparison_data = {}
    chart_data = {}
    
    for symbol in symbols:
        try:
            commodity_symbol = _ensure_commodity_symbol(symbol)
            
            price_data = get_commodity_price(commodity_symbol)
            comparison_data[commodity_symbol] = {
                "current_price": price_data.get("quote", {}).get("price"),
                "name": _get_commodity_name(commodity_symbol)
            }
            
            if include_chart:
                hist_data = get_commodity_history(commodity_symbol, period=period)
                if "data" in hist_data and hist_data["data"]:
                    prices = pd.Series(
                        [item["Close"] for item in hist_data["data"]],
                        index=[item["timestamp"] for item in hist_data["data"]]
                    )
                    
                    if normalize:
                        prices = (prices / prices.iloc[0] - 1) * 100
                    
                    chart_data[_get_commodity_name(commodity_symbol)] = prices
        except Exception as e:
            comparison_data[symbol] = {"error": str(e)}
    
    result = format_response(
        "COMMODITIES_COMPARISON",
        symbols=symbols,
        period=period,
        normalized=normalize,
        data=comparison_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            title = f"Commodities Comparison ({period})"
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


# Internal helper functions
def _ensure_commodity_symbol(symbol: str) -> str:
    """Ensure commodity symbol has proper format."""
    symbol = ensure_symbol(symbol)
    if not symbol.endswith("=F"):
        symbol = f"{symbol}=F"
    return symbol


def _get_commodity_name(symbol: str) -> str:
    """Get friendly name for commodity symbol."""
    names = {
        "GC=F": "Gold",
        "SI=F": "Silver", 
        "PL=F": "Platinum",
        "PA=F": "Palladium",
        "CL=F": "Crude Oil",
        "NG=F": "Natural Gas",
        "BZ=F": "Brent Oil",
        "RB=F": "Gasoline",
        "HO=F": "Heating Oil",
        "ZC=F": "Corn",
        "ZS=F": "Soybeans",
        "ZW=F": "Wheat",
        "HG=F": "Copper",
        "CC=F": "Cocoa",
        "KC=F": "Coffee",
        "SB=F": "Sugar",
        "CT=F": "Cotton",
    }
    return names.get(symbol, symbol.replace("=F", ""))


@ttl_cache(ttl=120, maxsize=256)
def _cached_commodity_quote(symbol: str) -> Dict[str, Any]:
    """Get cached commodity quote data."""
    ticker = get_ticker(symbol)
    try:
        fast_info = dict(ticker.fast_info)
    except Exception:
        fast_info = {}
    
    recent = history(symbol, interval="1d", period="5d", auto_adjust=False, include_actions=False)
    quote = {
        "symbol": symbol,
        "price": fast_info.get("last_price"),
        "currency": fast_info.get("currency", "USD"),
        "previous_close": fast_info.get("previous_close"),
        "regular_market_change": fast_info.get("regular_market_change"),
        "regular_market_change_percent": fast_info.get("regular_market_change_percent"),
        "regular_market_time": fast_info.get("regular_market_time"),
    }
    return {"quote": quote, "recent": recent}


# Export main functions
__all__ = [
    "get_commodity_price",
    "get_commodity_history",
    "get_precious_metals",
    "get_energy_commodities",
    "compare_commodities",
]
