"""
Complex Financial Analysis Examples using fin_lib

This module demonstrates advanced usage patterns combining multiple fin_lib modules
for comprehensive financial analysis using TTD (The Trade Desk) and SPX (S&P 500 Index).
"""

import fin_lib as fl
import pandas as pd
from datetime import datetime, timedelta


def comprehensive_stock_analysis(symbol="TTD"):
    """
    Comprehensive analysis of a single stock combining multiple analysis types.
    
    Args:
        symbol: Stock ticker symbol (default: TTD - The Trade Desk)
        
    Returns:
        Dictionary containing comprehensive analysis results
    """
    print(f"\n🔍 COMPREHENSIVE ANALYSIS: {symbol}")
    print("=" * 50)
    
    analysis_results = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # 1. Basic Market Data
    print("📊 Getting market data...")
    quote = fl.get_quote(symbol)
    historical = fl.get_historical_data(symbol, period="2y", include_chart=True)
    
    analysis_results["analysis"]["market_data"] = {
        "current_quote": quote,
        "historical_data_points": len(historical.get("data", [])),
        "has_chart": "chart" in historical
    }
    
    # 2. Technical Analysis
    print("📈 Performing technical analysis...")
    technical = fl.technical_analysis(
        symbol, 
        indicators=["RSI", "MACD", "BBANDS", "ATR", "OBV", "STOCH", "CCI"],
        period="1y",
        include_chart=True
    )
    
    # Individual technical indicators with charts
    rsi = fl.calculate_rsi(symbol, length=14, include_chart=True)
    macd = fl.calculate_macd(symbol, include_chart=True)
    bbands = fl.calculate_bollinger_bands(symbol, include_chart=True)
    
    analysis_results["analysis"]["technical"] = {
        "comprehensive_analysis": technical,
        "rsi_analysis": rsi,
        "macd_analysis": macd,
        "bollinger_bands": bbands
    }
    
    # 3. Fundamental Analysis
    print("💰 Analyzing fundamentals...")
    fundamentals = fl.get_fundamentals(symbol, include_chart=True)
    company_overview = fl.get_company_overview(symbol)
    financial_statements = fl.get_financial_statements(symbol)
    key_metrics = fl.get_key_metrics(symbol)
    valuation_ratios = fl.get_valuation_ratios(symbol)
    
    analysis_results["analysis"]["fundamentals"] = {
        "comprehensive": fundamentals,
        "company_overview": company_overview,
        "financial_statements": financial_statements,
        "key_metrics": key_metrics,
        "valuation_ratios": valuation_ratios
    }
    
    # 4. Advanced Analytics
    print("🧠 Computing advanced analytics...")
    alpha_beta = fl.alpha_intelligence.calculate_alpha_beta(
        symbol, 
        benchmark="^GSPC",  # S&P 500 as benchmark
        period="2y",
        include_chart=True
    )
    
    sharpe_ratio = fl.alpha_intelligence.calculate_sharpe_ratio(
        symbol,
        period="2y",
        risk_free_rate=0.045  # Current approximate 10-year treasury rate
    )
    
    analysis_results["analysis"]["advanced_analytics"] = {
        "alpha_beta": alpha_beta,
        "sharpe_ratio": sharpe_ratio
    }
    
    # 5. Options Analysis (if available)
    print("📋 Analyzing options...")
    try:
        options_chain = fl.options.get_options_chain(symbol, include_greeks=True)
        implied_vol = fl.options.get_implied_volatility(symbol, include_chart=True)
        
        analysis_results["analysis"]["options"] = {
            "options_chain": options_chain,
            "implied_volatility": implied_vol
        }
    except Exception as e:
        analysis_results["analysis"]["options"] = {
            "error": str(e),
            "message": "Options data may not be available for this symbol"
        }
    
    print(f"✅ Comprehensive analysis complete for {symbol}")
    return analysis_results


