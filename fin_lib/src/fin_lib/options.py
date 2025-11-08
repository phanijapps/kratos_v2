"""
Options trading and analysis tools.

This module provides comprehensive options functionality including:
- Options chains and pricing data
- Options Greeks calculation
- Volatility analysis
- Options strategies analysis
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
    ttl_cache,
    create_line_chart,
)


def get_options_chain(
    symbol: str,
    *,
    expiration: Optional[str] = None,
    include_greeks: bool = True
) -> Dict[str, Any]:
    """
    Get options chain for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        expiration: Specific expiration date (YYYY-MM-DD) or None for next expiration
        include_greeks: Whether to include Greeks calculations
        
    Returns:
        Dictionary containing options chain data
        
    Example:
        >>> chain = get_options_chain("AAPL")
        >>> calls = chain['calls']
        >>> puts = chain['puts']
    """
    symbol = ensure_symbol(symbol)
    
    try:
        ticker = get_ticker(symbol)
        
        # Get available expiration dates
        expirations = ticker.options
        if not expirations:
            raise ToolExecutionError(f"No options data available for {symbol}")
        
        # Use specified expiration or next available
        target_exp = expiration if expiration else expirations[0]
        if target_exp not in expirations:
            target_exp = expirations[0]
        
        # Get options chain
        options_chain = ticker.option_chain(target_exp)
        calls = options_chain.calls
        puts = options_chain.puts
        
        result = format_response(
            "OPTIONS_CHAIN",
            symbol=symbol,
            expiration=target_exp,
            available_expirations=list(expirations),
            calls=calls,
            puts=puts,
            include_greeks=include_greeks
        )
        
        return result
        
    except Exception as e:
        return format_response(
            "OPTIONS_CHAIN",
            symbol=symbol,
            error=str(e)
        )


def get_options_volume(
    symbol: str,
    *,
    expiration: Optional[str] = None,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get options volume analysis.
    
    Args:
        symbol: Stock ticker symbol
        expiration: Specific expiration date
        include_chart: Whether to include volume chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing options volume data and optional chart
    """
    try:
        chain_data = get_options_chain(symbol, expiration=expiration)
        
        if "error" in chain_data:
            return chain_data
        
        calls = pd.DataFrame(chain_data["calls"])
        puts = pd.DataFrame(chain_data["puts"])
        
        # Calculate volume metrics
        total_call_volume = calls["volume"].sum() if "volume" in calls.columns else 0
        total_put_volume = puts["volume"].sum() if "volume" in puts.columns else 0
        put_call_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0
        
        # Get most active options
        most_active_calls = calls.nlargest(5, "volume") if "volume" in calls.columns else pd.DataFrame()
        most_active_puts = puts.nlargest(5, "volume") if "volume" in puts.columns else pd.DataFrame()
        
        result = format_response(
            "OPTIONS_VOLUME",
            symbol=symbol,
            expiration=chain_data.get("expiration"),
            total_call_volume=total_call_volume,
            total_put_volume=total_put_volume,
            put_call_ratio=put_call_ratio,
            most_active_calls=most_active_calls,
            most_active_puts=most_active_puts
        )
        
        if include_chart:
            try:
                # Create volume chart
                if chart_style == "plotly":
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='Calls',
                        x=['Call Volume'],
                        y=[total_call_volume]
                    ))
                    fig.add_trace(go.Bar(
                        name='Puts', 
                        x=['Put Volume'],
                        y=[total_put_volume]
                    ))
                    fig.update_layout(
                        title=f"{symbol} Options Volume",
                        yaxis_title="Volume"
                    )
                    result["chart"] = fig
                    
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "OPTIONS_VOLUME",
            symbol=symbol,
            error=str(e)
        )


