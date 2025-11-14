"""
Authentication Service
Phase 3.2: User Authentication & Authorization System
Enhanced with complete email verification and token management
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, update
from fastapi import HTTPException, status

from app.models.user import User, UserSubscription
from app.models.auth_tokens import RefreshToken, LoginAttempt, SecurityEvent
from app.core.security import (
    jwt_manager,
    password_manager,
    security_utils
)
from app.core.config import get_settings
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Authentication service for user management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService(db)

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        profile_type: str = "personal_journaler"
    ) -> Dict[str, Any]:
        """Register new user"""
        try:
            # Validate email
            email = security_utils.sanitize_email(email)
            if not security_utils.validate_email(email):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid email format"
                )

            # Validate profile type
            if profile_type not in ["personal_journaler", "content_creator"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid profile type. Must be 'personal_journaler' or 'content_creator'"
                )

            # Validate password
            password_validation = password_manager.validate_password_strength(password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Password does not meet requirements",
                        "errors": password_validation["errors"]
                    }
                )

            # Check if user already exists
            existing_user = await self.db.execute(
                select(User).where(User.email == email)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )

            # Hash password using bcrypt with length handling
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                password = password_bytes.decode('utf-8', errors='ignore')
            from passlib.context import CryptContext
            pwd_context = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto",
                bcrypt__rounds=12
            )
            hashed_password = pwd_context.hash(password)

            # Create user
            db_user = User(
                email=email,
                password_hash=hashed_password,
                full_name=full_name or email.split("@")[0],
                is_active=True,
                is_verified=False,
                subscription=UserSubscription.FREE,
                profile_type=profile_type,
                library_access=True,
                preferences={
                    "theme_preference": "light",
                    "language": "en",
                    "timezone": "UTC",
                    "notification_email": True,
                    "notification_push": False,
                    "notification_marketing": False,
                    "notification_updates": True,
                    "profile_visibility": "private",
                    "share_analytics": False,
                    "allow_collaboration": True
                }
            )

            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            # Send verification email
            await self.email_service.send_verification_email(db_user)

            logger.info(f"User registered: {email}")

            return {
                "message": "User registered successfully. Please check your email to verify your account.",
                "user_id": db_user.id,
                "email": db_user.email,
                "profile_type": db_user.profile_type,
                "verification_required": True
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Registration failed due to internal error"
            )

    async def authenticate_user(
        self,
        email: str,
        password: str,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Validate email
            email = security_utils.sanitize_email(email)

            # Find user
            result = await self.db.execute(
                select(User).where(
                    and_(User.email == email, User.is_active == True)
                )
            )
            user = result.scalar_one_or_none()

            if not user:
                # Log failed login attempt
                await self._log_login_attempt(email, False, "User not found", request_ip, user_agent)
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            # Verify password using bcrypt with length handling
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            password = password_bytes.decode('utf-8', errors='ignore')

            from passlib.context import CryptContext
            pwd_context = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto",
                bcrypt__rounds=12
            )

            if not pwd_context.verify(password, user.password_hash):
                # Log failed login attempt
                await self._log_login_attempt(email, False, "Invalid password", request_ip, user_agent, user.id)
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            # Check if email is verified
            if not user.is_verified:
                await self._log_login_attempt(email, False, "Email not verified", request_ip, user_agent, user.id)
                raise HTTPException(
                    status_code=403,
                    detail="Please verify your email before logging in"
                )

            # Update last login and count
            user.update_last_login()
            await self.db.commit()

            # Create tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "subscription": user.subscription,
                "profile_type": user.profile_type,
            }

            access_token = jwt_manager.create_access_token(token_data)
            refresh_token = jwt_manager.create_refresh_token(token_data)

            # Store refresh token
            refresh_token_record = RefreshToken(
                user_id=user.id,
                token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=30),  # 30 days
                ip_address=request_ip,
                user_agent=user_agent
            )
            self.db.add(refresh_token_record)
            await self.db.commit()

            # Log successful login
            await self._log_login_attempt(email, True, None, request_ip, user_agent, user.id)

            logger.info(f"User authenticated: {email}")

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": jwt_manager.access_token_expire_minutes * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "subscription": user.subscription,
                    "profile_type": user.profile_type,
                    "library_access": user.library_access,
                    "is_verified": user.is_verified,
                    "has_openai_key": bool(user.openai_api_key)  # Show if user has configured API key
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication failed due to internal error"
            )

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            if jwt_manager.get_token_type(refresh_token) != "refresh":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token"
                )

            payload = jwt_manager.verify_token(refresh_token)
            if not payload:
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token expired or invalid"
                )

            # Get user to ensure still active
            user_id = int(payload["sub"])
            result = await self.db.execute(
                select(User).where(
                    and_(User.id == user_id, User.is_active == True)
                )
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="User not found or inactive"
                )

            # Create new access token
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "subscription": user.subscription,
                "profile_type": user.profile_type
            }

            new_access_token = jwt_manager.create_access_token(token_data)

            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": jwt_manager.access_token_expire_minutes * 60
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Token refresh failed due to internal error"
            )

    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email"""
        return await self.email_service.verify_email_token(token)

    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        return await self.email_service.send_password_reset_email(email)

    async def reset_password(
        self,
        token: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Reset password with token"""
        return await self.email_service.confirm_password_reset(token, new_password)

    async def get_current_user_from_token(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        try:
            payload = jwt_manager.verify_token(token)
            if not payload:
                return None

            user_id = int(payload["sub"])
            result = await self.db.execute(
                select(User).where(
                    and_(User.id == user_id, User.is_active == True)
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Failed to get user from token: {e}")
            return None

    async def logout_user(self, refresh_token: str) -> Dict[str, Any]:
        """Logout user by revoking refresh token"""
        try:
            # Find and revoke refresh token
            result = await self.db.execute(
                select(RefreshToken).where(RefreshToken.token == refresh_token)
            )
            token_record = result.scalar_one_or_none()

            if token_record:
                token_record.is_revoked = True
                await self.db.commit()

            return {
                "message": "Logged out successfully"
            }

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Logout failed due to internal error"
            )

    async def logout_all_sessions(self, user_id: int) -> Dict[str, Any]:
        """Logout user from all devices by revoking all refresh tokens"""
        try:
            await self.db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(is_revoked=True)
            )
            await self.db.commit()

            return {
                "message": "Logged out from all devices successfully"
            }

        except Exception as e:
            logger.error(f"Logout all sessions failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Logout failed due to internal error"
            )

    async def _log_login_attempt(
        self,
        email: str,
        success: bool,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[int] = None
    ):
        """Log login attempt for security monitoring"""
        try:
            login_attempt = LoginAttempt(
                email=email,
                success=success,
                failure_reason=failure_reason,
                ip_address=ip_address,
                user_agent=user_agent,
                user_id=user_id
            )
            self.db.add(login_attempt)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")

    async def revoke_refresh_token(self, token: str) -> Dict[str, Any]:
        """Revoke a specific refresh token"""
        try:
            result = await self.db.execute(
                select(RefreshToken).where(RefreshToken.token == token)
            )
            token_record = result.scalar_one_or_none()

            if not token_record:
                raise HTTPException(
                    status_code=404,
                    detail="Refresh token not found"
                )

            token_record.is_revoked = True
            await self.db.commit()

            return {
                "message": "Refresh token revoked successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to revoke refresh token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to revoke token"
            )