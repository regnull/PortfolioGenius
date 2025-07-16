# Experimental Langchain Agent with Multi-Source Financial Data

This directory contains experimental code for testing Langchain agents with OpenAI integration and comprehensive financial data access from multiple sources.

## Overview

The agent now supports **dual data sources** for comprehensive financial analysis:
- **Yahoo Finance**: Free stock data, news, and market summaries
- **Tiingo**: Professional-grade financial data with fundamentals and cryptocurrency support

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the experimental directory:
```bash
# Required for the agent
OPENAI_API_KEY=your_openai_api_key_here

# Required for Tiingo data (get free key at https://www.tiingo.com/)
TIINGO_API_KEY=your_tiingo_api_key_here
```

## Usage

### Interactive Mode
```bash
python langchain_agent.py
```

### Single Query Mode
```bash
python langchain_agent.py "What is the current price of Apple stock?"
```

### Test Individual Tools
```bash
# Test Yahoo Finance tools
python test_yahoo_finance.py

# Test Tiingo tools
python tiingo_tool.py
```

## Features

- **Dual-Source Financial AI Assistant**: Specialized agent with access to multiple financial data sources
- **Yahoo Finance Integration**: Real-time stock data, news, and market information
- **Tiingo Integration**: Professional-grade financial data, fundamentals, and cryptocurrency support
- **Interactive Mode**: Chat with the agent in real-time
- **Single Query Mode**: Run one-off queries from command line
- **Automatic Source Selection**: Agent chooses the best data source for each query
- **Comprehensive Testing**: Test suite for all tools and agent integration

## Available Tools

### Yahoo Finance Tools

#### 1. Stock Price Tool (`get_stock_price`)
- Get current and historical stock prices
- Parameters: `symbol` (e.g., AAPL), `period` (1d, 1mo, 1y, etc.)
- Returns: current price, change, percentage change, volume, market cap

#### 2. Stock News Tool (`get_stock_news`)
- Get recent news articles for companies
- Parameters: `symbol` (e.g., AAPL), `limit` (number of articles)
- Returns: headlines, summaries, publication dates, URLs

#### 3. Stock Info Tool (`get_stock_info`)
- Get comprehensive company information
- Parameters: `symbol` (e.g., AAPL)
- Returns: company details, financial metrics, analyst recommendations

#### 4. Market Summary Tool (`get_market_summary`)
- Get market indices and overall performance
- Parameters: `indices` (list of market indices)
- Returns: current values, changes for major indices (S&P 500, Dow, NASDAQ)

### Tiingo Tools

#### 1. Stock Price Tool (`get_tiingo_stock_price`)
- Get current and historical stock prices with professional-grade data
- Parameters: `symbol`, `start_date`, `end_date`, `frequency` (daily, weekly, monthly, or intraday)
- Returns: OHLCV data with 52-week highs/lows

#### 2. Stock Metadata Tool (`get_tiingo_stock_metadata`)
- Get detailed company information and metadata
- Parameters: `symbol` (e.g., AAPL)
- Returns: company name, description, exchange, available date ranges

#### 3. Stock News Tool (`get_tiingo_stock_news`)
- Get curated financial news articles with tags
- Parameters: `symbols` (list), `limit`, `start_date`, `end_date`
- Returns: tagged news articles from premium sources

#### 4. Fundamentals Tool (`get_tiingo_fundamentals`)
- Get comprehensive fundamental financial metrics
- Parameters: `symbol`, `start_date`, `end_date`
- Returns: market cap, P/E ratio, revenue, profit margins, EBITDA, etc.

#### 5. Crypto Price Tool (`get_tiingo_crypto_price`)
- Get cryptocurrency prices and historical data
- Parameters: `symbol` (e.g., BTCUSD), `start_date`, `end_date`, `frequency`
- Returns: current and historical crypto prices

## Example Queries

### Stock Analysis
- "What's the current price of Apple stock?"
- "Compare Apple and Google stock prices from Tiingo"
- "Show me Tesla's stock performance over the last month"

### Company Information
- "Get detailed information about Microsoft from Tiingo"
- "Tell me about Netflix's financial metrics"
- "What's Amazon's market cap and P/E ratio?"

### News & Market Data
- "What's the latest news about Tesla and Apple?"
- "How are the major market indices performing today?"
- "Show me recent news about tech stocks"

### Fundamentals & Analysis
- "What are the key financial metrics for Netflix?"
- "Compare the fundamentals of Apple and Microsoft"
- "Analyze the performance of tech stocks this month"

### Cryptocurrency
- "What's the current Bitcoin price?"
- "Show me Ethereum and Bitcoin price comparison"
- "What's the trend for major cryptocurrencies?"

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

## Configuration

The agent is configured with:
- Model: `gpt-4` (configurable)
- Temperature: `0.1` (low for consistent responses)
- Verbose: `True` (shows reasoning steps)
- Tools: Combined Yahoo Finance and Tiingo tools
- Automatic fallback between data sources

## Testing

Run the test suites to verify all tools are working:

```bash
# Test Yahoo Finance tools
python test_yahoo_finance.py

# Test Tiingo tools
python tiingo_tool.py

# Test the full agent
python langchain_agent.py "Test query"
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure `.env` file contains both `OPENAI_API_KEY` and `TIINGO_API_KEY`
   - Get Tiingo key at: https://www.tiingo.com/

2. **Rate Limiting**
   - Yahoo Finance: Try using Tiingo as alternative
   - Tiingo: Free tier has 1,000 requests per day
   - Agent will automatically try alternative sources

3. **Network Errors**
   - Check internet connection
   - Verify API endpoints are accessible
   - Try again in a few minutes

## Advanced Usage

### Specifying Data Sources
You can specify which data source to use in your queries:
- "Get Apple stock price from Yahoo Finance"
- "Show me Tesla fundamentals from Tiingo"
- "Compare prices using both Yahoo Finance and Tiingo"

### API Limits
- **Yahoo Finance**: Rate limited, no official API key required
- **Tiingo Free Tier**: 1,000 requests/day, 5 symbols per request
- **Tiingo Paid**: Higher limits and real-time data

## Next Steps

This foundation can be extended with:
- Portfolio analysis tools
- Technical analysis indicators
- Options data integration
- Economic indicators
- Custom financial calculations
- Real-time websocket feeds
- Advanced charting and visualization

For detailed Tiingo setup instructions, see: [SETUP_TIINGO.md](SETUP_TIINGO.md)