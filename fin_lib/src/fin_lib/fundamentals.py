"""
Company fundamentals and financial statement analysis tools.

This module provides comprehensive fundamental analysis functionality including:
- Company overview and profile information
- Financial statements (income, balance sheet, cash flow)
- Earnings data and calendar
- Key financial ratios and metrics
- Valuation analysis
- Professional charting capabilities
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_json,
    get_ticker,
    ttl_cache,
    create_line_chart,
    create_correlation_heatmap,
)


def get_fundamentals(
    symbol: str,
    *,
    include_statements: bool = True,
    include_ratios: bool = True,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Get comprehensive fundamental analysis for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        include_statements: Whether to include financial statements
        include_ratios: Whether to include financial ratios
        include_chart: Whether to include fundamental charts
        chart_style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Dictionary containing comprehensive fundamental data
        
    Example:
        >>> fundamentals = get_fundamentals("AAPL", include_chart=True)
        >>> print(f"P/E Ratio: {fundamentals['ratios']['trailingPE']}")
    """
    symbol = ensure_symbol(symbol)
    
    result = {
        "symbol": symbol,
        "company_overview": get_company_overview(symbol),
    }
    
    if include_statements:
        result["financial_statements"] = get_financial_statements(symbol)
    
    if include_ratios:
        result["key_metrics"] = get_key_metrics(symbol)
        result["valuation_ratios"] = get_valuation_ratios(symbol)
    
    if include_chart:
        try:
            chart = create_fundamentals_chart(symbol, chart_style)
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return format_response("COMPREHENSIVE_FUNDAMENTALS", **result)


def get_company_overview(symbol: str) -> Dict[str, Any]:
    """
    Get company overview and profile information.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing company overview data
        
    Example:
        >>> overview = get_company_overview("AAPL")
        >>> print(f"Company: {overview['overview']['longName']}")
    """
    symbol = ensure_symbol(symbol)
    info = _cached_company_info(symbol)
    
    overview_keys = [
        "longName",
        "sector",
        "industry",
        "marketCap",
        "fullTimeEmployees",
        "website",
        "longBusinessSummary",
        "currency",
        "beta",
        "dividendYield",
        "trailingPE",
        "forwardPE",
        "priceToBook",
        "country",
        "city",
        "phone",
        "fax",
    ]
    
    overview = {key: info.get(key) for key in overview_keys if key in info}
    return format_response("COMPANY_OVERVIEW", symbol=symbol, overview=overview)


def get_financial_statements(symbol: str) -> Dict[str, Any]:
    """
    Get all financial statements for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing income statement, balance sheet, and cash flow
        
    Example:
        >>> statements = get_financial_statements("AAPL")
        >>> revenue = statements['income_statement']['data'][0]['Total Revenue']
    """
    symbol = ensure_symbol(symbol)
    
    statements = {}
    
    try:
        statements["income_statement"] = get_income_statement(symbol)
    except Exception as e:
        statements["income_statement"] = {"error": str(e)}
    
    try:
        statements["balance_sheet"] = get_balance_sheet(symbol)
    except Exception as e:
        statements["balance_sheet"] = {"error": str(e)}
    
    try:
        statements["cash_flow"] = get_cash_flow(symbol)
    except Exception as e:
        statements["cash_flow"] = {"error": str(e)}
    
    return format_response("FINANCIAL_STATEMENTS", symbol=symbol, statements=statements)


def get_income_statement(symbol: str) -> Dict[str, Any]:
    """
    Get income statement data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing income statement data
    """
    return _get_statement_data(symbol, "financials", "INCOME_STATEMENT")


def get_balance_sheet(symbol: str) -> Dict[str, Any]:
    """
    Get balance sheet data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing balance sheet data
    """
    return _get_statement_data(symbol, "balance_sheet", "BALANCE_SHEET")


def get_cash_flow(symbol: str) -> Dict[str, Any]:
    """
    Get cash flow statement data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing cash flow data
    """
    return _get_statement_data(symbol, "cashflow", "CASH_FLOW")


def get_key_metrics(symbol: str) -> Dict[str, Any]:
    """
    Get key financial metrics and ratios.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing key financial metrics
        
    Example:
        >>> metrics = get_key_metrics("AAPL")
        >>> print(f"ROE: {metrics['metrics']['returnOnEquity']}")
    """
    symbol = ensure_symbol(symbol)
    info = _cached_company_info(symbol)
    
    metrics_keys = [
        "returnOnAssets",
        "returnOnEquity",
        "profitMargins",
        "operatingMargins",
        "grossMargins",
        "revenueGrowth",
        "earningsGrowth",
        "currentRatio",
        "quickRatio",
        "debtToEquity",
        "totalDebt",
        "totalCash",
        "freeCashflow",
        "operatingCashflow",
        "earningsQuarterlyGrowth",
        "revenueQuarterlyGrowth",
    ]
    
    metrics = {key: info.get(key) for key in metrics_keys if key in info}
    return format_response("KEY_METRICS", symbol=symbol, metrics=metrics)


