"""
Workflow de base pour les agents
Phase 3 - Orchestration des workflows
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from ..tools.graph_tools import GraphTools
from ..tools.llm_tools import LLMTools

logger = logging.getLogger(__name__)

class BaseWorkflow(ABC):
    """
    Classe abstraite de base pour tous les workflows
    """
    
    def __init__(self, name: str = "BaseWorkflow"):
        self.name = name
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
        self.context = {}
        self.steps = []
        logger.info(f"✅ {self.name} initialisé")
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Exécute le workflow
        """
        pass
    
    @abstractmethod
    def get_steps(self) -> List[str]:
        """
        Retourne la liste des étapes du workflow
        """
        pass
    
    def add_step(self, step: str, description: str) -> None:
        """
        Ajoute une étape au workflow
        """
        self.steps.append({
            "step": step,
            "description": description
        })
        logger.info(f"📝 Étape ajoutée : {step}")
    
    def get_progress(self) -> str:
        """
        Retourne la progression du workflow
        """
        total = len(self.steps)
        done = len([s for s in self.steps if s.get('done', False)])
        return f"📊 Progression : {done}/{total} étapes"
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Exécute une requête dans Neo4j
        """
        return self.graph_tools.execute_query(query, params or {})
    
    def generate_response(self, question: str, context: str) -> str:
        """
        Génère une réponse à partir du contexte
        """
        return self.llm_tools.generate_response(question, context)
    
    def close(self):
        """Ferme les connexions"""
        self.graph_tools.close()