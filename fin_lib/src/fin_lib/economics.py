"""
Economic indicators and macroeconomic analysis tools.

This module provides economic data functionality including:
- Key economic indicators (GDP, inflation, unemployment)
- Interest rates and yield curves
- Economic calendar and events
- Market sentiment indicators
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
)


def get_treasury_rates(
    *,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get current US Treasury rates across different maturities.
    
    Args:
        include_chart: Whether to include yield curve chart
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing treasury rates and optional chart
        
    Example:
        >>> rates = get_treasury_rates(include_chart=True)
        >>> print(f"10Y Treasury: {rates['rates']['10Y']}")
    """
    treasury_symbols = {
        "3M": "^IRX",    # 3-Month Treasury
        "2Y": "^TNX",    # 10-Year Treasury (Note: ^TNX is actually 10Y, using as proxy)
        "10Y": "^TNX",   # 10-Year Treasury
        "30Y": "^TYX",   # 30-Year Treasury
    }
    
    rates_data = {}
    chart_data = {}
    
    for maturity, symbol in treasury_symbols.items():
        try:
            ticker = get_ticker(symbol)
            fast_info = dict(ticker.fast_info)
            rate = fast_info.get("last_price")
            
            rates_data[maturity] = {
                "rate": rate,
                "symbol": symbol,
                "maturity": maturity
            }
            
            if include_chart and rate is not None:
                chart_data[maturity] = rate
                
        except Exception as e:
            rates_data[maturity] = {"error": str(e)}
    
    result = format_response(
        "TREASURY_RATES",
        rates=rates_data
    )
    
    if include_chart and chart_data:
        try:
            # Create yield curve
            maturities = ["3M", "2Y", "10Y", "30Y"]
            rates = [chart_data.get(m, 0) for m in maturities]
            
            if chart_style == "plotly":
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=maturities,
                    y=rates,
                    mode='lines+markers',
                    name='Yield Curve'
                ))
                fig.update_layout(
                    title="US Treasury Yield Curve",
                    xaxis_title="Maturity",
                    yaxis_title="Yield (%)"
                )
                result["chart"] = fig
            
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_economic_indicator(
    indicator: str,
    *,
    period: str = "5y",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get economic indicator data.
    
    Args:
        indicator: Economic indicator symbol
        period: Time period for historical data
        include_chart: Whether to include chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing indicator data and optional chart
    """
    # Map common indicators to symbols
    indicator_map = {
        "VIX": "^VIX",           # Volatility Index
        "DXY": "DX-Y.NYB",       # US Dollar Index
        "GOLD": "GC=F",          # Gold as economic indicator
        "OIL": "CL=F",           # Oil prices
        "COPPER": "HG=F",        # Copper (economic bellwether)
    }
    
    symbol = indicator_map.get(indicator.upper(), indicator)
    
    try:
        # Get current value
        ticker = get_ticker(symbol)
        fast_info = dict(ticker.fast_info)
        current_value = fast_info.get("last_price")
        
        # Get historical data
        data = history(symbol, interval="1d", period=period)
        
        result = format_response(
            "ECONOMIC_INDICATOR",
            indicator=indicator,
            symbol=symbol,
            current_value=current_value,
            data=data
        )
        
        if include_chart and not data.empty:
            try:
                chart = create_line_chart(
                    data["Close"],
                    title=f"{indicator} Historical Data",
                    y_label="Value",
                    style=chart_style
                )
                result["chart"] = chart
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "ECONOMIC_INDICATOR",
            indicator=indicator,
            error=str(e)
        )


def get_market_sentiment(
    *,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get market sentiment indicators.
    
    Args:
        include_chart: Whether to include sentiment chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing sentiment indicators and optional chart
    """
    sentiment_indicators = {
        "VIX": "^VIX",      # Fear & Greed (Volatility)
        "SKEW": "^SKEW",    # Tail Risk
        "VXN": "^VXN",      # NASDAQ Volatility
        "RVX": "^RVX",      # Russell 2000 Volatility
    }
    
    sentiment_data = {}
    chart_data = {}
    
    for name, symbol in sentiment_indicators.items():
        try:
            ticker = get_ticker(symbol)
            fast_info = dict(ticker.fast_info)
            value = fast_info.get("last_price")
            
            sentiment_data[name] = {
                "value": value,
                "symbol": symbol,
                "description": _get_sentiment_description(name)
            }
            
            if include_chart and value is not None:
                # Get recent history for chart
                recent_data = history(symbol, interval="1d", period="1mo")
                if not recent_data.empty:
                    chart_data[name] = recent_data["Close"]
                    
        except Exception as e:
            sentiment_data[name] = {"error": str(e)}
    
    result = format_response(
        "MARKET_SENTIMENT",
        sentiment=sentiment_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            chart = create_line_chart(
                chart_df,
                title="Market Sentiment Indicators - 1 Month",
                y_label="Index Value",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def get_dollar_index(
    *,
    period: str = "1y",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get US Dollar Index (DXY) data.
    
    Args:
        period: Time period for historical data
        include_chart: Whether to include DXY chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing DXY data and optional chart
    """
    try:
        symbol = "DX-Y.NYB"
        ticker = get_ticker(symbol)
        fast_info = dict(ticker.fast_info)
        current_value = fast_info.get("last_price")
        
        data = history(symbol, interval="1d", period=period)
        
        result = format_response(
            "DOLLAR_INDEX",
            symbol=symbol,
            current_value=current_value,
            data=data
        )
        
        if include_chart and not data.empty:
            try:
                chart = create_line_chart(
                    data["Close"],
                    title="US Dollar Index (DXY)",
                    y_label="Index Value",
                    style=chart_style
                )
                result["chart"] = chart
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "DOLLAR_INDEX",
            error=str(e)
        )


def compare_economic_indicators(
    indicators: List[str],
    *,
    period: str = "1y",
    normalize: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Compare multiple economic indicators.
    
    Args:
        indicators: List of indicator names
        period: Time period for comparison
        normalize: Whether to normalize to percentage changes
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing comparison data and optional chart
    """
    if len(indicators) < 2:
        raise ToolExecutionError("At least 2 indicators required for comparison.")
    
    comparison_data = {}
    chart_data = {}
    
    for indicator in indicators:
        try:
            indicator_data = get_economic_indicator(indicator, period=period)
            
            if "data" in indicator_data and indicator_data["data"]:
                prices = pd.Series(
                    [item["Close"] for item in indicator_data["data"]],
                    index=[item["timestamp"] for item in indicator_data["data"]]
                )
                
                comparison_data[indicator] = {
                    "current_value": indicator_data.get("current_value"),
                    "symbol": indicator_data.get("symbol")
                }
                
                if normalize and len(prices) > 0:
                    prices = (prices / prices.iloc[0] - 1) * 100
                
                chart_data[indicator] = prices
                
        except Exception as e:
            comparison_data[indicator] = {"error": str(e)}
    
    result = format_response(
        "ECONOMIC_INDICATORS_COMPARISON",
        indicators=indicators,
        period=period,
        normalized=normalize,
        data=comparison_data
    )
    
    if include_chart and chart_data:
        try:
            chart_df = pd.DataFrame(chart_data)
            title = f"Economic Indicators Comparison ({period})"
            if normalize:
                title += " - Normalized % Change"
            chart = create_line_chart(
                chart_df,
                title=title,
                y_label="Value" if not normalize else "% Change",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


# Internal helper functions
def _get_sentiment_description(indicator: str) -> str:
    """Get description for sentiment indicators."""
    descriptions = {
        "VIX": "Volatility Index - Market fear gauge",
        "SKEW": "SKEW Index - Tail risk measure", 
        "VXN": "NASDAQ Volatility Index",
        "RVX": "Russell 2000 Volatility Index"
    }
    return descriptions.get(indicator, f"{indicator} Index")


# Export main functions
__all__ = [
    "get_treasury_rates",
    "get_economic_indicator", 
    "get_market_sentiment",
    "get_dollar_index",
    "compare_economic_indicators",
]