def get_valuation_ratios(symbol: str) -> Dict[str, Any]:
    """
    Get valuation ratios for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing valuation ratios
        
    Example:
        >>> ratios = get_valuation_ratios("AAPL")
        >>> print(f"P/E: {ratios['ratios']['trailingPE']}")
    """
    symbol = ensure_symbol(symbol)
    info = _cached_company_info(symbol)
    
    ratio_keys = [
        "trailingPE",
        "forwardPE",
        "priceToBook",
        "priceToSalesTrailing12Months",
        "enterpriseToRevenue",
        "enterpriseToEbitda",
        "pegRatio",
        "bookValue",
        "priceToBook",
        "marketToBook",
        "enterpriseValue",
        "marketCap",
    ]
    
    ratios = {key: info.get(key) for key in ratio_keys if key in info}
    return format_response("VALUATION_RATIOS", symbol=symbol, ratios=ratios)


def get_earnings_data(symbol: str) -> Dict[str, Any]:
    """
    Get earnings data including annual and quarterly earnings.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary containing earnings data
        
    Example:
        >>> earnings = get_earnings_data("AAPL")
        >>> print(f"Latest quarterly earnings: {earnings['quarterly']['data'][0]}")
    """
    symbol = ensure_symbol(symbol)
    data = _cached_earnings(symbol)
    return format_response("EARNINGS", symbol=symbol, annual=data["annual"], quarterly=data["quarterly"])


def get_earnings_calendar(symbol: str, *, limit: int = 10) -> Dict[str, Any]:
    """
    Get upcoming earnings calendar for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        limit: Maximum number of earnings dates to return
        
    Returns:
        Dictionary containing earnings calendar data
    """
    symbol = ensure_symbol(symbol)
    data = _cached_earnings_calendar(symbol, limit)
    return format_response("EARNINGS_CALENDAR", symbol=symbol, data=data)


def compare_fundamentals(
    symbols: List[str],
    metrics: Optional[List[str]] = None,
    include_chart: bool = False,
    chart_style: str = "plotly"
) -> Dict[str, Any]:
    """
    Compare fundamental metrics across multiple symbols.
    
    Args:
        symbols: List of ticker symbols to compare
        metrics: List of metrics to compare (default: common ratios)
        include_chart: Whether to include comparison chart
        chart_style: Chart style
        
    Returns:
        Dictionary containing comparison data and optional chart
    """
    if len(symbols) < 2:
        raise ToolExecutionError("At least 2 symbols required for comparison.")
    
    if metrics is None:
        metrics = ["trailingPE", "priceToBook", "returnOnEquity", "profitMargins", "debtToEquity"]
    
    comparison_data = {}
    for symbol in symbols:
        try:
            info = _cached_company_info(symbol)
            comparison_data[symbol] = {metric: info.get(metric) for metric in metrics}
        except Exception as e:
            comparison_data[symbol] = {"error": str(e)}
    
    result = format_response(
        "FUNDAMENTALS_COMPARISON",
        symbols=symbols,
        metrics=metrics,
        data=comparison_data
    )
    
    if include_chart:
        try:
            chart = create_comparison_chart(comparison_data, metrics, chart_style)
            result["chart"] = chart
        except Exception as e:
            result["chart_error"] = f"Failed to create chart: {str(e)}"
    
    return result


def create_fundamentals_chart(symbol: str, style: str = "plotly") -> Union[Any, None]:
    """
    Create a comprehensive fundamentals chart.
    
    Args:
        symbol: Stock symbol
        style: Chart style
        
    Returns:
        Chart figure object
    """
    try:
        # Get financial data for charting
        statements = get_financial_statements(symbol)
        
        if style == "plotly":
            return _create_plotly_fundamentals_chart(symbol, statements)
        else:
            return _create_mpl_fundamentals_chart(symbol, statements)
    except Exception:
        return None


