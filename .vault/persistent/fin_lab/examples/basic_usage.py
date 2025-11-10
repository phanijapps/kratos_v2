"""
Basic usage examples for fin_lib.

This module demonstrates simple, common use cases for AI agents.
"""

import fin_lib as fl


def basic_stock_analysis():
    """Basic stock analysis workflow."""
    print("=== Basic Stock Analysis ===")
    
    # Get real-time quote
    quote = fl.get_quote("AAPL")
    if "error" not in quote:
        price = quote["quote"]["price"]
        change = quote["quote"]["regular_market_change"]
        print(f"AAPL: ${price} ({change:+.2f})")
    
    # Get historical data
    data = fl.get_historical_data("AAPL", period="1mo")
    if "error" not in data:
        print(f"Retrieved {len(data['data'])} data points")
    
    # Technical analysis
    rsi = fl.calculate_rsi("AAPL")
    if "error" not in rsi and "data" in rsi:
        current_rsi = rsi["data"][-1] if rsi["data"] else None
        print(f"Current RSI: {current_rsi}")


def multi_asset_overview():
    """Multi-asset market overview."""
    print("\n=== Multi-Asset Overview ===")
    
    # Stock quotes
    stocks = ["AAPL", "MSFT", "GOOGL"]
    quotes = fl.get_bulk_quotes(stocks)
    if "error" not in quotes:
        for quote in quotes["quotes"]:
            symbol = quote["symbol"]
            price = quote["price"]
            print(f"{symbol}: ${price}")
    
    # Forex rate
    forex = fl.forex.get_exchange_rate("USD", "EUR")
    if "error" not in forex:
        rate = forex["rate"]
        print(f"USD/EUR: {rate}")
    
    # Crypto price
    crypto = fl.crypto.get_crypto_price("BTC-USD")
    if "error" not in crypto:
        price = crypto["quote"]["price"]
        print(f"Bitcoin: ${price}")
    
    # Gold price
    gold = fl.commodities.get_commodity_price("GC=F")
    if "error" not in gold:
        price = gold["quote"]["price"]
        print(f"Gold: ${price}")


def technical_analysis_example():
    """Technical analysis example."""
    print("\n=== Technical Analysis ===")
    
    # Comprehensive technical analysis
    analysis = fl.technical_analysis("AAPL", indicators=["RSI", "MACD", "SMA"])
    if "error" not in analysis:
        indicators = analysis["indicators"]
        for indicator, data in indicators.items():
            if "error" not in data:
                print(f"{indicator}: Available")
            else:
                print(f"{indicator}: {data['error']}")
    
    # Individual indicators
    rsi = fl.calculate_rsi("AAPL", length=14)
    if "error" not in rsi:
        print("RSI calculation successful")
    
    macd = fl.calculate_macd("AAPL")
    if "error" not in macd:
        print("MACD calculation successful")


def fundamental_analysis_example():
    """Fundamental analysis example."""
    print("\n=== Fundamental Analysis ===")
    
    # Company overview
    overview = fl.get_company_overview("AAPL")
    if "error" not in overview:
        company_name = overview["overview"].get("longName", "N/A")
        sector = overview["overview"].get("sector", "N/A")
        print(f"Company: {company_name}")
        print(f"Sector: {sector}")
    
    # Key metrics
    metrics = fl.get_key_metrics("AAPL")
    if "error" not in metrics:
        pe_ratio = metrics["metrics"].get("trailingPE", "N/A")
        roe = metrics["metrics"].get("returnOnEquity", "N/A")
        print(f"P/E Ratio: {pe_ratio}")
        print(f"ROE: {roe}")


def advanced_analytics_example():
    """Advanced analytics example."""
    print("\n=== Advanced Analytics ===")
    
    # Alpha/Beta analysis
    alpha_beta = fl.alpha_intelligence.calculate_alpha_beta("AAPL")
    if "error" not in alpha_beta:
        alpha = alpha_beta["alpha"]
        beta = alpha_beta["beta"]
        print(f"Alpha: {alpha:.4f}, Beta: {beta:.4f}")
    
    # Sharpe ratio
    sharpe = fl.alpha_intelligence.calculate_sharpe_ratio("AAPL")
    if "error" not in sharpe:
        ratio = sharpe["sharpe_ratio"]
        print(f"Sharpe Ratio: {ratio:.4f}")
    
    # Portfolio optimization
    symbols = ["AAPL", "MSFT", "GOOGL"]
    portfolio = fl.alpha_intelligence.portfolio_optimization(symbols)
    if "error" not in portfolio:
        weights = portfolio["weights"]
        print("Optimal weights:")
        for symbol, weight in weights.items():
            print(f"  {symbol}: {weight:.2%}")


def error_handling_example():
    """Error handling example."""
    print("\n=== Error Handling ===")
    
    # Invalid symbol
    result = fl.get_quote("INVALID_SYMBOL")
    if "error" in result:
        print(f"Error: {result['message']}")
        print(f"Suggestion: {result['suggestion']}")
    
    # Insufficient data
    result = fl.calculate_rsi("AAPL", period="1d")  # Too short period
    if "error" in result:
        print(f"Error: {result['message']}")


def currency_conversion_example():
    """Currency conversion example."""
    print("\n=== Currency Conversion ===")
    
    # Convert USD to EUR
    conversion = fl.forex.convert_currency(1000, "USD", "EUR")
    if "error" not in conversion:
        amount = conversion["converted_amount"]
        rate = conversion["exchange_rate"]
        print(f"$1000 USD = €{amount:.2f} EUR (rate: {rate:.4f})")


def market_sentiment_example():
    """Market sentiment example."""
    print("\n=== Market Sentiment ===")
    
    # VIX and sentiment indicators
    sentiment = fl.economics.get_market_sentiment()
    if "error" not in sentiment:
        vix = sentiment["sentiment"]["VIX"]["value"]
        print(f"VIX (Fear Index): {vix}")
    
    # Treasury rates
    rates = fl.economics.get_treasury_rates()
    if "error" not in rates:
        ten_year = rates["rates"]["10Y"]["rate"]
        print(f"10-Year Treasury: {ten_year}%")


if __name__ == "__main__":
    """Run all examples."""
    try:
        basic_stock_analysis()
        multi_asset_overview()
        technical_analysis_example()
        fundamental_analysis_example()
        advanced_analytics_example()
        error_handling_example()
        currency_conversion_example()
        market_sentiment_example()
        
        print("\n=== All Examples Completed ===")
        
    except Exception as e:
        print(f"Example failed: {e}")
        print("This may be due to network issues or API rate limits.")
