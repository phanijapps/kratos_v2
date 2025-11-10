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

**Example (`BTC-USD`, captured 2025-11-09):**
```json
{
  "tool": "CRYPTO_QUOTE",
  "symbol": "BTC-USD",
  "quote": {
    "symbol": "BTC-USD",
    "price": 103412.5,
    "currency": "USD",
    "previous_close": 102283.6875,
    "open": 102287.390625,
    "day_high": 103831.765625,
    "day_low": 101468.875,
    "last_volume": 51466321920,
    "ten_day_average_volume": 65887180256,
    "three_month_average_volume": 62822893724,
    "market_cap": null,
    "shares": null,
    "fifty_day_average": 112289.613125,
    "two_hundred_day_average": 110248.229961,
    "year_high": 126198.070313,
    "year_low": 74436.679688,
    "year_change": 0.2709928533,
    "timezone": "UTC"
  },
  "recent": [
    {
      "timestamp": "2025-11-05T00:00:00",
      "Open": 101579.234375,
      "High": 104534.703125,
      "Low": 98989.914063,
      "Close": 103891.835938,
      "Adj Close": 103891.835938,
      "Volume": 77584934804
    },
    {
      "timestamp": "2025-11-06T00:00:00",
      "Open": 103893.664063,
      "High": 104147.304688,
      "Low": 100336.867188,
      "Close": 101301.289063,
      "Adj Close": 101301.289063,
      "Volume": 63932752861
    },
    {
      "timestamp": "2025-11-07T00:00:00",
      "Open": 101286.242188,
      "High": 104052.914063,
      "Low": 99257.054688,
      "Close": 103372.40625,
      "Adj Close": 103372.40625,
      "Volume": 92168030081
    },
    {
      "timestamp": "2025-11-08T00:00:00",
      "Open": 103371.703125,
      "High": 103373.5625,
      "Low": 101458.039063,
      "Close": 102282.117188,
      "Adj Close": 102282.117188,
      "Volume": 51446691095
    },
    {
      "timestamp": "2025-11-09T00:00:00",
      "Open": 102287.390625,
      "High": 103831.765625,
      "Low": 101468.875,
      "Close": 103412.5,
      "Adj Close": 103412.5,
      "Volume": 51466321920
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
