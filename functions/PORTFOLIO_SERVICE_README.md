# Portfolio Construction Cloud Function

AI-powered portfolio construction service with suggested trades management using multiple financial data sources and LangChain agents.

## Overview

This cloud function provides intelligent portfolio recommendations based on natural language investment goals. It uses AI agents with access to multiple financial data sources to create diversified, data-driven portfolio allocations. When connected to a portfolio, it automatically creates suggested trades that users can view, execute, or dismiss.

## Workflow

1. **Portfolio Construction**: AI creates portfolio recommendations
2. **Suggested Trades Creation**: Recommendations are converted to actionable trades
3. **Trade Management**: Users can view, execute, or dismiss suggested trades
4. **Trade Execution**: Suggested trades become actual trades in the portfolio

## Endpoints

### 1. `/construct_portfolio` (POST)

Main portfolio construction endpoint with optional suggested trades creation.

**Request Body:**
```json
{
    "portfolio_goal": "I want to invest $10,000 with high risk tolerance for a 10-year time horizon. Focus on growth stocks, ETFs, and cryptocurrency exposure for maximum capital appreciation.",
    "portfolio_id": "portfolio_123",  // Optional: creates suggested trades if provided
    "user_id": "user_456"             // Required if portfolio_id provided
}
```

**Response (with suggested trades):**
```json
{
    "portfolio_summary": {
        "total_investment": "$10,000",
        "risk_level": "High",
        "time_horizon": "10 years",
        "date_created": "December 15, 2024"
    },
    "recommendations": [
        {
            "ticker_symbol": "AAPL",
            "allocation_percent": 15.0,
            "rationale": "Strong fundamentals and market leadership",
            "notes": "Current price: $195.50, P/E: 32.5"
        }
    ],
    "portfolio_allocation": {
        "stocks": 60.0,
        "etfs": 25.0,
        "bonds": 5.0,
        "alternatives": 10.0
    },
    "risk_assessment": "High growth potential with significant volatility",
    "expected_annual_return": "8-12%",
    "rebalancing_schedule": "Semi-annual",
    "suggested_trades_created": {
        "count": 8,
        "trade_ids": ["trade_1", "trade_2", "..."],
        "portfolio_id": "portfolio_123"
    },
    "service_info": {
        "tools_used": 14,
        "api_keys_available": {
            "openai": true,
            "tiingo": true,
            "brave_search": false
        },
        "processing_timestamp": "2024-12-15T20:00:00"
    }
}
```

### 2. `/get_suggested_trades` (GET)

Get all suggested trades for a portfolio.

**Query Parameters:**
- `portfolio_id`: Portfolio ID
- `user_id`: User ID for authorization

**Response:**
```json
{
    "suggested_trades": [
        {
            "id": "trade_123",
            "portfolioId": "portfolio_123",
            "userId": "user_456",
            "symbol": "AAPL",
            "action": "buy",
            "quantity": 51.28,
            "target_price": 195.50,
            "dollar_amount": 1500.0,
            "allocation_percent": 15.0,
            "reasoning": "Strong fundamentals and market leadership. Current price: $195.50, P/E: 32.5",
            "priority": "high",
            "risk_level": "medium",
            "status": "pending",
            "created_at": "2024-12-15T20:00:00",
            "source": "ai_portfolio_construction"
        }
    ],
    "count": 8,
    "portfolio_id": "portfolio_123",
    "timestamp": "2024-12-15T20:00:00"
}
```

### 3. `/convert_suggested_trade` (POST)

Convert a suggested trade to an actual trade.

**Request Body:**
```json
{
    "suggested_trade_id": "trade_123",
    "user_id": "user_456",
    "trade_data": {           // Optional: override trade details
        "quantity": 50,
        "price": 195.50,
        "fees": 9.99,
        "notes": "Executed with custom parameters"
    }
}
```

**Response:**
```json
{
    "message": "Suggested trade successfully converted to actual trade",
    "actual_trade_id": "actual_trade_456",
    "suggested_trade_id": "trade_123",
    "timestamp": "2024-12-15T20:00:00"
}
```

### 4. `/dismiss_suggested_trade` (POST)

Dismiss a suggested trade.

**Request Body:**
```json
{
    "suggested_trade_id": "trade_123",
    "user_id": "user_456",
    "reason": "Don't want to invest in this stock right now"
}
```

**Response:**
```json
{
    "message": "Suggested trade successfully dismissed",
    "suggested_trade_id": "trade_123",
    "success": true,
    "timestamp": "2024-12-15T20:00:00"
}
```


## Firestore Collections

### `suggestedTrades`

