"""
Schémas Pydantic pour les agents
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum

class AgentType(str, Enum):
    """Types d'agents disponibles"""
    DIAGNOSTIC = "diagnostic"
    LOGISTICS = "logistics"
    MAINTENANCE = "maintenance"
    INCIDENT = "incident"

class ChatRequest(BaseModel):
    """Requête de chat avec un agent"""
    question: str = Field(..., description="Question posée à l'agent")
    agent_type: AgentType = Field(..., description="Type d'agent à utiliser")
    equipment_id: Optional[str] = Field(None, description="ID de l'équipement concerné")
    incident_id: Optional[str] = Field(None, description="ID de l'incident concerné")
    start_id: Optional[str] = Field(None, description="ID du nœud de départ")
    end_id: Optional[str] = Field(None, description="ID du nœud d'arrivée")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexte supplémentaire")

class ChatResponse(BaseModel):
    """Réponse du chat"""
    response: str = Field(..., description="Réponse de l'agent")
    agent_type: str = Field(..., description="Type d'agent utilisé")
    execution_time_ms: float = Field(..., description="Temps d'exécution en ms")
    sources: Optional[List[str]] = Field(default=[], description="Sources utilisées")

class AgentRequest(BaseModel):
    """Requête générique pour un agent"""
    action: str = Field(..., description="Action à exécuter")
    params: Optional[Dict[str, Any]] = Field(default={}, description="Paramètres de l'action")

class AgentResponse(BaseModel):
    """Réponse générique d'un agent"""
    result: Any = Field(..., description="Résultat de l'action")
    success: bool = Field(True, description="Succès de l'opération")
    message: Optional[str] = Field(None, description="Message d'information")
    errors: Optional[List[str]] = Field(default=[], description="Liste des erreurs")

class DiagnosticRequest(BaseModel):
    """Requête de diagnostic"""
    incident_id: str = Field(..., description="ID de l'incident à diagnostiquer")

class RouteRequest(BaseModel):
    """Requête de route"""
    start_id: str = Field(..., description="ID du nœud de départ")
    end_id: str = Field(..., description="ID du nœud d'arrivée")
    exclude_id: Optional[str] = Field(None, description="ID du nœud à exclure")

class RiskRequest(BaseModel):
    """Requête de risque"""
    equipment_id: str = Field(..., description="ID de l'équipement")