"""
Security Utilities
Phase 3.2: User Authentication & Authorization System
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTManager:
    """JWT token management for authentication"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = 30

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise ValueError("Token creation failed")

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise ValueError("Refresh token creation failed")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        payload = self.verify_token(token)
        if not payload:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        return datetime.utcnow() > datetime.fromtimestamp(exp)

    def get_token_type(self, token: str) -> Optional[str]:
        """Get token type (access or refresh)"""
        payload = self.verify_token(token)
        if not payload:
            return None

        return payload.get("type")

    def extract_user_id(self, token: str) -> Optional[int]:
        """Extract user ID from token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        return payload.get("sub")

    def extract_email(self, token: str) -> Optional[str]:
        """Extract email from token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        return payload.get("email")


class PasswordManager:
    """Password hashing and validation"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        try:
            hashed = pwd_context.hash(password)
            return hashed
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise ValueError("Password hashing failed")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            return is_valid
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        if len(password) > 128:
            errors.append("Password must be less than 128 characters long")

        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": PasswordManager._calculate_strength(password)
        }

    @staticmethod
    def _calculate_strength(password: str) -> str:
        """Calculate password strength"""
        score = 0

        # Length bonus
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1

        # Character variety bonus
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1

        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        else:
            return "strong"


class TokenManager:
    """Token management for email verification, password reset, etc."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token for database storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token_hash(token: str, hashed_token: str) -> bool:
        """Verify token against stored hash"""
        return TokenManager.hash_token(token) == hashed_token


class SecurityUtils:
    """General security utilities"""

    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email address"""
        return email.lower().strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def mask_sensitive_data(data: str) -> str:
        """Mask sensitive data for logging"""
        if len(data) <= 4:
            return "*" * len(data)
        return data[:2] + "*" * (len(data) - 4) + data[-2:]


# Global instances
jwt_manager = JWTManager()
password_manager = PasswordManager()
token_manager = TokenManager()
security_utils = SecurityUtils()