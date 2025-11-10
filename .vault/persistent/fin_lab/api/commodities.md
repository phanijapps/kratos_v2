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

**Example (`GC=F` / Gold futures, captured 2025-11-09):**
```json
{
  "tool": "COMMODITY_QUOTE",
  "symbol": "GC=F",
  "name": "Gold",
  "quote": {
    "symbol": "GC=F",
    "price": 4009.800049,
    "currency": "USD",
    "previous_close": 4005.5,
    "open": 3986.899902,
    "day_high": 4035.800049,
    "day_low": 3981.600098,
    "last_volume": 198894,
    "ten_day_average_volume": 20403,
    "three_month_average_volume": 4717,
    "market_cap": null,
    "fifty_day_average": 3874.811992,
    "two_hundred_day_average": 3371.055552,
    "year_high": 4358.0,
    "year_low": 2554.199951,
    "year_change": 0.5356158562,
    "timezone": "America/New_York"
  },
  "recent": [
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
      "Open": 3986.899902,
      "High": 4035.800049,
      "Low": 3981.600098,
      "Close": 4009.800049,
      "Adj Close": 4009.800049,
      "Volume": 198894
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
