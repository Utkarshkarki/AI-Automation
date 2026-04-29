"""
core/middleware.py — API Gateway middleware for auth, rate limiting, and logging.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from services.auth.security import decode_token

logger = logging.getLogger("api_gateway")

# Public routes that don't require authentication
PUBLIC_ROUTES = [
    "/auth/login",
    "/auth/register",
    "/health",
    "/payment/webhook",
    "/docs",
    "/openapi.json"
]

class GatewayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        
        # 1. Check if route is public
        is_public = any(path.startswith(route) for route in PUBLIC_ROUTES)
        
        # 2. Authentication Check for protected routes
        user_id = None
        if not is_public:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401, 
                    content={"detail": "Missing or invalid authentication token"}
                )
            
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if not payload or not payload.get("sub"):
                return JSONResponse(
                    status_code=401, 
                    content={"detail": "Token expired or invalid"}
                )
            user_id = payload.get("sub")
            
            # Attach user_id to request state so routes can access it
            request.state.user_id = user_id

        # 3. Request Logging & Timing
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            log_msg = f"{request.method} {path} - Status: {response.status_code} - Time: {process_time:.4f}s"
            if user_id:
                log_msg += f" - User: {user_id}"
            logger.info(log_msg)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"{request.method} {path} - Error: {str(e)} - Time: {process_time:.4f}s")
            raise
