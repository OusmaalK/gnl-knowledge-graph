"""
Classe de base pour les modèles LLM
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generator
import logging
import yaml
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseLLM(ABC):
    """
    Classe abstraite de base pour tous les modèles LLM
    """
    
    def __init__(self, model_name: str = "llama3:70b", config_path: Optional[str] = None):
        """
        Initialise le modèle LLM
        
        Args:
            model_name: Nom du modèle
            config_path: Chemin du fichier de configuration
        """
        self.model_name = model_name
        self.config = self._load_config(config_path)
        self._is_loaded = False
        logger.info(f"🤖 Modèle : {model_name}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Charge la configuration du modèle
        """
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                'config.yaml'
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # Récupérer la config du modèle spécifique
                model_config = config.get('models', {}).get(self.model_name, {})
                return model_config
        except Exception as e:
            logger.warning(f"⚠️ Config non trouvée, utilisation des valeurs par défaut : {e}")
            return {
                'temperature': 0.7,
                'top_p': 0.9,
                'context_length': 4096
            }
    
    @abstractmethod
    def load(self) -> bool:
        """
        Charge le modèle en mémoire
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse à partir d'un prompt
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming
        """
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Génère un embedding pour un texte
        """
        pass
    
    def is_loaded(self) -> bool:
        """Vérifie si le modèle est chargé"""
        return self._is_loaded
    
    def get_config(self) -> Dict:
        """Retourne la configuration du modèle"""
        return self.config
    
    def create_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """
        Crée un prompt structuré
        """
        return f"""<|system|>
{system_prompt}
<|user|>
{user_prompt}
<|assistant|>
"""
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Génère des réponses pour un lot de prompts
        """
        responses = []
        for prompt in prompts:
            try:
                response = self.generate(prompt, **kwargs)
                responses.append(response)
            except Exception as e:
                logger.error(f"❌ Erreur génération : {e}")
                responses.append("")
        return responses