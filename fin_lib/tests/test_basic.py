"""
Basic tests for fin_lib functionality.

These tests use real API calls with rate limiting for validation.
"""

import pytest
import time
from typing import Dict, Any

import fin_lib as fl


class TestBasicFunctionality:
    """Test basic fin_lib functionality with real API calls."""
    
    @pytest.fixture(autouse=True)
    def rate_limit(self):
        """Add delay between tests to respect API rate limits."""
        time.sleep(1)  # 1 second delay between tests
    
    def test_get_quote(self):
        """Test getting a stock quote."""
        result = fl.get_quote("AAPL")
        
        # Should not have error
        assert "error" not in result
        
        # Should have required fields
        assert "quote" in result
        assert "symbol" in result["quote"]
        assert result["quote"]["symbol"] == "AAPL"
    
    def test_get_historical_data(self):
        """Test getting historical data."""
        result = fl.get_historical_data("AAPL", period="5d")
        
        # Should not have error
        assert "error" not in result
        
        # Should have data
        assert "data" in result
        assert len(result["data"]) > 0
        
        # Should have required fields
        assert "symbol" in result
        assert result["symbol"] == "AAPL"
    
    def test_technical_analysis(self):
        """Test technical analysis."""
        result = fl.technical_analysis("AAPL", indicators=["RSI"], period="200d")
        
        # Should not have error
        assert "error" not in result
        
        # Should have indicators
        assert "indicators" in result
        assert "RSI" in result["indicators"]
    
    def test_forex_rate(self):
        """Test forex exchange rate."""
        result = fl.forex.get_exchange_rate("USD", "EUR")
        
        # Should not have error
        assert "error" not in result
        
        # Should have rate
        assert "rate" in result
        assert isinstance(result["rate"], (int, float))
    
    def test_crypto_price(self):
        """Test crypto price."""
        result = fl.crypto.get_crypto_price("BTC-USD")
        
        # Should not have error
        assert "error" not in result
        
        # Should have quote
        assert "quote" in result
        assert "price" in result["quote"]
    
    def test_commodity_price(self):
        """Test commodity price."""
        result = fl.commodities.get_commodity_price("GC=F")  # Gold
        
        # Should not have error
        assert "error" not in result
        
        # Should have quote
        assert "quote" in result
        assert "price" in result["quote"]
    
    def test_error_handling(self):
        """Test error handling with invalid symbol."""
        result = fl.get_quote("INVALID_SYMBOL_12345")
        
        # Should have error or handle gracefully
        # Note: Some invalid symbols might still return data
        assert isinstance(result, dict)
        assert "tool" in result
    
    def test_bulk_quotes(self):
        """Test bulk quotes."""
        symbols = ["AAPL", "MSFT"]
        result = fl.get_bulk_quotes(symbols)
        
        # Should not have error
        assert "error" not in result
        
        # Should have quotes
        assert "quotes" in result
        assert len(result["quotes"]) == len(symbols)
    
    def test_search_symbols(self):
        """Test symbol search."""
        result = fl.search_symbols("Apple")
        
        # Should not have error or handle gracefully
        assert isinstance(result, dict)
        assert "tool" in result
    
    def test_market_status(self):
        """Test market status."""
        result = fl.get_market_status()
        
        # Should not have error
        assert "error" not in result
        
        # Should have status
        assert "status" in result
        assert "region" in result["status"]


class TestAdvancedFunctionality:
    """Test advanced fin_lib functionality."""
    
    @pytest.fixture(autouse=True)
    def rate_limit(self):
        """Add delay between tests to respect API rate limits."""
        time.sleep(2)  # 2 second delay for advanced tests
    
    def test_alpha_beta_calculation(self):
        """Test alpha/beta calculation."""
        result = fl.alpha_intelligence.calculate_alpha_beta("AAPL", period="1y")
        
        # Should not have error
        assert "error" not in result
        
        # Should have alpha and beta
        assert "alpha" in result
        assert "beta" in result
        assert isinstance(result["alpha"], (int, float))
        assert isinstance(result["beta"], (int, float))
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        result = fl.alpha_intelligence.calculate_sharpe_ratio("AAPL", period="1y")
        
        # Should not have error
        assert "error" not in result
        
        # Should have Sharpe ratio
        assert "sharpe_ratio" in result
        assert isinstance(result["sharpe_ratio"], (int, float))
    
    def test_portfolio_optimization(self):
        """Test portfolio optimization."""
        symbols = ["AAPL", "MSFT"]
        result = fl.alpha_intelligence.portfolio_optimization(symbols, period="6mo")
        
        # Should not have error
        assert "error" not in result
        
        # Should have weights
        assert "weights" in result
        assert len(result["weights"]) == len(symbols)
        
        # Weights should sum to approximately 1
        total_weight = sum(result["weights"].values())
        assert abs(total_weight - 1.0) < 0.01


class TestModuleImports:
    """Test that all modules can be imported correctly."""
    
    def test_core_import(self):
        """Test core module import."""
        from fin_lib import core
        assert hasattr(core, 'get_quote')
    
    def test_technical_import(self):
        """Test technical module import."""
        from fin_lib import technical
        assert hasattr(technical, 'technical_analysis')
    
    def test_fundamentals_import(self):
        """Test fundamentals module import."""
        from fin_lib import fundamentals
        assert hasattr(fundamentals, 'get_fundamentals')
    
    def test_forex_import(self):
        """Test forex module import."""
        from fin_lib import forex
        assert hasattr(forex, 'get_exchange_rate')
    
    def test_crypto_import(self):
        """Test crypto module import."""
        from fin_lib import crypto
        assert hasattr(crypto, 'get_crypto_price')
    
    def test_commodities_import(self):
        """Test commodities module import."""
        from fin_lib import commodities
        assert hasattr(commodities, 'get_commodity_price')
    
    def test_economics_import(self):
        """Test economics module import."""
        from fin_lib import economics
        assert hasattr(economics, 'get_treasury_rates')
    
    def test_options_import(self):
        """Test options module import."""
        from fin_lib import options
        assert hasattr(options, 'get_options_chain')
    
    def test_alpha_intelligence_import(self):
        """Test alpha_intelligence module import."""
        from fin_lib import alpha_intelligence
        assert hasattr(alpha_intelligence, 'calculate_alpha_beta')


if __name__ == "__main__":
    """Run tests manually."""
    import sys
    
    print("Running basic fin_lib tests...")
    
    # Test imports
    try:
        import fin_lib as fl
        print("✓ fin_lib imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        sys.exit(1)
    
    # Test basic functionality
    try:
        quote = fl.get_quote("AAPL")
        if "error" not in quote:
            print("✓ get_quote() working")
        else:
            print(f"✗ get_quote() error: {quote['message']}")
    except Exception as e:
        print(f"✗ get_quote() exception: {e}")
    
    # Test forex
    try:
        rate = fl.forex.get_exchange_rate("USD", "EUR")
        if "error" not in rate:
            print("✓ forex.get_exchange_rate() working")
        else:
            print(f"✗ forex error: {rate['message']}")
    except Exception as e:
        print(f"✗ forex exception: {e}")
    
    print("Basic tests completed.")
