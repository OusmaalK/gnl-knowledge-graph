"""
Agent de base pour tous les agents IA
Phase 3 - Classe abstraite pour les agents spécialisés
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from .tools.graph_tools import GraphTools
from .tools.llm_tools import LLMTools

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Classe abstraite de base pour tous les agents IA
    """
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
        self.context = {}
        logger.info(f"✅ {self.name} initialisé")
    
    @abstractmethod
    def execute(self, query: str, params: Optional[Dict] = None) -> str:
        pass
    
    def get_graph_data(self, equipment_id: Optional[str] = None) -> Dict:
        data = {
            'statistics': self.graph_tools.get_statistics(),
            'supply_chain': self.graph_tools.get_supply_chain(),
        }
        if equipment_id:
            data['equipment'] = self.graph_tools.get_equipment_info(equipment_id)
            data['impact'] = self.graph_tools.get_impact_analysis(equipment_id)
            data['risk'] = self.graph_tools.get_risk_score(equipment_id)
            data['incidents'] = self.graph_tools.get_incident_history(equipment_id)
        return data
    
    def close(self):
        self.graph_tools.close()
