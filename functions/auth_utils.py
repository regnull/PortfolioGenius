import firebase_admin
from firebase_admin import auth, credentials
from flask import Request
from typing import Optional, Dict
import json


class AuthError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthUtils:
    """Utility class for Firebase authentication."""
    
    @staticmethod
    def init_firebase():
        """Initialize Firebase Admin SDK if not already initialized."""
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
    
    @staticmethod
    def verify_auth_token(request: Request) -> Dict[str, any]:
        """
        Verify Firebase auth token from request headers.
        
        Args:
            request: Flask request object
            
        Returns:
            Dictionary containing user information
            
        Raises:
            AuthError: If authentication fails
        """
        AuthUtils.init_firebase()
        
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthError("Authorization header is required")
        
        # Extract token from "Bearer <token>" format
        if not auth_header.startswith('Bearer '):
            raise AuthError("Authorization header must start with 'Bearer '")
        
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify the token
            decoded_token = auth.verify_id_token(token)
            
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'provider': decoded_token.get('firebase', {}).get('sign_in_provider'),
                'auth_time': decoded_token.get('auth_time'),
                'exp': decoded_token.get('exp')
            }
            
        except Exception as e:
            raise AuthError(f"Invalid or expired token: {str(e)}")
    
    @staticmethod
    def require_auth(func):
        """
        Decorator to require authentication for a function.
        
        Usage:
            @AuthUtils.require_auth
            def my_function(request, user_info):
                # user_info contains authenticated user data
                pass
        """
        def wrapper(request: Request):
            try:
                user_info = AuthUtils.verify_auth_token(request)
                return func(request, user_info)
            except AuthError as e:
                return json.dumps({
                    "error": "Authentication failed",
                    "message": str(e)
                }), 401, {'Content-Type': 'application/json'}
            except Exception as e:
                return json.dumps({
                    "error": "Internal server error",
                    "message": "Authentication verification failed"
                }), 500, {'Content-Type': 'application/json'}
        
        return wrapper