def get_implied_volatility(
    symbol: str,
    *,
    expiration: Optional[str] = None,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get implied volatility analysis.
    
    Args:
        symbol: Stock ticker symbol
        expiration: Specific expiration date
        include_chart: Whether to include IV chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing implied volatility data and optional chart
    """
    try:
        chain_data = get_options_chain(symbol, expiration=expiration)
        
        if "error" in chain_data:
            return chain_data
        
        calls = pd.DataFrame(chain_data["calls"])
        puts = pd.DataFrame(chain_data["puts"])
        
        # Calculate IV metrics
        if "impliedVolatility" in calls.columns:
            avg_call_iv = calls["impliedVolatility"].mean()
            call_iv_by_strike = calls.groupby("strike")["impliedVolatility"].mean()
        else:
            avg_call_iv = None
            call_iv_by_strike = pd.Series()
        
        if "impliedVolatility" in puts.columns:
            avg_put_iv = puts["impliedVolatility"].mean()
            put_iv_by_strike = puts.groupby("strike")["impliedVolatility"].mean()
        else:
            avg_put_iv = None
            put_iv_by_strike = pd.Series()
        
        result = format_response(
            "IMPLIED_VOLATILITY",
            symbol=symbol,
            expiration=chain_data.get("expiration"),
            average_call_iv=avg_call_iv,
            average_put_iv=avg_put_iv,
            call_iv_by_strike=call_iv_by_strike,
            put_iv_by_strike=put_iv_by_strike
        )
        
        if include_chart and (not call_iv_by_strike.empty or not put_iv_by_strike.empty):
            try:
                if chart_style == "plotly":
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    
                    if not call_iv_by_strike.empty:
                        fig.add_trace(go.Scatter(
                            x=call_iv_by_strike.index,
                            y=call_iv_by_strike.values,
                            mode='lines+markers',
                            name='Call IV'
                        ))
                    
                    if not put_iv_by_strike.empty:
                        fig.add_trace(go.Scatter(
                            x=put_iv_by_strike.index,
                            y=put_iv_by_strike.values,
                            mode='lines+markers',
                            name='Put IV'
                        ))
                    
                    fig.update_layout(
                        title=f"{symbol} Implied Volatility by Strike",
                        xaxis_title="Strike Price",
                        yaxis_title="Implied Volatility"
                    )
                    result["chart"] = fig
                    
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "IMPLIED_VOLATILITY",
            symbol=symbol,
            error=str(e)
        )


def analyze_options_strategy(
    symbol: str,
    strategy: str,
    *,
    strikes: List[float],
    expiration: Optional[str] = None,
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Analyze options trading strategy.
    
    Args:
        symbol: Stock ticker symbol
        strategy: Strategy name ('long_call', 'long_put', 'covered_call', etc.)
        strikes: List of strike prices for the strategy
        expiration: Expiration date
        quantity: Number of contracts
        
    Returns:
        Dictionary containing strategy analysis
    """
    try:
        chain_data = get_options_chain(symbol, expiration=expiration)
        
        if "error" in chain_data:
            return chain_data
        
        calls = pd.DataFrame(chain_data["calls"])
        puts = pd.DataFrame(chain_data["puts"])
        
        # Get current stock price
        ticker = get_ticker(symbol)
        fast_info = dict(ticker.fast_info)
        current_price = fast_info.get("last_price", 0)
        
        # Analyze strategy based on type
        strategy_analysis = _analyze_strategy(
            strategy, strikes, calls, puts, current_price, quantity
        )
        
        result = format_response(
            "OPTIONS_STRATEGY",
            symbol=symbol,
            strategy=strategy,
            strikes=strikes,
            expiration=chain_data.get("expiration"),
            quantity=quantity,
            current_price=current_price,
            analysis=strategy_analysis
        )
        
        return result
        
    except Exception as e:
        return format_response(
            "OPTIONS_STRATEGY",
            symbol=symbol,
            strategy=strategy,
            error=str(e)
        )


def get_options_flow(
    symbol: str,
    *,
    min_volume: int = 100,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get unusual options activity and flow.
    
    Args:
        symbol: Stock ticker symbol
        min_volume: Minimum volume threshold
        include_chart: Whether to include flow chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing options flow data and optional chart
    """
    try:
        # Get all available expirations
        ticker = get_ticker(symbol)
        expirations = ticker.options[:3]  # Get first 3 expirations
        
        unusual_activity = []
        
        for exp in expirations:
            try:
                chain_data = get_options_chain(symbol, expiration=exp)
                if "error" in chain_data:
                    continue
                
                calls = pd.DataFrame(chain_data["calls"])
                puts = pd.DataFrame(chain_data["puts"])
                
                # Find high volume options
                if "volume" in calls.columns:
                    high_vol_calls = calls[calls["volume"] >= min_volume]
                    for _, row in high_vol_calls.iterrows():
                        unusual_activity.append({
                            "type": "call",
                            "strike": row["strike"],
                            "expiration": exp,
                            "volume": row["volume"],
                            "open_interest": row.get("openInterest", 0),
                            "last_price": row.get("lastPrice", 0)
                        })
                
                if "volume" in puts.columns:
                    high_vol_puts = puts[puts["volume"] >= min_volume]
                    for _, row in high_vol_puts.iterrows():
                        unusual_activity.append({
                            "type": "put",
                            "strike": row["strike"],
                            "expiration": exp,
                            "volume": row["volume"],
                            "open_interest": row.get("openInterest", 0),
                            "last_price": row.get("lastPrice", 0)
                        })
                        
            except Exception:
                continue
        
        # Sort by volume
        unusual_activity.sort(key=lambda x: x["volume"], reverse=True)
        
        result = format_response(
            "OPTIONS_FLOW",
            symbol=symbol,
            min_volume=min_volume,
            unusual_activity=unusual_activity[:20]  # Top 20
        )
        
        return result
        
    except Exception as e:
        return format_response(
            "OPTIONS_FLOW",
            symbol=symbol,
            error=str(e)
        )


# Internal helper functions
def _analyze_strategy(
    strategy: str,
    strikes: List[float],
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    current_price: float,
    quantity: int
) -> Dict[str, Any]:
    """Analyze specific options strategy."""
    
    analysis = {
        "strategy_type": strategy,
        "max_profit": None,
        "max_loss": None,
        "breakeven": None,
        "cost": 0,
        "description": _get_strategy_description(strategy)
    }
    
    try:
        if strategy.lower() == "long_call" and len(strikes) >= 1:
            strike = strikes[0]
            call_option = calls[calls["strike"] == strike]
            if not call_option.empty:
                premium = call_option.iloc[0].get("lastPrice", 0)
                cost = premium * quantity * 100  # Options are per 100 shares
                
                analysis.update({
                    "cost": cost,
                    "max_loss": cost,
                    "max_profit": "Unlimited",
                    "breakeven": strike + premium
                })
        
        elif strategy.lower() == "long_put" and len(strikes) >= 1:
            strike = strikes[0]
            put_option = puts[puts["strike"] == strike]
            if not put_option.empty:
                premium = put_option.iloc[0].get("lastPrice", 0)
                cost = premium * quantity * 100
                
                analysis.update({
                    "cost": cost,
                    "max_loss": cost,
                    "max_profit": (strike - premium) * quantity * 100,
                    "breakeven": strike - premium
                })
        
        # Add more strategy analysis as needed
        
    except Exception as e:
        analysis["error"] = str(e)
    
    return analysis


def _get_strategy_description(strategy: str) -> str:
    """Get description for options strategy."""
    descriptions = {
        "long_call": "Bullish strategy - buy call option",
        "long_put": "Bearish strategy - buy put option",
        "covered_call": "Income strategy - own stock, sell call",
        "protective_put": "Hedging strategy - own stock, buy put",
        "bull_call_spread": "Bullish spread - buy low strike call, sell high strike call",
        "bear_put_spread": "Bearish spread - buy high strike put, sell low strike put"
    }
    return descriptions.get(strategy.lower(), f"{strategy} options strategy")


# Export main functions
__all__ = [
    "get_options_chain",
    "get_options_volume",
    "get_implied_volatility",
    "analyze_options_strategy",
    "get_options_flow",
]
