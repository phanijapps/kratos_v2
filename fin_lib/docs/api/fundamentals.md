# Fundamental Analysis API Reference

## Overview

Fundamental analysis functions for company data, financial statements, and valuation metrics.

> **Sample data note:** Outputs below were captured on 2025-11-08 using live requests. Long tables are truncated; full payloads are stored in `fin_lib/docs/api/sample_outputs.json`.

## Functions

### `get_fundamentals(symbol, include_statements=True, include_ratios=True, include_chart=False) -> Dict[str, Any]`
Get comprehensive fundamental analysis.

**Parameters:**
- `symbol`: Stock ticker
- `include_statements`: Include financial statements
- `include_ratios`: Include financial ratios
- `include_chart`: Include fundamental charts

**Returns:** Dictionary with comprehensive fundamental data

**Example (`AAPL`):**
```json
{
  "tool": "COMPREHENSIVE_FUNDAMENTALS",
  "symbol": "AAPL",
  "company_overview": {
    "tool": "COMPANY_OVERVIEW",
    "symbol": "AAPL",
    "overview": {
      "longName": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "marketCap": 3967007326208,
      "fullTimeEmployees": 166000,
      "website": "https://www.apple.com",
      "currency": "USD",
      "beta": 1.109,
      "dividendYield": 0.39,
      "trailingPE": 35.987934,
      "forwardPE": 32.306858,
      "priceToBook": 53.79082,
      "country": "United States",
      "city": "Cupertino"
    }
  },
  "financial_statements": {
    "tool": "FINANCIAL_STATEMENTS",
    "symbol": "AAPL",
    "statements": {
      "income_statement": {
        "tool": "INCOME_STATEMENT",
        "symbol": "AAPL",
        "data": [
          {
            "index": "Tax Effect Of Unusual Items",
            "2024-09-30 00:00:00": 0.0,
            "2023-09-30 00:00:00": 0.0,
            "2022-09-30 00:00:00": 0.0,
            "2021-09-30 00:00:00": 0.0
          },
          {
            "index": "Tax Rate For Calcs",
            "2024-09-30 00:00:00": 0.241,
            "2023-09-30 00:00:00": 0.147,
            "2022-09-30 00:00:00": 0.162,
            "2021-09-30 00:00:00": 0.133
          },
          "... 34 more entries ..."
        ]
      },
      "balance_sheet": {
        "tool": "BALANCE_SHEET",
        "symbol": "AAPL",
        "data": [
          {
            "index": "Treasury Shares Number",
            "2024-09-30 00:00:00": null,
            "2023-09-30 00:00:00": 0.0,
            "2022-09-30 00:00:00": null,
            "2021-09-30 00:00:00": null
          },
          {
            "index": "Ordinary Shares Number",
            "2024-09-30 00:00:00": 15116786000.0,
            "2023-09-30 00:00:00": 15550061000.0,
            "2022-09-30 00:00:00": 15943425000.0,
            "2021-09-30 00:00:00": 16426786000.0
          },
          "... 63 more entries ..."
        ]
      },
      "cash_flow": {
        "tool": "CASH_FLOW",
        "symbol": "AAPL",
        "data": [
          {
            "index": "Free Cash Flow",
            "2024-09-30 00:00:00": 108807000000.0,
            "2023-09-30 00:00:00": 99584000000.0,
            "2022-09-30 00:00:00": 111443000000.0,
            "2021-09-30 00:00:00": 92953000000.0
          },
          {
            "index": "Repurchase Of Capital Stock",
            "2024-09-30 00:00:00": -94949000000.0,
            "2023-09-30 00:00:00": -77550000000.0,
            "2022-09-30 00:00:00": -89402000000.0,
            "2021-09-30 00:00:00": -85971000000.0
          },
          "... 48 more entries ..."
        ]
      }
    }
  },
  "key_metrics": {
    "tool": "KEY_METRICS",
    "symbol": "AAPL",
    "metrics": {
      "returnOnAssets": 0.22964,
      "returnOnEquity": 1.71422,
      "profitMargins": 0.26915,
      "operatingMargins": 0.31647,
      "grossMargins": 0.46905,
      "revenueGrowth": 0.079,
      "earningsGrowth": 0.912,
      "currentRatio": 0.893,
      "quickRatio": 0.771,
      "debtToEquity": 152.411,
      "totalDebt": 112377004032,
      "totalCash": 54697000960,
      "freeCashflow": 78862254080,
      "operatingCashflow": 111482003456,
      "earningsQuarterlyGrowth": 0.864
    }
  },
  "valuation_ratios": {
    "tool": "VALUATION_RATIOS",
    "symbol": "AAPL",
    "ratios": {
      "trailingPE": 35.987934,
      "forwardPE": 32.306858,
      "priceToBook": 53.79082,
      "priceToSalesTrailing12Months": 9.532386,
      "enterpriseToRevenue": 9.671,
      "enterpriseToEbitda": 27.805,
      "bookValue": 4.991,
      "enterpriseValue": 4024687394816,
      "marketCap": 3967007326208
    }
  }
}
```

