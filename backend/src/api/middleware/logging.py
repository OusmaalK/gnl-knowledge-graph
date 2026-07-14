"""
Middleware de logging
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid
from typing import Dict

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour logger les requêtes
    """
    
    def __init__(self, app, logger_name: str = "api.access"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
    
    async def dispatch(self, request: Request, call_next):
        """
        Traite la requête avec logging
        """
        # Générer un ID de requête
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Log de la requête
        start_time = time.time()
        
        self.logger.info(
            f"Request {request_id}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Traiter la requête
        try:
            response = await call_next(request)
            
            # Log de la réponse
            duration = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"Response {request_id}",
                extra={
                    "status": response.status_code,
                    "duration_ms": f"{duration:.2f}"
                }
            )
            
            # Ajouter l'ID de requête dans les headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            self.logger.error(
                f"Error {request_id}",
                extra={
                    "error": str(e)
                }
            )
            raise