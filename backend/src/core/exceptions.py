"""
Exceptions du projet
"""

from typing import Optional, Dict, Any

class GNLException(Exception):
    """
    Exception de base pour le projet GNL
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(GNLException):
    """Exception pour les ressources non trouvées"""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} {identifier} non trouvé",
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )

class ValidationError(GNLException):
    """Exception pour les erreurs de validation"""
    
    def __init__(self, message: str, errors: list):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": errors}
        )

class AuthenticationError(GNLException):
    """Exception pour les erreurs d'authentification"""
    
    def __init__(self, message: str = "Authentification requise"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationError(GNLException):
    """Exception pour les erreurs d'autorisation"""
    
    def __init__(self, message: str = "Accès non autorisé"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )

class ConflictError(GNLException):
    """Exception pour les conflits"""
    
    def __init__(self, message: str, resource: str):
        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            status_code=409,
            details={"resource": resource}
        )

class DatabaseError(GNLException):
    """Exception pour les erreurs de base de données"""
    
    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details={"query": query}
        )