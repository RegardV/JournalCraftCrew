"""
Comprehensive Error Handling System
Phase 4: Error Handling and Logging
"""

import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class JournalPlatformException(Exception):
    """Base exception class for Journal Platform"""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        status_code: int = 500,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())
        super().__init__(self.message)

class ValidationError(JournalPlatformException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class AuthenticationError(JournalPlatformException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationError(JournalPlatformException):
    """Raised when user lacks permission"""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )

class NotFoundError(JournalPlatformException):
    """Raised when resource is not found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=status.HTTP_404_NOT_FOUND
        )

class RateLimitError(JournalPlatformException):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

class ExternalServiceError(JournalPlatformException):
    """Raised when external service fails"""

    def __init__(self, message: str, service_name: str = None):
        details = {"service": service_name} if service_name else {}
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )

class DatabaseError(JournalPlatformException):
    """Raised when database operation fails"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class FileOperationError(JournalPlatformException):
    """Raised when file operation fails"""

    def __init__(self, message: str, file_path: str = None):
        details = {"file_path": file_path} if file_path else {}
        super().__init__(
            message=message,
            error_code="FILE_OPERATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class ErrorReporter:
    """Centralized error reporting and logging"""

    @staticmethod
    def log_exception(
        request: Request = None,
        exception: Exception = None,
        user_id: str = None,
        additional_context: Dict[str, Any] = None
    ) -> str:
        """Log exception with comprehensive context"""
        error_id = str(uuid.uuid4())

        # Prepare log data
        log_data = {
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat(),
            "exception_type": exception.__class__.__name__,
            "exception_message": str(exception),
            "user_id": user_id,
            "request_method": request.method if request else None,
            "request_url": str(request.url) if request else None,
            "request_headers": dict(request.headers) if request else None,
            "client_ip": ErrorReporter._get_client_ip(request) if request else None,
            "additional_context": additional_context or {}
        }

        # Add traceback for unhandled exceptions
        if not isinstance(exception, JournalPlatformException):
            log_data["traceback"] = traceback.format_exc()

        # Log based on error severity
        if isinstance(exception, (AuthenticationError, AuthorizationError)):
            logger.warning(f"Security Exception: {log_data}")
        elif isinstance(exception, (ValidationError, NotFoundError)):
            logger.info(f"Client Error: {log_data}")
        else:
            logger.error(f"Server Error: {log_data}")

        return error_id

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client IP
        return request.client.host if request.client else "unknown"

class ErrorHandler:
    """Global error handler for FastAPI application"""

    @staticmethod
    def create_error_response(
        error_id: str,
        message: str,
        error_code: str,
        status_code: int,
        details: Dict[str, Any] = None,
        should_show_details: bool = False
    ) -> JSONResponse:
        """Create standardized error response"""

        response_content = {
            "error": {
                "message": message,
                "code": error_code,
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        # Add details in development or for specific error types
        if should_show_details and details:
            response_content["error"]["details"] = details

        return JSONResponse(
            status_code=status_code,
            content=response_content
        )

    @staticmethod
    async def handle_journal_platform_exception(
        request: Request,
        exc: JournalPlatformException
    ) -> JSONResponse:
        """Handle custom Journal Platform exceptions"""

        error_id = ErrorReporter.log_exception(
            request=request,
            exception=exc,
            additional_context=exc.details
        )

        # Show details only for validation errors in development
        should_show_details = isinstance(exc, ValidationError)

        return ErrorHandler.create_error_response(
            error_id=error_id,
            message=exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            details=exc.details,
            should_show_details=should_show_details
        )

    @staticmethod
    async def handle_validation_exception(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI validation errors"""

        # Convert validation errors to readable format
        details = {"validation_errors": []}
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            details["validation_errors"].append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })

        custom_exc = ValidationError(
            message="Request validation failed",
            details=details
        )

        error_id = ErrorReporter.log_exception(
            request=request,
            exception=custom_exc,
            additional_context=details
        )

        return ErrorHandler.create_error_response(
            error_id=error_id,
            message=custom_exc.message,
            error_code=custom_exc.error_code,
            status_code=custom_exc.status_code,
            details=details,
            should_show_details=True
        )

    @staticmethod
    async def handle_http_exception(
        request: Request,
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions"""

        custom_exc = JournalPlatformException(
            message=exc.detail,
            error_code="HTTP_ERROR",
            status_code=exc.status_code
        )

        error_id = ErrorReporter.log_exception(
            request=request,
            exception=custom_exc
        )

        return ErrorHandler.create_error_response(
            error_id=error_id,
            message=custom_exc.message,
            error_code=custom_exc.error_code,
            status_code=custom_exc.status_code
        )

    @staticmethod
    async def handle_generic_exception(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions"""

        custom_exc = JournalPlatformException(
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        error_id = ErrorReporter.log_exception(
            request=request,
            exception=exc
        )

        # Don't expose internal details in production
        return ErrorHandler.create_error_response(
            error_id=error_id,
            message=custom_exc.message,
            error_code=custom_exc.error_code,
            status_code=custom_exc.status_code
        )

def setup_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""

    app.add_exception_handler(
        JournalPlatformException,
        ErrorHandler.handle_journal_platform_exception
    )

    app.add_exception_handler(
        RequestValidationError,
        ErrorHandler.handle_validation_exception
    )

    app.add_exception_handler(
        StarletteHTTPException,
        ErrorHandler.handle_http_exception
    )

    app.add_exception_handler(
        Exception,
        ErrorHandler.handle_generic_exception
    )

    logger.info("Exception handlers registered successfully")