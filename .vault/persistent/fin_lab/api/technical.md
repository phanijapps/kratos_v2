# Technical Analysis API Reference

## Overview

Technical analysis functions for calculating indicators and performing chart analysis.

> **Sample data note:** Example payloads below were captured on 2025-11-08 and trimmed for readability. Full responses live in `fin_lib/docs/api/sample_outputs.json`.

**Supported indicator identifiers:** `SMA`, `EMA`, `WMA`, `DEMA`, `TEMA`, `TRIMA`, `KAMA`, `MAMA`, `VWAP`, `T3`, `MACD`, `MACDEXT`, `STOCH`, `STOCHF`, `RSI`, `STOCHRSI`, `WILLR`, `ADX`, `ADXR`, `APO`, `PPO`, `MOM`, `BOP`, `CCI`, `CMO`, `ROC`, `ROCR`, `AROON`, `AROONOSC`, `MFI`, `TRIX`, `ULTOSC`, `DX`, `MINUS_DI`, `PLUS_DI`, `MINUS_DM`, `PLUS_DM`, `BBANDS`, `MIDPOINT`, `MIDPRICE`, `SAR`, `TRANGE`, `ATR`, `NATR`, `AD`, `ADOSC`, `OBV`, `HT_TRENDLINE`, `HT_SINE`, `HT_TRENDMODE`, `HT_DCPERIOD`, `HT_DCPHASE`, `HT_PHASOR`.

## Functions

### `technical_analysis(symbol, indicators=None, period="1y", include_chart=False) -> Dict[str, Any]`
Perform comprehensive technical analysis.

**Parameters:**
- `symbol`: Stock ticker
- `indicators`: List of indicators (default: ["RSI", "MACD", "SMA", "EMA", "BBANDS", "ATR", "OBV"])
- `period`: Time period
- `include_chart`: Whether to include charts

**Returns:** Dictionary with technical analysis results

**Example (`AAPL`, indicators=`["RSI", "MACD", "SMA"]`, `period="6mo"`):**
```json
{
  "tool": "TECHNICAL_ANALYSIS",
  "symbol": "AAPL",
  "period": "6mo",
  "interval": "1d",
  "indicators": {
    "RSI": {
      "tool": "RSI",
      "symbol": "AAPL",
      "interval": "1d",
      "period": "6mo",
      "data": [
        {
          "timestamp": "2025-05-08T04:00:00",
          "RSI_14": null
        },
        {
          "timestamp": "2025-05-09T04:00:00",
          "RSI_14": 100.0
        },
        {
          "timestamp": "2025-05-12T04:00:00",
          "RSI_14": 100.0
        },
        {
          "timestamp": "2025-05-13T04:00:00",
          "RSI_14": 100.0
        },
        {
          "timestamp": "2025-05-14T04:00:00",
          "RSI_14": 97.602372
        },
        "... 123 more entries ..."
      ]
    },
    "MACD": {
      "tool": "MACD",
      "symbol": "AAPL",
      "interval": "1d",
      "period": "6mo",
      "data": [
        {
          "timestamp": "2025-05-08T04:00:00",
          "MACD_12_26_9": null,
          "MACDh_12_26_9": null,
          "MACDs_12_26_9": null
        },
        "... 123 more entries ..."
      ]
    },
    "SMA": {
      "tool": "SMA",
      "symbol": "AAPL",
      "interval": "1d",
      "period": "6mo",
      "data": [
        {
          "timestamp": "2025-05-08T04:00:00",
          "SMA_20": null
        },
        "... 123 more entries ..."
      ]
    }
  },
  "price_data": [
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
    "... 15 more entries ..."
  ]
}
```

### `calculate_rsi(symbol, length=14, period="200d", include_chart=False) -> Dict[str, Any]`
Calculate RSI indicator.

**Parameters:**
- `symbol`: Stock ticker
- `length`: RSI period
- `period`: Historical data period
- `include_chart`: Whether to include RSI chart

**Returns:** Dictionary with RSI data

**Example (`AAPL`, `period="6mo"`):**
```json
{
  "tool": "RSI",
  "symbol": "AAPL",
  "interval": "1d",
  "period": "6mo",
  "data": [
    {
      "timestamp": "2025-05-08T04:00:00",
      "RSI_14": null
    },
    {
      "timestamp": "2025-05-09T04:00:00",
      "RSI_14": 100.0
    },
    {
      "timestamp": "2025-05-12T04:00:00",
      "RSI_14": 100.0
    },
    {
      "timestamp": "2025-05-13T04:00:00",
      "RSI_14": 100.0
    },
    {
      "timestamp": "2025-05-14T04:00:00",
      "RSI_14": 97.602372
    },
    "... 123 more entries ..."
  ]
}
```

### `calculate_macd(symbol, fast=12, slow=26, signal=9, include_chart=False) -> Dict[str, Any]`
Calculate MACD indicator.

**Parameters:**
- `symbol`: Stock ticker
- `fast`: Fast EMA period
- `slow`: Slow EMA period
- `signal`: Signal line period
- `include_chart`: Whether to include MACD chart

**Returns:** Dictionary with MACD data

**Example (`AAPL`, `period="6mo"`):**
```json
{
  "tool": "MACD",
  "symbol": "AAPL",
  "interval": "1d",
  "period": "6mo",
  "data": [
    {
      "timestamp": "2025-05-08T04:00:00",
      "MACD_12_26_9": null,
      "MACDh_12_26_9": null,
      "MACDs_12_26_9": null
    },
    {
      "timestamp": "2025-05-09T04:00:00",
      "MACD_12_26_9": null,
      "MACDh_12_26_9": null,
      "MACDs_12_26_9": null
    },
    {
      "timestamp": "2025-05-12T04:00:00",
      "MACD_12_26_9": null,
      "MACDh_12_26_9": null,
      "MACDs_12_26_9": null
    },
    {
      "timestamp": "2025-05-13T04:00:00",
      "MACD_12_26_9": null,
      "MACDh_12_26_9": null,
      "MACDs_12_26_9": null
    },
    {
      "timestamp": "2025-05-14T04:00:00",
      "MACD_12_26_9": null,
      "MACDh_12_26_9": null,
      "MACDs_12_26_9": null
    },
    "... 123 more entries ..."
  ]
}
```

### `calculate_bollinger_bands(symbol, length=20, std=2, include_chart=False) -> Dict[str, Any]`
Calculate Bollinger Bands.

**Parameters:**
- `symbol`: Stock ticker
- `length`: Moving average period
- `std`: Standard deviation multiplier
- `include_chart`: Whether to include chart

**Returns:** Dictionary with Bollinger Bands data

**Example (`AAPL`, `period="6mo"`):**
```json
{
  "tool": "BBANDS",
  "symbol": "AAPL",
  "interval": "1d",
  "period": "6mo",
  "data": [
    {
      "timestamp": "2025-05-08T04:00:00",
      "BBL_20_2.0_2.0": null,
      "BBM_20_2.0_2.0": null,
      "BBU_20_2.0_2.0": null,
      "BBB_20_2.0_2.0": null,
      "BBP_20_2.0_2.0": null
    },
    {
      "timestamp": "2025-05-09T04:00:00",
      "BBL_20_2.0_2.0": null,
      "BBM_20_2.0_2.0": null,
      "BBU_20_2.0_2.0": null,
      "BBB_20_2.0_2.0": null,
      "BBP_20_2.0_2.0": null
    },
    "... 123 more entries ..."
  ]
}
```
