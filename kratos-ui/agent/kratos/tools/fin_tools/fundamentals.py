"""
Handlers for company fundamentals and corporate event tools.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base import (
    ToolExecutionError,
    ensure_symbol,
    format_response,
    get_json,
    get_ticker,
    ttl_cache,
)


@ttl_cache(ttl=1800, maxsize=256)
def _cached_company_info(symbol: str) -> Dict[str, Any]:
    ticker = get_ticker(symbol)
    try:
        return dict(ticker.info)
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch company overview for {symbol}: {exc}") from exc


def company_overview(symbol: str) -> Dict[str, Any]:
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
    ]
    overview = {key: info.get(key) for key in overview_keys if key in info}
    return format_response("COMPANY_OVERVIEW", symbol=symbol, overview=overview)


@ttl_cache(ttl=1800, maxsize=256)
def _cached_statement(symbol: str, attribute: str) -> Any:
    ticker = get_ticker(symbol)
    try:
        data = getattr(ticker, attribute)
    except AttributeError as exc:  # pragma: no cover
        raise ToolExecutionError(f"{attribute} is not supported: {exc}") from exc
    if data is None or data.empty:
        raise ToolExecutionError(f"No {attribute} data available for {symbol}.")
    return data


def statement_data(symbol: str, attribute: str, tool_name: str) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    data = _cached_statement(symbol, attribute)
    return format_response(tool_name, symbol=symbol, data=data)


@ttl_cache(ttl=1800, maxsize=256)
def _cached_earnings(symbol: str) -> Dict[str, Any]:
    ticker = get_ticker(symbol)
    try:
        annual = ticker.earnings
        quarterly = ticker.quarterly_earnings
    except Exception as exc:
        raise ToolExecutionError(f"Failed to fetch earnings for {symbol}: {exc}") from exc
    if (annual is None or annual.empty) and (quarterly is None or quarterly.empty):
        raise ToolExecutionError(f"No earnings data available for {symbol}.")
    return {"annual": annual, "quarterly": quarterly}


def earnings(symbol: str) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    data = _cached_earnings(symbol)
    return format_response("EARNINGS", symbol=symbol, annual=data["annual"], quarterly=data["quarterly"])


@ttl_cache(ttl=1800, maxsize=256)
def _cached_listing_status(symbol: str) -> Dict[str, Any]:
    info = _cached_company_info(symbol)
    return {
        "symbol": symbol,
        "exchange": info.get("fullExchangeName"),
        "quoteType": info.get("quoteType"),
        "currency": info.get("currency"),
        "is_active": info.get("quoteType") not in {"NONE", None},
    }


def listing_status(symbol: str) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    status = _cached_listing_status(symbol)
    return format_response("LISTING_STATUS", status=status)


@ttl_cache(ttl=1800, maxsize=256)
def _cached_earnings_calendar(symbol: str, limit: int) -> Any:
    ticker = get_ticker(symbol)
    data = ticker.get_earnings_dates(limit=limit)
    if data is None or data.empty:
        raise ToolExecutionError(f"No earnings calendar data available for {symbol}.")
    return data


def earnings_calendar(symbol: str, *, limit: int = 10) -> Dict[str, Any]:
    symbol = ensure_symbol(symbol)
    data = _cached_earnings_calendar(symbol, limit)
    return format_response("EARNINGS_CALENDAR", symbol=symbol, data=data)


@ttl_cache(ttl=1800, maxsize=32)
def _cached_ipo_calendar() -> Dict[str, Any]:
    return get_json("https://query2.finance.yahoo.com/v10/finance/ipoCalendar")


def ipo_calendar(*, region: str = "US") -> Dict[str, Any]:
    data = _cached_ipo_calendar()
    events = data.get("finance", {}).get("result", [{}])[0].get("upcoming", [])
    region_upper = (region or "GLOBAL").upper()
    if region_upper != "GLOBAL":
        events = [event for event in events if event.get("exchange", "").upper().startswith(region_upper)]
    return format_response("IPO_CALENDAR", region=region_upper, events=events)


HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "COMPANY_OVERVIEW": lambda **kwargs: company_overview(kwargs["symbol"]),
    "INCOME_STATEMENT": lambda **kwargs: statement_data(kwargs["symbol"], "financials", "INCOME_STATEMENT"),
    "BALANCE_SHEET": lambda **kwargs: statement_data(kwargs["symbol"], "balance_sheet", "BALANCE_SHEET"),
    "CASH_FLOW": lambda **kwargs: statement_data(kwargs["symbol"], "cashflow", "CASH_FLOW"),
    "EARNINGS": lambda **kwargs: earnings(kwargs["symbol"]),
    "LISTING_STATUS": lambda **kwargs: listing_status(kwargs["symbol"]),
    "EARNINGS_CALENDAR": lambda **kwargs: earnings_calendar(kwargs["symbol"], limit=kwargs.get("limit", 10)),
    "IPO_CALENDAR": lambda **kwargs: ipo_calendar(region=kwargs.get("region", "US")),
}


__all__ = ["HANDLERS"]