Documents contain:
```json
{
    "portfolioId": "portfolio_123",
    "userId": "user_456",
    "symbol": "AAPL",
    "action": "buy",
    "quantity": 51.28,
    "target_price": 195.50,
    "dollar_amount": 1500.0,
    "allocation_percent": 15.0,
    "reasoning": "Investment rationale",
    "priority": "high|medium|low",
    "risk_level": "high|medium|low",
    "status": "pending|executed|dismissed",
    "created_at": "2024-12-15T20:00:00",
    "source": "ai_portfolio_construction",
    "executed_at": "2024-12-15T21:00:00",      // if status = executed
    "actual_trade_id": "actual_trade_456",     // if status = executed
    "dismissed_at": "2024-12-15T21:00:00",     // if status = dismissed
    "dismissal_reason": "User reason"          // if status = dismissed
}
```

### `trades` (Enhanced)

Actual trades now include suggested trade references:
```json
{
    "portfolioId": "portfolio_123",
    "userId": "user_456",
    "symbol": "AAPL",
    "type": "buy",
    "quantity": 50,
    "price": 195.50,
    "date": "2024-12-15T21:00:00",
    "fees": 9.99,
    "notes": "Executed from suggested trade",
    "suggested_trade_id": "trade_123",         // if from suggested trade
    "source": "suggested_trade_conversion"     // or "manual_entry"
}
```

## Environment Variables

The service requires the following environment variables:

### Required
- `OPENAI_API_KEY`: OpenAI API key for AI portfolio construction

### Optional
- `TIINGO_API_KEY`: Tiingo API key for enhanced financial data ([Get free key](https://api.tiingo.com/))
- `BRAVE_API_KEY`: Brave Search API key for web search capabilities ([Get key](https://brave.com/search/api/))

### Setting Environment Variables

For Firebase Cloud Functions, set environment variables using:

```bash
# Set required OpenAI API key
firebase functions:config:set portfolio.openai_api_key="your_openai_key"

# Set optional Tiingo API key
firebase functions:config:set portfolio.tiingo_api_key="your_tiingo_key"

# Set optional Brave Search API key
firebase functions:config:set portfolio.brave_api_key="your_brave_key"

# Deploy with updated config
firebase deploy --only functions
```

## Available Data Sources

### Yahoo Finance (Always Available)
- Stock prices and historical data
- Company information and financial metrics
- Market indices and summaries
- Financial news

### Tiingo (Optional - Requires API Key)
- Professional-grade financial data
- Fundamental financial metrics
- Curated financial news
- Cryptocurrency prices

### Brave Search (Optional - Requires API Key)
- Real-time web search
- Current financial news
- Market sentiment analysis
- Educational content search

## Example Portfolio Goals

### Conservative
```json
{
    "portfolio_goal": "I want to invest $25,000 conservatively for retirement in 5 years. Focus on bonds, dividend ETFs, and stable large-cap stocks for steady income and capital preservation."
}
```

### Aggressive Growth
```json
{
    "portfolio_goal": "I'm 25 years old with $15,000 to invest aggressively for 20 years. I want maximum growth potential with tech stocks, small-cap growth, emerging markets, and cryptocurrency exposure."
}
```

### Balanced
```json
{
    "portfolio_goal": "I need a balanced portfolio for $50,000 with medium risk tolerance over 10 years. Mix of growth and value stocks, domestic and international ETFs, with some alternative investments."
}
```

## Error Handling

The service provides detailed error responses:

- `400 Bad Request`: Invalid input or missing required fields
- `401 Unauthorized`: Authentication issues
- `500 Internal Server Error`: Service configuration problems
- `502 Bad Gateway`: AI processing or external API errors

## Deployment

1. Ensure all required dependencies are in `requirements.txt`
2. Set environment variables using Firebase CLI
3. Deploy functions:

```bash
firebase deploy --only functions:construct_portfolio,functions:get_suggested_trades,functions:convert_suggested_trade,functions:dismiss_suggested_trade
```

## Testing

Test the endpoints locally or in production:

```bash
# Test portfolio construction
curl -X POST \
  https://your-project.cloudfunctions.net/construct_portfolio \
  -H "Content-Type: application/json" \
  -d '{"portfolio_goal": "I want to invest $10,000 with medium risk for 10 years"}'

```

## Features

- **AI-Powered Analysis**: Uses GPT-4 for intelligent portfolio construction
- **Multi-Source Data**: Combines Yahoo Finance, Tiingo, and web search data
- **Real-Time Prices**: Gets current market data for accurate recommendations
- **Flexible Input**: Accepts natural language investment goals
- **Detailed Rationale**: Provides investment thesis for each recommendation
- **Risk Assessment**: Analyzes portfolio risk and expected returns
- **Tool Status**: Reports available data sources and API key status
- **Suggested Trades Management**: Converts recommendations to actionable trades
- **Firestore Safety**: Automatic data sanitization prevents undefined value errors
- **User Authorization**: Ensures users only access their own data
- **Audit Trail**: Tracks conversion from suggested to actual trades 