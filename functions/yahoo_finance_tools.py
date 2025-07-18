#!/usr/bin/env python3
"""
Yahoo Finance Tool for Langchain Agent
Provides stock price data, company news, and financial information
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Type
from logging_utils import get_logger

logger = get_logger()
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class StockPriceInput(BaseModel):
    """Input schema for stock price tool"""
    symbol: str = Field(description="Stock symbol (e.g., AAPL, GOOGL)")
    period: str = Field(default="1d", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")


class StockNewsInput(BaseModel):
    """Input schema for stock news tool"""
    symbol: str = Field(description="Stock symbol (e.g., AAPL, GOOGL)")
    limit: int = Field(default=5, description="Number of news articles to return (max 10)")


class StockInfoInput(BaseModel):
    """Input schema for stock info tool"""
    symbol: str = Field(description="Stock symbol (e.g., AAPL, GOOGL)")


class MarketSummaryInput(BaseModel):
    """Input schema for market summary tool"""
    indices: List[str] = Field(default=["^GSPC", "^DJI", "^IXIC"], description="Market indices to check (default: S&P 500, Dow Jones, NASDAQ)")


class StockPriceTool(BaseTool):
    """Tool to get stock price data from Yahoo Finance"""
    
    name: str = "get_stock_price"
    description: str = """Get current and historical stock price data for a given symbol.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    - period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns current price, change, percentage change, and recent historical data."""
    
    args_schema: Type[BaseModel] = StockPriceInput
    
    def _run(self, symbol: str, period: str = "1d") -> str:
        try:
            # Get stock data
            stock = yf.Ticker(symbol.upper())
            
            # Get current info
            info = stock.info
            hist = stock.history(period=period)
            
            if hist.empty:
                return f"No data found for symbol: {symbol}"
            
            # Get current price and calculate changes
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            # Format the response
            result = {
                "symbol": symbol.upper(),
                "company_name": info.get('longName', 'N/A'),
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": info.get('volume', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "period": period,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error retrieving stock data for {symbol}: {str(e)}"


class StockNewsTool(BaseTool):
    """Tool to get company news from Yahoo Finance"""
    
    name: str = "get_stock_news"
    description: str = """Get recent news articles for a given stock symbol.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    - limit: Number of news articles to return (default: 5, max: 10)
    
    Returns recent news headlines, summaries, and publication dates."""
    
    args_schema: Type[BaseModel] = StockNewsInput
    
    def _run(self, symbol: str, limit: int = 5) -> str:
        try:
            # Limit the number of articles
            limit = min(limit, 10)
            
            # Get stock data
            stock = yf.Ticker(symbol.upper())
            
            # Get news
            news = stock.news
            
            if not news:
                return f"No news found for symbol: {symbol}"
            
            # Format news articles
            articles = []
            for i, article in enumerate(news[:limit]):
                articles.append({
                    "title": article.get('title', 'N/A'),
                    "publisher": article.get('publisher', 'N/A'),
                    "published_date": datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    "url": article.get('link', 'N/A'),
                    "summary": article.get('summary', 'N/A')[:200] + "..." if len(article.get('summary', '')) > 200 else article.get('summary', 'N/A')
                })
            
            result = {
                "symbol": symbol.upper(),
                "news_count": len(articles),
                "articles": articles,
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error retrieving news for {symbol}: {str(e)}"


class StockInfoTool(BaseTool):
    """Tool to get comprehensive stock information"""
    
    name: str = "get_stock_info"
    description: str = """Get comprehensive information about a stock including company details, 
    financial metrics, and key statistics.
    
    Parameters:
    - symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    
    Returns company info, financial metrics, analyst recommendations, and key statistics."""
    
    args_schema: Type[BaseModel] = StockInfoInput
    
    def _run(self, symbol: str) -> str:
        try:
            # Get stock data
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            
            if not info:
                return f"No information found for symbol: {symbol}"
            
            # Extract key information
            result = {
                "symbol": symbol.upper(),
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "country": info.get('country', 'N/A'),
                "website": info.get('website', 'N/A'),
                "business_summary": info.get('longBusinessSummary', 'N/A')[:300] + "..." if len(info.get('longBusinessSummary', '')) > 300 else info.get('longBusinessSummary', 'N/A'),
                "financial_metrics": {
                    "market_cap": info.get('marketCap', 'N/A'),
                    "enterprise_value": info.get('enterpriseValue', 'N/A'),
                    "trailing_pe": info.get('trailingPE', 'N/A'),
                    "forward_pe": info.get('forwardPE', 'N/A'),
                    "price_to_book": info.get('priceToBook', 'N/A'),
                    "debt_to_equity": info.get('debtToEquity', 'N/A'),
                    "return_on_equity": info.get('returnOnEquity', 'N/A'),
                    "revenue_growth": info.get('revenueGrowth', 'N/A'),
                    "earnings_growth": info.get('earningsGrowth', 'N/A')
                },
                "dividend_info": {
                    "dividend_yield": info.get('dividendYield', 'N/A'),
                    "dividend_rate": info.get('dividendRate', 'N/A'),
                    "payout_ratio": info.get('payoutRatio', 'N/A')
                },
                "analyst_info": {
                    "target_high_price": info.get('targetHighPrice', 'N/A'),
                    "target_low_price": info.get('targetLowPrice', 'N/A'),
                    "target_mean_price": info.get('targetMeanPrice', 'N/A'),
                    "recommendation_key": info.get('recommendationKey', 'N/A')
                },
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error retrieving stock info for {symbol}: {str(e)}"


class MarketSummaryTool(BaseTool):
    """Tool to get market summary and major indices"""
    
    name: str = "get_market_summary"
    description: str = """Get current market summary including major indices performance.
    
    Parameters:
    - indices: List of market indices to check (default: S&P 500, Dow Jones, NASDAQ)
    
    Returns current values, changes, and performance for major market indices."""
    
    args_schema: Type[BaseModel] = MarketSummaryInput
    
    def _run(self, indices: List[str] = None) -> str:
        try:
            if indices is None:
                indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
            
            market_data = {}
            
            # Index names mapping
            index_names = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones Industrial Average",
                "^IXIC": "NASDAQ Composite",
                "^RUT": "Russell 2000",
                "^VIX": "VIX (Volatility Index)"
            }
            
            for index in indices:
                try:
                    stock = yf.Ticker(index)
                    info = stock.info
                    hist = stock.history(period="2d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
                        
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                        
                        market_data[index] = {
                            "name": index_names.get(index, index),
                            "current_value": round(current_price, 2),
                            "previous_close": round(previous_close, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2)
                        }
                except Exception as e:
                    market_data[index] = {"error": str(e)}
            
            result = {
                "market_summary": market_data,
                "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error retrieving market summary: {str(e)}"


def get_yahoo_finance_tools():
    """Return a list of all Yahoo Finance tools"""
    return [
        StockPriceTool(),
        StockNewsTool(),
        StockInfoTool(),
        MarketSummaryTool()
    ]


if __name__ == "__main__":
    # Test the tools
    tools = get_yahoo_finance_tools()

    logger.info("Testing Yahoo Finance Tools")
    logger.info("=" * 50)

    # Test stock price tool
    logger.info("\n1. Testing Stock Price Tool:")
    price_tool = StockPriceTool()
    result = price_tool._run("AAPL", "1d")
    logger.info(result)

    # Test news tool
    logger.info("\n2. Testing Stock News Tool:")
    news_tool = StockNewsTool()
    result = news_tool._run("AAPL", 3)
    logger.info(result)

    # Test info tool
    logger.info("\n3. Testing Stock Info Tool:")
    info_tool = StockInfoTool()
    result = info_tool._run("AAPL")
    logger.info(result)

    # Test market summary tool
    logger.info("\n4. Testing Market Summary Tool:")
    market_tool = MarketSummaryTool()
    result = market_tool._run()
    logger.info(result)