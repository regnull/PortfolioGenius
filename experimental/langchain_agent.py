#!/usr/bin/env python3
"""
LangChain Agent with Comprehensive Financial Data and Web Search Tools
Supports Yahoo Finance, Tiingo APIs, and Brave Search for complete information access
"""

import os
import sys
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

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: Please set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    # Initialize the language model
    llm = ChatOpenAI(
        model="gpt-4o",
        # temperature=0.1,
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
        
        For portfolio construction, follow these steps:
        1. Research current market conditions and economic outlook
        2. Analyze suitable asset classes for medium-risk, 10-year investments
        3. Get current prices and fundamental analysis for recommended securities
        4. Construct a diversified portfolio with specific allocations
        5. Provide detailed reasoning for each recommendation
        
        CRITICAL: You must format your final portfolio recommendation as valid JSON with the following structure:
        
        {{
          "portfolio_summary": {{
            "total_investment": "$10,000",
            "risk_level": "Medium",
            "time_horizon": "10 years",
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
        - notes: Additional details including current price, key metrics, and specific considerations
        
        Return ONLY the JSON - do not include any additional text or explanation outside the JSON structure.
        """),
        ("user", "{input}"),
        ("assistant", "I'll research current market conditions and construct a comprehensive portfolio recommendation in JSON format."),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, all_tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)
    
    # Define the specific portfolio construction request
    today_date = datetime.now().strftime("%B %d, %Y")
    portfolio_request = f"""
    Today is {today_date}.
    
    I need you to construct a medium-risk investment portfolio with the following specifications:
    
    PORTFOLIO REQUIREMENTS:
    - Investment Amount: $10,000
    - Risk Level: Medium (balanced growth and stability)
    - Time Horizon: 10 years
    - Investment Type: Mix of individual stocks and ETFs
    - Diversification: Multiple sectors and asset classes
    
    DELIVERABLES NEEDED:
    1. Current market analysis and economic outlook
    2. Asset allocation strategy (stocks vs bonds vs alternatives)
    3. Specific stock recommendations with:
       - Current prices
       - Fundamental analysis
       - Investment thesis
       - Position size in dollars
    4. Specific ETF recommendations with:
       - Current prices
       - Expense ratios
       - Investment thesis
       - Position size in dollars
    5. Total portfolio allocation breakdown
    6. Risk assessment and expected returns
    7. Portfolio rebalancing recommendations
    
    Please provide specific ticker symbols, current prices, and exact dollar allocations for each position.
    Research current market conditions and use fundamental analysis to support your recommendations.
    """
    
    print("🎯 Portfolio Construction Request")
    print("=" * 60)
    print("Investment Amount: $10,000")
    print("Risk Level: Medium")
    print("Time Horizon: 10 years")
    print("Focus: Stocks and ETFs")
    print("=" * 60)
    print()
    
    print("🔍 Starting portfolio analysis and construction...")
    print("-" * 50)
    
    try:
        result = agent_executor.invoke({"input": portfolio_request})
        print("\n📊 PORTFOLIO RECOMMENDATION:")
        print("=" * 60)
        print(result["output"])
        print("\n" + "=" * 60)
        print("✅ Portfolio construction complete!")
    except Exception as e:
        print(f"❌ Error constructing portfolio: {e}")
        print("Please check your API keys and try again.")
    
    return

if __name__ == "__main__":
    main()