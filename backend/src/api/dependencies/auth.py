"""
Dépendances d'authentification
"""

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

from ...core.config import settings
from ...core.exceptions import GNLException

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security = HTTPBearer()

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Valide la clé API
    """
    if not api_key:
        raise GNLException(
            message="Clé API manquante",
            code="MISSING_API_KEY",
            status_code=401
        )
    
    if api_key != settings.API_SECRET_KEY:
        raise GNLException(
            message="Clé API invalide",
            code="INVALID_API_KEY",
            status_code=401
        )
    
    return api_key

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    Récupère l'utilisateur courant via JWT
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "exp": payload.get("exp")
        }
    except jwt.ExpiredSignatureError:
        raise GNLException(
            message="Token expiré",
            code="TOKEN_EXPIRED",
            status_code=401
        )
    except jwt.InvalidTokenError:
        raise GNLException(
            message="Token invalide",
            code="INVALID_TOKEN",
            status_code=401
        )

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")