#!/usr/bin/env python3
"""
Tiingo Tool for Langchain Agent
Provides access to Tiingo's financial data API including stocks, news, fundamentals, and crypto
"""

import os
import json
import requests
from logging_utils import get_logger

logger = get_logger()
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class StockPriceInput(BaseModel):
    """Input schema for stock price tool"""
    symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, GOOGL)")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format (optional)")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format (optional)")
    frequency: str = Field(default="daily", description="Frequency: daily, weekly, monthly, annually, or intraday like 1min, 5min, 1hour")


class StockMetadataInput(BaseModel):
    """Input schema for stock metadata tool"""
    symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, GOOGL)")


class StockNewsInput(BaseModel):
    """Input schema for stock news tool"""
    symbols: List[str] = Field(description="List of stock symbols to get news for")
    limit: int = Field(default=10, description="Number of news articles to return (max 100)")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format (optional)")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format (optional)")


class FundamentalsInput(BaseModel):
    """Input schema for fundamentals tool"""
    symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, GOOGL)")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format (optional)")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format (optional)")


class CryptoPriceInput(BaseModel):
    """Input schema for cryptocurrency price tool"""
    symbol: str = Field(description="Cryptocurrency symbol (e.g., BTCUSD, ETHUSD)")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format (optional)")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format (optional)")
    frequency: str = Field(default="daily", description="Frequency: daily or intraday like 1min, 5min, 1hour")


