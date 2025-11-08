"""
Shared utilities for financial tools.

This module centralizes core helpers such as caching, serialization, parameter validation,
and charting utilities so that individual category handlers can remain focused on 
domain-specific logic.
"""

from __future__ import annotations

import datetime as _dt
import time
from collections import OrderedDict
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd
import yfinance as yf

# Optional charting dependencies
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import mplfinance as mpf
    HAS_MPLFINANCE = True
except ImportError:
    HAS_MPLFINANCE = False

DataFrameLike = Union[pd.DataFrame, pd.Series]


class ToolExecutionError(Exception):
    """Raised when a financial tool fails to fulfill a request."""


def _clone(value: Any) -> Any:
    """Deep clone pandas objects and other data structures."""
    if isinstance(value, (pd.DataFrame, pd.Series)):
        return value.copy(deep=True)
    if isinstance(value, dict):
        return {key: _clone(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_clone(item) for item in value]
    return value


def ttl_cache(ttl: int = 300, maxsize: int = 128) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Lightweight TTL cache that stores the most recent results.

    Args:
        ttl: seconds before a cached item expires.
        maxsize: maximum number of cached entries.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: "OrderedDict[Tuple[Any, ...], Tuple[Any, float]]" = OrderedDict()

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                value, timestamp = cache[key]
                if now - timestamp < ttl:
                    cache.move_to_end(key)
                    return _clone(value)
                del cache[key]
            result = func(*args, **kwargs)
            cached_value = _clone(result)
            cache[key] = (cached_value, now)
            cache.move_to_end(key)
            while len(cache) > maxsize:
                cache.popitem(last=False)
            return _clone(cached_value)

        def cache_clear() -> None:
            cache.clear()

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        return wrapper

    return decorator


def _isoformat(value: Union[_dt.datetime, _dt.date, pd.Timestamp]) -> str:
    """Convert datetime objects to ISO format strings."""
    if isinstance(value, pd.Timestamp):
        if value.tzinfo is not None:
            value = value.tz_convert(None)
        value = value.to_pydatetime()
    if isinstance(value, _dt.datetime):
        if value.tzinfo is not None:
            value = value.astimezone(_dt.timezone.utc).replace(tzinfo=None)
        return value.isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    raise TypeError(f"Unsupported temporal type: {type(value)!r}")


def to_serializable_records(data: DataFrameLike) -> List[Dict[str, Any]]:
    """Convert a pandas DataFrame/Series to JSON-friendly dict records."""
    if isinstance(data, pd.Series):
        frame = data.to_frame(name=data.name or "value")
    else:
        frame = data.copy()
    frame = frame.reset_index(drop=False)
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = frame[column].apply(_isoformat)
        elif pd.api.types.is_object_dtype(frame[column]):
            frame[column] = frame[column].apply(
                lambda v: _isoformat(v) if isinstance(v, (pd.Timestamp, _dt.datetime, _dt.date)) else v
            )
    frame = frame.where(pd.notnull(frame), None)
    return frame.to_dict(orient="records")


def ensure_symbol(symbol: str) -> str:
    """Validate and normalize ticker symbol."""
    if not symbol or not isinstance(symbol, str):
        raise ToolExecutionError("A valid ticker symbol must be provided.")
    return symbol.upper().strip()


def validate_period_inputs(
    start: Optional[str], end: Optional[str], period: Optional[str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Validate that period inputs are mutually exclusive."""
    if period and (start or end):
        raise ToolExecutionError("Provide either start/end or period, not both.")
    return start, end, period


@lru_cache(maxsize=512)
def get_ticker(symbol: str) -> yf.Ticker:
    """Get yfinance Ticker object with caching."""
    try:
        return yf.Ticker(symbol)
    except Exception as exc:  # pragma: no cover - defensive
        raise ToolExecutionError(f"Failed to initialize ticker for {symbol}: {exc}") from exc


@ttl_cache(ttl=600, maxsize=256)
def _cached_history(
    symbol: str,
    interval: str,
    start: Optional[str],
    end: Optional[str],
    period: Optional[str],
    include_actions: bool,
    auto_adjust: bool,
) -> pd.DataFrame:
    """Cached historical data retrieval."""
    ticker = get_ticker(symbol)
    history = ticker.history(
        start=start,
        end=end,
        period=period,
        interval=interval,
        auto_adjust=auto_adjust,
        actions=include_actions,
    )
    if history.empty:
        raise ToolExecutionError(f"No historical data returned for {symbol}.")
    history.index.name = "timestamp"
    return history


def history(
    symbol: str,
    *,
    interval: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: Optional[str] = None,
    include_actions: bool = True,
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Get historical price data for a symbol."""
    symbol = ensure_symbol(symbol)
    start, end, period = validate_period_inputs(start, end, period)
    return _cached_history(symbol, interval, start, end, period, include_actions, auto_adjust)


@ttl_cache(ttl=600, maxsize=256)
def _cached_download(
    tickers: Tuple[str, ...],
    start: Optional[str],
    end: Optional[str],
    period: Optional[str],
    interval: str,
) -> pd.DataFrame:
    """Cached bulk data download."""
    data = yf.download(
        tickers=",".join(tickers),
        start=start,
        end=end,
        period=period,
        interval=interval,
    )
    if data.empty:
        raise ToolExecutionError(f"No data returned for {','.join(tickers)}.")
    return data


def download(
    symbols: Iterable[str],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: Optional[str] = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download historical data for multiple symbols."""
    tickers = tuple(ensure_symbol(symbol) for symbol in symbols)
    start, end, period = validate_period_inputs(start, end, period)
    return _cached_download(tickers, start, end, period, interval)


@ttl_cache(ttl=600, maxsize=128)
def get_json(url: str) -> Dict[str, Any]:
    """Fetch JSON data from URL with error handling."""
    import requests
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 429:
            # Rate limit - return structured error that agent can handle
            return {
                "error": "rate_limit",
                "message": "Yahoo Finance API rate limit exceeded. Please try again later.",
                "status_code": 429,
                "url": url,
                "retry_after": exc.response.headers.get("Retry-After", "60")
            }
        elif exc.response.status_code >= 500:
            # Server error - temporary issue
            return {
                "error": "server_error", 
                "message": f"Yahoo Finance server error ({exc.response.status_code}). Service may be temporarily unavailable.",
                "status_code": exc.response.status_code,
                "url": url
            }
        else:
            # Client error - likely permanent issue
            raise ToolExecutionError(f"HTTP {exc.response.status_code} error from {url}: {exc}")
    except requests.exceptions.Timeout:
        return {
            "error": "timeout",
            "message": "Request to Yahoo Finance timed out. The service may be slow or unavailable.",
            "url": url
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "connection_error",
            "message": "Could not connect to Yahoo Finance. Please check your internet connection.",
            "url": url
        }
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch data from {url}: {exc}") from exc
    
    if not isinstance(data, dict):
        raise ToolExecutionError(f"Unexpected response from {url}")
    return data


def format_response(tool_name: str, **payload: Any) -> Dict[str, Any]:
    """Format tool response with serialized data."""
    serialized: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (pd.DataFrame, pd.Series)):
            serialized[key] = to_serializable_records(value)
        else:
            serialized[key] = value
    return {"tool": tool_name, **serialized}


# Charting utilities
def create_candlestick_chart(
    data: pd.DataFrame,
    symbol: str,
    title: Optional[str] = None,
    show_volume: bool = True,
    style: str = "plotly"
) -> Union[go.Figure, plt.Figure]:
    """
    Create a candlestick chart from OHLCV data.
    
    Args:
        data: DataFrame with OHLCV columns
        symbol: Stock symbol for title
        title: Custom chart title
        show_volume: Whether to show volume subplot
        style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Chart figure object
    """
    if style == "plotly":
        return _create_plotly_candlestick(data, symbol, title, show_volume)
    else:
        return _create_mpl_candlestick(data, symbol, title, show_volume)


def _create_plotly_candlestick(
    data: pd.DataFrame, symbol: str, title: Optional[str], show_volume: bool
) -> Optional[Any]:
    """Create candlestick chart using Plotly."""
    if not HAS_PLOTLY:
        return None
        
    if show_volume and 'Volume' in data.columns:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(title or f'{symbol} Price', 'Volume'),
            row_width=[0.2, 0.7]
        )
        
        # Candlestick
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
        
        # Volume
        fig.add_trace(
            go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='lightblue'),
            row=2, col=1
        )
    else:
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        fig.update_layout(title=title or f'{symbol} Price Chart')
    
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def _create_mpl_candlestick(
    data: pd.DataFrame, symbol: str, title: Optional[str], show_volume: bool
) -> Optional[Any]:
    """Create candlestick chart using mplfinance."""
    if not HAS_MPLFINANCE:
        return None
        
    kwargs = {
        'type': 'candle',
        'style': 'charles',
        'title': title or f'{symbol} Price Chart',
        'ylabel': 'Price ($)',
        'volume': show_volume,
        'returnfig': True
    }
    
    fig, axes = mpf.plot(data, **kwargs)
    return fig


def create_line_chart(
    data: Union[pd.DataFrame, pd.Series],
    title: str,
    x_label: str = "Date",
    y_label: str = "Value",
    style: str = "plotly"
) -> Optional[Any]:
    """
    Create a line chart from time series data.
    
    Args:
        data: Time series data
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Chart figure object or None if dependencies missing
    """
    if style == "plotly" and HAS_PLOTLY:
        if isinstance(data, pd.Series):
            fig = px.line(x=data.index, y=data.values, title=title)
            fig.update_xaxes(title=x_label)
            fig.update_yaxes(title=y_label)
        else:
            fig = px.line(data, title=title)
        return fig
    elif style == "matplotlib" and HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(12, 6))
        if isinstance(data, pd.Series):
            ax.plot(data.index, data.values)
        else:
            for col in data.columns:
                ax.plot(data.index, data[col], label=col)
            ax.legend()
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    else:
        return None


def create_correlation_heatmap(
    data: pd.DataFrame,
    title: str = "Correlation Matrix",
    style: str = "plotly"
) -> Optional[Any]:
    """
    Create a correlation heatmap.
    
    Args:
        data: DataFrame with numeric columns
        title: Chart title
        style: Chart style ('plotly' or 'matplotlib')
        
    Returns:
        Chart figure object or None if dependencies missing
    """
    corr = data.corr()
    
    if style == "plotly" and HAS_PLOTLY:
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title=title,
            color_continuous_scale="RdBu"
        )
        return fig
    elif style == "matplotlib" and HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='RdBu', center=0, ax=ax)
        ax.set_title(title)
        plt.tight_layout()
        return fig
    else:
        return None


def clear_caches() -> None:
    """Utility to clear all TTL/LRU caches (mainly for testing)."""
    _cached_history.cache_clear()
    _cached_download.cache_clear()
    get_json.cache_clear()
    get_ticker.cache_clear()  # type: ignore[attr-defined]


__all__ = [
    "DataFrameLike",
    "ToolExecutionError",
    "ensure_symbol",
    "history",
    "download",
    "get_ticker",
    "format_response",
    "to_serializable_records",
    "ttl_cache",
    "get_json",
    "clear_caches",
    "create_candlestick_chart",
    "create_line_chart",
    "create_correlation_heatmap",
]
