"""
fin_lib - Professional Financial Analysis Library

A comprehensive financial analysis library designed for AI agents and quantitative analysis.
Provides clean APIs for stock market data, technical analysis, fundamental analysis,
forex, crypto, commodities, and economic indicators.

Key Features:
- Real-time and historical market data
- Technical analysis indicators and patterns
- Fundamental analysis metrics
- Multi-asset class support (stocks, forex, crypto, commodities)
- Professional charting and visualization
- AI agent optimized APIs
- Comprehensive error handling and caching

Quick Start:
    >>> import fin_lib as fl
    >>> 
    >>> # Get stock quote
    >>> quote = fl.get_quote("AAPL")
    >>> 
    >>> # Get historical data with technical indicators
    >>> data = fl.get_historical_data("AAPL", period="1y")
    >>> 
    >>> # Perform technical analysis
    >>> analysis = fl.technical_analysis("AAPL", indicators=["RSI", "MACD", "SMA"])
    >>> 
    >>> # Get fundamental metrics
    >>> fundamentals = fl.get_fundamentals("AAPL")

Modules:
    - core: Stock market data and quotes
    - technical: Technical analysis indicators
    - fundamentals: Company fundamental analysis
    - forex: Foreign exchange data
    - crypto: Cryptocurrency data
    - commodities: Commodity prices and data
    - economics: Economic indicators
    - options: Options analysis
    - alpha_intelligence: Advanced analytics
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Kratos Financial Tools"
__email__ = "dev@kratos.ai"

# Core imports for main API
from .base import ToolExecutionError, clear_caches
from .core import (
    get_quote,
    get_historical_data,
    get_bulk_quotes,
    search_symbols,
    get_market_status,
)
from .technical import (
    technical_analysis,
    get_technical_indicators,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
)
from .fundamentals import (
    get_fundamentals,
    get_financial_statements,
    get_key_metrics,
    get_valuation_ratios,
)

# Import submodules for direct access (e.g., fl.forex.get_exchange_rate)
from . import forex
from . import crypto
from . import commodities
from . import economics
from . import options
from . import alpha_intelligence

# Module-level convenience functions
def get_stock_data(symbol: str, period: str = "1y", include_technicals: bool = False) -> dict:
    """
    Get comprehensive stock data including price history and optionally technical indicators.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        include_technicals: Whether to include technical analysis
        
    Returns:
        Dictionary containing historical data and optional technical indicators
    """
    data = get_historical_data(symbol, period=period)
    
    if include_technicals:
        technicals = technical_analysis(symbol, period=period)
        data["technical_analysis"] = technicals
    
    return data

def get_market_overview(symbols: list[str]) -> dict:
    """
    Get market overview for multiple symbols.
    
    Args:
        symbols: List of ticker symbols
        
    Returns:
        Dictionary containing quotes and market status
    """
    quotes = get_bulk_quotes(symbols)
    status = get_market_status()
    
    return {
        "quotes": quotes,
        "market_status": status,
        "timestamp": status.get("status", {}).get("timestamp_utc")
    }

# Export main API functions
__all__ = [
    # Core functions
    "get_quote",
    "get_historical_data", 
    "get_bulk_quotes",
    "search_symbols",
    "get_market_status",
    
    # Technical analysis
    "technical_analysis",
    "get_technical_indicators",
    "calculate_rsi",
    "calculate_macd", 
    "calculate_bollinger_bands",
    
    # Fundamental analysis
    "get_fundamentals",
    "get_financial_statements",
    "get_key_metrics",
    "get_valuation_ratios",
    
    # Convenience functions
    "get_stock_data",
    "get_market_overview",
    
    # Utilities
    "ToolExecutionError",
    "clear_caches",
    
    # Version info
    "__version__",
]
