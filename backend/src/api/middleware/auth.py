"""
Middleware d'authentification
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from typing import List

from ...core.config import settings

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware d'authentification
    """
    
    def __init__(
        self,
        app,
        excluded_paths: List[str] = None
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/api/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Traite la requête
        """
        # Vérifier si le chemin est exclu
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Vérifier la clé API
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Clé API manquante"}
            )
        
        if api_key != settings.API_SECRET_KEY:
            return JSONResponse(
                status_code=401,
                content={"error": "Clé API invalide"}
            )
        
        return await call_next(request)