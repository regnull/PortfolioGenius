"""
Firestore Utilities
Helper functions for safely working with Firestore to prevent undefined value errors
"""

from typing import Dict, Any, List, Union
from datetime import datetime


def sanitize_for_firestore(data: Dict[str, Any], for_response: bool = False) -> Dict[str, Any]:
    """
    Sanitize data dictionary to ensure no undefined/None values are sent to Firestore.
    
    Args:
        data: Dictionary to sanitize
        for_response: If True, convert datetime objects to ISO strings for API responses
    
    Returns:
        Dict: Sanitized dictionary safe for Firestore
    """
    sanitized = {}
    
    for key, value in data.items():
        if value is None:
            # Skip None values entirely rather than converting them
            continue
        elif isinstance(value, str):
            # Clean and validate string values
            cleaned_str = value.strip()
            if cleaned_str:  # Only add non-empty strings
                sanitized[key] = cleaned_str
        elif isinstance(value, (int, float)):
            # Ensure numeric values are properly typed
            if isinstance(value, float):
                sanitized[key] = float(value)
            else:
                sanitized[key] = int(value)
        elif isinstance(value, bool):
            sanitized[key] = bool(value)
        elif isinstance(value, datetime):
            if for_response:
                # Convert datetime to ISO string for API responses
                sanitized[key] = value.isoformat()
            else:
                sanitized[key] = value
        elif hasattr(value, 'isoformat'):
            # Handle Firestore datetime objects (DatetimeWithNanoseconds)
            if for_response:
                sanitized[key] = value.isoformat()
            else:
                sanitized[key] = value
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            nested_sanitized = sanitize_for_firestore(value, for_response)
            if nested_sanitized:  # Only add if not empty
                sanitized[key] = nested_sanitized
        elif isinstance(value, list):
            # Filter out None values from lists and sanitize items
            sanitized_list = []
            for item in value:
                if item is not None:
                    if isinstance(item, dict):
                        item_sanitized = sanitize_for_firestore(item, for_response)
                        if item_sanitized:
                            sanitized_list.append(item_sanitized)
                    elif isinstance(item, datetime):
                        if for_response:
                            sanitized_list.append(item.isoformat())
                        else:
                            sanitized_list.append(item)
                    elif hasattr(item, 'isoformat'):
                        # Handle Firestore datetime objects in lists
                        if for_response:
                            sanitized_list.append(item.isoformat())
                        else:
                            sanitized_list.append(item)
                    else:
                        sanitized_list.append(item)
            if sanitized_list:  # Only add if not empty
                sanitized[key] = sanitized_list
        else:
            # For any other type, include as-is
            sanitized[key] = value
    
    return sanitized


def safe_firestore_add(collection_ref, data: Dict[str, Any]) -> str:
    """
    Safely add a document to Firestore with proper data sanitization.
    
    Args:
        collection_ref: Firestore collection reference
        data: Document data to add
    
    Returns:
        str: Document ID of the added document
    """
    try:
        # Sanitize the data before adding to Firestore
        sanitized_data = sanitize_for_firestore(data, for_response=False)
        
        # Add the document
        doc_ref = collection_ref.add(sanitized_data)
        
        return doc_ref[1].id  # Return the document ID
        
    except Exception as e:
        raise RuntimeError(f"Error adding document to Firestore: {e}")


def safe_firestore_update(doc_ref, data: Dict[str, Any]) -> None:
    """
    Safely update a Firestore document with proper data sanitization.
    
    Args:
        doc_ref: Firestore document reference
        data: Data to update
    """
    try:
        # Sanitize the data before updating in Firestore
        sanitized_data = sanitize_for_firestore(data, for_response=False)
        
        # Update the document
        doc_ref.update(sanitized_data)
        
    except Exception as e:
        raise RuntimeError(f"Error updating document in Firestore: {e}")


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present and not empty.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
    
    Raises:
        ValueError: If any required field is missing or empty
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    if empty_fields:
        raise ValueError(f"Empty required fields: {', '.join(empty_fields)}")


def clean_string_field(value: Any, default: str = "") -> str:
    """
    Clean and validate a string field.
    
    Args:
        value: Value to clean
        default: Default value if cleaning fails
    
    Returns:
        str: Cleaned string value
    """
    if value is None:
        return default
    
    if isinstance(value, str):
        return value.strip()
    
    # Convert other types to string
    try:
        return str(value).strip()
    except:
        return default


def clean_numeric_field(value: Any, default: Union[int, float] = 0) -> Union[int, float]:
    """
    Clean and validate a numeric field.
    
    Args:
        value: Value to clean
        default: Default value if cleaning fails
    
    Returns:
        Union[int, float]: Cleaned numeric value
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return value
    
    # Try to convert string to number
    if isinstance(value, str):
        try:
            # Remove common currency symbols and formatting
            cleaned = value.replace('$', '').replace(',', '').strip()
            if '.' in cleaned:
                return float(cleaned)
            else:
                return int(cleaned)
        except ValueError:
            return default
    
    return default 