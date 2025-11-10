# Alpha Intelligence API Reference

## Overview

Advanced analytics functions for risk-adjusted returns, portfolio optimization, and performance metrics.

> **Sample data note:** The outputs below were captured on 2025-11-08. Additional context is available in `fin_lib/docs/api/sample_outputs.json`.

## Functions

### `calculate_alpha_beta(symbol, benchmark="^GSPC", period="2y", include_chart=False) -> Dict[str, Any]`
Calculate alpha and beta.

**Parameters:**
- `symbol`: Stock ticker
- `benchmark`: Benchmark symbol
- `period`: Time period
- `include_chart`: Include regression chart

**Returns:** Dictionary with alpha/beta analysis

**Example (`AAPL` vs `^GSPC`, `period="1y"`):**
```json
{
  "tool": "ALPHA_BETA_ANALYSIS",
  "symbol": "AAPL",
  "benchmark": "^GSPC",
  "period": "1y",
  "alpha": 0.050261,
  "beta": 1.309316,
  "r_squared": 0.568106,
  "correlation": 0.753728,
  "tracking_error": 0.214511,
  "data_points": 249
}
```

### `calculate_sharpe_ratio(symbol, period="1y", risk_free_rate=0.02) -> Dict[str, Any]`
Calculate Sharpe ratio.

**Parameters:**
- `symbol`: Stock ticker
- `period`: Time period
- `risk_free_rate`: Risk-free rate

**Returns:** Dictionary with Sharpe ratio and risk metrics

**Example (`AAPL`, `period="1y"`, `risk_free_rate=0.02`):**
```json
{
  "tool": "SHARPE_RATIO_ANALYSIS",
  "symbol": "AAPL",
  "period": "1y",
  "annual_return": 0.22604,
  "annual_volatility": 0.326408,
  "sharpe_ratio": 0.631237,
  "sortino_ratio": 0.849194,
  "max_drawdown": -0.333605,
  "risk_free_rate": 0.02
}
```

### `portfolio_optimization(symbols, period="1y", method="max_sharpe", include_chart=False) -> Dict[str, Any]`
Optimize portfolio weights.

**Parameters:**
- `symbols`: List of ticker symbols
- `period`: Time period
- `method`: Optimization method ("max_sharpe", "min_vol", "equal_weight")
- `include_chart`: Include correlation heatmap

**Returns:** Dictionary with optimal weights and metrics

**Example (`["AAPL", "MSFT", "GOOGL"]`, `period="1y"`, method `max_sharpe`):**
```json
{
  "tool": "PORTFOLIO_OPTIMIZATION",
  "symbols": [
    "AAPL",
    "MSFT",
    "GOOGL"
  ],
  "period": "1y",
  "method": "max_sharpe",
  "weights": {
    "AAPL": 0.0,
    "MSFT": 0.044081,
    "GOOGL": 0.955919
  },
  "expected_return": 0.496301,
  "volatility": 0.317256,
  "sharpe_ratio": 1.501312,
  "risk_free_rate": 0.02
}
```
