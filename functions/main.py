import json
from firebase_functions import https_fn, options
from flask import Flask, jsonify
from request_utils import handle_cors, parse_json_body
from google.cloud import firestore
from datetime import datetime
import os


# Heavy imports moved inside functions to avoid initialization timeout
# from stock_service import StockPriceService
# from auth_utils import AuthUtils, AuthError  
# from advisory_service import AdvisoryService, dict_to_position, dict_to_trade, advice_to_dict
# from portfolio_service import PortfolioService

@https_fn.on_request(memory=options.MemoryOption.GB_1)
def get_stock_price(req):
    """
    Firebase function for getting stock prices.
    This provides a direct endpoint: /get_stock_price
    
    Expects POST request with JSON body: {"ticker": "AAPL"}
    Requires Authorization header with Bearer token.
    """
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers
    
    try:
        # Lazy import to avoid initialization timeout
        from auth_utils import AuthUtils, AuthError
        
        # Verify authentication
        user_info = AuthUtils.verify_auth_token(req)
        
        # Get request data
        request_data = parse_json_body(req)
        if 'ticker' not in request_data:
            response = {
                "error": "Bad Request",
                "message": "Request body must contain 'ticker' field"
            }
            return (json.dumps(response), 400, headers)
        
        ticker = request_data['ticker']
        
        # Lazy import to avoid initialization timeout
        from stock_service import StockPriceService
        
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


@https_fn.on_request(memory=options.MemoryOption.GB_1)
def generate_suggested_trades(req):
    """Generate suggested trades and store them in Firestore."""
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        expected_token = os.getenv('CLOUD_TASKS_BEARER_TOKEN')
        if not expected_token:
            response = {
                'error': 'Server configuration error',
                'message': 'CLOUD_TASKS_BEARER_TOKEN is not set'
            }
            return (json.dumps(response), 500, headers)

        auth_header = req.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            response = {
                'error': 'Unauthorized',
                'message': 'Missing bearer token'
            }
            return (json.dumps(response), 401, headers)

        token = auth_header.split('Bearer ')[1]
        if token != expected_token:
            response = {
                'error': 'Unauthorized',
                'message': 'Invalid token'
            }
            return (json.dumps(response), 401, headers)

        request_data = parse_json_body(req)
        portfolio_id = request_data.get('portfolio_id')
        user_id = request_data.get('user_id')

        if not portfolio_id or not user_id:
            response = {
                'error': 'Bad Request',
                'message': 'portfolio_id and user_id are required in request body'
            }
            return (json.dumps(response), 400, headers)

        db = firestore.Client()
        portfolio_doc = db.collection('portfolios').document(portfolio_id).get()
        if not portfolio_doc.exists:
            response = {
                'error': 'Not Found',
                'message': 'Portfolio not found'
            }
            return (json.dumps(response), 404, headers)

        portfolio_data = portfolio_doc.to_dict()
        if portfolio_data.get('userId') != user_id:
            response = {
                'error': 'Unauthorized',
                'message': 'Portfolio does not belong to user'
            }
            return (json.dumps(response), 403, headers)

        portfolio_goal = portfolio_data.get('goal') or ''
        if not portfolio_goal:
            response = {
                'error': 'Bad Request',
                'message': 'Portfolio goal is required to generate suggestions'
            }
            return (json.dumps(response), 400, headers)

        from portfolio_service import PortfolioService
        portfolio_service = PortfolioService()
        result = portfolio_service.construct_portfolio_with_trades(
            portfolio_goal, portfolio_id, user_id
        )

        count = result.get('suggested_trades_created', {}).get('count', 0)
        response = {
            'portfolio_id': portfolio_id,
            'trades_created': count,
            'timestamp': datetime.now().isoformat()
        }
        return (json.dumps(response), 200, headers)

    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': f'Failed to generate suggested trades: {str(e)}'
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request(memory=options.MemoryOption.GB_1)
def request_suggested_trades(req):
    """Queue a Cloud Task to generate suggested trades for a portfolio."""
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        request_data = parse_json_body(req)
        portfolio_id = request_data.get('portfolio_id')
        user_id = request_data.get('user_id')
        if not portfolio_id or not user_id:
            response = {
                'error': 'Bad Request',
                'message': 'portfolio_id and user_id are required in request body'
            }
            return (json.dumps(response), 400, headers)

        from google.cloud import tasks_v2

        project = os.getenv('GCP_PROJECT') or os.getenv('PROJECT_ID') or os.getenv('GCLOUD_PROJECT')
        location = os.getenv('CLOUD_TASKS_LOCATION', 'us-central1')
        queue = os.getenv('CLOUD_TASKS_QUEUE', 'portfolio-tasks')

        if not project:
            response = {
                'error': 'Server configuration error',
                'message': 'Project ID environment variable is not set'
            }
            return (json.dumps(response), 500, headers)

        token = os.getenv('CLOUD_TASKS_BEARER_TOKEN')
        if not token:
            response = {
                'error': 'Server configuration error',
                'message': 'CLOUD_TASKS_BEARER_TOKEN is not set'
            }
            return (json.dumps(response), 500, headers)

        function_base = os.getenv('CLOUD_FUNCTIONS_BASE_URL', f'https://{location}-{project}.cloudfunctions.net')
        url = f'{function_base}/generate_suggested_trades'

        payload = json.dumps({'portfolio_id': portfolio_id, 'user_id': user_id}).encode()

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(project, location, queue)

        task = {
            'http_request': {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': url,
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                'body': payload
            }
        }

        client.create_task(request={'parent': parent, 'task': task})

        response = {
            'queued': True,
            'portfolio_id': portfolio_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        return (json.dumps(response), 200, headers)

    except ValueError as e:
        response = {
            'error': 'Bad Request',
            'message': str(e)
        }
        return (json.dumps(response), 400, headers)

    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': f'Failed to create Cloud Task: {str(e)}'
        }
        return (json.dumps(response), 500, headers)




