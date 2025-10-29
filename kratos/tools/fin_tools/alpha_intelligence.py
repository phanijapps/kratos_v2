"""
Handlers for alpha intelligence focused tools such as news, movers, and analytics.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_json,
    get_ticker,
    history,
    ttl_cache,
)

_POSITIVE_WORDS = {"beat", "strong", "surge", "growth", "record", "outperform", "upgrade", "bullish"}
_NEGATIVE_WORDS = {"miss", "weak", "drop", "decline", "downgrade", "bearish", "lawsuit", "loss"}


def _compute_sentiment(text: str) -> float:
    if not text:
        return 0.0
    words = {word.strip(".,!?").lower() for word in text.split()}
    pos_hits = len(words & _POSITIVE_WORDS)
    neg_hits = len(words & _NEGATIVE_WORDS)
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    return round((pos_hits - neg_hits) / total, 3)


@ttl_cache(ttl=600, maxsize=128)
def _cached_news(symbol: str, limit: int) -> List[Dict[str, Any]]:
    ticker = get_ticker(symbol)
    try:
        news_items = ticker.news or []
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch news for {symbol}: {exc}") from exc
    processed = []
    for item in news_items[:limit]:
        sentiment = _compute_sentiment(item.get("title", "") + " " + item.get("summary", ""))
        processed.append({**item, "sentiment_score": sentiment})
    return processed


def news_sentiment(symbol: str, *, limit: int = 10) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    return format_response("NEWS_SENTIMENT", symbol=symbol, news=_cached_news(symbol, limit))




@ttl_cache(ttl=120, maxsize=32)
def _cached_top_movers(scr_id: str) -> List[Dict[str, Any]]:
    url = f"https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds={scr_id}&count=25"
    data = get_json(url)
    results = data.get("finance", {}).get("result", [])
    if not results:
        return []
    return results[0].get("quotes", [])


def top_gainers_losers() -> Dict[str, Any]:
    try:
        gainers = _cached_top_movers("day_gainers")
        losers = _cached_top_movers("day_losers")
        actives = _cached_top_movers("most_actives")
        
        # Check if any of the responses contain errors
        error_responses = []
        for name, data in [("gainers", gainers), ("losers", losers), ("most_active", actives)]:
            if isinstance(data, dict) and data.get("error"):
                error_responses.append(f"{name}: {data.get('message', 'Unknown error')}")
        
        if error_responses:
            # Return structured error response that agent can handle
            return format_response(
                "TOP_GAINERS_LOSERS",
                error="api_unavailable",
                message="Market movers data temporarily unavailable due to API limitations. " + "; ".join(error_responses),
                details={"gainers": gainers, "losers": losers, "most_active": actives},
                suggestion="Try again in a few minutes, or use alternative data sources for market analysis."
            )
        
    except ToolExecutionError as exc:
        return format_response(
            "TOP_GAINERS_LOSERS",
            error="tool_error",
            message=f"Failed to fetch market movers: {exc}",
            suggestion="The market movers service may be temporarily unavailable. Try using individual stock quotes instead."
        )
    
    return format_response("TOP_GAINERS_LOSERS", gainers=gainers, losers=losers, most_active=actives)


@ttl_cache(ttl=600, maxsize=128)
def _cached_insider_transactions(symbol: str) -> Any:
    ticker = get_ticker(symbol)
    data = ticker.get_insider_transactions()
    if data is None or data.empty:
        raise ToolExecutionError(f"No insider transactions available for {symbol}.")
    return data


def insider_transactions(symbol: str) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    try:
        data = _cached_insider_transactions(symbol)
    except ToolExecutionError as exc:
        raise exc
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch insider transactions for {symbol}: {exc}") from exc
    return format_response("INSIDER_TRANSACTIONS", symbol=symbol, data=data)


def analytics_fixed_window(symbol: str, *, window: int = 30) -> Dict[str, Any]:
    data = history(symbol, interval="1d", period=f"{max(window * 2, 60)}d")
    closing = data["Close"]
    window = int(window)
    rolling = closing.rolling(window=window)
    metrics = {
        "mean": float(rolling.mean().iloc[-1]),
        "std": float(rolling.std().iloc[-1]),
        "min": float(rolling.min().iloc[-1]),
        "max": float(rolling.max().iloc[-1]),
        "return_pct": float(((closing.iloc[-1] / closing.iloc[-window]) - 1) * 100) if len(closing) > window else None,
    }
    return format_response("ANALYTICS_FIXED_WINDOW", symbol=ensure_symbol(symbol), window=window, metrics=metrics)


def analytics_sliding_window(symbol: str, *, window: int = 30, step: int = 5) -> Dict[str, Any]:
    data = history(symbol, interval="1d", period=f"{max(window * 3, 120)}d")
    closing = data["Close"]
    window = int(window)
    step = max(1, int(step))
    slices = []
    for start_idx in range(0, len(closing) - window + 1, step):
        slice_close = closing.iloc[start_idx : start_idx + window]
        slices.append(
            {
                "start": slice_close.index[0].isoformat(),
                "end": slice_close.index[-1].isoformat(),
                "return_pct": float(((slice_close.iloc[-1] / slice_close.iloc[0]) - 1) * 100),
                "volatility": float(slice_close.pct_change().std() * math.sqrt(window)),
            }
        )
    return format_response(
        "ANALYTICS_SLIDING_WINDOW",
        symbol=ensure_symbol(symbol),
        window=window,
        step=step,
        slices=slices,
    )


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "NEWS_SENTIMENT": lambda **kwargs: news_sentiment(kwargs["symbol"], limit=kwargs.get("limit", 10)),
    "TOP_GAINERS_LOSERS": lambda **kwargs: top_gainers_losers(),
    "INSIDER_TRANSACTIONS": lambda **kwargs: insider_transactions(kwargs["symbol"]),
    "ANALYTICS_FIXED_WINDOW": lambda **kwargs: analytics_fixed_window(kwargs["symbol"], window=kwargs.get("window", 30)),
    "ANALYTICS_SLIDING_WINDOW": lambda **kwargs: analytics_sliding_window(
        kwargs["symbol"],
        window=kwargs.get("window", 30),
        step=kwargs.get("step", 5),
    ),
}


__all__ = ["HANDLERS"]
