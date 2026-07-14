"""
Schémas Pydantic pour l'API
"""

from .graph import (
    NodeResponse,
    RelationshipResponse,
    GraphQueryRequest,
    GraphQueryResponse
)
from .agents import (
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse
)
from .responses import (
    HealthResponse,
    ErrorResponse,
    PaginatedResponse
)

__all__ = [
    'NodeResponse',
    'RelationshipResponse',
    'GraphQueryRequest',
    'GraphQueryResponse',
    'AgentRequest',
    'AgentResponse',
    'ChatRequest',
    'ChatResponse',
    'HealthResponse',
    'ErrorResponse',
    'PaginatedResponse'
]