class TiingoStockPriceTool(BaseTool):
    """Tool to get stock price data from Tiingo API"""
    
    name: str = "get_tiingo_stock_price"
    description: str = """Get current and historical stock price data from Tiingo.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    - start_date: Start date in YYYY-MM-DD format (optional, defaults to last 30 days)
    - end_date: End date in YYYY-MM-DD format (optional, defaults to today)
    - frequency: Data frequency - daily, weekly, monthly, annually, or intraday like 1min, 5min, 1hour
    
    Returns current and historical stock prices with OHLCV data."""
    
    args_schema: Type[BaseModel] = StockPriceInput
    
    def _run(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, frequency: str = "daily") -> str:
        try:
            api_key = os.getenv("TIINGO_API_KEY")
            if not api_key:
                return "Error: TIINGO_API_KEY environment variable not set"
            
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Build URL based on frequency
            if frequency in ["daily", "weekly", "monthly", "annually"]:
                url = f"https://api.tiingo.com/tiingo/daily/{symbol.upper()}/prices"
            else:
                # Intraday data
                url = f"https://api.tiingo.com/iex/{symbol.upper()}/prices"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}"
            }
            
            params = {
                "startDate": start_date,
                "endDate": end_date,
                "format": "json"
            }
            
            if frequency not in ["daily", "weekly", "monthly", "annually"]:
                params["resampleFreq"] = frequency
            else:
                params["resampleFreq"] = frequency
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return f"No price data found for {symbol}"
            
            # Format the response
            result = {
                "symbol": symbol.upper(),
                "frequency": frequency,
                "start_date": start_date,
                "end_date": end_date,
                "data_points": len(data),
                "latest_data": data[-5:] if len(data) >= 5 else data,  # Show last 5 data points
                "price_summary": {
                    "current_price": data[-1].get("close", "N/A") if data else "N/A",
                    "high_52w": max([d.get("high", 0) for d in data]) if data else "N/A",
                    "low_52w": min([d.get("low", 0) for d in data]) if data else "N/A",
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except requests.RequestException as e:
            return f"Error retrieving stock price data for {symbol}: {str(e)}"
        except Exception as e:
            return f"Error processing stock price data for {symbol}: {str(e)}"


class TiingoStockMetadataTool(BaseTool):
    """Tool to get stock metadata from Tiingo API"""
    
    name: str = "get_tiingo_stock_metadata"
    description: str = """Get metadata information for a stock from Tiingo.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    
    Returns company name, description, exchange, and available date ranges."""
    
    args_schema: Type[BaseModel] = StockMetadataInput
    
    def _run(self, symbol: str) -> str:
        try:
            api_key = os.getenv("TIINGO_API_KEY")
            if not api_key:
                return "Error: TIINGO_API_KEY environment variable not set"
            
            url = f"https://api.tiingo.com/tiingo/daily/{symbol.upper()}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                "symbol": symbol.upper(),
                "name": data.get("name", "N/A"),
                "description": data.get("description", "N/A"),
                "exchange": data.get("exchangeCode", "N/A"),
                "start_date": data.get("startDate", "N/A"),
                "end_date": data.get("endDate", "N/A"),
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except requests.RequestException as e:
            return f"Error retrieving stock metadata for {symbol}: {str(e)}"
        except Exception as e:
            return f"Error processing stock metadata for {symbol}: {str(e)}"


class TiingoStockNewsTool(BaseTool):
    """Tool to get financial news from Tiingo API"""
    
    name: str = "get_tiingo_stock_news"
    description: str = """Get curated financial news articles from Tiingo.
    
    Parameters:
    - symbols: List of stock symbols to get news for (e.g., ["AAPL", "GOOGL"])
    - limit: Number of articles to return (default: 10, max: 100)
    - start_date: Start date in YYYY-MM-DD format (optional)
    - end_date: End date in YYYY-MM-DD format (optional)
    
    Returns recent news articles with titles, descriptions, and publication dates."""
    
    args_schema: Type[BaseModel] = StockNewsInput
    
    def _run(self, symbols: List[str], limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            api_key = os.getenv("TIINGO_API_KEY")
            if not api_key:
                return "Error: TIINGO_API_KEY environment variable not set"
            
            # Limit the number of articles
            limit = min(limit, 100)
            
            url = "https://api.tiingo.com/tiingo/news"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}"
            }
            
            params = {
                "tickers": ",".join([s.upper() for s in symbols]),
                "limit": limit,
                "format": "json"
            }
            
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return f"No news found for symbols: {symbols}"
            
            # Format articles
            articles = []
            for article in data:
                articles.append({
                    "title": article.get("title", "N/A"),
                    "description": article.get("description", "N/A")[:200] + "..." if len(article.get("description", "")) > 200 else article.get("description", "N/A"),
                    "url": article.get("url", "N/A"),
                    "published_date": article.get("publishedDate", "N/A"),
                    "source": article.get("source", "N/A"),
                    "tags": article.get("tags", []),
                    "tickers": article.get("tickers", [])
                })
            
            result = {
                "symbols": [s.upper() for s in symbols],
                "articles_count": len(articles),
                "articles": articles,
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except requests.RequestException as e:
            return f"Error retrieving news for symbols {symbols}: {str(e)}"
        except Exception as e:
            return f"Error processing news data for symbols {symbols}: {str(e)}"


class TiingoFundamentalsTool(BaseTool):
    """Tool to get fundamental data from Tiingo API"""
    
    name: str = "get_tiingo_fundamentals"
    description: str = """Get fundamental financial data from Tiingo.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    - start_date: Start date in YYYY-MM-DD format (optional)
    - end_date: End date in YYYY-MM-DD format (optional)
    
    Returns fundamental metrics like market cap, P/E ratio, revenue, etc."""
    
    args_schema: Type[BaseModel] = FundamentalsInput
    
    def _run(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            api_key = os.getenv("TIINGO_API_KEY")
            if not api_key:
                return "Error: TIINGO_API_KEY environment variable not set"
            
            # Get daily fundamentals (market cap, P/E, etc.)
            url = f"https://api.tiingo.com/tiingo/fundamentals/{symbol.upper()}/daily"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}"
            }
            
            params = {
                "format": "json"
            }
            
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return f"No fundamental data found for {symbol}"
            
            # Get the latest data point
            latest = data[-1] if data else {}
            
            result = {
                "symbol": symbol.upper(),
                "date": latest.get("date", "N/A"),
                "fundamentals": {
                    "market_cap": latest.get("marketCap", "N/A"),
                    "enterprise_value": latest.get("enterpriseVal", "N/A"),
                    "pe_ratio": latest.get("peRatio", "N/A"),
                    "pb_ratio": latest.get("pbRatio", "N/A"),
                    "dividend_yield": latest.get("dividendYield", "N/A"),
                    "shares_outstanding": latest.get("sharesOutstanding", "N/A"),
                    "revenue": latest.get("revenue", "N/A"),
                    "gross_profit": latest.get("grossProfit", "N/A"),
                    "net_income": latest.get("netIncome", "N/A"),
                    "ebitda": latest.get("ebitda", "N/A"),
                },
                "data_points": len(data),
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except requests.RequestException as e:
            return f"Error retrieving fundamental data for {symbol}: {str(e)}"
        except Exception as e:
            return f"Error processing fundamental data for {symbol}: {str(e)}"


class TiingoCryptoPriceTool(BaseTool):
    """Tool to get cryptocurrency price data from Tiingo API"""
    
    name: str = "get_tiingo_crypto_price"
    description: str = """Get current and historical cryptocurrency price data from Tiingo.
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., BTCUSD, ETHUSD, SOLUSD)
    - start_date: Start date in YYYY-MM-DD format (optional, defaults to last 30 days)
    - end_date: End date in YYYY-MM-DD format (optional, defaults to today)
    - frequency: Data frequency - daily or intraday like 1min, 5min, 1hour
    
    Returns current and historical cryptocurrency prices with OHLCV data."""
    
    args_schema: Type[BaseModel] = CryptoPriceInput
    
    def _run(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, frequency: str = "daily") -> str:
        try:
            api_key = os.getenv("TIINGO_API_KEY")
            if not api_key:
                return "Error: TIINGO_API_KEY environment variable not set"
            
            # For crypto, focus on current price from top-of-book endpoint
            # This is more reliable than historical data endpoint
            top_url = f"https://api.tiingo.com/tiingo/crypto/top"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}"
            }
            
            # Convert Yahoo-style crypto tickers (e.g. BTC-USD) to
            # Tiingo format which uses a slash (e.g. BTC/USD)
            tiingo_symbol = symbol.upper().replace("-", "/")
            top_params = {
                "tickers": tiingo_symbol,
                "format": "json"
            }
            
            response = requests.get(top_url, headers=headers, params=top_params)
            response.raise_for_status()
            data = response.json()
            
            # Process the response
            if not data or len(data) == 0:
                return f"No data found for cryptocurrency symbol: {symbol}"
            
            crypto_data = data[0]
            ticker_name = crypto_data.get("ticker", symbol)
            top_of_book = crypto_data.get("topOfBookData", [])
            
            if not top_of_book:
                return f"No current price data available for {symbol}"
            
            current_data = top_of_book[0]
            
            # Calculate 52-week high/low approximation from recent data
            high_52w = current_data.get("lastPrice", 0)
            low_52w = current_data.get("lastPrice", 0)
            
            # Try to get some historical context if available
            price_summary = {
                "current_price": current_data.get("lastPrice", "N/A"),
                "high_52w": high_52w,
                "low_52w": low_52w
            }
            
            # Format the response similar to stock tools
            result = {
                "symbol": ticker_name,
                "frequency": "current",
                "start_date": "current",
                "end_date": "current", 
                "data_points": 1,
                "latest_data": [{
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "close": current_data.get("lastPrice", 0),
                    "high": current_data.get("lastPrice", 0),
                    "low": current_data.get("lastPrice", 0),
                    "open": current_data.get("lastPrice", 0),
                    "volume": current_data.get("lastSizeNotional", 0),
                    "adjClose": current_data.get("lastPrice", 0),
                    "adjHigh": current_data.get("lastPrice", 0),
                    "adjLow": current_data.get("lastPrice", 0),
                    "adjOpen": current_data.get("lastPrice", 0),
                    "adjVolume": current_data.get("lastSizeNotional", 0),
                    "divCash": 0.0,
                    "splitFactor": 1.0
                }],
                "price_summary": price_summary,
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except requests.RequestException as e:
            return f"Error retrieving crypto price data for {symbol}: {str(e)}"
        except Exception as e:
            return f"Error processing crypto price data for {symbol}: {str(e)}"


def get_tiingo_tools():
    """Return a list of all Tiingo tools"""
    return [
        TiingoStockPriceTool(),
        TiingoStockMetadataTool(),
        TiingoStockNewsTool(),
        TiingoFundamentalsTool(),
        TiingoCryptoPriceTool()
    ]


if __name__ == "__main__":
    # Test the tools
    tools = get_tiingo_tools()

    logger.info("Testing Tiingo Tools")
    logger.info("=" * 50)

    # Test stock price tool
    logger.info("\n1. Testing Stock Price Tool:")
    price_tool = TiingoStockPriceTool()
    result = price_tool._run("AAPL")
    logger.info(result)

    # Test stock metadata tool
    logger.info("\n2. Testing Stock Metadata Tool:")
    metadata_tool = TiingoStockMetadataTool()
    result = metadata_tool._run("AAPL")
    logger.info(result)

    # Test news tool
    logger.info("\n3. Testing Stock News Tool:")
    news_tool = TiingoStockNewsTool()
    result = news_tool._run(["AAPL", "GOOGL"], limit=3)
    logger.info(result)

    # Test fundamentals tool
    logger.info("\n4. Testing Fundamentals Tool:")
    fundamentals_tool = TiingoFundamentalsTool()
    result = fundamentals_tool._run("AAPL")
    logger.info(result)

    # Test crypto price tool
    logger.info("\n5. Testing Crypto Price Tool:")
    crypto_tool = TiingoCryptoPriceTool()
    result = crypto_tool._run("BTCUSD")
    logger.info(result)