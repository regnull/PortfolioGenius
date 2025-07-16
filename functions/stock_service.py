from abc import ABC, abstractmethod
from typing import Dict, Optional
import yfinance as yf
import requests
from datetime import datetime


class StockPriceProvider(ABC):
    """Abstract base class for stock price providers."""
    
    @abstractmethod
    def get_stock_price(self, ticker: str) -> Dict[str, any]:
        """
        Get stock price data for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Dictionary containing stock price data with keys:
            - price: Current stock price
            - currency: Currency of the price
            - timestamp: Timestamp of the price
            - provider: Name of the provider
        """
        pass


class YahooFinanceProvider(StockPriceProvider):
    """Yahoo Finance implementation of stock price provider."""
    
    def get_stock_price(self, ticker: str) -> Dict[str, any]:
        """Get stock price from Yahoo Finance API."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if 'regularMarketPrice' not in info and 'currentPrice' not in info:
                raise ValueError(f"No price data found for ticker: {ticker}")
            
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            currency = info.get('currency', 'USD')
            
            return {
                'price': price,
                'currency': currency,
                'timestamp': datetime.now().isoformat(),
                'provider': 'yahoo_finance',
                'ticker': ticker.upper(),
                'company_name': info.get('longName', ''),
                'market_cap': info.get('marketCap'),
                'volume': info.get('volume')
            }
            
        except Exception as e:
            raise Exception(f"Error fetching stock price for {ticker}: {str(e)}")


class StockPriceService:
    """Service class for getting stock prices with pluggable providers."""
    
    def __init__(self, provider: StockPriceProvider = None):
        """Initialize with a stock price provider."""
        self.provider = provider or YahooFinanceProvider()
    
    def get_price(self, ticker: str) -> Dict[str, any]:
        """Get stock price using the configured provider."""
        if not ticker or not ticker.strip():
            raise ValueError("Ticker symbol is required")
        
        ticker = ticker.strip().upper()
        return self.provider.get_stock_price(ticker)
    
    def set_provider(self, provider: StockPriceProvider):
        """Switch to a different stock price provider."""
        self.provider = provider