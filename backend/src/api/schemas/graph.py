"""
Schémas Pydantic pour les opérations sur le graphe
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class NodeResponse(BaseModel):
    """Réponse pour un nœud"""
    id: str
    labels: List[str]
    properties: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RelationshipResponse(BaseModel):
    """Réponse pour une relation"""
    source: str
    target: str
    type: str
    properties: Dict[str, Any]
    created_at: Optional[datetime] = None

class GraphQueryRequest(BaseModel):
    """Requête pour interroger le graphe"""
    query: str = Field(..., description="Requête Cypher")
    params: Optional[Dict[str, Any]] = Field(default={}, description="Paramètres de la requête")
    limit: Optional[int] = Field(default=100, ge=1, le=1000)

class GraphQueryResponse(BaseModel):
    """Réponse pour une requête graphe"""
    results: List[Dict[str, Any]]
    count: int
    execution_time_ms: float

class NodeCreateRequest(BaseModel):
    """Requête pour créer un nœud"""
    label: str = Field(..., description="Label du nœud")
    properties: Dict[str, Any] = Field(..., description="Propriétés du nœud")

class RelationshipCreateRequest(BaseModel):
    """Requête pour créer une relation"""
    source_id: str = Field(..., description="ID du nœud source")
    target_id: str = Field(..., description="ID du nœud cible")
    type: str = Field(..., description="Type de relation")
    properties: Optional[Dict[str, Any]] = Field(default={}, description="Propriétés de la relation")