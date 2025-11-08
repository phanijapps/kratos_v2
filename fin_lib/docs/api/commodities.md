# Commodities API Reference

## Overview

Commodities functions for raw materials and precious metals pricing.

> **Sample data note:** Responses below were gathered on 2025-11-08. Refer to `fin_lib/docs/api/sample_outputs.json` for the untrimmed payloads.

## Functions

### `get_commodity_price(symbol, include_chart=False) -> Dict[str, Any]`
Get commodity price.

**Parameters:**
- `symbol`: Commodity symbol (e.g., "GC=F" for gold)
- `include_chart`: Include price chart

**Returns:** Dictionary with commodity price data

**Example (`GC=F` / Gold futures):**
```json
{
  "tool": "COMMODITY_QUOTE",
  "symbol": "GC=F",
  "name": "Gold",
  "quote": {
    "symbol": "GC=F",
    "price": null,
    "currency": "USD",
    "previous_close": null,
    "regular_market_change": null,
    "regular_market_change_percent": null,
    "regular_market_time": null
  },
  "recent": [
    {
      "timestamp": "2025-11-03T05:00:00",
      "Open": 3976.199951,
      "High": 4020.0,
      "Low": 3959.0,
      "Close": 4000.300049,
      "Adj Close": 4000.300049,
      "Volume": 0
    },
    {
      "timestamp": "2025-11-04T05:00:00",
      "Open": 3994.199951,
      "High": 3995.399902,
      "Low": 3927.399902,
      "Close": 3947.699951,
      "Adj Close": 3947.699951,
      "Volume": 657
    },
    {
      "timestamp": "2025-11-05T05:00:00",
      "Open": 3929.899902,
      "High": 3983.5,
      "Low": 3929.899902,
      "Close": 3980.300049,
      "Adj Close": 3980.300049,
      "Volume": 559
    },
    {
      "timestamp": "2025-11-06T05:00:00",
      "Open": 4004.0,
      "High": 4007.5,
      "Low": 3979.899902,
      "Close": 3979.899902,
      "Adj Close": 3979.899902,
      "Volume": 650
    },
    {
      "timestamp": "2025-11-07T05:00:00",
      "Open": 3980.800049,
      "High": 3999.399902,
      "Low": 3980.800049,
      "Close": 3999.399902,
      "Adj Close": 3999.399902,
      "Volume": 650
    }
  ]
}
```

### `get_precious_metals(include_prices=True, include_chart=False) -> Dict[str, Any]`
Get precious metals data.

**Parameters:**
- `include_prices`: Include current prices
- `include_chart`: Include comparison chart

**Returns:** Dictionary with precious metals data

**Example (gold, silver, platinum, palladium):**
```json
{
  "tool": "PRECIOUS_METALS",
  "metals": [
    {
      "symbol": "GC=F",
      "name": "Gold",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "SI=F",
      "name": "Silver",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "PL=F",
      "name": "Platinum",
      "price": null,
      "change": null,
      "change_percent": null
    },
    {
      "symbol": "PA=F",
      "name": "Palladium",
      "price": null,
      "change": null,
      "change_percent": null
    }
  ]
}
```
