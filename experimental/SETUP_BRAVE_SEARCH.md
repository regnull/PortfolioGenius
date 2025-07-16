# Brave Search API Setup Guide

## Overview
This guide helps you set up the Brave Search API integration for your comprehensive AI assistant. Brave Search provides real-time web search, news, images, videos, and AI-powered summaries.

## Getting Your API Key

### 1. Sign Up for Brave Search API
1. Visit [https://api.search.brave.com/](https://api.search.brave.com/)
2. Click "Get started" or "Sign up"
3. Create an account or sign in with existing credentials
4. Complete the registration process

### 2. Get Your API Key
1. Once logged in, go to your dashboard
2. Navigate to the API keys section
3. Generate a new API key
4. Copy your API key (it will look like a long string)

### 3. Add to Environment Variables
Add your API key to your `.env` file:

```bash
# Add this line to your .env file
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

## Available Brave Search Tools

### 1. Web Search (`brave_web_search`)
- **Purpose**: Search the web for current information and real-time data
- **Best for**: Current events, research, real-time information
- **Example**: "What are the latest developments in AI?"

### 2. News Search (`brave_news_search`)
- **Purpose**: Search for recent news articles from across the web
- **Best for**: Breaking news, current events, recent developments
- **Example**: "Recent news about climate change"

### 3. Image Search (`brave_image_search`)
- **Purpose**: Search for images on any topic
- **Best for**: Visual content, illustrations, examples
- **Example**: "Show me modern architecture images"

### 4. Video Search (`brave_video_search`)
- **Purpose**: Search for videos including tutorials and explanations
- **Best for**: Educational content, tutorials, demonstrations
- **Example**: "Find Python programming tutorials"

### 5. AI Summarizer (`brave_ai_summarizer`)
- **Purpose**: Get AI-powered summaries of complex topics
- **Best for**: Quick overviews, research summaries, topic explanations
- **Example**: "Summarize renewable energy trends"

## Usage Examples

### Financial Research Enhanced with Web Search
```bash
# Traditional financial query
python langchain_agent.py "What is Tesla's current stock price?"

# Enhanced with web search
python langchain_agent.py "What is Tesla's current stock price and latest news?"

# Comprehensive analysis
python langchain_agent.py "Full analysis of Tesla including stock price, fundamentals, and recent developments"
```

### Current Events and Research
```bash
# Web search for current events
python langchain_agent.py "What happened in the stock market today?"

# News search for specific topics
python langchain_agent.py "Recent news about artificial intelligence"

# AI-powered summaries
python langchain_agent.py "Summarize the latest developments in renewable energy"
```

### Educational and Visual Content
```bash
# Find tutorial videos
python langchain_agent.py "Find Python machine learning tutorial videos"

# Search for images
python langchain_agent.py "Show me images of sustainable architecture"

# Research with visual examples
python langchain_agent.py "Explain quantum computing with visual examples"
```

## API Limits and Pricing

### Free Tier
- **5,000 requests per month**
- **1 request per second**
- **Web, news, image, video, and AI summarizer access**
- **No credit card required for basic usage**

### Paid Plans
- **Base**: $3 per 1,000 requests (up to 20M/month)
- **Pro**: $5 per 1,000 requests (unlimited)
- **Enterprise**: Custom pricing

## Testing Your Setup

### 1. Test Individual Tools
```bash
# Test Brave Search tools
python brave_search_tool.py
```

### 2. Test Full Integration
```bash
# Run comprehensive test
python test_comprehensive.py
```

### 3. Test Agent Integration
```bash
# Test web search capability
python langchain_agent.py "What are the latest developments in electric vehicles?"

# Test news search
python langchain_agent.py "Recent news about space exploration"

# Test AI summarizer
python langchain_agent.py "Summarize current trends in artificial intelligence"
```

## Troubleshooting

### Common Issues

1. **"BRAVE_SEARCH_API_KEY not set"**
   - Make sure your `.env` file contains the API key
   - Verify the key is spelled correctly
   - Restart your terminal/application after adding the key

2. **Rate Limiting**
   - Free tier: 5,000 requests/month, 1 request/second
   - Monitor your usage in the Brave Search dashboard
   - Consider upgrading if you need higher limits

3. **API Errors**
   - Check that your API key is valid and active
   - Verify internet connectivity
   - Try simpler queries first

4. **No Search Results**
   - Try different search terms
   - Check if the query is too specific or too broad
   - Verify the API endpoint is accessible

### Performance Tips

1. **Use specific search terms** for better results
2. **Limit result count** for faster responses
3. **Use appropriate tools** for different content types
4. **Combine with financial tools** for comprehensive analysis

## Integration Benefits

### Enhanced Financial Analysis
- Real-time market news and developments
- Current events affecting stock prices
- Research on companies and industries
- Visual content for presentations

### Comprehensive Research
- Web search for any topic
- AI-powered summaries for quick insights
- Educational videos and tutorials
- Image search for visual content

### Real-time Information
- Breaking news and current events
- Market developments and trends
- Research papers and articles
- Social media trends and discussions

## Best Practices

1. **Combine data sources** for comprehensive analysis
2. **Use specific queries** for better results
3. **Monitor API usage** to stay within limits
4. **Cache results** when possible to save API calls
5. **Use appropriate tools** for different content types

## Support and Documentation

- **Official Documentation**: [https://api.search.brave.com/docs](https://api.search.brave.com/docs)
- **Community Support**: [https://community.brave.com/](https://community.brave.com/)
- **API Status**: [https://status.brave.com/](https://status.brave.com/)

## Privacy and Security

Brave Search API offers:
- **Privacy-focused**: No user profiling or tracking
- **Independent index**: Not relying on other search engines
- **Secure**: HTTPS encryption for all requests
- **Open source**: Transparent algorithms and processes

---

🚀 **Ready to enhance your AI assistant with real-time web search capabilities!**

Your comprehensive AI assistant now combines:
- **Financial data** from Yahoo Finance and Tiingo
- **Real-time web search** from Brave Search
- **AI-powered analysis** for complete insights 