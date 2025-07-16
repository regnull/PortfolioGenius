import json
from firebase_functions import https_fn
from flask import Flask, jsonify
from stock_service import StockPriceService
from auth_utils import AuthUtils, AuthError
from advisory_service import AdvisoryService, dict_to_position, dict_to_trade, advice_to_dict
from google.cloud import firestore


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