@https_fn.on_request(memory=options.MemoryOption.GB_1)
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
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        
        # Parse request body
        try:
            request_data = parse_json_body(req)
        except ValueError as e:
            response = {
                "error": "Bad Request",
                "message": str(e)
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
        
        # Lazy import to avoid initialization timeout
        from portfolio_service import PortfolioService
        
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




@https_fn.on_request(memory=options.MemoryOption.GB_1)
def get_suggested_trades(req):
    """
    Firebase function to get suggested trades for a portfolio.
    This provides a direct endpoint: /get_suggested_trades
    
    Expects GET request with query parameters:
    - portfolio_id: ID of the portfolio
    - user_id: ID of the user (for authorization)
    
    Returns list of suggested trades for the portfolio.
    """
    cors_result = handle_cors(req, ['GET'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        
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
        
        # Lazy import to avoid initialization timeout
        from portfolio_service import PortfolioService
        
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


@https_fn.on_request(memory=options.MemoryOption.GB_1)
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
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        
        # Parse request body
        try:
            request_data = parse_json_body(req)
        except ValueError as e:
            response = {
                "error": "Bad Request",
                "message": str(e)
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
        
        # Lazy import to avoid initialization timeout
        from portfolio_service import PortfolioService
        
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


@https_fn.on_request(memory=options.MemoryOption.GB_1)
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
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        
        # Parse request body
        try:
            request_data = parse_json_body(req)
        except ValueError as e:
            response = {
                "error": "Bad Request",
                "message": str(e)
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
        
        # Lazy import to avoid initialization timeout
        from portfolio_service import PortfolioService
        
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


@https_fn.on_request(memory=options.MemoryOption.GB_1)
def lookup_symbol(req):
    """Firebase function to look up a company's name for a stock ticker."""
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        from auth_utils import AuthUtils, AuthError
        from stock_service import StockPriceService

        user_info = AuthUtils.verify_auth_token(req)
        request_data = parse_json_body(req)
        if 'ticker' not in request_data:
            response = {
                "error": "Bad Request",
                "message": "Request body must contain 'ticker' field",
            }
            return (json.dumps(response), 400, headers)

        ticker = request_data['ticker']
        stock_service = StockPriceService()
        stock_data = stock_service.get_price(ticker)

        response = {
            "success": True,
            "ticker": stock_data['ticker'],
            "company_name": stock_data.get('company_name', ''),
        }
        return (json.dumps(response), 200, headers)

    except AuthError as e:
        response = {
            "error": "Authentication failed",
            "message": str(e),
        }
        return (json.dumps(response), 401, headers)

    except ValueError as e:
        response = {
            "error": "Bad Request",
            "message": str(e),
        }
        return (json.dumps(response), 400, headers)

    except Exception as e:
        response = {
            "error": "Internal Server Error",
            "message": f"Failed to lookup symbol: {str(e)}",
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request(memory=options.MemoryOption.GB_1)
def get_portfolio_advice(req):
    """Generate portfolio advice using an LLM and update the portfolio."""
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        # Verify bearer token matches environment variable
        expected_token = os.getenv('CLOUD_TASKS_BEARER_TOKEN')
        if not expected_token:
            response = {
                'error': 'Server configuration error',
                'message': 'CLOUD_TASKS_BEARER_TOKEN is not set'
            }
            return (json.dumps(response), 500, headers)

        auth_header = req.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            response = {
                'error': 'Unauthorized',
                'message': 'Missing bearer token'
            }
            return (json.dumps(response), 401, headers)

        token = auth_header.split('Bearer ')[1]
        if token != expected_token:
            response = {
                'error': 'Unauthorized',
                'message': 'Invalid token'
            }
            return (json.dumps(response), 401, headers)

        request_data = parse_json_body(req)
        portfolio_id = request_data.get('portfolio_id')
        if not portfolio_id:
            response = {
                'error': 'Bad Request',
                'message': 'portfolio_id is required in request body'
            }
            return (json.dumps(response), 400, headers)

        db = firestore.Client()

        portfolio_doc = db.collection('portfolios').document(portfolio_id).get()
        if not portfolio_doc.exists:
            response = {
                'error': 'Not Found',
                'message': 'Portfolio not found'
            }
            return (json.dumps(response), 404, headers)

        portfolio_data = portfolio_doc.to_dict()
        portfolio_goal = portfolio_data.get('goal', '')
        cash_balance = portfolio_data.get('cashBalance', 0.0)

        positions_ref = db.collection('portfolios').document(portfolio_id).collection('positions')
        position_docs = positions_ref.get()
        positions = [doc.to_dict() for doc in position_docs]

        from portfolio_service import PortfolioService
        advice_service = PortfolioService()
        advice_text = advice_service.generate_portfolio_advice(
            portfolio_goal, cash_balance, positions
        )

        portfolio_ref = db.collection('portfolios').document(portfolio_id)
        update_data = {
            'advice': advice_text,
            'updatedAt': datetime.now()
        }
        from firestore_utils import safe_firestore_update
        safe_firestore_update(portfolio_ref, update_data)

        response = {
            'portfolio_id': portfolio_id,
            'advice': advice_text,
            'timestamp': datetime.now().isoformat()
        }

        return (json.dumps(response), 200, headers)

    except ValueError as e:
        response = {
            'error': 'Bad Request',
            'message': str(e)
        }
        return (json.dumps(response), 400, headers)

    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': f'Failed to generate portfolio advice: {str(e)}'
        }
        return (json.dumps(response), 500, headers)


@https_fn.on_request(memory=options.MemoryOption.GB_1)
def request_portfolio_performance(req):
    """Queue a Cloud Task to generate portfolio performance and advice."""
    cors_result = handle_cors(req, ['POST'])
    if cors_result.must_return:
        return cors_result.result
    headers = cors_result.headers

    try:
        request_data = parse_json_body(req)
        portfolio_id = request_data.get('portfolio_id')
        if not portfolio_id:
            response = {
                'error': 'Bad Request',
                'message': 'portfolio_id is required in request body'
            }
            return (json.dumps(response), 400, headers)

        from google.cloud import tasks_v2

        project = os.getenv('GCP_PROJECT') or os.getenv('PROJECT_ID') or os.getenv('GCLOUD_PROJECT')
        location = os.getenv('CLOUD_TASKS_LOCATION', 'us-central1')
        queue = os.getenv('CLOUD_TASKS_QUEUE', 'portfolio-tasks')

        if not project:
            response = {
                'error': 'Server configuration error',
                'message': 'Project ID environment variable is not set'
            }
            return (json.dumps(response), 500, headers)

        token = os.getenv('CLOUD_TASKS_BEARER_TOKEN')
        if not token:
            response = {
                'error': 'Server configuration error',
                'message': 'CLOUD_TASKS_BEARER_TOKEN is not set'
            }
            return (json.dumps(response), 500, headers)

        function_base = os.getenv('CLOUD_FUNCTIONS_BASE_URL', f'https://{location}-{project}.cloudfunctions.net')
        url = f'{function_base}/get_portfolio_advice'

        payload = json.dumps({'portfolio_id': portfolio_id}).encode()

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(project, location, queue)

        task = {
            'http_request': {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': url,
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                'body': payload
            }
        }

        client.create_task(request={'parent': parent, 'task': task})

        response = {
            'queued': True,
            'portfolio_id': portfolio_id,
            'timestamp': datetime.now().isoformat()
        }
        return (json.dumps(response), 200, headers)

    except ValueError as e:
        response = {
            'error': 'Bad Request',
            'message': str(e)
        }
        return (json.dumps(response), 400, headers)

    except Exception as e:
        response = {
            'error': 'Internal Server Error',
            'message': f'Failed to create Cloud Task: {str(e)}'
        }
        return (json.dumps(response), 500, headers)
