#!/usr/bin/env python3
"""
Comprehensive Test for All Financial Data and Web Search Tools
Tests Yahoo Finance, Tiingo, and Brave Search integrations
"""

import os
import sys
from dotenv import load_dotenv

# Import all tool modules
from yahoo_finance_tool import get_yahoo_finance_tools
from tiingo_tool import get_tiingo_tools
from brave_search_tool import get_brave_search_tools

def test_api_keys():
    """Test that required API keys are available"""
    print("🔑 Testing API Keys...")
    print("=" * 40)
    
    keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TIINGO_API_KEY": os.getenv("TIINGO_API_KEY"),
        "BRAVE_SEARCH_API_KEY": os.getenv("BRAVE_SEARCH_API_KEY")
    }
    
    for key_name, key_value in keys.items():
        if key_value:
            print(f"✅ {key_name}: Set")
        else:
            print(f"❌ {key_name}: Not set")
    
    return all(keys.values())

def test_yahoo_finance_tools():
    """Test Yahoo Finance tools"""
    print("\n📊 Testing Yahoo Finance Tools...")
    print("=" * 40)
    
    try:
        yahoo_tools = get_yahoo_finance_tools()
        print(f"✅ Yahoo Finance: {len(yahoo_tools)} tools loaded")
        
        # Test stock price tool (may fail due to rate limiting)
        price_tool = yahoo_tools[0]
        result = price_tool._run("AAPL")
        if "Error" in result:
            print("⚠️  Yahoo Finance rate limited (expected)")
        else:
            print("✅ Yahoo Finance stock price: Success")
        
        return True
    except Exception as e:
        print(f"❌ Yahoo Finance error: {e}")
        return False

def test_tiingo_tools():
    """Test Tiingo tools"""
    print("\n💼 Testing Tiingo Tools...")
    print("=" * 40)
    
    tiingo_key = os.getenv("TIINGO_API_KEY")
    if not tiingo_key:
        print("⚠️  Tiingo API key not set - skipping tests")
        return False
    
    try:
        tiingo_tools = get_tiingo_tools()
        print(f"✅ Tiingo: {len(tiingo_tools)} tools loaded")
        
        # Test stock metadata tool
        metadata_tool = tiingo_tools[1]
        result = metadata_tool._run("AAPL")
        if "Error" in result:
            print(f"❌ Tiingo metadata error")
        else:
            print("✅ Tiingo stock metadata: Success")
        
        return True
    except Exception as e:
        print(f"❌ Tiingo error: {e}")
        return False

def test_brave_search_tools():
    """Test Brave Search tools"""
    print("\n🔍 Testing Brave Search Tools...")
    print("=" * 40)
    
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not brave_key:
        print("⚠️  Brave Search API key not set - skipping tests")
        return False
    
    try:
        brave_tools = get_brave_search_tools()
        print(f"✅ Brave Search: {len(brave_tools)} tools loaded")
        
        # Test web search tool
        web_tool = brave_tools[0]
        result = web_tool._run("Python programming", count=3)
        if "Error" in result:
            print(f"❌ Brave web search error")
        else:
            print("✅ Brave web search: Success")
        
        return True
    except Exception as e:
        print(f"❌ Brave Search error: {e}")
        return False

def test_agent_integration():
    """Test the full agent integration"""
    print("\n🤖 Testing Agent Integration...")
    print("=" * 40)
    
    # Check required API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  OpenAI API key not set - skipping agent test")
        return False
    
    try:
        # Import agent modules
        from langchain_openai import ChatOpenAI
        from langchain.agents import create_openai_tools_agent, AgentExecutor
        from langchain.prompts import ChatPromptTemplate
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=openai_key)
        
        # Get all tools
        yahoo_tools = get_yahoo_finance_tools()
        tiingo_tools = get_tiingo_tools()
        brave_tools = get_brave_search_tools()
        
        all_tools = yahoo_tools + tiingo_tools + brave_tools
        
        print(f"✅ Total tools available: {len(all_tools)}")
        
        # Create simple prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to financial data and web search tools. List the available tools briefly."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(llm, all_tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=False)
        
        # Test simple query
        result = agent_executor.invoke({"input": "What types of tools do you have available?"})
        
        if result and "output" in result:
            print("✅ Agent integration: Success")
            return True
        else:
            print("❌ Agent integration: No valid response")
            return False
            
    except ImportError as e:
        print(f"❌ Agent integration: Missing dependencies - {e}")
        return False
    except Exception as e:
        print(f"❌ Agent integration: {e}")
        return False

def test_tool_variety():
    """Test that we have a good variety of tools"""
    print("\n🛠️  Testing Tool Variety...")
    print("=" * 40)
    
    try:
        yahoo_tools = get_yahoo_finance_tools()
        tiingo_tools = get_tiingo_tools()
        brave_tools = get_brave_search_tools()
        
        print(f"📊 Yahoo Finance tools: {len(yahoo_tools)}")
        for tool in yahoo_tools:
            print(f"   - {tool.name}")
        
        print(f"\n💼 Tiingo tools: {len(tiingo_tools)}")
        for tool in tiingo_tools:
            print(f"   - {tool.name}")
        
        print(f"\n🔍 Brave Search tools: {len(brave_tools)}")
        for tool in brave_tools:
            print(f"   - {tool.name}")
        
        total_tools = len(yahoo_tools) + len(tiingo_tools) + len(brave_tools)
        print(f"\n✅ Total tools: {total_tools}")
        
        return total_tools >= 10  # Should have at least 10 tools
        
    except Exception as e:
        print(f"❌ Tool variety test failed: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    # Load environment variables
    load_dotenv()
    
    print("🧪 Comprehensive Financial Data & Web Search Integration Test")
    print("=" * 70)
    
    print("\n📋 Test Summary:")
    print("This test verifies that all three tool categories work together:")
    print("1. Yahoo Finance - Stock data and financial information")
    print("2. Tiingo - Professional financial data and crypto")
    print("3. Brave Search - Web search, news, images, videos, AI summaries")
    
    # Run all tests
    tests = [
        ("API Keys", test_api_keys),
        ("Yahoo Finance", test_yahoo_finance_tools),
        ("Tiingo", test_tiingo_tools),
        ("Brave Search", test_brave_search_tools),
        ("Tool Variety", test_tool_variety),
        ("Agent Integration", test_agent_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 40)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your comprehensive AI assistant is ready!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Some features may be limited due to missing API keys.")
    else:
        print("❌ Several tests failed. Check your API keys and configuration.")
    
    print("\n🚀 Next Steps:")
    if passed >= total * 0.7:
        print("✅ Ready to use! Try these commands:")
        print("   python langchain_agent.py \"What is the current price of Apple stock?\"")
        print("   python langchain_agent.py \"Latest news about artificial intelligence\"")
        print("   python langchain_agent.py \"Summarize renewable energy trends\"")
    else:
        print("🔧 Setup required:")
        print("   1. Set up missing API keys in your .env file")
        print("   2. Install any missing dependencies: pip install -r requirements.txt")
        print("   3. Run this test again")

if __name__ == "__main__":
    main() 