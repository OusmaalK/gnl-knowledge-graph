"""
Modèle Llama via Ollama
"""

import requests
import json
from typing import Dict, List, Any, Optional, Generator
import logging
import os
from .base import BaseLLM

logger = logging.getLogger(__name__)

class LlamaModel(BaseLLM):
    """
    Modèle Llama via l'API Ollama
    """
    
    def __init__(self, model_name: str = "llama3:70b", api_url: Optional[str] = None):
        """
        Initialise le modèle Llama
        
        Args:
            model_name: Nom du modèle
            api_url: URL de l'API Ollama
        """
        super().__init__(model_name)
        self.api_url = api_url or os.getenv('LLM_API_URL', 'http://localhost:11434')
        self._is_loaded = False
        logger.info(f"🔗 API Ollama : {self.api_url}")
    
    def load(self) -> bool:
        """
        Vérifie que le modèle est disponible
        """
        try:
            # Vérifier la disponibilité du modèle
            response = requests.post(
                f"{self.api_url}/api/show",
                json={"name": self.model_name}
            )
            
            if response.status_code == 200:
                self._is_loaded = True
                logger.info(f"✅ Modèle {self.model_name} chargé")
                return True
            else:
                logger.error(f"❌ Modèle {self.model_name} non disponible")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement : {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse
        """
        if not self._is_loaded:
            if not self.load():
                return "❌ Modèle non disponible"
        
        try:
            params = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.get('temperature', 0.7)),
                    "top_p": kwargs.get('top_p', self.config.get('top_p', 0.9)),
                    "top_k": kwargs.get('top_k', self.config.get('top_k', 40)),
                    "num_predict": kwargs.get('max_tokens', 2048)
                }
            }
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=params,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"❌ Erreur API : {response.status_code}")
                return f"❌ Erreur : {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erreur génération : {e}")
            return f"❌ Erreur : {str(e)}"
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming
        """
        if not self._is_loaded:
            if not self.load():
                yield "❌ Modèle non disponible"
                return
        
        try:
            params = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.get('temperature', 0.7)),
                    "top_p": kwargs.get('top_p', self.config.get('top_p', 0.9))
                }
            }
            
            with requests.post(
                f"{self.api_url}/api/generate",
                json=params,
                stream=True,
                timeout=120
            ) as response:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ Erreur streaming : {e}")
            yield f"❌ Erreur : {str(e)}"
    
    def embed(self, text: str) -> List[float]:
        """
        Génère un embedding avec le modèle
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('embedding', [])
            else:
                logger.error(f"❌ Erreur embedding : {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur embedding : {e}")
            return []
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        Génère une réponse en mode chat
        """
        if not self._is_loaded:
            if not self.load():
                return "❌ Modèle non disponible"
        
        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.get('temperature', 0.7))
                }
            }
            
            response = requests.post(
                f"{self.api_url}/api/chat",
                json=params,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                return f"❌ Erreur : {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erreur chat : {e}")
            return f"❌ Erreur : {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """
        Liste les modèles disponibles
        """
        try:
            response = requests.get(f"{self.api_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
            return []

if __name__ == "__main__":
    # Test du modèle
    model = LlamaModel()
    if model.load():
        response = model.generate("Bonjour, que pouvez-vous me dire sur le GNL ?")
        print(response)