### `get_company_overview(symbol: str) -> Dict[str, Any]`
Get company overview and profile.

**Parameters:**
- `symbol`: Stock ticker

**Returns:** Dictionary with company overview

**Example (`AAPL`):**
```json
{
  "tool": "COMPANY_OVERVIEW",
  "symbol": "AAPL",
  "overview": {
    "longName": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "marketCap": 3967007326208,
    "fullTimeEmployees": 166000,
    "website": "https://www.apple.com",
    "currency": "USD",
    "beta": 1.109,
    "dividendYield": 0.39,
    "trailingPE": 35.987934,
    "forwardPE": 32.306858,
    "priceToBook": 53.79082,
    "country": "United States",
    "city": "Cupertino",
    "phone": "(408) 996-1010"
  }
}
```

### `get_financial_statements(symbol: str) -> Dict[str, Any]`
Get all financial statements.

**Parameters:**
- `symbol`: Stock ticker

**Returns:** Dictionary with income statement, balance sheet, and cash flow

**Example (`AAPL`):**
```json
{
  "tool": "FINANCIAL_STATEMENTS",
  "symbol": "AAPL",
  "statements": {
    "income_statement": {
      "tool": "INCOME_STATEMENT",
      "symbol": "AAPL",
      "data": [
        {
          "index": "Tax Effect Of Unusual Items",
          "2024-09-30 00:00:00": 0.0,
          "2023-09-30 00:00:00": 0.0,
          "2022-09-30 00:00:00": 0.0,
          "2021-09-30 00:00:00": 0.0
        },
        {
          "index": "Tax Rate For Calcs",
          "2024-09-30 00:00:00": 0.241,
          "2023-09-30 00:00:00": 0.147,
          "2022-09-30 00:00:00": 0.162,
          "2021-09-30 00:00:00": 0.133
        },
        "... 34 more entries ..."
      ]
    },
    "balance_sheet": {
      "tool": "BALANCE_SHEET",
      "symbol": "AAPL",
      "data": [
        {
          "index": "Treasury Shares Number",
          "2024-09-30 00:00:00": null,
          "2023-09-30 00:00:00": 0.0,
          "2022-09-30 00:00:00": null,
          "2021-09-30 00:00:00": null
        },
        {
          "index": "Ordinary Shares Number",
          "2024-09-30 00:00:00": 15116786000.0,
          "2023-09-30 00:00:00": 15550061000.0,
          "2022-09-30 00:00:00": 15943425000.0,
          "2021-09-30 00:00:00": 16426786000.0
        },
        "... 63 more entries ..."
      ]
    },
    "cash_flow": {
      "tool": "CASH_FLOW",
      "symbol": "AAPL",
      "data": [
        {
          "index": "Free Cash Flow",
          "2024-09-30 00:00:00": 108807000000.0,
          "2023-09-30 00:00:00": 99584000000.0,
          "2022-09-30 00:00:00": 111443000000.0,
          "2021-09-30 00:00:00": 92953000000.0
        },
        {
          "index": "Repurchase Of Capital Stock",
          "2024-09-30 00:00:00": -94949000000.0,
          "2023-09-30 00:00:00": -77550000000.0,
          "2022-09-30 00:00:00": -89402000000.0,
          "2021-09-30 00:00:00": -85971000000.0
        },
        "... 48 more entries ..."
      ]
    }
  }
}
```

### `get_key_metrics(symbol: str) -> Dict[str, Any]`
Get key financial metrics and ratios.

**Parameters:**
- `symbol`: Stock ticker

**Returns:** Dictionary with financial metrics

**Example (`AAPL`):**
```json
{
  "tool": "KEY_METRICS",
  "symbol": "AAPL",
  "metrics": {
    "returnOnAssets": 0.22964,
    "returnOnEquity": 1.71422,
    "profitMargins": 0.26915,
    "operatingMargins": 0.31647,
    "grossMargins": 0.46905,
    "revenueGrowth": 0.079,
    "earningsGrowth": 0.912,
    "currentRatio": 0.893,
    "quickRatio": 0.771,
    "debtToEquity": 152.411,
    "totalDebt": 112377004032,
    "totalCash": 54697000960,
    "freeCashflow": 78862254080,
    "operatingCashflow": 111482003456,
    "earningsQuarterlyGrowth": 0.864
  }
}
```

### `get_valuation_ratios(symbol: str) -> Dict[str, Any]`
Get valuation ratios.

**Parameters:**
- `symbol`: Stock ticker

**Returns:** Dictionary with valuation ratios

**Example (`AAPL`):**
```json
{
  "tool": "VALUATION_RATIOS",
  "symbol": "AAPL",
  "ratios": {
    "trailingPE": 35.987934,
    "forwardPE": 32.306858,
    "priceToBook": 53.79082,
    "priceToSalesTrailing12Months": 9.532386,
    "enterpriseToRevenue": 9.671,
    "enterpriseToEbitda": 27.805,
    "bookValue": 4.991,
    "enterpriseValue": 4024687394816,
    "marketCap": 3967007326208
  }
}
```
