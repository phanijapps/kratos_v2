"""
Advanced analytics and alpha intelligence tools.

This module provides sophisticated financial analysis functionality including:
- Advanced statistical analysis
- Risk metrics and portfolio analytics
- Market regime detection
- Alpha generation strategies
- Professional charting capabilities
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_ticker,
    history,
    ttl_cache,
    create_line_chart,
    create_correlation_heatmap,
)


def calculate_alpha_beta(
    symbol: str,
    benchmark: str = "^GSPC",
    *,
    period: str = "2y",
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Calculate alpha and beta relative to a benchmark.
    
    Args:
        symbol: Stock ticker symbol
        benchmark: Benchmark symbol (default: S&P 500)
        period: Time period for analysis
        include_chart: Whether to include regression chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing alpha, beta, and regression analysis
        
    Example:
        >>> analysis = calculate_alpha_beta("AAPL", "^GSPC", period="1y")
        >>> print(f"Alpha: {analysis['alpha']}, Beta: {analysis['beta']}")
    """
    try:
        # Get historical data for both symbol and benchmark
        symbol_data = history(symbol, interval="1d", period=period)
        benchmark_data = history(benchmark, interval="1d", period=period)
        
        if symbol_data.empty or benchmark_data.empty:
            raise ToolExecutionError("Insufficient data for alpha/beta calculation")
        
        # Calculate returns
        symbol_returns = symbol_data["Close"].pct_change().dropna()
        benchmark_returns = benchmark_data["Close"].pct_change().dropna()
        
        # Align data
        aligned_data = pd.DataFrame({
            "symbol": symbol_returns,
            "benchmark": benchmark_returns
        }).dropna()
        
        if len(aligned_data) < 30:
            raise ToolExecutionError("Insufficient aligned data for regression analysis")
        
        # Calculate beta using linear regression
        covariance = aligned_data["symbol"].cov(aligned_data["benchmark"])
        benchmark_variance = aligned_data["benchmark"].var()
        beta = covariance / benchmark_variance
        
        # Calculate alpha (annualized)
        symbol_mean_return = aligned_data["symbol"].mean() * 252
        benchmark_mean_return = aligned_data["benchmark"].mean() * 252
        alpha = symbol_mean_return - beta * benchmark_mean_return
        
        # Calculate R-squared
        correlation = aligned_data["symbol"].corr(aligned_data["benchmark"])
        r_squared = correlation ** 2
        
        # Calculate tracking error
        tracking_error = (aligned_data["symbol"] - beta * aligned_data["benchmark"]).std() * np.sqrt(252)
        
        result = format_response(
            "ALPHA_BETA_ANALYSIS",
            symbol=symbol,
            benchmark=benchmark,
            period=period,
            alpha=alpha,
            beta=beta,
            r_squared=r_squared,
            correlation=correlation,
            tracking_error=tracking_error,
            data_points=len(aligned_data)
        )
        
        if include_chart:
            try:
                if chart_style == "plotly":
                    import plotly.graph_objects as go
                    import plotly.express as px
                    
                    # Create scatter plot with regression line
                    fig = px.scatter(
                        x=aligned_data["benchmark"],
                        y=aligned_data["symbol"],
                        title=f"{symbol} vs {benchmark} Regression",
                        labels={"x": f"{benchmark} Returns", "y": f"{symbol} Returns"}
                    )
                    
                    # Add regression line
                    x_range = np.linspace(aligned_data["benchmark"].min(), aligned_data["benchmark"].max(), 100)
                    y_line = alpha/252 + beta * x_range
                    fig.add_trace(go.Scatter(
                        x=x_range,
                        y=y_line,
                        mode='lines',
                        name=f'Regression Line (β={beta:.2f})',
                        line=dict(color='red')
                    ))
                    
                    result["chart"] = fig
                    
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "ALPHA_BETA_ANALYSIS",
            symbol=symbol,
            benchmark=benchmark,
            error=str(e)
        )


