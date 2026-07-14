"""
Schémas de réponse communs
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class HealthResponse(BaseModel):
    """Réponse de health check"""
    status: str = Field(..., description="Statut du service")
    version: str = Field(..., description="Version de l'API")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Optional[Dict[str, bool]] = Field(default={}, description="Statut des services")

class ErrorResponse(BaseModel):
    """Réponse d'erreur"""
    error: str = Field(..., description="Message d'erreur")
    code: Optional[str] = Field(None, description="Code d'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails de l'erreur")
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel, Generic[T]):
    """Réponse paginée"""
    items: List[T] = Field(..., description="Liste des éléments")
    total: int = Field(..., description="Nombre total d'éléments")
    page: int = Field(1, description="Page actuelle")
    per_page: int = Field(20, description="Nombre d'éléments par page")
    total_pages: int = Field(..., description="Nombre total de pages")

class SuccessResponse(BaseModel):
    """Réponse de succès"""
    success: bool = Field(True, description="Succès de l'opération")
    message: Optional[str] = Field(None, description="Message d'information")
    data: Optional[Any] = Field(None, description="Données retournées")