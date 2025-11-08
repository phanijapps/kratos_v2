# Cryptocurrency API Reference

## Overview

Cryptocurrency functions for digital asset prices and analysis.

> **Sample data note:** Examples below were captured on 2025-11-08 (see `fin_lib/docs/api/sample_outputs.json` for full payloads).

## Functions

### `get_crypto_price(symbol, include_chart=False) -> Dict[str, Any]`
Get cryptocurrency price.

**Parameters:**
- `symbol`: Crypto symbol (e.g., "BTC-USD")
- `include_chart`: Include price chart

**Returns:** Dictionary with crypto price data

**Example (`BTC-USD`):**
```json
{
  "tool": "CRYPTO_QUOTE",
  "symbol": "BTC-USD",
  "quote": {
    "symbol": "BTC-USD",
    "price": null,
    "currency": "USD",
    "previous_close": null,
    "regular_market_change": null,
    "regular_market_change_percent": null,
    "regular_market_time": null
  },
  "recent": [
    {
      "timestamp": "2025-11-04T00:00:00",
      "Open": 106541.421875,
      "High": 107264.882812,
      "Low": 98962.0625,
      "Close": 101590.523438,
      "Adj Close": 101590.523438,
      "Volume": 110967184773
    },
    {
      "timestamp": "2025-11-05T00:00:00",
      "Open": 101579.234375,
      "High": 104534.703125,
      "Low": 98989.914062,
      "Close": 103891.835938,
      "Adj Close": 103891.835938,
      "Volume": 77584934804
    },
    {
      "timestamp": "2025-11-06T00:00:00",
      "Open": 103893.664062,
      "High": 104147.304688,
      "Low": 100336.867188,
      "Close": 101301.289062,
      "Adj Close": 101301.289062,
      "Volume": 63932752861
    },
    {
      "timestamp": "2025-11-07T00:00:00",
      "Open": 101286.242188,
      "High": 104052.914062,
      "Low": 99257.054688,
      "Close": 103372.40625,
      "Adj Close": 103372.40625,
      "Volume": 92168030081
    },
    {
      "timestamp": "2025-11-08T00:00:00",
      "Open": 103296.953125,
      "High": 103359.0625,
      "Low": 101463.195312,
      "Close": 101957.59375,
      "Adj Close": 101957.59375,
      "Volume": 60705103872
    }
  ]
}
```

### `get_major_cryptos(include_prices=True, include_chart=False) -> Dict[str, Any]`
Get major cryptocurrency data.

**Parameters:**
- `include_prices`: Include current prices
- `include_chart`: Include comparison chart

**Returns:** Dictionary with major crypto data

**Example (top 10 majors):**
```json
{
  "tool": "MAJOR_CRYPTOCURRENCIES",
  "cryptos": [
    {
      "symbol": "BTC-USD",
      "name": "Bitcoin",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "ETH-USD",
      "name": "Ethereum",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "BNB-USD",
      "name": "Binance Coin",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "XRP-USD",
      "name": "Ripple",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "ADA-USD",
      "name": "Cardano",
      "price": null,
      "change": null,
      "change_percent": null
    },
    "... 5 more entries ..."
  ]
}
```
