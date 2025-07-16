# Comprehensive AI Assistant with Financial Data & Web Search

This directory contains a comprehensive AI assistant with access to financial data and web search capabilities through multiple integrated APIs.

## Overview

The assistant now supports **three major data sources** for comprehensive analysis:
- **Yahoo Finance**: Free stock data, news, and market summaries
- **Tiingo**: Professional-grade financial data with fundamentals and cryptocurrency support
- **Brave Search**: Real-time web search, news, images, videos, and AI-powered summaries

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

# Required for Brave Search (get free key at https://api.search.brave.com/)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

## Usage

### Interactive Mode
```bash
python langchain_agent.py
```

### Single Query Mode
```bash
python langchain_agent.py "What is the current price of Apple stock?"
python langchain_agent.py "Latest news about artificial intelligence"
python langchain_agent.py "Summarize renewable energy trends"
```

### Test All Integrations
```bash
# Run comprehensive tests
python test_comprehensive.py

# Test individual components
python test_yahoo_finance.py    # Yahoo Finance tools
python tiingo_tool.py          # Tiingo tools
python brave_search_tool.py    # Brave Search tools
```

## Features

- **🤖 Comprehensive AI Assistant**: Access to financial data, web search, and real-time information
- **📊 Multi-Source Financial Data**: Yahoo Finance, Tiingo for stocks, crypto, and fundamentals
- **🔍 Advanced Web Search**: Brave Search for current events, research, and multimedia content
- **🔄 Intelligent Tool Selection**: Agent automatically chooses the best data source for each query
- **📱 Interactive Mode**: Real-time chat interface with help commands
- **⚡ Real-time Data**: Access to current market data, news, and web information

## Available Tools

### Yahoo Finance Tools (4 tools)

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

### Tiingo Tools (5 tools)

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

### Brave Search Tools (5 tools)

#### 1. Web Search Tool (`brave_web_search`)
- Search the web for current information and real-time data
- Parameters: `query`, `count`, `country`, `search_lang`, `safesearch`
- Returns: web search results with titles, URLs, descriptions, and metadata

#### 2. News Search Tool (`brave_news_search`)
- Search for recent news articles from across the web
- Parameters: `query`, `count`, `country`, `search_lang`, `freshness`
- Returns: recent news articles with titles, URLs, descriptions, and sources

#### 3. Image Search Tool (`brave_image_search`)
- Search for images on any topic
- Parameters: `query`, `count`, `safesearch`
- Returns: image search results with URLs, titles, sources, and metadata

#### 4. Video Search Tool (`brave_video_search`)
- Search for videos including tutorials and explanations
- Parameters: `query`, `count`, `country`, `search_lang`
- Returns: video search results with titles, URLs, descriptions, duration, and creators

#### 5. AI Summarizer Tool (`brave_ai_summarizer`)
- Get AI-powered summaries of complex topics
- Parameters: `query`, `count`, `country`, `search_lang`
- Returns: AI-generated summaries based on multiple search results

## Example Queries

### Financial Analysis
- "What's the current price of Apple stock?"
- "Compare Apple and Google stock prices from both sources"
- "Show me Tesla's stock performance over the last month"
- "What are Netflix's key financial metrics?"

### Current Events & Research
- "What are the latest developments in artificial intelligence?"
- "Recent news about climate change policy"
- "Summarize renewable energy trends in 2024"
- "What happened in the stock market today?"

### Market Data & News
- "Latest news about Tesla and Apple earnings"
- "How are the major market indices performing today?"
- "What's the current Bitcoin and Ethereum prices?"
- "Show me recent developments in electric vehicles"

### Multimedia & Educational
- "Find Python tutorial videos"
- "Show me images of modern sustainable architecture"
- "Explain quantum computing with visual examples"

## Data Sources Comparison

| Feature | Yahoo Finance | Tiingo | Brave Search |
|---------|---------------|--------|--------------|
| Stock Prices | ✅ Free | ✅ Free tier | ❌ N/A |
| Historical Data | ✅ Extensive | ✅ Extensive | ❌ N/A |
| News | ✅ Basic | ✅ Curated & tagged | ✅ Real-time web news |
| Fundamentals | ✅ Basic | ✅ Comprehensive | ❌ N/A |
| Cryptocurrency | ❌ Limited | ✅ Extensive | ❌ N/A |
| Real-time Data | ✅ 15-min delay | ✅ Real-time available | ✅ Real-time |
| Web Search | ❌ N/A | ❌ N/A | ✅ Comprehensive |
| AI Summaries | ❌ N/A | ❌ N/A | ✅ AI-powered |
| Images/Videos | ❌ N/A | ❌ N/A | ✅ Extensive |
| API Reliability | ⚠️ Rate limited | ✅ Stable | ✅ Stable |

## Configuration

The agent is configured with:
- Model: `gpt-4` (configurable)
- Temperature: `0.1` (low for consistent responses)
- Verbose: `True` (shows reasoning steps)
- Tools: All Yahoo Finance, Tiingo, and Brave Search tools
- Intelligent tool selection based on query type

## Testing

Run the comprehensive test suite to verify all integrations:

```bash
# Full system test
python test_comprehensive.py

# Individual component tests
python test_yahoo_finance.py    # Yahoo Finance integration
python tiingo_tool.py          # Tiingo integration
python brave_search_tool.py    # Brave Search integration
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure `.env` file contains all required API keys
   - Get Tiingo key at: https://www.tiingo.com/
   - Get Brave Search key at: https://api.search.brave.com/

2. **Rate Limiting**
   - Yahoo Finance: Agent will automatically use alternatives
   - Tiingo: Free tier has 1,000 requests per day
   - Brave Search: Free tier has 5,000 requests per month

3. **Network Errors**
   - Check internet connection
   - Verify API endpoints are accessible
   - Try again in a few minutes

### API Limits

- **Yahoo Finance**: Rate limited, no official API key required
- **Tiingo Free Tier**: 1,000 requests/day, 5 symbols per request
- **Brave Search Free Tier**: 5,000 requests/month, 1 request/second
- **Tiingo/Brave Paid**: Higher limits and additional features

## Advanced Usage

### Intelligent Tool Selection
The agent automatically selects the best tools based on your query:
- Financial data → Yahoo Finance or Tiingo
- Current events → Brave Search news
- Research → Brave Search web
- Visual content → Brave Search images/videos
- Quick overviews → Brave Search AI summarizer

### Multi-Source Analysis
You can request comparisons and analysis from multiple sources:
- "Compare Apple stock data from Yahoo Finance and Tiingo"
- "Get Tesla news from both financial sources and web search"
- "Show me market analysis with supporting web research"

### Specialized Queries
- **Time-sensitive**: "What happened in the last hour in tech stocks?"
- **Visual research**: "Show me charts and images about renewable energy"
- **Educational**: "Find tutorial videos about Python machine learning"
- **Comprehensive**: "Full analysis of Microsoft including fundamentals and recent news"

## Next Steps

This comprehensive system can be extended with:
- **Additional data sources**: Economic indicators, options data
- **Real-time features**: WebSocket feeds, live market data
- **Advanced analytics**: Technical indicators, portfolio analysis
- **Visualization**: Charts, graphs, and interactive dashboards
- **Custom tools**: Specialized financial calculations and models

For detailed setup instructions:
- Tiingo: See [SETUP_TIINGO.md](SETUP_TIINGO.md)
- Brave Search: Visit [https://api.search.brave.com/](https://api.search.brave.com/)

---

🚀 **Ready to use!** Your comprehensive AI assistant combines the power of financial data with real-time web search capabilities.