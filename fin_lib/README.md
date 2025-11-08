# fin_lib - Professional Financial Analysis Library

A comprehensive financial analysis library designed for AI agents and quantitative analysis. Built on yfinance with professional charting capabilities and token-optimized APIs.

## Features

- **Real-time Market Data**: Stocks, forex, crypto, commodities
- **Technical Analysis**: 40+ indicators with pandas-ta
- **Fundamental Analysis**: Financial statements, ratios, metrics
- **Advanced Analytics**: Alpha/beta, Sharpe ratio, portfolio optimization
- **Professional Charts**: Plotly and matplotlib integration
- **AI Agent Optimized**: Clean APIs, structured responses, comprehensive error handling

## Quick Install

```bash
pip install ./fin_lib
```

## Quick Start

```python
import fin_lib as fl

# Stock analysis
quote = fl.get_quote("AAPL")
data = fl.get_historical_data("AAPL", period="1y", include_chart=True)
analysis = fl.technical_analysis("AAPL", indicators=["RSI", "MACD"])

# Multi-asset analysis
forex_rate = fl.forex.get_exchange_rate("USD", "EUR")
crypto_price = fl.crypto.get_crypto_price("BTC-USD")
gold_price = fl.commodities.get_commodity_price("GC=F")

# Advanced analytics
alpha_beta = fl.alpha_intelligence.calculate_alpha_beta("AAPL")
portfolio = fl.alpha_intelligence.portfolio_optimization(["AAPL", "MSFT", "GOOGL"])
```

## Core Modules

### 📈 Core (`fin_lib.core`)
- Real-time quotes and bulk quotes
- Historical data (intraday to monthly)
- Symbol search and market status
- Professional candlestick charts

### 📊 Technical Analysis (`fin_lib.technical`)
- 40+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Comprehensive technical analysis workflows
- Interactive indicator charts
- Pandas-ta integration

### 💰 Fundamental Analysis (`fin_lib.fundamentals`)
- Company overview and profile
- Financial statements (income, balance sheet, cash flow)
- Key metrics and valuation ratios
- Earnings data and calendar

### 💱 Forex (`fin_lib.forex`)
- Currency exchange rates
- Major, minor, and exotic pairs
- Currency conversion utilities
- Forex volatility analysis

### ₿ Cryptocurrency (`fin_lib.crypto`)
- Real-time crypto prices
- Major cryptocurrencies tracking
- Crypto volatility and returns
- Portfolio comparison charts

### 🥇 Commodities (`fin_lib.commodities`)
- Precious metals (gold, silver, platinum)
- Energy commodities (oil, natural gas)
- Agricultural and industrial metals
- Commodity comparison analysis

### 📉 Economics (`fin_lib.economics`)
- Treasury rates and yield curves
- Economic indicators (VIX, DXY)
- Market sentiment analysis
- Dollar index tracking

### 📋 Options (`fin_lib.options`)
- Options chains and Greeks
- Implied volatility analysis
- Options strategies analysis
- Unusual options activity

### 🧠 Alpha Intelligence (`fin_lib.alpha_intelligence`)
- Alpha/beta calculation
- Sharpe and Sortino ratios
- Portfolio optimization (Modern Portfolio Theory)
- Value at Risk (VaR) calculation
- Market regime detection

## AI Agent Integration

Designed specifically for AI agents with:

- **Token-Optimized APIs**: Concise function signatures and responses
- **Structured Error Handling**: Consistent error formats with suggestions
- **Comprehensive Documentation**: Markdown docs with examples
- **JSON-Serializable Responses**: All data structures are JSON-friendly
- **Professional Charting**: Optional chart generation for visualization

## Example Workflows

### Stock Analysis Workflow
```python
import fin_lib as fl

# Get comprehensive stock analysis
symbol = "AAPL"

# Basic data
quote = fl.get_quote(symbol)
history = fl.get_historical_data(symbol, period="1y")

# Technical analysis
technical = fl.technical_analysis(symbol, indicators=["RSI", "MACD", "BBANDS"])
rsi = fl.calculate_rsi(symbol, include_chart=True)

# Fundamental analysis
fundamentals = fl.get_fundamentals(symbol, include_chart=True)
overview = fl.get_company_overview(symbol)

# Advanced analytics
alpha_beta = fl.alpha_intelligence.calculate_alpha_beta(symbol)
sharpe = fl.alpha_intelligence.calculate_sharpe_ratio(symbol)
```

### Multi-Asset Portfolio Analysis
```python
import fin_lib as fl

# Define portfolio
symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]

# Get current prices
quotes = fl.get_bulk_quotes(symbols)

# Portfolio optimization
portfolio = fl.alpha_intelligence.portfolio_optimization(
    symbols, 
    method="max_sharpe", 
    include_chart=True
)

# Individual analysis
for symbol in symbols:
    analysis = fl.technical_analysis(symbol)
    fundamentals = fl.get_fundamentals(symbol)
```

### Market Overview Dashboard
```python
import fin_lib as fl

# Market status
market_status = fl.get_market_status()

# Major indices (using search or direct symbols)
indices = ["^GSPC", "^IXIC", "^DJI"]  # S&P 500, NASDAQ, Dow Jones
index_quotes = fl.get_bulk_quotes(indices)

# Economic indicators
treasury_rates = fl.economics.get_treasury_rates(include_chart=True)
market_sentiment = fl.economics.get_market_sentiment(include_chart=True)
dollar_index = fl.economics.get_dollar_index(include_chart=True)

# Commodities
precious_metals = fl.commodities.get_precious_metals(include_chart=True)
energy = fl.commodities.get_energy_commodities(include_chart=True)

# Crypto
major_cryptos = fl.crypto.get_major_cryptos(include_chart=True)

# Forex
major_pairs = fl.forex.get_major_pairs(include_chart=True)
```

## Error Handling

All functions return structured error responses:

```python
result = fl.get_quote("INVALID_SYMBOL")
if "error" in result:
    print(f"Error: {result['message']}")
    print(f"Suggestion: {result['suggestion']}")
```

## Performance Features

- **Intelligent Caching**: TTL-based caching (60-1800 seconds)
- **Rate Limit Handling**: Automatic retry with exponential backoff
- **Memory Optimization**: Large datasets automatically serialized
- **Concurrent Safe**: Thread-safe caching implementation

## Dependencies

- **Core**: `yfinance`, `pandas`, `numpy`
- **Technical**: `pandas-ta`
- **Charts**: `plotly`, `matplotlib`, `seaborn`, `mplfinance`
- **Advanced**: `scipy` (for portfolio optimization)

## Documentation

- [API Reference](docs/API_REFERENCE.md) - Complete function documentation
- [Integration Guide](docs/INTEGRATION_GUIDE.md) - AI agent integration patterns
- [Examples](examples/) - Practical usage examples

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: Report bugs and feature requests
- Documentation: Check docs/ directory for detailed guides
- Examples: See examples/ directory for usage patterns
