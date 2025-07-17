import json
from firebase_functions import https_fn
from flask import Flask, jsonify
from stock_service import StockPriceService
from auth_utils import AuthUtils, AuthError
from advisory_service import AdvisoryService, dict_to_position, dict_to_trade, advice_to_dict
from portfolio_service import PortfolioService
from google.cloud import firestore
from datetime import datetime
import os


@https_fn.on_request()
def health(req):
    """
    Basic health check endpoint for Firebase Cloud Functions.
    Returns a simple OK status to verify the function is running.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    response = {
        "status": "OK",
        "message": "Portfolio Genius API is healthy",
        "timestamp": "2025-01-16T00:00:00Z"
    }
    
    return (json.dumps(response), 200, headers)




@https_fn.on_request()
def get_stock_price(req):
    """
    Firebase function for getting stock prices.
    This provides a direct endpoint: /get_stock_price
    
    Expects POST request with JSON body: {"ticker": "AAPL"}
    Requires Authorization header with Bearer token.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    if req.method != 'POST':
        response = {
            "error": "Method Not Allowed",
            "message": "Only POST requests are supported"
        }
        return (json.dumps(response), 405, headers)
    
    try:
        # Verify authentication
        user_info = AuthUtils.verify_auth_token(req)
        
        # Get request data
        request_data = req.get_json()
        if not request_data or 'ticker' not in request_data:
            response = {
                "error": "Bad Request",
                "message": "Request body must contain 'ticker' field"
            }
            return (json.dumps(response), 400, headers)
        
        ticker = request_data['ticker']
        
        # Get stock price
        stock_service = StockPriceService()
        stock_data = stock_service.get_price(ticker)
        
        # Add user context to response
        response = {
            "success": True,
            "data": stock_data,
            "user_id": user_info['uid'],
            "timestamp": stock_data['timestamp']
        }
        
        return (json.dumps(response), 200, headers)
        
    except AuthError as e:
        response = {
            "error": "Authentication failed",
            "message": str(e)
        }
        return (json.dumps(response), 401, headers)
        
    except ValueError as e:
        response = {
            "error": "Bad Request",
            "message": str(e)
        }
        return (json.dumps(response), 400, headers)
        
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to fetch stock price: {str(e)}"
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def portfolio_advisory(req):
    """
    Firebase function for portfolio advisory service.
    This provides a direct endpoint: /portfolio_advisory
    
    Expects POST request with JSON body:
    {
        "portfolio_id": "string"
    }
    
    Requires Authorization header with Bearer token.
    
    This function will:
    1. Verify user authorization and portfolio ownership
    2. Fetch portfolio data from Firestore
    3. Generate advisory using the advisory service
    4. Write suggested trades to suggestedTrades collection under portfolio
    5. Write advice to the advice field in the portfolio document
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    if req.method != 'POST':
        response = {
            "error": "Method Not Allowed",
            "message": "Only POST requests are supported"
        }
        return (json.dumps(response), 405, headers)
    
    try:
        # Verify authentication
        user_info = AuthUtils.verify_auth_token(req)
        user_id = user_info['uid']
        
        # Get request data
        request_data = req.get_json()
        if not request_data:
            response = {
                "error": "Bad Request",
                "message": "Request body is required"
            }
            return (json.dumps(response), 400, headers)
        
        # Validate required fields
        portfolio_id = request_data.get('portfolio_id')
        if not portfolio_id:
            response = {
                "error": "Bad Request",
                "message": "Missing required field: portfolio_id"
            }
            return (json.dumps(response), 400, headers)
        
        # Initialize Firestore client
        db = firestore.Client()
        
        # Fetch portfolio document and verify ownership
        portfolio_ref = db.collection('portfolios').document(portfolio_id)
        portfolio_doc = portfolio_ref.get()
        
        if not portfolio_doc.exists:
            response = {
                "error": "Not Found",
                "message": "Portfolio not found"
            }
            return (json.dumps(response), 404, headers)
        
        portfolio_data = portfolio_doc.to_dict()
        
        # Check if user owns this portfolio
        if portfolio_data.get('userId') != user_id:
            response = {
                "error": "Forbidden",
                "message": "You do not have permission to access this portfolio"
            }
            return (json.dumps(response), 403, headers)
        
        # Fetch positions for this portfolio
        positions_ref = db.collection('positions').where('portfolioId', '==', portfolio_id)
        positions_docs = positions_ref.get()
        
        positions_data = []
        for doc in positions_docs:
            pos_data = doc.to_dict()
            positions_data.append({
                'symbol': pos_data.get('symbol', ''),
                'name': pos_data.get('name', ''),
                'quantity': pos_data.get('quantity', 0),
                'open_price': pos_data.get('openPrice', 0),
                'current_price': pos_data.get('currentPrice', pos_data.get('openPrice', 0)),
                'type': pos_data.get('type', 'stock'),
                'status': pos_data.get('status', 'open'),
                'total_value': pos_data.get('totalValue', 0),
                'gain_loss': pos_data.get('gainLoss', 0),
                'gain_loss_percent': pos_data.get('gainLossPercent', 0)
            })
        
        # Fetch recent trades for this portfolio (optional)
        trades_ref = db.collection('trades').where('portfolioId', '==', portfolio_id).order_by('date', direction=firestore.Query.DESCENDING).limit(10)
        trades_docs = trades_ref.get()
        
        trades_data = []
        for doc in trades_docs:
            trade_data = doc.to_dict()
            trades_data.append({
                'symbol': trade_data.get('symbol', ''),
                'type': trade_data.get('type', 'buy'),
                'quantity': trade_data.get('quantity', 0),
                'price': trade_data.get('price', 0),
                'date': trade_data.get('date', firestore.SERVER_TIMESTAMP),
                'fees': trade_data.get('fees'),
                'notes': trade_data.get('notes')
            })
        
        # Convert data to objects
        positions = [dict_to_position(pos) for pos in positions_data]
        recent_trades = [dict_to_trade(trade) for trade in trades_data]
        
        # Get portfolio goal
        portfolio_goal = portfolio_data.get('goal', 'Moderate risk investment portfolio')
        
        # Get advice from advisory service
        advisory_service = AdvisoryService()
        advice = advisory_service.analyze_portfolio(
            portfolio_goal=portfolio_goal,
            positions=positions,
            recent_trades=recent_trades
        )
        
        # Write suggested trades to suggestedTrades collection under portfolio
        suggested_trades_ref = db.collection('portfolios').document(portfolio_id).collection('suggestedTrades')
        
        # Clear existing suggested trades
        existing_trades = suggested_trades_ref.get()
        batch = db.batch()
        for doc in existing_trades:
            batch.delete(doc.reference)
        batch.commit()
        
        # Add new suggested trades
        batch = db.batch()
        for trade in advice.suggested_trades:
            trade_ref = suggested_trades_ref.document()
            batch.set(trade_ref, {
                'symbol': trade.symbol,
                'action': trade.action,
                'quantity': trade.quantity,
                'targetPrice': trade.target_price,
                'reasoning': trade.reasoning,
                'priority': trade.priority,
                'riskLevel': trade.risk_level,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'status': 'pending'
            })
        batch.commit()
        
        # Write advice to the advice field in the portfolio document
        portfolio_ref.update({
            'advice': advice.advice,
            'portfolioScore': advice.portfolio_score,
            'riskAssessment': advice.risk_assessment,
            'diversificationScore': advice.diversification_score,
            'lastAdvisoryDate': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        # Return success response
        response = {
            "success": True,
            "message": "Portfolio advisory generated successfully",
            "data": {
                "portfolio_id": portfolio_id,
                "advice": advice.advice,
                "portfolio_score": advice.portfolio_score,
                "risk_assessment": advice.risk_assessment,
                "diversification_score": advice.diversification_score,
                "suggested_trades_count": len(advice.suggested_trades)
            },
            "user_id": user_id,
            "timestamp": advice.timestamp.isoformat()
        }
        
        return (json.dumps(response), 200, headers)
        
    except AuthError as e:
        response = {
            "error": "Authentication failed",
            "message": str(e)
        }
        return (json.dumps(response), 401, headers)
        
    except ValueError as e:
        response = {
            "error": "Bad Request",
            "message": str(e)
        }
        return (json.dumps(response), 400, headers)
        
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to generate portfolio advice: {str(e)}"
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def construct_portfolio(req):
    """
    Firebase function for AI-powered portfolio construction.
    This provides a direct endpoint: /construct_portfolio
    
    Expects POST request with JSON body: {
        "portfolio_goal": "I want to invest $10,000 with medium risk for 10 years...",
        "portfolio_id": "portfolio_123",  // Optional: if provided, creates suggested trades
        "user_id": "user_456"             // Required if portfolio_id provided
    }
    
    Returns JSON portfolio recommendation with allocations and rationale.
    If portfolio_id provided, also creates suggested trades in Firestore.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Validate request method
        if req.method != 'POST':
            response = {
                "error": "Method Not Allowed",
                "message": "Only POST requests are supported"
            }
            return (json.dumps(response), 405, headers)
        
        # Parse request body
        try:
            request_data = req.get_json()
            if not request_data:
                raise ValueError("Request body must be valid JSON")
        except Exception as e:
            response = {
                "error": "Bad Request",
                "message": f"Invalid JSON in request body: {str(e)}"
            }
            return (json.dumps(response), 400, headers)
        
        # Validate required fields
        portfolio_goal = request_data.get('portfolio_goal')
        if not portfolio_goal:
            response = {
                "error": "Bad Request",
                "message": "portfolio_goal is required in request body"
            }
            return (json.dumps(response), 400, headers)
        
        if not isinstance(portfolio_goal, str) or len(portfolio_goal.strip()) == 0:
            response = {
                "error": "Bad Request",
                "message": "portfolio_goal must be a non-empty string"
            }
            return (json.dumps(response), 400, headers)
        
        # Optional fields for creating suggested trades
        portfolio_id = request_data.get('portfolio_id')
        user_id = request_data.get('user_id')
        
        # If portfolio_id provided, user_id is required
        if portfolio_id and not user_id:
            response = {
                "error": "Bad Request",
                "message": "user_id is required when portfolio_id is provided"
            }
            return (json.dumps(response), 400, headers)
        
        # Initialize portfolio service
        try:
            portfolio_service = PortfolioService()
        except ValueError as e:
            response = {
                "error": "Service Configuration Error",
                "message": f"Portfolio service initialization failed: {str(e)}"
            }
            return (json.dumps(response), 500, headers)
        
        # Construct portfolio
        try:
            if portfolio_id and user_id:
                # Create portfolio with suggested trades
                portfolio_recommendation = portfolio_service.construct_portfolio_with_trades(
                    portfolio_goal.strip(), portfolio_id, user_id
                )
            else:
                # Just create portfolio recommendation without suggested trades
                portfolio_recommendation = portfolio_service.construct_portfolio(portfolio_goal.strip())
            
            # Add metadata about the service
            tools_info = portfolio_service.get_available_tools_info()
            portfolio_recommendation['service_info'] = {
                'tools_used': tools_info['total_tools'],
                'api_keys_available': tools_info['api_keys_status'],
                'processing_timestamp': datetime.now().isoformat()
            }
            
            return (json.dumps(portfolio_recommendation), 200, headers)
            
        except ValueError as e:
            response = {
                "error": "Portfolio Construction Failed",
                "message": f"Failed to parse AI response: {str(e)}"
            }
            return (json.dumps(response), 502, headers)
            
        except RuntimeError as e:
            response = {
                "error": "Portfolio Construction Failed", 
                "message": f"AI portfolio construction error: {str(e)}"
            }
            return (json.dumps(response), 502, headers)
    
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to construct portfolio: {str(e)}"
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def portfolio_tools_status(req):
    """
    Firebase function to check portfolio service tools and API key status.
    This provides a direct endpoint: /portfolio_tools_status
    
    Returns information about available tools and API key configuration.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Initialize portfolio service to check status
        try:
            portfolio_service = PortfolioService()
            tools_info = portfolio_service.get_available_tools_info()
            
            response = {
                "status": "OK",
                "message": "Portfolio service is available",
                "tools_info": tools_info,
                "timestamp": datetime.now().isoformat()
            }
            return (json.dumps(response), 200, headers)
            
        except ValueError as e:
            response = {
                "status": "Configuration Error",
                "message": str(e),
                "tools_info": {
                    "total_tools": 0,
                    "api_keys_status": {
                        "openai": False,
                        "tiingo": bool(os.getenv("TIINGO_API_KEY")),
                        "brave_search": bool(os.getenv("BRAVE_API_KEY"))
                    },
                    "available_tools": []
                },
                "timestamp": datetime.now().isoformat()
            }
            return (json.dumps(response), 500, headers)
    
    except Exception as e:
        response = {
            "status": "Error",
            "message": f"Failed to check portfolio service status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def get_suggested_trades(req):
    """
    Firebase function to get suggested trades for a portfolio.
    This provides a direct endpoint: /get_suggested_trades
    
    Expects GET request with query parameters:
    - portfolio_id: ID of the portfolio
    - user_id: ID of the user (for authorization)
    
    Returns list of suggested trades for the portfolio.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Validate request method
        if req.method != 'GET':
            response = {
                "error": "Method Not Allowed",
                "message": "Only GET requests are supported"
            }
            return (json.dumps(response), 405, headers)
        
        # Get query parameters
        portfolio_id = req.args.get('portfolio_id')
        user_id = req.args.get('user_id')
        status = req.args.get('status')  # Optional status filter
        
        if not portfolio_id:
            response = {
                "error": "Bad Request",
                "message": "portfolio_id query parameter is required"
            }
            return (json.dumps(response), 400, headers)
        
        if not user_id:
            response = {
                "error": "Bad Request",
                "message": "user_id query parameter is required"
            }
            return (json.dumps(response), 400, headers)
        
        # Initialize portfolio service
        try:
            portfolio_service = PortfolioService()
        except ValueError as e:
            response = {
                "error": "Service Configuration Error",
                "message": f"Portfolio service initialization failed: {str(e)}"
            }
            return (json.dumps(response), 500, headers)
        
        # Get suggested trades
        try:
            suggested_trades = portfolio_service.get_suggested_trades(portfolio_id, user_id, status)
            
            response = {
                "suggested_trades": suggested_trades,
                "count": len(suggested_trades),
                "portfolio_id": portfolio_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return (json.dumps(response), 200, headers)
            
        except RuntimeError as e:
            response = {
                "error": "Failed to Get Suggested Trades",
                "message": str(e)
            }
            return (json.dumps(response), 500, headers)
    
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to get suggested trades: {str(e)}"
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def convert_suggested_trade(req):
    """
    Firebase function to convert a suggested trade to an actual trade.
    This provides a direct endpoint: /convert_suggested_trade
    
    Expects POST request with JSON body: {
        "suggested_trade_id": "trade_123",
        "user_id": "user_456",
        "trade_data": {           // Optional: override trade details
            "quantity": 10,
            "price": 195.50,
            "fees": 9.99,
            "notes": "Custom execution notes"
        }
    }
    
    Returns the ID of the created actual trade.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Validate request method
        if req.method != 'POST':
            response = {
                "error": "Method Not Allowed",
                "message": "Only POST requests are supported"
            }
            return (json.dumps(response), 405, headers)
        
        # Parse request body
        try:
            request_data = req.get_json()
            if not request_data:
                raise ValueError("Request body must be valid JSON")
        except Exception as e:
            response = {
                "error": "Bad Request",
                "message": f"Invalid JSON in request body: {str(e)}"
            }
            return (json.dumps(response), 400, headers)
        
        # Validate required fields
        suggested_trade_id = request_data.get('suggested_trade_id')
        user_id = request_data.get('user_id')
        
        if not suggested_trade_id:
            response = {
                "error": "Bad Request",
                "message": "suggested_trade_id is required in request body"
            }
            return (json.dumps(response), 400, headers)
        
        if not user_id:
            response = {
                "error": "Bad Request",
                "message": "user_id is required in request body"
            }
            return (json.dumps(response), 400, headers)
        
        # Optional trade data overrides
        trade_data = request_data.get('trade_data')
        
        # Initialize portfolio service
        try:
            portfolio_service = PortfolioService()
        except ValueError as e:
            response = {
                "error": "Service Configuration Error",
                "message": f"Portfolio service initialization failed: {str(e)}"
            }
            return (json.dumps(response), 500, headers)
        
        # Convert suggested trade to actual trade
        try:
            actual_trade_id = portfolio_service.convert_suggested_trade_to_actual(
                suggested_trade_id, user_id, trade_data
            )
            
            response = {
                "message": "Suggested trade successfully converted to actual trade",
                "actual_trade_id": actual_trade_id,
                "suggested_trade_id": suggested_trade_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return (json.dumps(response), 200, headers)
            
        except ValueError as e:
            response = {
                "error": "Bad Request",
                "message": str(e)
            }
            return (json.dumps(response), 400, headers)
            
        except RuntimeError as e:
            response = {
                "error": "Trade Conversion Failed",
                "message": str(e)
            }
            return (json.dumps(response), 500, headers)
    
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to convert suggested trade: {str(e)}"
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request()
def dismiss_suggested_trade(req):
    """
    Firebase function to dismiss a suggested trade.
    This provides a direct endpoint: /dismiss_suggested_trade
    
    Expects POST request with JSON body: {
        "suggested_trade_id": "trade_123",
        "user_id": "user_456",
        "reason": "Optional reason for dismissal"
    }
    
    Returns success status.
    """
    # Handle preflight CORS requests
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Validate request method
        if req.method != 'POST':
            response = {
                "error": "Method Not Allowed",
                "message": "Only POST requests are supported"
            }
            return (json.dumps(response), 405, headers)
        
        # Parse request body
        try:
            request_data = req.get_json()
            if not request_data:
                raise ValueError("Request body must be valid JSON")
        except Exception as e:
            response = {
                "error": "Bad Request",
                "message": f"Invalid JSON in request body: {str(e)}"
            }
            return (json.dumps(response), 400, headers)
        
        # Validate required fields
        suggested_trade_id = request_data.get('suggested_trade_id')
        user_id = request_data.get('user_id')
        
        if not suggested_trade_id:
            response = {
                "error": "Bad Request",
                "message": "suggested_trade_id is required in request body"
            }
            return (json.dumps(response), 400, headers)
        
        if not user_id:
            response = {
                "error": "Bad Request",
                "message": "user_id is required in request body"
            }
            return (json.dumps(response), 400, headers)
        
        # Optional reason for dismissal
        reason = request_data.get('reason')
        
        # Initialize portfolio service
        try:
            portfolio_service = PortfolioService()
        except ValueError as e:
            response = {
                "error": "Service Configuration Error",
                "message": f"Portfolio service initialization failed: {str(e)}"
            }
            return (json.dumps(response), 500, headers)
        
        # Dismiss the suggested trade
        try:
            success = portfolio_service.dismiss_suggested_trade(suggested_trade_id, user_id, reason)
            
            response = {
                "message": "Suggested trade successfully dismissed",
                "suggested_trade_id": suggested_trade_id,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            return (json.dumps(response), 200, headers)
            
        except ValueError as e:
            response = {
                "error": "Bad Request",
                "message": str(e)
            }
            return (json.dumps(response), 400, headers)
            
        except RuntimeError as e:
            response = {
                "error": "Dismissal Failed",
                "message": str(e)
            }
            return (json.dumps(response), 500, headers)
    
    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to dismiss suggested trade: {str(e)}"
        }
        return (json.dumps(response), 500, headers)