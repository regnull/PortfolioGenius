import json
from dataclasses import dataclass
from typing import List, Optional, Tuple
from flask import Request


@dataclass
class CORSResult:
    """Return object for :func:`handle_cors`."""

    must_return: bool
    headers: dict
    result: Optional[Tuple[str, int, dict]] = None


def handle_cors(req: Request, allowed_methods: List[str]) -> CORSResult:
    """Handle CORS preflight and method validation for HTTP functions.

    Args:
        req: Incoming Flask request object.
        allowed_methods: List of allowed HTTP methods (e.g. ["POST"])

    Returns:
        :class:`CORSResult` instance describing how the caller should proceed.
    """
    methods_str = ', '.join(allowed_methods)

    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': f'{methods_str}, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return CORSResult(True, headers, ('', 204, headers))

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': f'{methods_str}, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

    if req.method not in allowed_methods:
        response = {
            'error': 'Method Not Allowed',
            'message': f"Only {', '.join(allowed_methods)} requests are supported"
        }
        return CORSResult(True, headers, (json.dumps(response), 405, headers))

    return CORSResult(False, headers)


def parse_json_body(req: Request) -> dict:
    """Parse and validate JSON body from a request."""
    try:
        data = req.get_json()
        if not data:
            raise ValueError('Request body must be valid JSON')
        return data
    except Exception as e:
        raise ValueError(f"Invalid JSON in request body: {str(e)}")
