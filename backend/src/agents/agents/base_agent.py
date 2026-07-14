"""
Agent de base pour tous les agents IA - Version enrichie
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from ..tools.graph_tools import GraphTools
from ..tools.llm_tools import LLMTools

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
        """
        Exécute la tâche principale de l'agent
        """
        pass
    
    def get_graph_data(self, equipment_id: Optional[str] = None) -> Dict:
        """
        Récupère les données du graphe
        """
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
    
    def get_graph_context(self) -> str:
        """
        Récupère le contexte du graphe pour le LLM
        """
        return self.graph_tools.get_context_for_llm()
    
    def format_context(self, data: Dict) -> str:
        """
        Formate les données en contexte textuel pour le LLM
        """
        context = []
        
        stats = data.get('statistics', {})
        if stats:
            context.append(f"📊 Statistiques du réseau GNL :")
            context.append(f"   - Total nœuds : {stats.get('total_nodes', 0)}")
            context.append(f"   - Total relations : {stats.get('total_relations', 0)}")
            context.append(f"   - Incidents : {stats.get('total_incidents', 0)}")
            context.append("")
        
        equip = data.get('equipment', {})
        if equip:
            context.append(f"🔍 Équipement analysé :")
            context.append(f"   - ID : {equip.get('id', 'N/A')}")
            context.append(f"   - Nom : {equip.get('nom', 'N/A')}")
            context.append(f"   - Type : {equip.get('type', 'N/A')}")
            context.append(f"   - Statut : {equip.get('statut', 'N/A')}")
            context.append(f"   - Incidents : {equip.get('nombre_incidents', 0)}")
            context.append("")
        
        return "\n".join(context)
    
    def generate_with_llm(self, question: str, data: Dict = None) -> str:
        """
        Génère une réponse enrichie avec le LLM
        """
        if data is None:
            data = {}
        
        # Récupérer le contexte du graphe
        graph_context = self.get_graph_context()
        
        # Ajouter les données spécifiques si disponibles
        if data.get('equipment'):
            equip = data['equipment']
            graph_context += f"\n\n📍 Équipement spécifique : {equip.get('nom', 'N/A')} ({equip.get('id', 'N/A')})"
            graph_context += f"\n   - Type : {equip.get('type', 'N/A')}"
            graph_context += f"\n   - Statut : {equip.get('statut', 'N/A')}"
            graph_context += f"\n   - Incidents : {equip.get('nombre_incidents', 0)}"
        
        if data.get('incidents'):
            graph_context += "\n\n🚨 Incidents associés :"
            for inc in data['incidents'][:5]:
                graph_context += f"\n   - {inc['id']} : {inc['description']} (Gravité: {inc['gravite']})"
        
        return self.llm_tools.enrich_with_context(question, graph_context)
    
    def generate_response(self, question: str, context: str) -> str:
        """
        Génère une réponse à partir du contexte
        """
        return self.llm_tools.generate_response(question, context)
    
    def close(self):
        """Ferme les connexions"""
        self.graph_tools.close()