def market_comparison_analysis(symbols=["TTD", "^GSPC"], benchmark="^GSPC"):
    """
    Compare multiple symbols against a benchmark with comprehensive metrics.
    
    Args:
        symbols: List of symbols to analyze (default: TTD vs S&P 500)
        benchmark: Benchmark symbol for comparison
        
    Returns:
        Dictionary containing comparative analysis
    """
    print(f"\n📊 MARKET COMPARISON ANALYSIS")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Benchmark: {benchmark}")
    print("=" * 50)
    
    comparison_results = {
        "symbols": symbols,
        "benchmark": benchmark,
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # 1. Current Market Data Comparison
    print("📈 Getting current market data...")
    bulk_quotes = fl.get_bulk_quotes(symbols)
    market_status = fl.get_market_status()
    
    comparison_results["analysis"]["market_data"] = {
        "bulk_quotes": bulk_quotes,
        "market_status": market_status
    }
    
    # 2. Historical Performance Comparison
    print("📊 Comparing historical performance...")
    comparison_chart = fl.compare_symbols(
        symbols,
        period="2y",
        normalize=True,  # Show percentage changes
        include_chart=True
    )
    
    comparison_results["analysis"]["performance_comparison"] = comparison_chart
    
    # 3. Individual Alpha/Beta Analysis
    print("🧠 Computing alpha/beta for each symbol...")
    alpha_beta_results = {}
    
    for symbol in symbols:
        if symbol != benchmark:  # Don't compare benchmark to itself
            try:
                alpha_beta = fl.alpha_intelligence.calculate_alpha_beta(
                    symbol,
                    benchmark=benchmark,
                    period="2y",
                    include_chart=True
                )
                alpha_beta_results[symbol] = alpha_beta
            except Exception as e:
                alpha_beta_results[symbol] = {"error": str(e)}
    
    comparison_results["analysis"]["alpha_beta_analysis"] = alpha_beta_results
    
    # 4. Risk-Adjusted Returns Comparison
    print("📊 Analyzing risk-adjusted returns...")
    sharpe_ratios = {}
    
    for symbol in symbols:
        try:
            sharpe = fl.alpha_intelligence.calculate_sharpe_ratio(
                symbol,
                period="2y",
                risk_free_rate=0.045
            )
            sharpe_ratios[symbol] = sharpe
        except Exception as e:
            sharpe_ratios[symbol] = {"error": str(e)}
    
    comparison_results["analysis"]["risk_adjusted_returns"] = sharpe_ratios
    
    # 5. Technical Analysis Comparison
    print("📈 Comparing technical indicators...")
    technical_comparison = {}
    
    for symbol in symbols:
        try:
            technical = fl.technical_analysis(
                symbol,
                indicators=["RSI", "MACD", "ATR"],
                period="6mo"
            )
            technical_comparison[symbol] = technical
        except Exception as e:
            technical_comparison[symbol] = {"error": str(e)}
    
    comparison_results["analysis"]["technical_comparison"] = technical_comparison
    
    print("✅ Market comparison analysis complete")
    return comparison_results


def portfolio_optimization_analysis(symbols=["TTD", "AAPL", "MSFT", "GOOGL", "TSLA"]):
    """
    Advanced portfolio optimization using Modern Portfolio Theory.
    
    Args:
        symbols: List of symbols for portfolio optimization
        
    Returns:
        Dictionary containing portfolio optimization results
    """
    print(f"\n🎯 PORTFOLIO OPTIMIZATION ANALYSIS")
    print(f"Symbols: {', '.join(symbols)}")
    print("=" * 50)
    
    portfolio_results = {
        "symbols": symbols,
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # 1. Current Portfolio Snapshot
    print("📊 Getting current portfolio data...")
    current_quotes = fl.get_bulk_quotes(symbols)
    portfolio_results["analysis"]["current_data"] = current_quotes
    
    # 2. Portfolio Optimization - Maximum Sharpe Ratio
    print("🎯 Optimizing for maximum Sharpe ratio...")
    max_sharpe_portfolio = fl.alpha_intelligence.portfolio_optimization(
        symbols,
        period="2y",
        method="max_sharpe",
        include_chart=True
    )
    
    # 3. Portfolio Optimization - Minimum Volatility
    print("🛡️ Optimizing for minimum volatility...")
    min_vol_portfolio = fl.alpha_intelligence.portfolio_optimization(
        symbols,
        period="2y",
        method="min_vol",
        include_chart=True
    )
    
    # 4. Equal Weight Portfolio for Comparison
    print("⚖️ Creating equal weight portfolio...")
    equal_weight_portfolio = fl.alpha_intelligence.portfolio_optimization(
        symbols,
        period="2y",
        method="equal_weight",
        include_chart=True
    )
    
    portfolio_results["analysis"]["optimizations"] = {
        "max_sharpe": max_sharpe_portfolio,
        "min_volatility": min_vol_portfolio,
        "equal_weight": equal_weight_portfolio
    }
    
    # 5. Individual Stock Analysis for Portfolio Context
    print("🔍 Analyzing individual stocks...")
    individual_analysis = {}
    
    for symbol in symbols:
        try:
            # Get key metrics for each stock
            alpha_beta = fl.alpha_intelligence.calculate_alpha_beta(symbol, period="1y")
            sharpe = fl.alpha_intelligence.calculate_sharpe_ratio(symbol, period="1y")
            
            individual_analysis[symbol] = {
                "alpha_beta": alpha_beta,
                "sharpe_ratio": sharpe
            }
        except Exception as e:
            individual_analysis[symbol] = {"error": str(e)}
    
    portfolio_results["analysis"]["individual_stocks"] = individual_analysis
    
    print("✅ Portfolio optimization analysis complete")
    return portfolio_results


def multi_asset_market_overview():
    """
    Comprehensive multi-asset market overview combining stocks, forex, crypto, and commodities.
    
    Returns:
        Dictionary containing multi-asset market analysis
    """
    print(f"\n🌍 MULTI-ASSET MARKET OVERVIEW")
    print("=" * 50)
    
    market_overview = {
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # 1. Stock Market Overview
    print("📈 Stock market overview...")
    major_indices = ["^GSPC", "^IXIC", "^DJI", "^RUT"]  # S&P 500, NASDAQ, Dow, Russell 2000
    index_quotes = fl.get_bulk_quotes(major_indices)
    market_status = fl.get_market_status()
    
    # Individual stock analysis
    ttd_analysis = fl.technical_analysis("TTD", indicators=["RSI", "MACD"], period="3mo")
    
    market_overview["analysis"]["equities"] = {
        "major_indices": index_quotes,
        "market_status": market_status,
        "ttd_technical": ttd_analysis
    }
    
    # 2. Forex Market
    print("💱 Forex market overview...")
    major_pairs = fl.forex.get_major_pairs(include_rates=True, include_chart=True)
    usd_eur = fl.forex.get_exchange_rate("USD", "EUR", include_chart=True)
    
    market_overview["analysis"]["forex"] = {
        "major_pairs": major_pairs,
        "usd_eur_detailed": usd_eur
    }
    
    # 3. Cryptocurrency Market
    print("₿ Cryptocurrency overview...")
    major_cryptos = fl.crypto.get_major_cryptos(include_prices=True, include_chart=True)
    btc_price = fl.crypto.get_crypto_price("BTC-USD", include_chart=True)
    
    market_overview["analysis"]["crypto"] = {
        "major_cryptos": major_cryptos,
        "btc_detailed": btc_price
    }
    
    # 4. Commodities Market
    print("🥇 Commodities overview...")
    precious_metals = fl.commodities.get_precious_metals(include_prices=True, include_chart=True)
    energy_commodities = fl.commodities.get_energy_commodities(include_prices=True, include_chart=True)
    gold_price = fl.commodities.get_commodity_price("GC=F", include_chart=True)
    
    market_overview["analysis"]["commodities"] = {
        "precious_metals": precious_metals,
        "energy": energy_commodities,
        "gold_detailed": gold_price
    }
    
    # 5. Economic Indicators
    print("📊 Economic indicators...")
    treasury_rates = fl.economics.get_treasury_rates(include_chart=True)
    market_sentiment = fl.economics.get_market_sentiment(include_chart=True)
    dollar_index = fl.economics.get_dollar_index(include_chart=True)
    
    market_overview["analysis"]["economics"] = {
        "treasury_rates": treasury_rates,
        "market_sentiment": market_sentiment,
        "dollar_index": dollar_index
    }
    
    print("✅ Multi-asset market overview complete")
    return market_overview


def advanced_ttd_vs_spx_analysis():
    """
    Advanced comparative analysis between TTD and SPX with multiple timeframes and metrics.
    
    Returns:
        Dictionary containing detailed TTD vs SPX analysis
    """
    print(f"\n🔬 ADVANCED TTD vs SPX ANALYSIS")
    print("=" * 50)
    
    analysis_results = {
        "comparison": "TTD vs ^GSPC",
        "timestamp": datetime.now().isoformat(),
        "analysis": {}
    }
    
    # 1. Multi-timeframe Performance Analysis
    print("📊 Multi-timeframe performance analysis...")
    timeframes = ["1mo", "3mo", "6mo", "1y", "2y"]
    performance_analysis = {}
    
    for timeframe in timeframes:
        try:
            comparison = fl.compare_symbols(
                ["TTD", "^GSPC"],
                period=timeframe,
                normalize=True,
                include_chart=True
            )
            performance_analysis[timeframe] = comparison
        except Exception as e:
            performance_analysis[timeframe] = {"error": str(e)}
    
    analysis_results["analysis"]["performance_by_timeframe"] = performance_analysis
    
    # 2. Risk-Return Analysis
    print("📈 Risk-return analysis...")
    ttd_alpha_beta = fl.alpha_intelligence.calculate_alpha_beta(
        "TTD",
        benchmark="^GSPC",
        period="2y",
        include_chart=True
    )
    
    ttd_sharpe = fl.alpha_intelligence.calculate_sharpe_ratio("TTD", period="2y")
    spx_sharpe = fl.alpha_intelligence.calculate_sharpe_ratio("^GSPC", period="2y")
    
    analysis_results["analysis"]["risk_return"] = {
        "ttd_alpha_beta": ttd_alpha_beta,
        "ttd_sharpe": ttd_sharpe,
        "spx_sharpe": spx_sharpe
    }
    
    # 3. Technical Analysis Comparison
    print("📊 Technical analysis comparison...")
    ttd_technical = fl.technical_analysis(
        "TTD",
        indicators=["RSI", "MACD", "BBANDS", "ATR", "STOCH", "CCI", "OBV"],
        period="1y",
        include_chart=True
    )
    
    spx_technical = fl.technical_analysis(
        "^GSPC",
        indicators=["RSI", "MACD", "BBANDS", "ATR", "STOCH", "CCI", "OBV"],
        period="1y",
        include_chart=True
    )
    
    analysis_results["analysis"]["technical_comparison"] = {
        "ttd": ttd_technical,
        "spx": spx_technical
    }
    
    # 4. Volatility Analysis
    print("📊 Volatility analysis...")
    # Get historical data for volatility calculations
    ttd_hist = fl.get_historical_data("TTD", period="1y")
    spx_hist = fl.get_historical_data("^GSPC", period="1y")
    
    analysis_results["analysis"]["volatility_data"] = {
        "ttd_historical": ttd_hist,
        "spx_historical": spx_hist
    }
    
    # 5. Fundamental Analysis (TTD only, as SPX is an index)
    print("💰 TTD fundamental analysis...")
    ttd_fundamentals = fl.get_fundamentals("TTD", include_chart=True)
    ttd_overview = fl.get_company_overview("TTD")
    ttd_metrics = fl.get_key_metrics("TTD")
    
    analysis_results["analysis"]["ttd_fundamentals"] = {
        "comprehensive": ttd_fundamentals,
        "company_overview": ttd_overview,
        "key_metrics": ttd_metrics
    }
    
    print("✅ Advanced TTD vs SPX analysis complete")
    return analysis_results


def run_all_examples():
    """
    Run all complex analysis examples and return combined results.
    
    Returns:
        Dictionary containing all analysis results
    """
    print("🚀 RUNNING ALL COMPLEX ANALYSIS EXAMPLES")
    print("=" * 60)
    
    all_results = {
        "execution_timestamp": datetime.now().isoformat(),
        "examples": {}
    }
    
    try:
        # 1. Comprehensive Stock Analysis
        all_results["examples"]["comprehensive_ttd"] = comprehensive_stock_analysis("TTD")
        
        # 2. Market Comparison Analysis
        all_results["examples"]["market_comparison"] = market_comparison_analysis(["TTD", "^GSPC"])
        
        # 3. Portfolio Optimization
        all_results["examples"]["portfolio_optimization"] = portfolio_optimization_analysis()
        
        # 4. Multi-Asset Market Overview
        all_results["examples"]["multi_asset_overview"] = multi_asset_market_overview()
        
        # 5. Advanced TTD vs SPX Analysis
        all_results["examples"]["ttd_vs_spx_advanced"] = advanced_ttd_vs_spx_analysis()
        
        print("\n🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        all_results["error"] = str(e)
    
    return all_results


if __name__ == "__main__":
    """
    Example usage of the complex analysis functions.
    """
    print("fin_lib Complex Analysis Examples")
    print("Using TTD (The Trade Desk) and SPX (S&P 500) tickers")
    print("=" * 60)
    
    # Run individual examples
    print("\n1. Running comprehensive TTD analysis...")
    ttd_analysis = comprehensive_stock_analysis("TTD")
    
    print("\n2. Running TTD vs SPX comparison...")
    comparison = market_comparison_analysis(["TTD", "^GSPC"])
    
    print("\n3. Running portfolio optimization...")
    portfolio = portfolio_optimization_analysis(["TTD", "AAPL", "MSFT", "GOOGL"])
    
    print("\n4. Running multi-asset market overview...")
    market_overview = multi_asset_market_overview()
    
    print("\n5. Running advanced TTD vs SPX analysis...")
    advanced_analysis = advanced_ttd_vs_spx_analysis()
    
    print("\n✅ All examples completed!")
    print("Check the returned dictionaries for detailed analysis results.")
