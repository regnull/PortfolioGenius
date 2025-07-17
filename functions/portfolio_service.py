"""
Portfolio Construction Service for Firebase Cloud Functions
Provides AI-powered portfolio recommendations using multiple financial data sources
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from google.cloud import firestore
from firestore_utils import safe_firestore_add, safe_firestore_update, clean_string_field, clean_numeric_field, sanitize_for_firestore

# Import tool modules (we'll need to copy these)
from yahoo_finance_tools import get_yahoo_finance_tools
from tiingo_tools import get_tiingo_tools
from brave_search_tools import get_brave_search_tools


class PortfolioService:
    """Service for constructing investment portfolios using AI and financial data tools"""
    
    def __init__(self):
        """Initialize the portfolio service with API keys from environment"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tiingo_api_key = os.getenv("TIINGO_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize Firestore
        self.db = firestore.Client()
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=self.openai_api_key
        )
        
        # Get all available tools
        self.all_tools = []
        
        # Add Yahoo Finance tools (always available)
        self.all_tools.extend(get_yahoo_finance_tools())
        
        # Add Tiingo tools if API key is available
        if self.tiingo_api_key:
            self.all_tools.extend(get_tiingo_tools())
        
        # Add Brave Search tools if API key is available
        if self.brave_api_key:
            self.all_tools.extend(get_brave_search_tools())
        
        # Define the prompt template for portfolio construction
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial advisor and portfolio manager with access to comprehensive financial data and research tools.
            
            Your task is to construct a specific investment portfolio based on the user's requirements.
            
            IMPORTANT: You MUST use the available tools to gather current market data and financial information. Do NOT rely on your training data for current prices, market conditions, or financial metrics.
            
            You have access to the following tools:
            
            YAHOO FINANCE TOOLS:
            - get_stock_price: Get current and historical stock prices from Yahoo Finance
            - get_stock_news: Get recent news articles for companies from Yahoo Finance
            - get_stock_info: Get comprehensive company information and financial metrics
            - get_market_summary: Get market indices and overall market performance
            
            TIINGO TOOLS (if available):
            - get_tiingo_stock_price: Get current and historical stock prices from Tiingo
            - get_tiingo_stock_metadata: Get detailed stock metadata and company information
            - get_tiingo_stock_news: Get curated financial news from Tiingo
            - get_tiingo_fundamentals: Get fundamental financial metrics and ratios
            - get_tiingo_crypto_price: Get cryptocurrency prices and historical data
            
            BRAVE SEARCH TOOLS (if available):
            - brave_web_search: Search the web for current information and real-time data
            - brave_news_search: Search for recent news articles from across the web
            - brave_image_search: Search for images on any topic
            - brave_video_search: Search for videos including tutorials and explanations
            - brave_ai_summarizer: Get AI-powered summaries of complex topics
            
            For portfolio construction, you MUST follow these steps:
            1. FIRST: Use get_market_summary to understand current market conditions
            2. THEN: Use get_stock_info or get_tiingo_stock_metadata for each recommended stock/ETF to get current prices and fundamentals
            3. Use get_tiingo_crypto_price for any cryptocurrency recommendations (if available)
            4. Use brave_news_search or financial news tools to understand current market sentiment (if available)
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
        self.agent = create_openai_tools_agent(self.llm, self.all_tools, self.prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.all_tools, verbose=False)
    
    def _sanitize_for_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data dictionary to ensure no undefined/None values are sent to Firestore.
        
        Args:
            data: Dictionary to sanitize
        
        Returns:
            Dict: Sanitized dictionary safe for Firestore
        """
        sanitized = {}
        
        for key, value in data.items():
            if value is None:
                # Skip None values entirely rather than converting them
                continue
            elif isinstance(value, str) and value.strip() == '':
                # Skip empty strings if they're not meaningful
                continue
            elif isinstance(value, (int, float)) and value == 0 and key in ['quantity', 'target_price', 'price']:
                # Keep zero values for numeric fields as they might be meaningful
                sanitized[key] = float(value)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                nested_sanitized = self._sanitize_for_firestore(value)
                if nested_sanitized:  # Only add if not empty
                    sanitized[key] = nested_sanitized
            elif isinstance(value, list):
                # Filter out None values from lists
                sanitized_list = [item for item in value if item is not None]
                if sanitized_list:  # Only add if not empty
                    sanitized[key] = sanitized_list
            else:
                # Convert other types to appropriate formats
                if isinstance(value, str):
                    sanitized[key] = value.strip()
                elif isinstance(value, (int, float)):
                    sanitized[key] = float(value) if isinstance(value, float) else int(value)
                else:
                    sanitized[key] = value
        
        return sanitized
    
    def construct_portfolio(self, portfolio_goal: str) -> Dict[str, Any]:
        """
        Construct an investment portfolio based on a natural language description of goals.
        
        Args:
            portfolio_goal (str): Natural language description of portfolio requirements.
                                 Example: "I want to invest $10,000 with medium risk for 10 years, 
                                 focusing on stocks and ETFs with some crypto exposure"
        
        Returns:
            dict: JSON portfolio recommendation with allocations and rationale
        
        Raises:
            ValueError: If portfolio recommendation cannot be parsed as JSON
            RuntimeError: If there's an error during portfolio construction
        """
        try:
            # Format the portfolio request with today's date
            today_date = datetime.now().strftime("%B %d, %Y")
            
            portfolio_request = f"""
            Today is {today_date}.
            
            {portfolio_goal}
            
            Please research current market conditions, analyze suitable investments, and provide a comprehensive portfolio recommendation in the specified JSON format.
            Include current prices, fundamental analysis, and detailed rationale for each recommendation.
            """
            
            # Execute the agent
            result = self.agent_executor.invoke({"input": portfolio_request})
            
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
    
    def get_available_tools_info(self) -> Dict[str, Any]:
        """
        Get information about available tools and API keys status.
        
        Returns:
            dict: Information about available tools and their status
        """
        return {
            "total_tools": len(self.all_tools),
            "api_keys_status": {
                "openai": bool(self.openai_api_key),
                "tiingo": bool(self.tiingo_api_key),
                "brave_search": bool(self.brave_api_key)
            },
            "available_tools": [tool.name for tool in self.all_tools]
        }
    
    def _create_suggested_trades_from_portfolio(self, portfolio_recommendation: Dict[str, Any], portfolio_id: str, user_id: str) -> List[str]:
        """
        Convert portfolio recommendations into suggested trades and save to Firestore.
        
        Args:
            portfolio_recommendation: The AI-generated portfolio recommendation
            portfolio_id: ID of the portfolio to create suggestions for
            user_id: ID of the user who owns the portfolio
        
        Returns:
            List[str]: List of suggested trade document IDs
        """
        suggested_trade_ids = []
        
        # Get recommendations from the portfolio
        recommendations = portfolio_recommendation.get('recommendations', [])
        total_investment = portfolio_recommendation.get('portfolio_summary', {}).get('total_investment', '$10,000')
        
        # Parse investment amount (remove $ and commas)
        try:
            investment_amount = float(total_investment.replace('$', '').replace(',', ''))
        except (ValueError, AttributeError):
            investment_amount = 10000.0  # Default fallback
        
        for recommendation in recommendations:
            try:
                ticker_symbol = recommendation.get('ticker_symbol', '').upper().strip()
                allocation_percent = recommendation.get('allocation_percent', 0)
                rationale = recommendation.get('rationale', '').strip()
                notes = recommendation.get('notes', '').strip()
                
                # Skip if essential fields are missing
                if not ticker_symbol or allocation_percent <= 0:
                    print(f"Skipping recommendation due to missing essential fields: {recommendation}")
                    continue
                
                # Calculate dollar amount for this allocation
                dollar_amount = investment_amount * (allocation_percent / 100)
                
                # Extract current price from notes if available
                current_price = None
                if 'price:' in notes.lower():
                    try:
                        # Extract price from notes like "Current price: $195.50"
                        price_part = notes.lower().split('price:')[1].split(',')[0].strip()
                        current_price = float(price_part.replace('$', '').strip())
                    except (IndexError, ValueError):
                        current_price = None
                
                # Calculate suggested quantity if we have a price
                suggested_quantity = None
                if current_price and current_price > 0:
                    suggested_quantity = round(dollar_amount / current_price, 2)
                
                # Create suggested trade document with all required fields
                suggested_trade = {
                    'portfolioId': str(portfolio_id),
                    'userId': str(user_id),
                    'symbol': ticker_symbol,
                    'name': ticker_symbol,  # Add name field for display
                    'type': 'stock',  # Default type - could be enhanced with actual asset type detection
                    'action': 'buy',  # New portfolio recommendations are always buy actions
                    'quantity': suggested_quantity if suggested_quantity is not None else 0,
                    'estimatedPrice': current_price if current_price is not None else 0,
                    'target_price': current_price if current_price is not None else 0,  # Keep for backward compatibility
                    'dollar_amount': dollar_amount,
                    'allocation_percent': float(allocation_percent),
                    'rationale': f"{rationale}. {notes}".strip() if rationale or notes else "AI portfolio recommendation",
                    'reasoning': f"{rationale}. {notes}".strip() if rationale or notes else "AI portfolio recommendation",  # Keep for backward compatibility
                    'priority': self._determine_priority(allocation_percent),
                    'risk_level': self._determine_risk_level(recommendation),
                    'status': 'pending',  # pending, executed, dismissed
                    'createdAt': datetime.now(),
                    'created_at': datetime.now(),  # Keep for backward compatibility
                    'updatedAt': datetime.now(),
                    'source': 'ai_portfolio_construction',
                    'portfolio_recommendation_id': portfolio_recommendation.get('portfolio_summary', {}).get('date_created', datetime.now().isoformat())
                }
                
                # Validate all fields are not None/undefined before saving
                for field_name, field_value in suggested_trade.items():
                    if field_value is None:
                        if field_name in ['quantity', 'target_price', 'estimatedPrice']:
                            suggested_trade[field_name] = 0  # Set numeric fields to 0
                        elif field_name in ['reasoning', 'rationale', 'portfolio_recommendation_id', 'name']:
                            suggested_trade[field_name] = ''  # Set string fields to empty string
                        else:
                            print(f"Warning: Field {field_name} is None in suggested trade for {ticker_symbol}")
                
                # Save to Firestore
                doc_ref = safe_firestore_add(self.db.collection('suggestedTrades'), suggested_trade)
                suggested_trade_ids.append(doc_ref[1].id)
                
            except Exception as e:
                print(f"Error creating suggested trade for {recommendation}: {e}")
                continue
        
        return suggested_trade_ids
    
    def _determine_priority(self, allocation_percent: float) -> str:
        """Determine priority based on allocation percentage."""
        if allocation_percent >= 15:
            return 'high'
        elif allocation_percent >= 8:
            return 'medium'
        else:
            return 'low'
    
    def _determine_risk_level(self, recommendation: Dict[str, Any]) -> str:
        """Determine risk level based on the recommendation content."""
        rationale = recommendation.get('rationale', '').lower()
        notes = recommendation.get('notes', '').lower()
        content = f"{rationale} {notes}"
        
        # High risk indicators
        high_risk_keywords = ['crypto', 'volatile', 'speculative', 'growth', 'emerging', 'small-cap']
        # Low risk indicators  
        low_risk_keywords = ['stable', 'dividend', 'bond', 'conservative', 'blue-chip', 'utility']
        
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in content)
        low_risk_count = sum(1 for keyword in low_risk_keywords if keyword in content)
        
        if high_risk_count > low_risk_count:
            return 'high'
        elif low_risk_count > high_risk_count:
            return 'low'
        else:
            return 'medium'
    
    def construct_portfolio_with_trades(self, portfolio_goal: str, portfolio_id: str, user_id: str) -> Dict[str, Any]:
        """
        Construct an investment portfolio and create suggested trades for it.
        
        Args:
            portfolio_goal (str): Natural language description of portfolio requirements
            portfolio_id (str): ID of the portfolio to create suggestions for
            user_id (str): ID of the user who owns the portfolio
        
        Returns:
            dict: Portfolio recommendation with suggested trades created
        """
        try:
            # First, construct the portfolio using the existing method
            portfolio_recommendation = self.construct_portfolio(portfolio_goal)
            
            # Create suggested trades from the recommendations
            suggested_trade_ids = self._create_suggested_trades_from_portfolio(
                portfolio_recommendation, portfolio_id, user_id
            )
            
            # Add suggested trades info to the response
            portfolio_recommendation['suggested_trades_created'] = {
                'count': len(suggested_trade_ids),
                'trade_ids': suggested_trade_ids,
                'portfolio_id': portfolio_id
            }
            
            return portfolio_recommendation
            
        except Exception as e:
            raise RuntimeError(f"Error constructing portfolio with trades: {e}")
    
    def get_suggested_trades(self, portfolio_id: str, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """
        Get suggested trades for a portfolio, optionally filtered by status.
        
        Args:
            portfolio_id (str): Portfolio ID
            user_id (str): User ID for authorization
            status (str, optional): Filter by status ('pending', 'converted', 'dismissed')
        
        Returns:
            List[Dict]: List of suggested trades
        """
        try:
            # Build base query
            trades_ref = self.db.collection('suggestedTrades')\
                .where('portfolioId', '==', portfolio_id)\
                .where('userId', '==', user_id)
            
            # Add status filter if provided
            if status:
                trades_ref = trades_ref.where('status', '==', status)
            
            # Order by creation date (most recent first)
            trades_ref = trades_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
            
            trades_docs = trades_ref.get()
            
            suggested_trades = []
            for doc in trades_docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                
                # Use safe Firestore utilities to handle datetime conversion
                trade_data = sanitize_for_firestore(trade_data, for_response=True)
                
                suggested_trades.append(trade_data)
            
            return suggested_trades
            
        except Exception as e:
            raise RuntimeError(f"Error fetching suggested trades: {e}")
    
    def convert_suggested_trade_to_actual(self, suggested_trade_id: str, user_id: str, trade_data: Dict[str, Any] = None) -> str:
        """
        Convert a suggested trade to an actual trade.
        
        Args:
            suggested_trade_id (str): ID of the suggested trade
            user_id (str): User ID for authorization
            trade_data (Dict, optional): Override data for the actual trade
        
        Returns:
            str: ID of the created actual trade
        """
        try:
            # Get the suggested trade
            suggested_trade_ref = self.db.collection('suggestedTrades').document(suggested_trade_id)
            suggested_trade_doc = suggested_trade_ref.get()
            
            if not suggested_trade_doc.exists:
                raise ValueError("Suggested trade not found")
            
            suggested_trade = suggested_trade_doc.to_dict()
            
            # Verify user ownership
            if suggested_trade.get('userId') != user_id:
                raise ValueError("You do not have permission to access this suggested trade")
            
            # Get values with defaults to avoid None/undefined
            default_quantity = suggested_trade.get('quantity', 0)
            default_price = suggested_trade.get('estimatedPrice', suggested_trade.get('target_price', 0))
            default_reasoning = suggested_trade.get('rationale', suggested_trade.get('reasoning', 'AI portfolio recommendation'))
            
            # Handle trade_data overrides
            final_quantity = default_quantity
            final_price = default_price
            final_fees = 0
            final_notes = f"Executed from suggested trade: {default_reasoning}"
            
            if trade_data:
                final_quantity = trade_data.get('quantity', default_quantity)
                final_price = trade_data.get('price', default_price)
                final_fees = trade_data.get('fees', 0)
                custom_notes = trade_data.get('notes', '')
                if custom_notes:
                    final_notes = custom_notes
            
            # Ensure all values are properly typed and not None
            final_quantity = float(final_quantity) if final_quantity is not None else 0.0
            final_price = float(final_price) if final_price is not None else 0.0
            final_fees = float(final_fees) if final_fees is not None else 0.0
            
            # Create actual trade document
            actual_trade = {
                'portfolioId': str(suggested_trade.get('portfolioId', '')),
                'userId': str(user_id),
                'symbol': str(suggested_trade.get('symbol', '')),
                'type': str(suggested_trade.get('action', 'buy')),  # buy/sell
                'quantity': final_quantity,
                'price': final_price,
                'date': datetime.now(),
                'fees': final_fees,
                'notes': str(final_notes),
                'suggested_trade_id': str(suggested_trade_id),
                'source': 'suggested_trade_conversion'
            }
            
            # Validate all fields are not None/undefined before saving
            for field_name, field_value in actual_trade.items():
                if field_value is None:
                    if field_name in ['quantity', 'price', 'fees']:
                        actual_trade[field_name] = 0.0  # Set numeric fields to 0
                    else:
                        actual_trade[field_name] = ''  # Set string fields to empty string
                        print(f"Warning: Field {field_name} is None in actual trade")
            
            # Save actual trade to Firestore
            trade_ref = safe_firestore_add(self.db.collection('trades'), actual_trade)
            actual_trade_id = trade_ref[1].id
            
            # Update suggested trade status to executed
            update_data = {
                'status': 'executed',
                'executed_at': datetime.now(),
                'actual_trade_id': str(actual_trade_id)
            }
            safe_firestore_update(suggested_trade_ref, update_data)
            
            return actual_trade_id
            
        except Exception as e:
            raise RuntimeError(f"Error converting suggested trade to actual: {e}")
    
    def dismiss_suggested_trade(self, suggested_trade_id: str, user_id: str, reason: str = None) -> bool:
        """
        Dismiss a suggested trade.
        
        Args:
            suggested_trade_id (str): ID of the suggested trade
            user_id (str): User ID for authorization
            reason (str, optional): Reason for dismissal
        
        Returns:
            bool: Success status
        """
        try:
            # Get the suggested trade
            suggested_trade_ref = self.db.collection('suggestedTrades').document(suggested_trade_id)
            suggested_trade_doc = suggested_trade_ref.get()
            
            if not suggested_trade_doc.exists:
                raise ValueError("Suggested trade not found")
            
            suggested_trade = suggested_trade_doc.to_dict()
            
            # Verify user ownership
            if suggested_trade.get('userId') != user_id:
                raise ValueError("You do not have permission to access this suggested trade")
            
            # Update suggested trade status to dismissed
            update_data = {
                'status': 'dismissed',
                'dismissed_at': datetime.now()
            }
            
            # Only add reason if it's provided and not empty
            if reason and reason.strip():
                update_data['dismissal_reason'] = str(reason.strip())
            
            safe_firestore_update(suggested_trade_ref, update_data)
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error dismissing suggested trade: {e}") 