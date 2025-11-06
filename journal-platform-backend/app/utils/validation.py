"""
Input Validation Utilities
Phase 4: Security Hardening
"""

import re
import html
from typing import Any, Optional, List
from pydantic import validator, Field
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security-focused input validation utilities"""

    # Common attack patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
    ]

    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bor\s+\d+\s*=\s*\d+|\band\s+\d+\s*=\s*\d+)",
        r"(\bEXEC\b|\bEXECUTE\b)",
    ]

    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent XSS and injection attacks"""
        if not input_string:
            return ""

        # Check length
        if len(input_string) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input exceeds maximum length of {max_length} characters"
            )

        # HTML escape
        sanitized = html.escape(input_string)

        # Remove dangerous patterns
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Potential XSS attack detected: {input_string[:50]}...")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )

        return sanitized

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format with additional security checks"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False

        # Additional security checks
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '(', ')', ';', '\\', '/']
        if any(char in email for char in dangerous_chars):
            return False

        return True

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, List[str]]:
        """Validate password strength and return feedback"""
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        if len(password) > 128:
            errors.append("Password cannot exceed 128 characters")

        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Check for common patterns
        common_patterns = [
            r'password', r'123456', r'qwerty', r'admin', r'letmein',
            r'welcome', r'monkey', r'1234567890', r'abc123'
        ]

        for pattern in common_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                errors.append("Password contains common patterns that are not secure")
                break

        return len(errors) == 0, errors

    @staticmethod
    def validate_file_upload(filename: str, file_size: int, allowed_extensions: List[str]) -> bool:
        """Validate uploaded files for security"""
        # Check file extension
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''

        if file_extension not in allowed_extensions:
            logger.warning(f"Invalid file extension attempted: {file_extension}")
            return False

        # Check for dangerous characters in filename
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in filename for char in dangerous_chars):
            logger.warning(f"Dangerous filename detected: {filename}")
            return False

        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes")
            return False

        return True

    @staticmethod
    def sanitize_html_content(content: str, allowed_tags: List[str] = None) -> str:
        """Basic HTML sanitization for user-generated content"""
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']

        # Remove all HTML tags except allowed ones
        content = html.escape(content)

        # Re-allow specific tags (basic implementation)
        for tag in allowed_tags:
            content = content.replace(f'&lt;{tag}&gt;', f'<{tag}>')
            content = content.replace(f'&lt;/{tag}&gt;', f'</{tag}>')

        return content

    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_string.lower()))

    @staticmethod
    def check_sql_injection(input_string: str) -> bool:
        """Check for potential SQL injection attempts"""
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {input_string[:50]}...")
                return True
        return False

# Pydantic validators for common fields
def validate_string_field(value: str, field_name: str, max_length: int = 255, required: bool = True) -> str:
    """Common string field validation"""
    if value is None:
        if required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} is required"
            )
        return ""

    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be a string"
        )

    if len(value.strip()) == 0 and required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be empty"
        )

    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot exceed {max_length} characters"
        )

    # Check for SQL injection
    if SecurityValidator.check_sql_injection(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected"
        )

    return SecurityValidator.sanitize_string(value.strip(), max_length)