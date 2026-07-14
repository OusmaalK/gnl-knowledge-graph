"""
Dépendances pour les agents
"""

from typing import Dict, Any
from ...agents import DiagnosticAgent, LogisticsAgent, MaintenanceAgent
from ...agents.agents.incident_agent import IncidentAgent
from ..schemas.agents import AgentType

def get_agent(agent_type: AgentType) -> Any:
    """
    Fournit un agent IA
    """
    agents = {
        AgentType.DIAGNOSTIC: DiagnosticAgent(),
        AgentType.INCIDENT: IncidentAgent(),
        AgentType.LOGISTICS: LogisticsAgent(),
        AgentType.MAINTENANCE: MaintenanceAgent()
    }
    
    return agents.get(agent_type)