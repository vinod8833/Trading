"""
Comprehensive Error Handling & Validation Service
Handles all API errors gracefully with user-friendly messages
"""

import logging
import json
from typing import Dict, Any, Optional, Tuple
from rest_framework import status
from rest_framework.response import Response
from decimal import Decimal

logger = logging.getLogger(__name__)


class APIError:
    """Standard API error response"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict] = None,
        user_message: Optional[str] = None
    ):
        self.message = message  # Internal message for logging
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or message  # User-friendly message
    
    def to_response(self) -> Response:
        """Convert to DRF Response"""
        return Response(
            {
                'success': False,
                'error': self.error_code,
                'message': self.user_message,
                'details': self.details,
                'timestamp': __import__('datetime').datetime.now().isoformat(),
            },
            status=self.status_code
        )
    
    def log(self):
        """Log the error"""
        logger.error(
            f"API Error [{self.error_code}]: {self.message}",
            extra={'details': self.details}
        )


class ValidationError(APIError):
    """Validation error"""
    
    def __init__(self, message: str, field: str = None, details: Dict = None):
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or ({"field": field} if field else {}),
            user_message=f"Invalid {field}: {message}" if field else message
        )


class AuthenticationError(APIError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code='AUTH_ERROR',
            status_code=status.HTTP_401_UNAUTHORIZED,
            user_message="Please log in to continue"
        )


class NotFoundError(APIError):
    """Resource not found"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            error_code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND,
            user_message=f"The requested {resource.lower()} does not exist"
        )


class DataUnavailableError(APIError):
    """Data is unavailable for analysis"""
    
    def __init__(self, reason: str = "Data unavailable"):
        super().__init__(
            message=reason,
            error_code='DATA_UNAVAILABLE',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            user_message="Market data is currently unavailable. Please try again later or use historical data."
        )


class AnalysisError(APIError):
    """Analysis generation failed"""
    
    def __init__(self, reason: str = "Analysis failed"):
        super().__init__(
            message=reason,
            error_code='ANALYSIS_ERROR',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_message="Unable to generate analysis. Please verify input data and try again."
        )


class PayloadValidator:
    """Validate request payloads"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: list) -> Tuple[bool, Optional[ValidationError]]:
        """Check if all required fields are present"""
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)
        
        if missing:
            return False, ValidationError(
                f"Missing required fields: {', '.join(missing)}",
                details={'missing_fields': missing}
            )
        
        return True, None
    
    @staticmethod
    def validate_numeric(value: Any, field_name: str, min_val: float = None, max_val: float = None) -> Tuple[bool, Optional[ValidationError]]:
        """Validate numeric field"""
        try:
            num = float(value)
            
            if min_val is not None and num < min_val:
                return False, ValidationError(
                    f"Value must be at least {min_val}",
                    field=field_name
                )
            
            if max_val is not None and num > max_val:
                return False, ValidationError(
                    f"Value must be at most {max_val}",
                    field=field_name
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, ValidationError(
                f"Must be a valid number",
                field=field_name
            )
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> Tuple[bool, Optional[ValidationError]]:
        """Validate stock symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False, ValidationError(
                "Stock symbol must be a non-empty string",
                field='stock_symbol'
            )
        
        symbol = symbol.strip().upper()
        if len(symbol) > 10:
            return False, ValidationError(
                "Stock symbol too long (max 10 characters)",
                field='stock_symbol'
            )
        
        if not symbol.isalnum():
            return False, ValidationError(
                "Stock symbol must contain only letters and numbers",
                field='stock_symbol'
            )
        
        return True, None
    
    @staticmethod
    def validate_price_array(prices: list, field_name: str = 'prices') -> Tuple[bool, Optional[ValidationError]]:
        """Validate array of prices"""
        if not prices or not isinstance(prices, list):
            return False, ValidationError(
                "Prices must be a non-empty array",
                field=field_name
            )
        
        if len(prices) < 20:
            return False, ValidationError(
                "Need at least 20 price points for analysis",
                field=field_name
            )
        
        try:
            numeric_prices = [float(p) for p in prices]
            if any(p < 0 for p in numeric_prices):
                return False, ValidationError(
                    "Prices cannot be negative",
                    field=field_name
                )
            return True, None
        except (ValueError, TypeError):
            return False, ValidationError(
                "All prices must be valid numbers",
                field=field_name
            )
    
    @staticmethod
    def validate_trading_style(style: str) -> Tuple[bool, Optional[ValidationError]]:
        """Validate trading style"""
        valid_styles = ['INTRADAY', 'SWING', 'POSITIONAL', 'LONG_TERM', 'OPTIONS', 'AI_ALGO', 'INVESTOR']
        
        if style not in valid_styles:
            return False, ValidationError(
                f"Invalid trading style. Must be one of: {', '.join(valid_styles)}",
                field='trading_style'
            )
        
        return True, None


class ResponseFormatter:
    """Format successful API responses"""
    
    @staticmethod
    def success(data: Any, message: str = "Success", status_code: int = status.HTTP_200_OK) -> Response:
        """Format successful response"""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
                'timestamp': __import__('datetime').datetime.now().isoformat(),
            },
            status=status_code
        )
    
    @staticmethod
    def paginated(items: list, total: int, page: int, page_size: int) -> Dict:
        """Format paginated response"""
        return {
            'success': True,
            'data': items,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
            },
            'timestamp': __import__('datetime').datetime.now().isoformat(),
        }


class SafeAnalysisExecutor:
    """Safely execute analysis with error handling"""
    
    @staticmethod
    def execute_analysis(func, *args, **kwargs) -> Tuple[bool, Any, Optional[APIError]]:
        """
        Execute analysis function safely
        Returns: (success: bool, result: Any, error: Optional[APIError])
        """
        try:
            result = func(*args, **kwargs)
            return True, result, None
            
        except ValueError as e:
            error = AnalysisError(f"Invalid value: {str(e)}")
            error.log()
            return False, None, error
            
        except TypeError as e:
            error = AnalysisError(f"Type error: {str(e)}")
            error.log()
            return False, None, error
            
        except KeyError as e:
            error = AnalysisError(f"Missing data: {str(e)}")
            error.log()
            return False, None, error
            
        except ZeroDivisionError as e:
            error = AnalysisError("Division by zero in calculation")
            error.log()
            return False, None, error
            
        except Exception as e:
            error = AnalysisError(f"Unexpected error: {str(e)}")
            error.log()
            return False, None, error


# Error code mapping for frontend
ERROR_MESSAGES = {
    'VALIDATION_ERROR': 'Please check your input and try again',
    'AUTH_ERROR': 'Please log in to continue',
    'NOT_FOUND': 'Resource not found',
    'DATA_UNAVAILABLE': 'Data is not available. Market may be closed. Try again later.',
    'ANALYSIS_ERROR': 'Unable to generate analysis. Please try with different inputs.',
    'NETWORK_ERROR': 'Network error. Please check your connection.',
    'RATE_LIMIT': 'Too many requests. Please wait a moment and try again.',
}


def get_user_friendly_error(error_code: str, default: str = "An error occurred") -> str:
    """Get user-friendly error message"""
    return ERROR_MESSAGES.get(error_code, default)