def calculate_sharpe_ratio(
    symbol: str,
    *,
    period: str = "1y",
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate Sharpe ratio for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period for analysis
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        Dictionary containing Sharpe ratio and related metrics
    """
    try:
        data = history(symbol, interval="1d", period=period)
        
        if data.empty:
            raise ToolExecutionError("No data available for Sharpe ratio calculation")
        
        # Calculate returns
        returns = data["Close"].pct_change().dropna()
        
        if len(returns) < 30:
            raise ToolExecutionError("Insufficient data for Sharpe ratio calculation")
        
        # Calculate metrics
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        
        # Additional risk metrics
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return format_response(
            "SHARPE_RATIO_ANALYSIS",
            symbol=symbol,
            period=period,
            annual_return=annual_return,
            annual_volatility=annual_volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            risk_free_rate=risk_free_rate
        )
        
    except Exception as e:
        return format_response(
            "SHARPE_RATIO_ANALYSIS",
            symbol=symbol,
            error=str(e)
        )


def detect_market_regime(
    symbol: str = "^GSPC",
    *,
    period: str = "2y",
    window: int = 60,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Detect market regimes using volatility and trend analysis.
    
    Args:
        symbol: Market index symbol (default: S&P 500)
        period: Time period for analysis
        window: Rolling window for regime detection
        include_chart: Whether to include regime chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing regime analysis and optional chart
    """
    try:
        data = history(symbol, interval="1d", period=period)
        
        if data.empty or len(data) < window * 2:
            raise ToolExecutionError("Insufficient data for regime detection")
        
        # Calculate returns and volatility
        returns = data["Close"].pct_change().dropna()
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        rolling_return = returns.rolling(window=window).mean() * 252
        
        # Define regime thresholds
        vol_median = rolling_vol.median()
        return_median = rolling_return.median()
        
        # Classify regimes
        regimes = []
        for i in range(len(rolling_vol)):
            vol = rolling_vol.iloc[i]
            ret = rolling_return.iloc[i]
            
            if pd.isna(vol) or pd.isna(ret):
                regimes.append("Unknown")
            elif vol > vol_median and ret > return_median:
                regimes.append("Bull Volatile")
            elif vol > vol_median and ret <= return_median:
                regimes.append("Bear Volatile")
            elif vol <= vol_median and ret > return_median:
                regimes.append("Bull Calm")
            else:
                regimes.append("Bear Calm")
        
        # Current regime
        current_regime = regimes[-1] if regimes else "Unknown"
        
        # Regime statistics
        regime_counts = pd.Series(regimes).value_counts()
        regime_percentages = (regime_counts / len(regimes) * 100).round(2)
        
        result = format_response(
            "MARKET_REGIME_DETECTION",
            symbol=symbol,
            period=period,
            window=window,
            current_regime=current_regime,
            regime_history=regimes[-30:],  # Last 30 periods
            regime_statistics=regime_percentages.to_dict(),
            vol_threshold=vol_median,
            return_threshold=return_median
        )
        
        if include_chart:
            try:
                if chart_style == "plotly":
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        subplot_titles=('Price', 'Rolling Volatility', 'Rolling Returns'),
                        vertical_spacing=0.05
                    )
                    
                    # Price chart
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data["Close"],
                        name="Price"
                    ), row=1, col=1)
                    
                    # Volatility chart
                    fig.add_trace(go.Scatter(
                        x=rolling_vol.index,
                        y=rolling_vol,
                        name="Volatility"
                    ), row=2, col=1)
                    
                    # Returns chart
                    fig.add_trace(go.Scatter(
                        x=rolling_return.index,
                        y=rolling_return,
                        name="Returns"
                    ), row=3, col=1)
                    
                    fig.update_layout(title=f"{symbol} Market Regime Analysis")
                    result["chart"] = fig
                    
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "MARKET_REGIME_DETECTION",
            symbol=symbol,
            error=str(e)
        )


