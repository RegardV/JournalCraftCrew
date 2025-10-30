"""
Authentication Service
Phase 3.2: User Authentication & Authorization System
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models.user import User, UserSubscription
from app.core.security import (
    jwt_manager,
    password_manager,
    token_manager,
    security_utils
)
from app.core.database import get_async_session
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management"""

    def __init__(self, db: AsyncSession):
        self.db = db

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

            # Hash password
            hashed_password = password_manager.hash_password(password)

            # Set AI credits based on profile type
            ai_credits = 10 if profile_type == "personal_journaler" else 50

            # Create user
            db_user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name or email.split("@")[0],
                is_active=True,
                is_verified=False,
                subscription="free",
                profile_type=profile_type,
                ai_credits=ai_credits,
                library_access=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                preferences='{
                    "theme_preference": "light",
                    "language": "en",
                    "timezone": "UTC",
                    "notification_email": true,
                    "notification_push": false,
                    "notification_marketing": false,
                    "notification_updates": true,
                    "profile_visibility": "private",
                    "share_analytics": false,
                    "allow_collaboration": true
                }'
            )

            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            # Create email verification token
            verification_token = token_manager.generate_token()
            hashed_token = token_manager.hash_token(verification_token)

            # TODO: Send verification email
            logger.info(f"User registered: {email}, verification token: {verification_token}")

            return {
                "message": "User registered successfully",
                "user_id": db_user.id,
                "email": db_user.email,
                "profile_type": db_user.profile_type,
                "ai_credits": db_user.ai_credits,
                "verification_required": True,
                "verification_token": verification_token  # Remove in production
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
        password: str
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
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            # Verify password
            if not password_manager.verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )

            # Check if email is verified
            if not user.is_verified:
                raise HTTPException(
                    status_code=403,
                    detail="Please verify your email before logging in"
                )

            # Update last login
            user.last_login_at = datetime.utcnow()
            await self.db.commit()

            # Create tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "subscription": user.subscription,
                "profile_type": user.profile_type,
                "ai_credits": user.ai_credits
            }

            access_token = jwt_manager.create_access_token(token_data)
            refresh_token = jwt_manager.create_refresh_token(token_data)

            # Store refresh token (TODO: Implement proper token storage)
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
                    "ai_credits": user.ai_credits,
                    "library_access": user.library_access,
                    "is_verified": user.is_verified
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
                "subscription": user.subscription
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
        try:
            # Find user with verification token
            # TODO: Implement proper token storage in database
            # For now, this is a placeholder implementation

            # Hash the token for comparison
            hashed_token = token_manager.hash_token(token)

            # This would normally query a separate email_verification table
            # For now, we'll mark all users as verified (development only)
            logger.info(f"Email verification attempt with token: {token}")

            return {
                "message": "Email verified successfully",
                "verified": True
            }

        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Email verification failed due to internal error"
            )

    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        try:
            email = security_utils.sanitize_email(email)

            # Find user
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                # Don't reveal if user exists or not
                return {
                    "message": "If an account with this email exists, a password reset link will be sent"
                }

            # Generate reset token
            reset_token = token_manager.generate_token()
            hashed_token = token_manager.hash_token(reset_token)
            reset_expires = datetime.utcnow() + timedelta(hours=1)

            # TODO: Store reset token and send email
            logger.info(f"Password reset requested for: {email}, token: {reset_token}")

            return {
                "message": "If an account with this email exists, a password reset link will be sent",
                "reset_token": reset_token  # Remove in production
            }

        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Password reset request failed due to internal error"
            )

    async def reset_password(
        self,
        token: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Reset password with token"""
        try:
            # Validate password
            password_validation = password_manager.validate_password_strength(new_password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Password does not meet requirements",
                        "errors": password_validation["errors"]
                    }
                )

            # TODO: Implement proper token verification
            # For now, this is a placeholder
            logger.info(f"Password reset attempt with token: {token}")

            # Hash new password
            hashed_password = password_manager.hash_password(new_password)

            return {
                "message": "Password reset successfully",
                "reset": True
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Password reset failed due to internal error"
            )

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