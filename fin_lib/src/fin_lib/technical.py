"""
Technical analysis tools using pandas-ta.

This module provides comprehensive technical analysis functionality including:
- Moving averages (SMA, EMA, WMA, etc.)
- Momentum indicators (RSI, MACD, Stochastic)
- Volatility indicators (Bollinger Bands, ATR)
- Volume indicators (OBV, MFI)
- Trend indicators (ADX, Aroon)
- Professional charting capabilities
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd

from .base import (
    DataFrameLike,
    ToolExecutionError,
    ensure_symbol,
    format_response,
    history,
    create_line_chart,
    create_candlestick_chart,
)

try:
    import pandas_ta as ta
except ModuleNotFoundError:
    ta = None


def technical_analysis(
    symbol: str,
    *,
    indicators: Optional[List[str]] = None,
    period: str = "1y",
    interval: str = "1d",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Perform comprehensive technical analysis on a symbol.
    
    Args:
        symbol: Stock ticker symbol
        indicators: List of indicators to calculate (default: common indicators)
        period: Time period for analysis
        interval: Data interval
        include_chart: Whether to include charts
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing technical analysis results and optional charts
        
    Example:
        >>> analysis = technical_analysis("AAPL", indicators=["RSI", "MACD", "SMA"])
        >>> print(f"RSI: {analysis['indicators']['RSI']['data'][-1]}")
    """
    if ta is None:
        raise ToolExecutionError(
            "Technical analysis requires pandas-ta. Install with: pip install pandas-ta"
        )
    
    if indicators is None:
        indicators = ["RSI", "MACD", "SMA", "EMA", "BBANDS", "ATR", "OBV"]
    
    symbol = ensure_symbol(symbol)
    
    # Get historical data
    try:
        data = history(symbol, interval=interval, period=period)
    except Exception as e:
        raise ToolExecutionError(f"Failed to get historical data for {symbol}: {e}")
    
    if len(data) < 50:
        raise ToolExecutionError(
            f"Insufficient data for technical analysis. Got {len(data)} points, need at least 50."
        )
    
    # Calculate indicators
    results = {}
    for indicator in indicators:
        try:
            result = calculate_technical_indicator(
                indicator,
                symbol=symbol,
                interval=interval,
                period=period
            )
            results[indicator] = result
        except Exception as e:
            results[indicator] = {"error": str(e)}
    
    response = format_response(
        "TECHNICAL_ANALYSIS",
        symbol=symbol,
        period=period,
        interval=interval,
        indicators=results,
        price_data=data.tail(20)  # Include recent price data
    )
    
    if include_chart:
        try:
            # Create price chart with indicators
            chart = create_technical_chart(data, symbol, indicators, chart_style)
            response["chart"] = chart
        except Exception as e:
            response["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return response


def get_technical_indicators(
    symbol: str,
    indicators: List[str],
    *,
    period: str = "1y",
    interval: str = "1d"
) -> Dict[str, Any]:
    """
    Get specific technical indicators for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        indicators: List of indicator names
        period: Time period
        interval: Data interval
        
    Returns:
        Dictionary containing indicator results
    """
    return technical_analysis(
        symbol, 
        indicators=indicators, 
        period=period, 
        interval=interval,
        include_chart=False
    )


def calculate_rsi(
    symbol: str,
    *,
    length: int = 14,
    period: str = "200d",
    interval: str = "1d",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Calculate RSI (Relative Strength Index) for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        length: RSI period (default: 14)
        period: Historical data period
        interval: Data interval
        include_chart: Whether to include RSI chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing RSI data and optional chart
    """
    result = calculate_technical_indicator(
        "RSI",
        symbol=symbol,
        interval=interval,
        period=period,
        length=length
    )
    
    if include_chart and "data" in result and not result.get("error"):
        try:
            rsi_data = pd.Series(result["data"])
            chart = create_line_chart(
                rsi_data,
                title=f"{symbol} RSI ({length})",
                y_label="RSI",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def calculate_macd(
    symbol: str,
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    period: str = "200d",
    interval: str = "1d",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Calculate MACD (Moving Average Convergence Divergence) for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        period: Historical data period
        interval: Data interval
        include_chart: Whether to include MACD chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing MACD data and optional chart
    """
    result = calculate_technical_indicator(
        "MACD",
        symbol=symbol,
        interval=interval,
        period=period,
        fastperiod=fast,
        slowperiod=slow,
        signalperiod=signal
    )
    
    if include_chart and "data" in result and not result.get("error"):
        try:
            macd_data = pd.DataFrame(result["data"])
            chart = create_line_chart(
                macd_data,
                title=f"{symbol} MACD ({fast},{slow},{signal})",
                y_label="MACD",
                style=chart_style
            )
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def calculate_bollinger_bands(
    symbol: str,
    *,
    length: int = 20,
    std: int = 2,
    period: str = "200d",
    interval: str = "1d",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Calculate Bollinger Bands for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        length: Moving average period
        std: Standard deviation multiplier
        period: Historical data period
        interval: Data interval
        include_chart: Whether to include Bollinger Bands chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing Bollinger Bands data and optional chart
    """
    result = calculate_technical_indicator(
        "BBANDS",
        symbol=symbol,
        interval=interval,
        period=period,
        length=length,
        nbdevup=std,
        nbdevdn=std
    )
    
    if include_chart and "data" in result and not result.get("error"):
        try:
            # Get price data for chart
            price_data = history(symbol, interval=interval, period=period)
            bb_data = pd.DataFrame(result["data"])
            
            # Create combined chart with price and Bollinger Bands
            chart = create_bollinger_chart(price_data, bb_data, symbol, chart_style)
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def create_technical_chart(
    data: pd.DataFrame,
    symbol: str,
    indicators: List[str],
    style: str = "plotly"
) -> Union[Any, None]:
    """
    Create a comprehensive technical analysis chart.
    
    Args:
        data: Price data DataFrame
        symbol: Stock symbol
        indicators: List of indicators to include
        style: Chart style
        
    Returns:
        Chart figure object
    """
    if style == "plotly":
        return _create_plotly_technical_chart(data, symbol, indicators)
    else:
        return _create_mpl_technical_chart(data, symbol, indicators)


def create_bollinger_chart(
    price_data: pd.DataFrame,
    bb_data: pd.DataFrame,
    symbol: str,
    style: str = "plotly"
) -> Union[Any, None]:
    """Create a Bollinger Bands chart with price data."""
    if style == "plotly":
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            name='Close Price',
            line=dict(color='blue')
        ))
        
        # Add Bollinger Bands
        if 'BBU_20_2.0' in bb_data.columns:
            fig.add_trace(go.Scatter(
                x=bb_data.index,
                y=bb_data['BBU_20_2.0'],
                name='Upper Band',
                line=dict(color='red', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=bb_data.index,
                y=bb_data['BBL_20_2.0'],
                name='Lower Band',
                line=dict(color='red', dash='dash'),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)'
            ))
        
        fig.update_layout(title=f"{symbol} Bollinger Bands")
        return fig
    
    return None


def _create_plotly_technical_chart(data: pd.DataFrame, symbol: str, indicators: List[str]):
    """Create technical chart using Plotly."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create subplots for price and indicators
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Price', 'Technical Indicators'),
            row_heights=[0.7, 0.3]
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol
            ),
            row=1, col=1
        )
        
        # Add volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_layout(xaxis_rangeslider_visible=False)
        return fig
        
    except Exception:
        return None


def _create_mpl_technical_chart(data: pd.DataFrame, symbol: str, indicators: List[str]):
    """Create technical chart using matplotlib."""
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Price chart
        ax1.plot(data.index, data['Close'], label='Close Price')
        ax1.set_title(f'{symbol} Technical Analysis')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        
        # Volume chart
        ax2.bar(data.index, data['Volume'], alpha=0.7, label='Volume')
        ax2.set_ylabel('Volume')
        ax2.legend()
        
        plt.tight_layout()
        return fig
        
    except Exception:
        return None


# Core technical indicator calculation function
def calculate_technical_indicator(
    tool_name: str,
    *,
    symbol: str,
    interval: str = "1d",
    period: Optional[str] = "200d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    **params: Any,
) -> Dict[str, Any]:
    """Calculate a specific technical indicator."""
    if ta is None:
        return format_response(
            tool_name,
            symbol=symbol,
            error="missing_dependency",
            message="Technical indicators require the pandas-ta package.",
            suggestion="Install pandas-ta to enable technical analysis tools: pip install pandas-ta"
        )
    
    symbol = ensure_symbol(symbol)
    
    # Get historical data
    try:
        history_df = history(
            symbol,
            interval=interval,
            period=period,
            start=start,
            end=end,
            auto_adjust=True,
            include_actions=False,
        )
    except ToolExecutionError as exc:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="data_unavailable",
            message=f"Could not retrieve historical data for {symbol}: {exc}",
            suggestion="Try a different symbol, time period, or check if the symbol exists."
        )
    
    # Check if we have enough data
    if len(history_df) < 50:
        return format_response(
            tool_name,
            symbol=symbol,
            interval=interval,
            period=period,
            error="insufficient_data",
            message=f"Insufficient data for {tool_name}. Got {len(history_df)} points, need at least 50.",
            suggestion="Try a longer time period (e.g., '1y' instead of '1mo')."
        )
    
    # Prepare data for pandas-ta
    context = _prepare_ta_context(history_df)
    
    # Calculate indicator
    try:
        result = _calculate_indicator(tool_name, context, **params)
    except Exception as exc:
        return format_response(
            tool_name,
            symbol=symbol,
            error="calculation_failed",
            message=f"Failed to calculate {tool_name}: {exc}",
            suggestion="Try different parameters or a longer time period."
        )
    
    if result is None or (isinstance(result, (pd.DataFrame, pd.Series)) and result.empty):
        return format_response(
            tool_name,
            symbol=symbol,
            error="no_data_returned",
            message=f"{tool_name} calculation returned no data.",
            suggestion="Try a longer time period or different parameters."
        )
    
    return format_response(
        tool_name,
        symbol=symbol,
        interval=interval,
        period=period,
        data=result,
    )


