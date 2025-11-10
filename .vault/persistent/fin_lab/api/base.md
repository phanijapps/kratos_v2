# Base API Reference

## Overview

fin_lib is a professional financial analysis library designed for AI agents and quantitative analysis. It provides clean, token-optimized APIs for comprehensive financial data analysis.

> **Sample data note:** Every example response in this document was captured on 2025-11-08 using live market data and truncated for brevity. See `fin_lib/docs/api/sample_outputs.json` for the full payloads.

## Installation

```bash
pip install ./fin_lib
```

## Quick Start

```python
import fin_lib as fl

# Get stock quote
quote = fl.get_quote("AAPL")
print(f"Price: ${quote['quote']['price']}")

# Get historical data with chart
data = fl.get_historical_data("AAPL", period="1y", include_chart=True)

# Technical analysis
analysis = fl.technical_analysis("AAPL", indicators=["RSI", "MACD"])

# Fundamental analysis
fundamentals = fl.get_fundamentals("AAPL")
```

## Core Stock Market Functions

### `get_quote(symbol: str) -> Dict[str, Any]`
Fetch the latest quote snapshot, combining near-real-time metadata from Yahoo Finance (`fast_info`) with the most recent OHLC bar so you always have a fallback price.

**Parameters:**
- `symbol`: Stock ticker (e.g., "AAPL", "TTD")

**Returns:** Dictionary with quote metadata (`quote`) and the latest historical row (`data`)

**Example (`TTD`, captured 2025-11-09):**
```json
{
  "tool": "GLOBAL_QUOTE",
  "quote": {
    "symbol": "TTD",
    "price": 43.0,
    "currency": "USD",
    "previous_close": 46.3109,
    "open": 46.0,
    "day_high": 46.0,
    "day_low": 41.772999,
    "last_volume": 34230600,
    "ten_day_average_volume": 13357920,
    "three_month_average_volume": 16620781,
    "market_cap": 20794579281.0,
    "shares": 483594867,
    "fifty_day_average": 49.7993,
    "two_hundred_day_average": 65.9111,
    "year_high": 141.529999,
    "year_low": 41.772999,
    "year_change": -0.667543,
    "timezone": "America/New_York"
  },
  "data": [
    {
      "timestamp": "2025-11-07T05:00:00",
      "Open": 46.0,
      "High": 46.0,
      "Low": 41.772999,
      "Close": 43.0,
      "Adj Close": 43.0,
      "Volume": 34230600,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    }
  ]
}
```

### `get_historical_data(symbol, period="1y", interval="1d", include_chart=False) -> Dict[str, Any]`
Get historical price data.

**Parameters:**
- `symbol`: Stock ticker
- `period`: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
- `interval`: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
- `include_chart`: Whether to include candlestick chart

**Returns:** Dictionary with historical data and optional chart

**Example (`AAPL`, `period="1mo"`, `interval="1d"`):**
```json
{
  "tool": "TIME_SERIES_DAILY",
  "symbol": "AAPL",
  "interval": "1d",
  "period": "1mo",
  "start": null,
  "end": null,
  "adjusted": true,
  "data": [
    {
      "timestamp": "2025-10-08T04:00:00",
      "Open": 256.519989,
      "High": 258.519989,
      "Low": 256.109985,
      "Close": 258.059998,
      "Volume": 36496900,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    {
      "timestamp": "2025-10-09T04:00:00",
      "Open": 257.809998,
      "High": 258.0,
      "Low": 253.139999,
      "Close": 254.039993,
      "Volume": 38322000,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    {
      "timestamp": "2025-10-10T04:00:00",
      "Open": 254.940002,
      "High": 256.380005,
      "Low": 244.0,
      "Close": 245.270004,
      "Volume": 61999100,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    {
      "timestamp": "2025-10-13T04:00:00",
      "Open": 249.380005,
      "High": 249.690002,
      "Low": 245.559998,
      "Close": 247.660004,
      "Volume": 38142900,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    {
      "timestamp": "2025-10-14T04:00:00",
      "Open": 246.600006,
      "High": 248.850006,
      "Low": 244.699997,
      "Close": 247.770004,
      "Volume": 35478000,
      "Dividends": 0.0,
      "Stock Splits": 0.0
    },
    "... 18 more entries ..."
  ]
}
```

### `get_bulk_quotes(symbols: List[str]) -> Dict[str, Any]`
Get quotes for multiple symbols.

**Parameters:**
- `symbols`: List of ticker symbols

**Returns:** Dictionary with quotes for all symbols

**Example (`["AAPL", "MSFT", "GOOGL"]`):**
```json
{
  "tool": "REALTIME_BULK_QUOTES",
  "quotes": [
    {
      "symbol": "AAPL",
      "price": null,
      "currency": "USD",
      "regular_market_change": null,
      "regular_market_change_percent": null,
      "regular_market_time": null
    },
    {
      "symbol": "MSFT",
      "price": null,
      "currency": "USD",
      "regular_market_change": null,
      "regular_market_change_percent": null,
      "regular_market_time": null
    },
    {
      "symbol": "GOOGL",
      "price": null,
      "currency": "USD",
      "regular_market_change": null,
      "regular_market_change_percent": null,
      "regular_market_time": null
    }
  ]
}
```

### `search_symbols(keywords: str, region="US", quotes_count=10) -> Dict[str, Any]`
Search for stock symbols by keywords.

**Parameters:**
- `keywords`: Search terms
- `region`: Market region (US, CA, GB, etc.)
- `quotes_count`: Maximum results

**Returns:** Dictionary with search results or structured errors

**Example (rate-limited response for `"apple"` in US):**
```json
{
  "tool": "SYMBOL_SEARCH",
  "query": "apple",
  "region": "US",
  "error": "rate_limit",
  "message": "Yahoo Finance API rate limit exceeded. Please try again later.",
  "suggestion": "Try searching for a more specific symbol or company name, or try again later."
}
```

### `get_market_status(region="US") -> Dict[str, Any]`
Get current market status.

**Parameters:**
- `region`: Market region

**Returns:** Dictionary with market status info

**Example (`US`):**
```json
{
  "tool": "MARKET_STATUS",
  "status": {
    "region": "US",
    "timestamp_utc": "2025-11-08T18:14:38.009315+00:00",
    "is_weekend": true,
    "is_open": false,
    "hours": {
      "open": "09:30",
      "close": "16:00",
      "timezone": "America/New_York"
    },
    "note": "Status approximated using standard exchange hours; holidays not accounted for."
  }
}
```
