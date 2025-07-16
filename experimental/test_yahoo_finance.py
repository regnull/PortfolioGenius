#!/usr/bin/env python3
"""
Test script for Yahoo Finance tools
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_yahoo_finance_tools():
    """Test the Yahoo Finance tools independently"""
    
    print("🧪 Testing Yahoo Finance Tools")
    print("=" * 50)
    
    try:
        from yahoo_finance_tool import get_yahoo_finance_tools
        
        tools = get_yahoo_finance_tools()
        print(f"✅ Loaded {len(tools)} Yahoo Finance tools")
        
        # Test each tool
        for tool in tools:
            print(f"\n📊 Testing {tool.name}:")
            print(f"Description: {tool.description}")
            
        # Test stock price tool
        print("\n" + "="*50)
        print("🔍 Testing Stock Price Tool with AAPL")
        price_tool = tools[0]  # StockPriceTool
        result = price_tool._run("AAPL", "1d")
        print(result)
        
        # Test news tool
        print("\n" + "="*50)
        print("📰 Testing Stock News Tool with AAPL")
        news_tool = tools[1]  # StockNewsTool
        result = news_tool._run("AAPL", 3)
        print(result)
        
        # Test market summary
        print("\n" + "="*50)
        print("📈 Testing Market Summary Tool")
        market_tool = tools[3]  # MarketSummaryTool
        result = market_tool._run()
        print(result)
        
    except Exception as e:
        print(f"❌ Error testing Yahoo Finance tools: {e}")
        return False
    
    return True

def test_agent_integration():
    """Test the agent with Yahoo Finance tools"""
    
    print("\n🤖 Testing Agent Integration")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping agent test - OPENAI_API_KEY not set")
        return False
    
    try:
        from langchain_agent import run_agent_single_query
        
        # Test queries
        test_queries = [
            "What is the current price of Apple stock?",
            "Get me the latest news about Tesla",
            "Show me the market summary for today",
            "What are the financial metrics for Microsoft?"
        ]
        
        for query in test_queries:
            print(f"\n🗣️  Query: {query}")
            result = run_agent_single_query(query)
            if result:
                print(f"🤖 Response: {result}")
            else:
                print("❌ No response received")
                
    except Exception as e:
        print(f"❌ Error testing agent integration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = True
    
    # Test Yahoo Finance tools
    if not test_yahoo_finance_tools():
        success = False
    
    # Test agent integration if OpenAI key is available
    if os.getenv("OPENAI_API_KEY"):
        if not test_agent_integration():
            success = False
    else:
        print("\n⚠️  OpenAI API key not found. Set OPENAI_API_KEY to test agent integration.")
    
    print("\n" + "="*50)
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)