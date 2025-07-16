# Tiingo Integration Setup Guide

## Overview
This guide helps you set up the Tiingo tools for your LangChain financial agent. Tiingo provides comprehensive financial data including stock prices, news, fundamentals, and cryptocurrency data.

## API Key Setup

### 1. Get Your Tiingo API Key
1. Visit [https://www.tiingo.com/](https://www.tiingo.com/)
2. Sign up for a free account
3. Go to your account settings/API section
4. Copy your API key

### 2. Environment Variables
Create a `.env` file in the experimental directory with:

```bash
# Required for the agent
OPENAI_API_KEY=your_openai_api_key_here

# Required for Tiingo data
TIINGO_API_KEY=your_tiingo_api_key_here
```

## Available Tiingo Tools

### 1. Stock Price Tool (`get_tiingo_stock_price`)
- **Purpose**: Get current and historical stock prices
- **Parameters**: 
  - `symbol`: Stock ticker (e.g., "AAPL", "GOOGL")
  - `start_date`: Start date (YYYY-MM-DD, optional)
  - `end_date`: End date (YYYY-MM-DD, optional)
  - `frequency`: Data frequency (daily, weekly, monthly, annually, or intraday like 1min, 5min, 1hour)
- **Example**: "What is the current price of Apple stock?"

### 2. Stock Metadata Tool (`get_tiingo_stock_metadata`)
- **Purpose**: Get detailed company information and metadata
- **Parameters**: 
  - `symbol`: Stock ticker (e.g., "AAPL")
- **Example**: "Tell me about Apple Inc company information"

### 3. Stock News Tool (`get_tiingo_stock_news`)
- **Purpose**: Get curated financial news articles
- **Parameters**: 
  - `symbols`: List of stock symbols (e.g., ["AAPL", "GOOGL"])
  - `limit`: Number of articles (default: 10, max: 100)
  - `start_date`: Start date (optional)
  - `end_date`: End date (optional)
- **Example**: "What's the latest news about Tesla and Apple?"

### 4. Fundamentals Tool (`get_tiingo_fundamentals`)
- **Purpose**: Get fundamental financial metrics
- **Parameters**: 
  - `symbol`: Stock ticker (e.g., "AAPL")
  - `start_date`: Start date (optional)
  - `end_date`: End date (optional)
- **Returns**: Market cap, P/E ratio, revenue, profit margins, etc.
- **Example**: "What are Microsoft's key financial metrics?"

### 5. Crypto Price Tool (`get_tiingo_crypto_price`)
- **Purpose**: Get cryptocurrency prices and historical data
- **Parameters**: 
  - `symbol`: Crypto symbol (e.g., "BTCUSD", "ETHUSD")
  - `start_date`: Start date (optional)
  - `end_date`: End date (optional)
  - `frequency`: Data frequency (daily or intraday)
- **Example**: "What's the current Bitcoin price?"

## Usage Examples

### Command Line
```bash
# Single query
python langchain_agent.py "What is the current price of AAPL using Tiingo?"

# Interactive mode
python langchain_agent.py
```

### Example Queries
- **Stock Prices**: "Compare Apple and Google stock prices from Tiingo"
- **Company Info**: "Get detailed information about Tesla from Tiingo"
- **Financial News**: "Show me recent news about Microsoft and Amazon"
- **Fundamentals**: "What are the key financial metrics for Netflix?"
- **Cryptocurrency**: "What's the current Bitcoin and Ethereum prices?"
- **Market Analysis**: "Analyze the performance of tech stocks this month"

## Data Sources Comparison

| Feature | Yahoo Finance | Tiingo |
|---------|---------------|--------|
| Stock Prices | ✅ Free | ✅ Free tier available |
| Historical Data | ✅ Extensive | ✅ Extensive |
| News | ✅ Basic | ✅ Curated & tagged |
| Fundamentals | ✅ Basic | ✅ Comprehensive |
| Cryptocurrency | ❌ Limited | ✅ Extensive |
| Real-time Data | ✅ 15-min delay | ✅ Real-time available |
| API Reliability | ⚠️ Rate limited | ✅ Stable |

## Testing the Integration

Run the test script to verify everything works:

```bash
python tiingo_tool.py
```

This will test all five Tiingo tools and display sample data.

## Troubleshooting

### Common Issues

1. **"TIINGO_API_KEY not set"**
   - Make sure you have a `.env` file with your API key
   - Verify the key is correct and active

2. **Rate Limiting**
   - Tiingo free tier has rate limits
   - Consider upgrading for higher limits
   - Agent will automatically try alternative sources

3. **Network Errors**
   - Check internet connection
   - Verify Tiingo API is accessible
   - Try again in a few minutes

### API Limits (Free Tier)
- **Requests**: 1,000 per day
- **Symbols**: 5 unique symbols per request
- **Historical Data**: Up to 1 year
- **Real-time**: 15-minute delay

## Benefits of Using Tiingo

1. **Higher Quality Data**: Professional-grade financial data
2. **Better Fundamentals**: Comprehensive financial metrics
3. **Curated News**: Tagged and categorized news articles
4. **Cryptocurrency Support**: Extensive crypto data
5. **Reliability**: More stable than free alternatives
6. **Real-time Options**: Upgrade paths for real-time data

## Next Steps

1. Set up your API key
2. Test the individual tools
3. Run the agent with sample queries
4. Explore combining Yahoo Finance and Tiingo data for comprehensive analysis

The agent will automatically choose the best data source for each query, and you can specify which source to use in your questions. 