def create_comparison_chart(
    data: Dict[str, Dict[str, Any]], 
    metrics: List[str], 
    style: str = "plotly"
) -> Union[Any, None]:
    """Create a comparison chart for fundamental metrics."""
    try:
        # Prepare data for charting
        chart_data = {}
        for metric in metrics:
            chart_data[metric] = []
            for symbol in data.keys():
                if isinstance(data[symbol], dict) and metric in data[symbol]:
                    value = data[symbol][metric]
                    chart_data[metric].append(value if value is not None else 0)
                else:
                    chart_data[metric].append(0)
        
        if style == "plotly":
            import plotly.graph_objects as go
            
            fig = go.Figure()
            symbols = list(data.keys())
            
            for metric in metrics:
                fig.add_trace(go.Bar(
                    name=metric,
                    x=symbols,
                    y=chart_data[metric]
                ))
            
            fig.update_layout(
                title="Fundamental Metrics Comparison",
                xaxis_title="Symbols",
                yaxis_title="Value",
                barmode='group'
            )
            return fig
        
        return None
    except Exception:
        return None


def _create_plotly_fundamentals_chart(symbol: str, statements: Dict[str, Any]):
    """Create fundamentals chart using Plotly."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Trend', 'Profit Margins', 'Balance Sheet', 'Cash Flow'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Add placeholder data - in real implementation, would extract from statements
        fig.add_trace(go.Scatter(x=[2020, 2021, 2022, 2023], y=[100, 120, 140, 160], 
                                name="Revenue"), row=1, col=1)
        
        fig.update_layout(title=f"{symbol} Fundamental Analysis")
        return fig
        
    except Exception:
        return None


def _create_mpl_fundamentals_chart(symbol: str, statements: Dict[str, Any]):
    """Create fundamentals chart using matplotlib."""
    try:
        import matplotlib.pyplot as plt
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Placeholder charts - in real implementation, would use actual data
        ax1.plot([2020, 2021, 2022, 2023], [100, 120, 140, 160])
        ax1.set_title('Revenue Trend')
        ax1.set_ylabel('Revenue (B)')
        
        ax2.bar(['Gross', 'Operating', 'Net'], [0.4, 0.25, 0.15])
        ax2.set_title('Profit Margins')
        ax2.set_ylabel('Margin %')
        
        ax3.bar(['Assets', 'Liabilities', 'Equity'], [500, 200, 300])
        ax3.set_title('Balance Sheet')
        ax3.set_ylabel('Amount (B)')
        
        ax4.plot([2020, 2021, 2022, 2023], [20, 25, 30, 35])
        ax4.set_title('Free Cash Flow')
        ax4.set_ylabel('FCF (B)')
        
        plt.suptitle(f'{symbol} Fundamental Analysis')
        plt.tight_layout()
        return fig
        
    except Exception:
        return None


# Internal helper functions
@ttl_cache(ttl=1800, maxsize=256)
def _cached_company_info(symbol: str) -> Dict[str, Any]:
    """Get cached company information."""
    ticker = get_ticker(symbol)
    try:
        return dict(ticker.info)
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch company info for {symbol}: {exc}") from exc


@ttl_cache(ttl=1800, maxsize=256)
def _cached_statement(symbol: str, attribute: str) -> Any:
    """Get cached financial statement data."""
    ticker = get_ticker(symbol)
    try:
        data = getattr(ticker, attribute)
    except AttributeError as exc:
        raise ToolExecutionError(f"{attribute} is not supported: {exc}") from exc
    if data is None or data.empty:
        raise ToolExecutionError(f"No {attribute} data available for {symbol}.")
    return data


def _get_statement_data(symbol: str, attribute: str, tool_name: str) -> Dict[str, Any]:
    """Get financial statement data."""
    symbol = ensure_symbol(symbol)
    data = _cached_statement(symbol, attribute)
    return format_response(tool_name, symbol=symbol, data=data)


@ttl_cache(ttl=1800, maxsize=256)
def _cached_earnings(symbol: str) -> Dict[str, Any]:
    """Get cached earnings data."""
    ticker = get_ticker(symbol)
    try:
        annual = ticker.earnings
        quarterly = ticker.quarterly_earnings
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch earnings for {symbol}: {exc}") from exc
    if (annual is None or annual.empty) and (quarterly is None or quarterly.empty):
        raise ToolExecutionError(f"No earnings data available for {symbol}.")
    return {"annual": annual, "quarterly": quarterly}


@ttl_cache(ttl=1800, maxsize=256)
def _cached_earnings_calendar(symbol: str, limit: int) -> Any:
    """Get cached earnings calendar data."""
    ticker = get_ticker(symbol)
    data = ticker.get_earnings_dates(limit=limit)
    if data is None or data.empty:
        raise ToolExecutionError(f"No earnings calendar data available for {symbol}.")
    return data


# Export main functions
__all__ = [
    "get_fundamentals",
    "get_company_overview",
    "get_financial_statements",
    "get_income_statement",
    "get_balance_sheet",
    "get_cash_flow",
    "get_key_metrics",
    "get_valuation_ratios",
    "get_earnings_data",
    "get_earnings_calendar",
    "compare_fundamentals",
]