def portfolio_optimization(
    symbols: List[str],
    *,
    period: str = "1y",
    method: str = "max_sharpe",
    risk_free_rate: float = 0.02,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Perform portfolio optimization using Modern Portfolio Theory.
    
    Args:
        symbols: List of ticker symbols
        period: Time period for analysis
        method: Optimization method ('max_sharpe', 'min_vol', 'equal_weight')
        risk_free_rate: Risk-free rate
        include_chart: Whether to include efficient frontier chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing optimal portfolio weights and metrics
    """
    try:
        if len(symbols) < 2:
            raise ToolExecutionError("At least 2 symbols required for portfolio optimization")
        
        # Get price data for all symbols
        price_data = {}
        for symbol in symbols:
            try:
                data = history(symbol, interval="1d", period=period)
                if not data.empty:
                    price_data[symbol] = data["Close"]
            except Exception:
                continue
        
        if len(price_data) < 2:
            raise ToolExecutionError("Insufficient data for portfolio optimization")
        
        # Create returns matrix
        prices_df = pd.DataFrame(price_data).dropna()
        returns_df = prices_df.pct_change().dropna()
        
        if len(returns_df) < 30:
            raise ToolExecutionError("Insufficient return data for optimization")
        
        # Calculate expected returns and covariance matrix
        expected_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        # Optimize portfolio based on method
        if method == "equal_weight":
            weights = np.array([1/len(symbols)] * len(symbols))
        elif method == "max_sharpe":
            weights = _optimize_max_sharpe(expected_returns, cov_matrix, risk_free_rate)
        elif method == "min_vol":
            weights = _optimize_min_volatility(cov_matrix)
        else:
            raise ToolExecutionError(f"Unknown optimization method: {method}")
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(expected_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_vol
        
        # Create weights dictionary
        weights_dict = {symbol: float(weight) for symbol, weight in zip(symbols, weights)}
        
        result = format_response(
            "PORTFOLIO_OPTIMIZATION",
            symbols=symbols,
            period=period,
            method=method,
            weights=weights_dict,
            expected_return=portfolio_return,
            volatility=portfolio_vol,
            sharpe_ratio=sharpe_ratio,
            risk_free_rate=risk_free_rate
        )
        
        if include_chart:
            try:
                # Create correlation heatmap
                corr_matrix = returns_df.corr()
                chart = create_correlation_heatmap(
                    corr_matrix,
                    title="Portfolio Correlation Matrix",
                    style=chart_style
                )
                result["chart"] = chart
                
            except Exception as e:
                result["chart_error"] = f"Failed to create chart: {str(e)}"
        
        return result
        
    except Exception as e:
        return format_response(
            "PORTFOLIO_OPTIMIZATION",
            symbols=symbols,
            error=str(e)
        )


def calculate_var(
    symbol: str,
    *,
    period: str = "1y",
    confidence_level: float = 0.05,
    method: str = "historical"
) -> Dict[str, Any]:
    """
    Calculate Value at Risk (VaR) for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period for analysis
        confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
        method: VaR calculation method ('historical', 'parametric')
        
    Returns:
        Dictionary containing VaR metrics
    """
    try:
        data = history(symbol, interval="1d", period=period)
        
        if data.empty:
            raise ToolExecutionError("No data available for VaR calculation")
        
        returns = data["Close"].pct_change().dropna()
        
        if len(returns) < 30:
            raise ToolExecutionError("Insufficient data for VaR calculation")
        
        if method == "historical":
            var = np.percentile(returns, confidence_level * 100)
        elif method == "parametric":
            mean_return = returns.mean()
            std_return = returns.std()
            from scipy import stats
            var = stats.norm.ppf(confidence_level, mean_return, std_return)
        else:
            raise ToolExecutionError(f"Unknown VaR method: {method}")
        
        # Calculate Conditional VaR (Expected Shortfall)
        cvar = returns[returns <= var].mean()
        
        # Annualize VaR
        var_annual = var * np.sqrt(252)
        cvar_annual = cvar * np.sqrt(252)
        
        return format_response(
            "VALUE_AT_RISK",
            symbol=symbol,
            period=period,
            confidence_level=confidence_level,
            method=method,
            daily_var=var,
            daily_cvar=cvar,
            annual_var=var_annual,
            annual_cvar=cvar_annual,
            data_points=len(returns)
        )
        
    except Exception as e:
        return format_response(
            "VALUE_AT_RISK",
            symbol=symbol,
            error=str(e)
        )


# Internal helper functions
def _optimize_max_sharpe(expected_returns: pd.Series, cov_matrix: pd.DataFrame, risk_free_rate: float) -> np.ndarray:
    """Optimize portfolio for maximum Sharpe ratio."""
    from scipy.optimize import minimize
    
    n_assets = len(expected_returns)
    
    def neg_sharpe(weights):
        portfolio_return = np.sum(expected_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(portfolio_return - risk_free_rate) / portfolio_vol
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1/n_assets] * n_assets)
    
    result = minimize(neg_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x


def _optimize_min_volatility(cov_matrix: pd.DataFrame) -> np.ndarray:
    """Optimize portfolio for minimum volatility."""
    from scipy.optimize import minimize
    
    n_assets = len(cov_matrix)
    
    def portfolio_vol(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1/n_assets] * n_assets)
    
    result = minimize(portfolio_vol, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x


# Export main functions
__all__ = [
    "calculate_alpha_beta",
    "calculate_sharpe_ratio",
    "detect_market_regime",
    "portfolio_optimization",
    "calculate_var",
]
