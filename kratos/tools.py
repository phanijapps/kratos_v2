import json

ALPHA_VANTAGE_SUBAGENTS = [
  {
    "category": "core_stock_apis",
    "description": "Provides comprehensive stock market data including real-time quotes, historical time series, and symbol search capabilities",
    "system_prompt": "You are a stock market data specialist. Your role is to fetch and analyze stock market data using Alpha Vantage APIs. You have access to real-time quotes, historical OHLCV data spanning 20+ years across multiple timeframes (intraday, daily, weekly, monthly), and symbol search capabilities. When users request stock data, determine the appropriate time series interval, fetch the data, and present it in a clear, actionable format. Always include adjusted data when relevant for dividend and split events.",
    "tools": [
      {"tool": "TIME_SERIES_INTRADAY", "description": "Current and 20+ years of historical intraday OHLCV data"},
      {"tool": "TIME_SERIES_DAILY", "description": "Daily time series (OHLCV) covering 20+ years"},
      {"tool": "TIME_SERIES_DAILY_ADJUSTED", "description": "Daily adjusted OHLCV with split/dividend events"},
      {"tool": "TIME_SERIES_WEEKLY", "description": "Weekly time series (last trading day of week)"},
      {"tool": "TIME_SERIES_WEEKLY_ADJUSTED", "description": "Weekly adjusted time series with dividends"},
      {"tool": "TIME_SERIES_MONTHLY", "description": "Monthly time series (last trading day of month)"},
      {"tool": "TIME_SERIES_MONTHLY_ADJUSTED", "description": "Monthly adjusted time series with dividends"},
      {"tool": "GLOBAL_QUOTE", "description": "Latest price and volume for a ticker"},
      {"tool": "REALTIME_BULK_QUOTES", "description": "Realtime quotes for up to 100 symbols"},
      {"tool": "SYMBOL_SEARCH", "description": "Search for symbols by keywords"},
      {"tool": "MARKET_STATUS", "description": "Current market status worldwide"}
    ]
  },
  {
    "category": "options_data_apis",
    "description": "Delivers real-time and historical options market data with Greeks calculations",
    "system_prompt": "You are an options market data analyst. Your expertise is in retrieving and interpreting options chain data, Greeks, and historical options information for US equities. When users request options data, fetch the complete options chain with calculated Greeks (delta, gamma, theta, vega, rho) and provide insights on implied volatility, strike prices, and expiration dates. Support both real-time and historical analysis spanning 15+ years.",
    "tools": [
      {"tool": "REALTIME_OPTIONS", "description": "Realtime US options data with Greeks"},
      {"tool": "HISTORICAL_OPTIONS", "description": "Historical options chain for 15+ years"}
    ]
  },
  {
    "category": "alpha_intelligence",
    "description": "Advanced market intelligence including sentiment analysis, earnings transcripts, market movers, and insider trading",
    "system_prompt": "You are a market intelligence analyst specializing in news sentiment, earnings analysis, and insider trading patterns. Your tools provide access to live market news with AI-powered sentiment scoring, earnings call transcripts with LLM-generated insights, real-time market movers (top gainers, losers, most active), insider transaction tracking, and advanced analytics over both fixed and sliding time windows. When analyzing market events, synthesize multiple data sources to provide comprehensive intelligence reports that identify trends, anomalies, and trading signals.",
    "tools": [
      {"tool": "NEWS_SENTIMENT", "description": "Live and historical market news & sentiment"},
      {"tool": "TOP_GAINERS_LOSERS", "description": "Top 20 gainers, losers, and most active"},
      {"tool": "INSIDER_TRANSACTIONS", "description": "Latest and historical insider transactions"},
      {"tool": "ANALYTICS_FIXED_WINDOW", "description": "Advanced analytics over fixed windows"},
      {"tool": "ANALYTICS_SLIDING_WINDOW", "description": "Advanced analytics over sliding windows"}
    ]
  },
  {
    "category": "fundamental_data",
    "description": "Company financial statements, earnings data, and corporate event calendars",
    "system_prompt": "You are a fundamental analysis expert. Your role is to retrieve and analyze company financial data including income statements, balance sheets, cash flow statements, earnings reports, and company overviews with key financial ratios. You also track corporate events through earnings and IPO calendars. When analyzing companies, assess financial health using multiple statements, calculate key metrics (P/E, ROE, debt ratios, growth rates), and provide comparative analysis across reporting periods. Present findings in a structured format suitable for investment decisions.",
    "tools": [
      {"tool": "COMPANY_OVERVIEW", "description": "Company information, financial ratios, and metrics"},
      {"tool": "INCOME_STATEMENT", "description": "Annual and quarterly income statements"},
      {"tool": "BALANCE_SHEET", "description": "Annual and quarterly balance sheets"},
      {"tool": "CASH_FLOW", "description": "Annual and quarterly cash flow statements"},
      {"tool": "EARNINGS", "description": "Annual and quarterly earnings data"},
      {"tool": "LISTING_STATUS", "description": "Listing and delisting data for equities"},
      {"tool": "EARNINGS_CALENDAR", "description": "Earnings calendar for upcoming earnings"},
      {"tool": "IPO_CALENDAR", "description": "Initial public offering calendar"}
    ]
  },
  {
    "category": "forex",
    "description": "Foreign exchange rates across multiple timeframes",
    "system_prompt": "You are a forex market specialist. Your tools provide foreign exchange rate data across intraday, daily, weekly, and monthly intervals for currency pairs worldwide. When users request FX data, determine the appropriate currency pair and timeframe, retrieve the exchange rate history, and identify trends, support/resistance levels, and volatility patterns. Support analysis for major, minor, and exotic currency pairs.",
    "tools": [
      {"tool": "FX_INTRADAY", "description": "Intraday foreign exchange rates"},
      {"tool": "FX_DAILY", "description": "Daily foreign exchange rates"},
      {"tool": "FX_WEEKLY", "description": "Weekly foreign exchange rates"},
      {"tool": "FX_MONTHLY", "description": "Monthly foreign exchange rates"}
    ]
  },
  {
    "category": "cryptocurrencies",
    "description": "Digital and cryptocurrency market data with exchange rates and historical time series",
    "system_prompt": "You are a cryptocurrency market analyst. Your tools provide real-time exchange rates and historical time series data for digital currencies across intraday, daily, weekly, and monthly intervals. When analyzing crypto markets, retrieve pricing data for major cryptocurrencies (Bitcoin, Ethereum, etc.) against both fiat and crypto pairs, identify market trends, calculate volatility metrics, and track price movements across different timeframes. Present data in both crypto-to-crypto and crypto-to-fiat formats.",
    "tools": [
      {"tool": "CURRENCY_EXCHANGE_RATE", "description": "Exchange rate between digital/crypto currencies"},
      {"tool": "DIGITAL_CURRENCY_INTRADAY", "description": "Intraday time series for digital currencies"},
      {"tool": "DIGITAL_CURRENCY_DAILY", "description": "Daily time series for digital currencies"},
      {"tool": "DIGITAL_CURRENCY_WEEKLY", "description": "Weekly time series for digital currencies"},
      {"tool": "DIGITAL_CURRENCY_MONTHLY", "description": "Monthly time series for digital currencies"}
    ]
  },
  {
    "category": "commodities",
    "description": "Global commodities pricing for energy, metals, and agricultural products",
    "system_prompt": "You are a commodities market expert. Your tools provide global pricing data for energy commodities (WTI crude oil, Brent crude, natural gas), industrial metals (copper, aluminum), and agricultural products (wheat, corn, cotton, sugar, coffee). When users request commodity data, fetch the relevant prices, analyze historical trends, identify seasonal patterns, and correlate movements across related commodities. Support both individual commodity analysis and cross-commodity comparisons.",
    "tools": [
      {"tool": "WTI", "description": "West Texas Intermediate (WTI) crude oil prices"},
      {"tool": "BRENT", "description": "Brent crude oil prices"},
      {"tool": "NATURAL_GAS", "description": "Henry Hub natural gas spot prices"},
      {"tool": "COPPER", "description": "Global copper prices"},
      {"tool": "ALUMINUM", "description": "Global aluminum prices"},
      {"tool": "WHEAT", "description": "Global wheat prices"},
      {"tool": "CORN", "description": "Global corn prices"},
      {"tool": "COTTON", "description": "Global cotton prices"},
      {"tool": "SUGAR", "description": "Global sugar prices"},
      {"tool": "COFFEE", "description": "Global coffee prices"},
      {"tool": "ALL_COMMODITIES", "description": "All commodities prices"}
    ]
  },
  {
    "category": "economic_indicators",
    "description": "Macroeconomic indicators including GDP, inflation, unemployment, and interest rates",
    "system_prompt": "You are a macroeconomic data analyst. Your tools provide access to critical economic indicators including GDP metrics, treasury yields, federal funds rate, inflation (CPI), retail sales, durable goods orders, unemployment rate, and non-farm payroll data. When analyzing economic conditions, retrieve relevant indicators, identify trends in economic growth, inflation, employment, and monetary policy. Correlate multiple indicators to assess overall economic health and provide context for market movements.",
    "tools": [
      {"tool": "REAL_GDP", "description": "Real Gross Domestic Product"},
      {"tool": "REAL_GDP_PER_CAPITA", "description": "Real GDP per capita"},
      {"tool": "TREASURY_YIELD", "description": "Daily treasury yield rates"},
      {"tool": "FEDERAL_FUNDS_RATE", "description": "Federal funds rate (interest rates)"},
      {"tool": "CPI", "description": "Consumer Price Index"},
      {"tool": "INFLATION", "description": "Inflation rates"},
      {"tool": "RETAIL_SALES", "description": "Retail sales data"},
      {"tool": "DURABLES", "description": "Durable goods orders"},
      {"tool": "UNEMPLOYMENT", "description": "Unemployment rate"},
      {"tool": "NONFARM_PAYROLL", "description": "Non-farm payroll data"}
    ]
  },
  {
    "category": "technical_indicators",
    "description": "Comprehensive technical analysis indicators including moving averages, oscillators, momentum, volatility, and volume indicators",
    "system_prompt": "You are a technical analysis specialist. Your tools calculate 49+ technical indicators across multiple categories: moving averages (SMA, EMA, WMA, DEMA, TEMA, etc.), oscillators (RSI, Stochastic, Williams %R), momentum indicators (MACD, ROC, MOM), trend indicators (ADX, Aroon), volatility measures (Bollinger Bands, ATR), volume indicators (OBV, AD), and Hilbert Transform indicators. When performing technical analysis, select appropriate indicators based on the trading strategy, calculate values over relevant timeframes, identify buy/sell signals, support/resistance levels, and trend confirmations. Combine multiple indicators to reduce false signals and provide comprehensive trading insights.",
    "tools": [
      {"tool": "SMA", "description": "Simple moving average (SMA) values"},
      {"tool": "EMA", "description": "Exponential moving average (EMA) values"},
      {"tool": "WMA", "description": "Weighted moving average (WMA) values"},
      {"tool": "DEMA", "description": "Double exponential moving average (DEMA) values"},
      {"tool": "TEMA", "description": "Triple exponential moving average (TEMA) values"},
      {"tool": "TRIMA", "description": "Triangular moving average (TRIMA) values"},
      {"tool": "KAMA", "description": "Kaufman adaptive moving average (KAMA) values"},
      {"tool": "MAMA", "description": "MESA adaptive moving average (MAMA) values"},
      {"tool": "VWAP", "description": "Volume weighted average price (VWAP) for intraday time series"},
      {"tool": "T3", "description": "Triple exponential moving average (T3) values"},
      {"tool": "MACD", "description": "Moving average convergence / divergence (MACD) values"},
      {"tool": "MACDEXT", "description": "Moving average convergence / divergence values with controllable moving average type"},
      {"tool": "STOCH", "description": "Stochastic oscillator (STOCH) values"},
      {"tool": "STOCHF", "description": "Stochastic fast (STOCHF) values"},
      {"tool": "RSI", "description": "Relative strength index (RSI) values"},
      {"tool": "STOCHRSI", "description": "Stochastic relative strength index (STOCHRSI) values"},
      {"tool": "WILLR", "description": "Williams' %R (WILLR) values"},
      {"tool": "ADX", "description": "Average directional movement index (ADX) values"},
      {"tool": "ADXR", "description": "Average directional movement index rating (ADXR) values"},
      {"tool": "APO", "description": "Absolute price oscillator (APO) values"},
      {"tool": "PPO", "description": "Percentage price oscillator (PPO) values"},
      {"tool": "MOM", "description": "Momentum (MOM) values"},
      {"tool": "BOP", "description": "Balance of power (BOP) values"},
      {"tool": "CCI", "description": "Commodity channel index (CCI) values"},
      {"tool": "CMO", "description": "Chande momentum oscillator (CMO) values"},
      {"tool": "ROC", "description": "Rate of change (ROC) values"},
      {"tool": "ROCR", "description": "Rate of change ratio (ROCR) values"},
      {"tool": "AROON", "description": "Aroon (AROON) values"},
      {"tool": "AROONOSC", "description": "Aroon oscillator (AROONOSC) values"},
      {"tool": "MFI", "description": "Money flow index (MFI) values"},
      {"tool": "TRIX", "description": "1-day rate of change of a triple smooth exponential moving average (TRIX) values"},
      {"tool": "ULTOSC", "description": "Ultimate oscillator (ULTOSC) values"},
      {"tool": "DX", "description": "Directional movement index (DX) values"},
      {"tool": "MINUS_DI", "description": "Minus directional indicator (MINUS_DI) values"},
      {"tool": "PLUS_DI", "description": "Plus directional indicator (PLUS_DI) values"},
      {"tool": "MINUS_DM", "description": "Minus directional movement (MINUS_DM) values"},
      {"tool": "PLUS_DM", "description": "Plus directional movement (PLUS_DM) values"},
      {"tool": "BBANDS", "description": "Bollinger bands (BBANDS) values"},
      {"tool": "MIDPOINT", "description": "Midpoint values - (highest value + lowest value)/2"},
      {"tool": "MIDPRICE", "description": "Midpoint price values - (highest high + lowest low)/2"},
      {"tool": "SAR", "description": "Parabolic SAR (SAR) values"},
      {"tool": "TRANGE", "description": "True range (TRANGE) values"},
      {"tool": "ATR", "description": "Average true range (ATR) values"},
      {"tool": "NATR", "description": "Normalized average true range (NATR) values"},
      {"tool": "AD", "description": "Chaikin A/D line (AD) values"},
      {"tool": "ADOSC", "description": "Chaikin A/D oscillator (ADOSC) values"},
      {"tool": "OBV", "description": "On balance volume (OBV) values"},
      {"tool": "HT_TRENDLINE", "description": "Hilbert transform, instantaneous trendline (HT_TRENDLINE) values"},
      {"tool": "HT_SINE", "description": "Hilbert transform, sine wave (HT_SINE) values"},
      {"tool": "HT_TRENDMODE", "description": "Hilbert transform, trend vs cycle mode (HT_TRENDMODE) values"},
      {"tool": "HT_DCPERIOD", "description": "Hilbert transform, dominant cycle period (HT_DCPERIOD) values"},
      {"tool": "HT_DCPHASE", "description": "Hilbert transform, dominant cycle phase (HT_DCPHASE) values"},
      {"tool": "HT_PHASOR", "description": "Hilbert transform, phasor components (HT_PHASOR) values"}
    ]
  }
]
