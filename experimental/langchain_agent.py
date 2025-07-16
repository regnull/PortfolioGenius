#!/usr/bin/env python3
"""
LangChain Agent with Financial Data Tools
Supports Yahoo Finance and Tiingo APIs for comprehensive financial data access
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

# Import Yahoo Finance tools
from yahoo_finance_tool import get_yahoo_finance_tools

# Import Tiingo tools
from tiingo_tool import get_tiingo_tools

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
        model="gpt-4",
        temperature=0.1,
        api_key=openai_api_key
    )
    
    # Get all available tools
    yahoo_tools = get_yahoo_finance_tools()
    tiingo_tools = get_tiingo_tools()
    
    # Combine all tools
    # all_tools = yahoo_tools + tiingo_tools
    all_tools = tiingo_tools
    
    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI financial assistant with access to comprehensive financial data from multiple sources. 
        You can help users with stock market information, company analysis, financial data, news, and market insights.
        
        You have access to the following financial data tools:
        
        TIINGO TOOLS:
        - get_tiingo_stock_price: Get current and historical stock prices from Tiingo
        - get_tiingo_stock_metadata: Get detailed stock metadata and company information
        - get_tiingo_stock_news: Get curated financial news from Tiingo
        - get_tiingo_fundamentals: Get fundamental financial metrics and ratios
        - get_tiingo_crypto_price: Get cryptocurrency prices and historical data
        
        Always provide clear, helpful responses and explain the data sources you're using.
        If rate limiting occurs, try alternative data sources.
        
        Format your responses in a clear, professional manner suitable for financial analysis.
        """),
        ("user", "{input}"),
        ("assistant", "I'll help you with that financial question. Let me gather the relevant data for you."),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, all_tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)
    
    # Check if a query was provided as a command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        print("=" * 50)
        
        try:
            result = agent_executor.invoke({"input": query})
            print("\nResponse:")
            print(result["output"])
        except Exception as e:
            print(f"Error processing query: {e}")
        
        return
    
    # Interactive mode
    print("Financial AI Assistant")
    print("=" * 50)
    print("Available data sources: Yahoo Finance, Tiingo")
    print("Type 'help' for available commands or 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("Ask me about stocks, market data, or financial news: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- Ask about stock prices: 'What is the current price of AAPL?'")
                print("- Get company info: 'Tell me about Apple Inc'")
                print("- Get financial news: 'What's the latest news about Tesla?'")
                print("- Get fundamentals: 'What are the key metrics for Microsoft?'")
                print("- Get crypto prices: 'What's the current Bitcoin price?'")
                print("- Market summary: 'How are the markets doing today?'")
                print("- Compare data: 'Compare Apple and Google stock performance'")
                print("- Type 'quit' to exit")
                print()
                continue
            
            if not user_input:
                continue
            
            print(f"\nQuery: {user_input}")
            print("-" * 40)
            
            # Process the query
            try:
                result = agent_executor.invoke({"input": user_input})
                print("\nResponse:")
                print(result["output"])
            except Exception as e:
                print(f"Error processing query: {e}")
                print("Please try again with a different query.")
            
            print("\n" + "=" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()