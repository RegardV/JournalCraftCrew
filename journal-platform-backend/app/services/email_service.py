"""
Email Service
Phase 3.2: Email Service for Authentication
Handles sending verification emails, password resets, and notifications
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from fastapi import HTTPException, status
import secrets
import logging

from app.models.user import User
from app.models.auth_tokens import EmailVerification, PasswordReset, SecurityEvent
from app.core.config import get_settings
from app.core.security import security_utils

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Email service for authentication and notifications"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_verification_email(
        self,
        user: User,
        request_client: Optional[str] = None,
        request_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email verification email"""
        try:
            # Generate secure token
            token = secrets.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry

            # Clean up any existing verification tokens for this user
            await self.db.execute(
                delete(EmailVerification).where(EmailVerification.user_id == user.id)
            )

            # Store verification token
            verification = EmailVerification(
                user_id=user.id,
                token=token,
                email=user.email,
                expires_at=expires_at
            )
            self.db.add(verification)

            # Log security event
            security_event = SecurityEvent(
                user_id=user.id,
                event_type="verification_email_sent",
                description=f"Email verification sent to {user.email}",
                ip_address=request_ip,
                user_agent=request_client,
                metadata=f'{{"token": "{token[:8]}..."}}'  # Only log partial token
            )
            self.db.add(security_event)

            await self.db.commit()

            # Send email (mock implementation for now)
            await self._send_email(
                to_email=user.email,
                subject="Verify your Journal Craft Crew account",
                template="verification_email",
                variables={
                    "user_name": user.full_name or user.email.split("@")[0],
                    "verification_url": f"{settings.FRONTEND_URL}/verify-email?token={token}",
                    "expiry_hours": 24
                }
            )

            logger.info(f"Verification email sent to {user.email}")

            return {
                "message": "Verification email sent successfully",
                "email": user.email,
                "expires_at": expires_at.isoformat()
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to send verification email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email"
            )

    async def verify_email_token(self, token: str) -> Dict[str, Any]:
        """Verify email using token"""
        try:
            # Find verification token
            result = await self.db.execute(
                select(EmailVerification).where(
                    and_(
                        EmailVerification.token == token,
                        EmailVerification.is_used == False
                    )
                )
            )
            verification = result.scalar_one_or_none()

            if not verification:
                await self._log_security_event(
                    None, "verification_failed",
                    f"Invalid verification token used: {token[:8]}...",
                    severity="warning"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired verification token"
                )

            if verification.is_expired():
                await self._log_security_event(
                    verification.user_id, "verification_failed",
                    f"Expired verification token used: {token[:8]}...",
                    severity="warning"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Verification token has expired"
                )

            # Get user
            user_result = await self.db.execute(
                select(User).where(User.id == verification.user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Mark token as used
            verification.is_used = True

            # Mark user as verified
            user.is_verified = True
            user.verification_token = None  # Clear any old token

            # Log security event
            await self._log_security_event(
                user.id, "email_verified",
                f"Email verified: {user.email}"
            )

            await self.db.commit()

            # Send welcome email
            await self._send_email(
                to_email=user.email,
                subject="Welcome to Journal Craft Crew!",
                template="welcome_email",
                variables={
                    "user_name": user.full_name or user.email.split("@")[0],
                    "login_url": f"{settings.FRONTEND_URL}/login"
                }
            )

            logger.info(f"Email verified for user: {user.email}")

            return {
                "message": "Email verified successfully",
                "email": user.email,
                "verified": True
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Email verification failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Email verification failed"
            )

    async def send_password_reset_email(
        self,
        email: str,
        request_client: Optional[str] = None,
        request_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            # Find user
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            # Always return success to prevent email enumeration
            if not user:
                logger.info(f"Password reset requested for non-existent email: {email}")
                return {
                    "message": "If an account with this email exists, a password reset link will be sent"
                }

            # Generate secure token
            token = secrets.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

            # Clean up any existing reset tokens for this user
            await self.db.execute(
                delete(PasswordReset).where(PasswordReset.user_id == user.id)
            )

            # Store reset token
            password_reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
                ip_address=request_ip,
                user_agent=request_client
            )
            self.db.add(password_reset)

            # Log security event
            await self._log_security_event(
                user.id, "password_reset_requested",
                f"Password reset requested for {user.email}",
                ip_address=request_ip,
                user_agent=request_client,
                severity="warning"
            )

            await self.db.commit()

            # Send email
            await self._send_email(
                to_email=user.email,
                subject="Reset your Journal Craft Crew password",
                template="password_reset_email",
                variables={
                    "user_name": user.full_name or user.email.split("@")[0],
                    "reset_url": f"{settings.FRONTEND_URL}/reset-password?token={token}",
                    "expiry_hours": 1
                }
            )

            logger.info(f"Password reset email sent to {user.email}")

            return {
                "message": "If an account with this email exists, a password reset link will be sent",
                "expires_at": expires_at.isoformat()
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to send password reset email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send password reset email"
            )

    async def verify_password_reset_token(self, token: str) -> Dict[str, Any]:
        """Verify password reset token"""
        try:
            # Find reset token
            result = await self.db.execute(
                select(PasswordReset).where(
                    and_(
                        PasswordReset.token == token,
                        PasswordReset.is_used == False
                    )
                )
            )
            password_reset = result.scalar_one_or_none()

            if not password_reset:
                await self._log_security_event(
                    None, "password_reset_failed",
                    f"Invalid password reset token used: {token[:8]}...",
                    severity="warning"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired reset token"
                )

            if password_reset.is_expired():
                await self._log_security_event(
                    None, "password_reset_failed",
                    f"Expired password reset token used: {token[:8]}...",
                    severity="warning"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Reset token has expired"
                )

            return {
                "message": "Reset token is valid",
                "user_id": password_reset.user_id,
                "valid": True
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password reset token verification failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Token verification failed"
            )

    async def confirm_password_reset(
        self,
        token: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Confirm password reset with new password"""
        try:
            # Verify token first
            token_check = await self.verify_password_reset_token(token)
            user_id = token_check["user_id"]

            # Get user
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Update password
            # Hash password using bcrypt with proper length handling
            password_bytes = new_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                new_password = password_bytes.decode('utf-8', errors='ignore')

            from passlib.context import CryptContext
            pwd_context = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto",
                bcrypt__rounds=12
            )
            user.password_hash = pwd_context.hash(new_password)

            # Mark reset token as used
            password_reset_result = await self.db.execute(
                select(PasswordReset).where(PasswordReset.token == token)
            )
            password_reset = password_reset_result.scalar_one_or_none()
            if password_reset:
                password_reset.is_used = True

            # Clear any old reset tokens
            user.reset_password_token = None
            user.reset_password_expires = None

            # Log security event
            await self._log_security_event(
                user.id, "password_reset_completed",
                "Password was reset successfully",
                severity="warning"
            )

            await self.db.commit()

            # Send confirmation email
            await self._send_email(
                to_email=user.email,
                subject="Your Journal Craft Crew password has been reset",
                template="password_reset_confirmation_email",
                variables={
                    "user_name": user.full_name or user.email.split("@")[0],
                    "login_url": f"{settings.FRONTEND_URL}/login"
                }
            )

            logger.info(f"Password reset completed for user: {user.email}")

            return {
                "message": "Password reset successfully",
                "reset": True
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password reset confirmation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Password reset failed"
            )

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        template: str,
        variables: Dict[str, Any]
    ):
        """Send email (mock implementation)"""
        # In production, this would integrate with an email service like SendGrid, AWS SES, etc.
        logger.info(f"MOCK EMAIL - To: {to_email}, Subject: {subject}, Template: {template}")
        logger.info(f"Email variables: {variables}")

        # Simulate email sending delay
        await asyncio.sleep(0.1)

    async def _log_security_event(
        self,
        user_id: Optional[int],
        event_type: str,
        description: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: str = "info",
        metadata: Optional[str] = None
    ):
        """Log security events for audit trail"""
        try:
            security_event = SecurityEvent(
                user_id=user_id,
                event_type=event_type,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                severity=severity,
                metadata=metadata
            )
            self.db.add(security_event)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")