def _prepare_ta_context(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for pandas-ta calculations."""
    return pd.DataFrame({
        'open': data['Open'],
        'high': data['High'],
        'low': data['Low'],
        'close': data['Close'],
        'volume': data['Volume']
    })


def _calculate_indicator(indicator: str, context: pd.DataFrame, **params) -> DataFrameLike:
    """Calculate specific technical indicator."""
    indicator = indicator.upper()
    
    # Common parameters
    length = params.get('length', params.get('timeperiod', 14))
    
    if indicator == 'RSI':
        return ta.rsi(context['close'], length=length)
    elif indicator == 'MACD':
        return ta.macd(
            context['close'],
            fast=params.get('fastperiod', 12),
            slow=params.get('slowperiod', 26),
            signal=params.get('signalperiod', 9)
        )
    elif indicator == 'SMA':
        return ta.sma(context['close'], length=params.get('length', 20))
    elif indicator == 'EMA':
        return ta.ema(context['close'], length=params.get('length', 20))
    elif indicator == 'BBANDS':
        return ta.bbands(
            context['close'],
            length=params.get('length', 20),
            std=params.get('nbdevup', params.get('nbdevdn', 2))
        )
    elif indicator == 'ATR':
        return ta.atr(context['high'], context['low'], context['close'], length=length)
    elif indicator == 'OBV':
        return ta.obv(context['close'], context['volume'])
    elif indicator == 'STOCH':
        return ta.stoch(
            context['high'],
            context['low'],
            context['close'],
            k=params.get('fastkperiod', 14),
            d=params.get('slowkperiod', 3)
        )
    elif indicator == 'ADX':
        return ta.adx(context['high'], context['low'], context['close'], length=length)
    elif indicator == 'CCI':
        return ta.cci(context['high'], context['low'], context['close'], length=params.get('length', 20))
    elif indicator == 'WILLR':
        return ta.willr(context['high'], context['low'], context['close'], length=length)
    elif indicator == 'MFI':
        return ta.mfi(
            context['high'], context['low'], context['close'], context['volume'], length=length
        )
    else:
        raise ToolExecutionError(f"Unsupported indicator: {indicator}")


# Export main functions
__all__ = [
    "technical_analysis",
    "get_technical_indicators",
    "calculate_rsi",
    "calculate_macd",
    "calculate_bollinger_bands",
    "calculate_technical_indicator",
    "create_technical_chart",
]
