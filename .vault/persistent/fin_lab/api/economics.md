# Economics API Reference

## Overview

Economic indicators and market sentiment functions.

> **Sample data note:** Responses captured on 2025-11-08 are shown below (see `fin_lib/docs/api/sample_outputs.json` for details).

## Functions

### `get_treasury_rates(include_chart=False) -> Dict[str, Any]`
Get US Treasury rates.

**Parameters:**
- `include_chart`: Include yield curve chart

**Returns:** Dictionary with treasury rates

**Example (US curve snapshot):**
```json
{
  "tool": "TREASURY_RATES",
  "rates": {
    "3M": {
      "rate": null,
      "symbol": "^IRX",
      "maturity": "3M"
    },
    "2Y": {
      "rate": null,
      "symbol": "^TNX",
      "maturity": "2Y"
    },
    "10Y": {
      "rate": null,
      "symbol": "^TNX",
      "maturity": "10Y"
    },
    "30Y": {
      "rate": null,
      "symbol": "^TYX",
      "maturity": "30Y"
    }
  }
}
```

### `get_market_sentiment(include_chart=False) -> Dict[str, Any]`
Get market sentiment indicators.

**Parameters:**
- `include_chart`: Include sentiment chart

**Returns:** Dictionary with sentiment data

**Example (volatility complex):**
```json
{
  "tool": "MARKET_SENTIMENT",
  "sentiment": {
    "VIX": {
      "value": null,
      "symbol": "^VIX",
      "description": "Volatility Index - Market fear gauge"
    },
    "SKEW": {
      "value": null,
      "symbol": "^SKEW",
      "description": "SKEW Index - Tail risk measure"
    },
    "VXN": {
      "value": null,
      "symbol": "^VXN",
      "description": "NASDAQ Volatility Index"
    },
    "RVX": {
      "error": "'currency'"
    }
  }
}
```
