"""
Security Middleware for Journal Platform Backend
Phase 4: Security Hardening
"""

import time
import asyncio
from typing import Dict, Optional, List
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Max requests per period
        self.period = period  # Time period in seconds
        self.clients: Dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with rate limiting"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old entries for this client
        client_requests = self.clients[client_ip]
        while client_requests and client_requests[0] <= current_time - self.period:
            client_requests.popleft()

        # Check if rate limit exceeded
        if len(client_requests) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        client_requests.append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - len(client_requests)))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
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

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Comprehensive production security headers middleware"""

    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,  # 1 year
        include_subdomains: bool = True,
        preload: bool = True,
        report_to: str = None,
        exclude_paths: List[str] = None
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains
        self.preload = preload
        self.report_to = report_to
        self.exclude_paths = exclude_paths or ['/health', '/metrics', '/docs', '/openapi.json']

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and add comprehensive security headers"""
        response = await call_next(request)

        # Skip security headers for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return response

        # Generate nonce for CSP if needed
        nonce = self._generate_nonce() if self._needs_nonce(request.url.path) else None

        # Apply comprehensive security headers
        self._apply_security_headers(response, request, nonce)

        return response

    def _generate_nonce(self) -> str:
        """Generate cryptographically secure nonce for CSP"""
        import secrets
        return secrets.token_urlsafe(16)

    def _needs_nonce(self, path: str) -> bool:
        """Determine if CSP nonce is needed for this path"""
        nonce_required_paths = ["/", "/dashboard", "/projects", "/ai-workflow", "/settings"]
        return any(path.startswith(p) for p in nonce_required_paths)

    def _apply_security_headers(self, response: Response, request: Request, nonce: str = None):
        """Apply comprehensive production security headers"""

        # 1. Content Security Policy (CSP) - Production-hardened with nonce support
        csp_directives = [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}'" if nonce else "script-src 'self'",
            "style-src 'self' fonts.googleapis.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' fonts.gstatic.com data:",
            "connect-src 'self' ws: wss: https:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-src 'none'",
            "object-src 'none'",
            "media-src 'self' blob:",
            "manifest-src 'self'",
            "worker-src 'self' blob:",
        ]

        if self.report_to:
            csp_directives.append(f"report-to {self.report_to}")
            csp_directives.append(f"report-uri {self.report_to}")

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 2. X-Frame-Options (prevent clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # 3. X-Content-Type-Options (prevent MIME sniffing)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. X-XSS-Protection (legacy XSS protection for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Referrer Policy (enhanced privacy)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Permissions Policy (comprehensive feature restrictions)
        permissions_policy = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=(self)",
            "encrypted-media=(self)",
            "fullscreen=(self)",
            "picture-in-picture=(self)",
            "web-share=(self)",
            "sync-xhr=(self)",
            "oversized-images=(self)",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_policy)

        # 7. Strict-Transport-Security (HSTS) - HTTPS only
        if request.url.scheme == "https" and not request.url.hostname == "localhost":
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        # 8. Cross-Origin Embedder Policy (COEP)
        response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"

        # 9. Cross-Origin Opener Policy (COOP)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # 10. Cross-Origin Resource Policy (CORP)
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # 11. Cache Control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        # 12. Remove all server information headers
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        if "X-AspNet-Version" in response.headers:
            del response.headers["X-AspNet-Version"]
        if "X-AspNetMvc-Version" in response.headers:
            del response.headers["X-AspNetMvc-Version"]

        # 13. Add nonce to response if generated (for frontend usage)
        if nonce:
            response.headers["X-CSP-Nonce"] = nonce

        # 14. Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["X-Download-Options"] = "noopen"

        # 15. Clear Site Data on logout for sensitive pages
        if request.url.path in ["/api/auth/logout", "/api/auth/register"]:
            response.headers["Clear-Site-Data"] = "\"cache\", \"cookies\", \"storage\", \"executionContexts\""

def setup_cors_middleware(app) -> None:
    """Configure CORS middleware with proper security settings"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",   # Production build
            "http://localhost:5173",   # Development server
            "http://localhost:5174",   # Development server (alternate port)
            "https://yourdomain.com"   # Production domain
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
    )

async def setup_security_middleware(app) -> None:
    """Setup all security middleware"""
    # Add rate limiting (100 requests per minute per IP)
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    logger.info("Security middleware configured successfully")