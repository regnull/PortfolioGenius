#!/usr/bin/env python3
"""
LangChain Agent with Comprehensive Financial Data and Web Search Tools
Supports Yahoo Finance, Tiingo APIs, and Brave Search for complete information access
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

# Import Yahoo Finance tools
from yahoo_finance_tool import get_yahoo_finance_tools

# Import Tiingo tools
from tiingo_tool import get_tiingo_tools

# Import Brave Search tools
from brave_search_tool import get_brave_search_tools


def construct_portfolio(portfolio_goal):
    """
    Construct an investment portfolio based on a natural language description of goals.
    
    Args:
        portfolio_goal (str): Natural language description of portfolio requirements.
                             Example: "I want to invest $10,000 with medium risk for 10 years, 
                             focusing on stocks and ETFs with some crypto exposure"
    
    Returns:
        dict: JSON portfolio recommendation with allocations and rationale
    """
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Initialize the language model
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        api_key=openai_api_key
    )
    
    # Get all available tools
    yahoo_tools = get_yahoo_finance_tools()
    tiingo_tools = get_tiingo_tools()
    brave_search_tools = get_brave_search_tools()
    
    # Combine all tools
    all_tools = yahoo_tools + tiingo_tools + brave_search_tools
    
    # Define the prompt template for portfolio construction
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert financial advisor and portfolio manager with access to comprehensive financial data and research tools.
        
        Your task is to construct a specific investment portfolio based on the user's requirements.
        
        IMPORTANT: You MUST use the available tools to gather current market data and financial information. Do NOT rely on your training data for current prices, market conditions, or financial metrics.
        
        You have access to the following tools:
        
        YAHOO FINANCE TOOLS:
        - get_stock_price: Get current and historical stock prices from Yahoo Finance
        - get_stock_news: Get recent news articles for companies from Yahoo Finance
        - get_stock_info: Get comprehensive company information and financial metrics
        - get_market_summary: Get market indices and overall market performance
        
        TIINGO TOOLS:
        - get_tiingo_stock_price: Get current and historical stock prices from Tiingo
        - get_tiingo_stock_metadata: Get detailed stock metadata and company information
        - get_tiingo_stock_news: Get curated financial news from Tiingo
        - get_tiingo_fundamentals: Get fundamental financial metrics and ratios
        - get_tiingo_crypto_price: Get cryptocurrency prices and historical data
        
        BRAVE SEARCH TOOLS:
        - brave_web_search: Search the web for current information and real-time data
        - brave_news_search: Search for recent news articles from across the web
        - brave_image_search: Search for images on any topic
        - brave_video_search: Search for videos including tutorials and explanations
        - brave_ai_summarizer: Get AI-powered summaries of complex topics
        
        For portfolio construction, you MUST follow these steps:
        1. FIRST: Use get_market_summary to understand current market conditions
        2. THEN: Use get_stock_info or get_tiingo_stock_metadata for each recommended stock/ETF to get current prices and fundamentals
        3. Use get_tiingo_crypto_price for any cryptocurrency recommendations
        4. Use brave_news_search or financial news tools to understand current market sentiment
        5. ONLY AFTER gathering current data, construct your portfolio recommendations
        
        CRITICAL: You must format your final portfolio recommendation as valid JSON with the following structure:
        
        {{
          "portfolio_summary": {{
            "total_investment": "investment_amount",
            "risk_level": "risk_level",
            "time_horizon": "time_horizon",
            "date_created": "current_date"
          }},
          "recommendations": [
            {{
              "ticker_symbol": "AAPL",
              "allocation_percent": 15.0,
              "rationale": "Strong fundamentals, market leader in technology sector with consistent revenue growth",
              "notes": "Current price: $XXX.XX, P/E ratio: XX.X, recommended for long-term growth"
            }}
          ],
          "portfolio_allocation": {{
            "stocks": XX.X,
            "etfs": XX.X,
            "bonds": XX.X,
            "alternatives": XX.X
          }},
          "risk_assessment": "Brief risk analysis",
          "expected_annual_return": "X-X%",
          "rebalancing_schedule": "Quarterly/Semi-annual/Annual"
        }}
        
        Each recommendation must include:
        - ticker_symbol: The stock/ETF ticker symbol
        - allocation_percent: Percentage of total portfolio (must sum to 100%)
        - rationale: Investment thesis and reasoning for inclusion
        - notes: Additional details including ACTUAL CURRENT PRICES from tools, key metrics, and specific considerations
        
        You MUST use tools to get current prices and market data. Return ONLY the JSON - do not include any additional text or explanation outside the JSON structure.
        """),
        ("user", "{input}"),
        ("assistant", "I'll start by gathering current market data and financial information using the available tools to construct your portfolio recommendation."),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, all_tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)
    
    # Format the portfolio request with today's date
    today_date = datetime.now().strftime("%B %d, %Y")
    
    portfolio_request = f"""
    Today is {today_date}.
    
    {portfolio_goal}
    
    Please research current market conditions, analyze suitable investments, and provide a comprehensive portfolio recommendation in the specified JSON format.
    Include current prices, fundamental analysis, and detailed rationale for each recommendation.
    """
    
    # Execute the agent
    try:
        result = agent_executor.invoke({"input": portfolio_request})
        
        # Parse the JSON response
        response_text = result["output"].strip()
        
        # Clean up the response to extract just the JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            response_text = response_text[3:-3].strip()
        
        # Parse and return the JSON
        portfolio_recommendation = json.loads(response_text)
        return portfolio_recommendation
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse portfolio recommendation as JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Error constructing portfolio: {e}")


def main():
    """
    Main function for standalone execution with default portfolio parameters.
    """
    # Default portfolio goal as a simple string
    default_portfolio_goal = """
    I want to invest $10,000 with high risk tolerance for a 10-year time horizon.
    I'm looking for aggressive growth and am comfortable with volatility.
    Focus on high-growth stocks, growth ETFs, emerging markets, and cryptocurrency exposure.
    I want maximum growth potential and am willing to accept significant short-term fluctuations.
    Include tech stocks, small-cap growth companies, and alternative investments like crypto.
    Prioritize capital appreciation over income generation.
    """
    
    print("🎯 Portfolio Construction Request")
    print("=" * 60)
    print("Goal: High-risk aggressive growth portfolio")
    print("Amount: $10,000")
    print("Assets: Growth stocks, ETFs, Crypto, Emerging markets")
    print("=" * 60)
    print()
    
    print("🔍 Starting portfolio analysis and construction...")
    print("-" * 50)
    
    try:
        portfolio_recommendation = construct_portfolio(default_portfolio_goal)
        
        print("\n📊 PORTFOLIO RECOMMENDATION:")
        print("=" * 60)
        print(json.dumps(portfolio_recommendation, indent=2))
        print("\n" + "=" * 60)
        print("✅ Portfolio construction complete!")
        
        return portfolio_recommendation
        
    except Exception as e:
        print(f"❌ Error constructing portfolio: {e}")
        print("Please check your API keys and try again.")
        return None

if __name__ == "__main__":
    main()