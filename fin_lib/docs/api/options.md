# Options API Reference

## Overview

Options trading functions for chains, Greeks, and implied volatility analysis.

> **Sample data note:** Option responses were captured on 2025-11-08 using the next weekly AAPL expiry. Full payloads: `fin_lib/docs/api/sample_outputs.json`.

## Functions

### `get_options_chain(symbol, expiration=None, include_greeks=True) -> Dict[str, Any]`
Get options chain.

**Parameters:**
- `symbol`: Stock ticker
- `expiration`: Expiration date (YYYY-MM-DD) or None for next
- `include_greeks`: Include Greeks calculations

**Returns:** Dictionary with options chain data

**Example (`AAPL`, next available expiration):**
```json
{
  "tool": "OPTIONS_CHAIN",
  "symbol": "AAPL",
  "expiration": "2025-11-14",
  "available_expirations": [
    "2025-11-14",
    "2025-11-21",
    "2025-11-28",
    "2025-12-05",
    "2025-12-12",
    "... 14 more entries ..."
  ],
  "calls": [
    {
      "contractSymbol": "AAPL251114C00110000",
      "lastTradeDate": "2025-11-05T19:11:51",
      "strike": 110.0,
      "lastPrice": 161.1,
      "bid": 157.15,
      "ask": 160.0,
      "volume": 4.0,
      "openInterest": 1,
      "impliedVolatility": 2.53516,
      "inTheMoney": true
    },
    {
      "contractSymbol": "AAPL251114C00120000",
      "lastTradeDate": "2025-11-07T19:14:29",
      "strike": 120.0,
      "lastPrice": 147.94,
      "bid": 147.05,
      "ask": 149.95,
      "volume": 1.0,
      "openInterest": 4,
      "impliedVolatility": 2.023442,
      "inTheMoney": true
    },
    "... 64 more entries ..."
  ],
  "puts": [
    {
      "contractSymbol": "AAPL251114P00110000",
      "lastTradeDate": "2025-10-31T13:30:10",
      "strike": 110.0,
      "lastPrice": 0.03,
      "bid": 0.0,
      "ask": 0.21,
      "volume": 2.0,
      "openInterest": 2,
      "impliedVolatility": 2.53516,
      "inTheMoney": false
    },
    {
      "contractSymbol": "AAPL251114P00140000",
      "lastTradeDate": "2025-10-24T15:16:58",
      "strike": 140.0,
      "lastPrice": 0.02,
      "bid": 0.0,
      "ask": 0.14,
      "volume": 392.0,
      "openInterest": 392,
      "impliedVolatility": 1.804688,
      "inTheMoney": false
    },
    "... 52 more entries ..."
  ],
  "include_greeks": true
}
```

### `get_implied_volatility(symbol, expiration=None, include_chart=False) -> Dict[str, Any]`
Get implied volatility analysis.

**Parameters:**
- `symbol`: Stock ticker
- `expiration`: Expiration date
- `include_chart`: Include IV chart

**Returns:** Dictionary with implied volatility data

**Example (`AAPL`, expiration `2025-11-14`):**
```json
{
  "tool": "IMPLIED_VOLATILITY",
  "symbol": "AAPL",
  "expiration": "2025-11-14",
  "average_call_iv": 0.801561,
  "average_put_iv": 0.733223,
  "call_iv_by_strike": [
    {
      "strike": 110.0,
      "impliedVolatility": 2.53516
    },
    {
      "strike": 120.0,
      "impliedVolatility": 2.023442
    },
    {
      "strike": 130.0,
      "impliedVolatility": 3.160158
    },
    {
      "strike": 140.0,
      "impliedVolatility": 1.890626
    },
    {
      "strike": 145.0,
      "impliedVolatility": 2.631839
    },
    "... 64 more entries ..."
  ],
  "put_iv_by_strike": [
    {
      "strike": 110.0,
      "impliedVolatility": 2.53516
    },
    {
      "strike": 125.0,
      "impliedVolatility": 2.082036
    },
    {
      "strike": 135.0,
      "impliedVolatility": 1.898438
    },
    {
      "strike": 140.0,
      "impliedVolatility": 1.804688
    },
    {
      "strike": 145.0,
      "impliedVolatility": 1.73047
    },
    "... 52 more entries ..."
  ]
}
```
