# Forex API Reference

## Overview

Foreign exchange functions for currency rates and conversions.

> **Sample data note:** Example payloads were captured on 2025-11-08 (see `fin_lib/docs/api/sample_outputs.json` for the full responses).

## Functions

### `get_exchange_rate(from_currency, to_currency, include_chart=False) -> Dict[str, Any]`
Get currency exchange rate.

**Parameters:**
- `from_currency`: Base currency (e.g., "USD")
- `to_currency`: Quote currency (e.g., "EUR")
- `include_chart`: Include rate chart

**Returns:** Dictionary with exchange rate data

**Example (`USD` ➜ `EUR`):**
```json
{
  "tool": "CURRENCY_EXCHANGE_RATE",
  "from_currency": "USD",
  "to_currency": "EUR",
  "pair": "USDEUR=X",
  "rate": 0.8643,
  "recent": [
    {
      "timestamp": "2025-11-03T00:00:00",
      "Open": 0.86745,
      "High": 0.8691,
      "Low": 0.8664,
      "Close": 0.86745,
      "Adj Close": 0.86745,
      "Volume": 0
    },
    {
      "timestamp": "2025-11-04T00:00:00",
      "Open": 0.86812,
      "High": 0.87157,
      "Low": 0.86708,
      "Close": 0.86812,
      "Adj Close": 0.86812,
      "Volume": 0
    },
    {
      "timestamp": "2025-11-05T00:00:00",
      "Open": 0.87066,
      "High": 0.87183,
      "Low": 0.86972,
      "Close": 0.87066,
      "Adj Close": 0.87066,
      "Volume": 0
    },
    {
      "timestamp": "2025-11-06T00:00:00",
      "Open": 0.86981,
      "High": 0.87003,
      "Low": 0.86633,
      "Close": 0.86981,
      "Adj Close": 0.86981,
      "Volume": 0
    },
    {
      "timestamp": "2025-11-07T00:00:00",
      "Open": 0.86586,
      "High": 0.86727,
      "Low": 0.86282,
      "Close": 0.86586,
      "Adj Close": 0.86586,
      "Volume": 0
    },
    "... 1 more entries ..."
  ]
}
```

### `convert_currency(amount, from_currency, to_currency) -> Dict[str, Any]`
Convert currency amount.

**Parameters:**
- `amount`: Amount to convert
- `from_currency`: Source currency
- `to_currency`: Target currency

**Returns:** Dictionary with conversion result

**Example (`100 USD ➜ JPY`):**
```json
{
  "tool": "CURRENCY_CONVERSION",
  "original_amount": 100,
  "from_currency": "USD",
  "to_currency": "JPY",
  "exchange_rate": 152.947998,
  "converted_amount": 15294.799805,
  "conversion_string": "100 USD = 15294.7998 JPY"
}
```
