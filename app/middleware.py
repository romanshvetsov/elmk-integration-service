import time
import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import asyncio
from typing import Dict, Tuple
import time

from .config import settings

logger = structlog.get_logger()


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside window
        client_requests[:] = [req_time for req_time in client_requests 
                            if now - req_time < self.window_seconds]
        
        if len(client_requests) >= self.max_requests:
            return False
        
        client_requests.append(now)
        return True


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
                client_ip=client_ip
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time,
                client_ip=client_ip
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app, max_requests: int, window_seconds: int):
        super().__init__(app)
        self.rate_limiter = RateLimiter(max_requests, window_seconds)
    
    async def dispatch(self, request: Request, call_next):
        # Extract client identifier (IP for now, could be user ID in auth context)
        client_id = request.client.host if request.client else "unknown"
        
        if not self.rate_limiter.is_allowed(client_id):
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                max_requests=self.rate_limiter.max_requests,
                window_seconds=self.rate_limiter.window_seconds
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Limit: {self.rate_limiter.max_requests} per {self.rate_limiter.window_seconds} seconds"
                }
            )
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "Unhandled exception",
                error=str(e),
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host if request.client else "unknown"
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred"
                }
            )