"""
Classe de base pour les outils
Phase 3 - Fondation des outils d'analyse
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Classe abstraite de base pour tous les outils
    """
    
    def __init__(self, name: str = "BaseTool"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.logger.info(f"✅ {name} initialisé")
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Exécute l'outil avec les paramètres donnés
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Retourne la description de l'outil
        """
        pass
    
    def validate_params(self, params: Dict, required: List[str]) -> bool:
        """
        Valide les paramètres requis
        """
        missing = [p for p in required if p not in params]
        if missing:
            self.logger.error(f"Paramètres manquants : {missing}")
            return False
        return True
    
    def format_result(self, data: Any) -> str:
        """
        Formate le résultat pour l'affichage
        """
        return str(data)