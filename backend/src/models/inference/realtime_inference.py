"""
Inférence en temps réel pour l'API et les agents
"""

import logging
from typing import Dict, Any, Optional, Generator
import asyncio
from ..llm.llama import LlamaModel

logger = logging.getLogger(__name__)

class RealtimeInference:
    """
    Gestion de l'inférence en temps réel
    """
    
    def __init__(self, model_name: str = "llama3:70b"):
        """
        Initialise l'inférence en temps réel
        """
        self.model = LlamaModel(model_name)
        self._cache = {}
        self._max_cache_size = 1000
        logger.info(f"⚡ Realtime Inference - Modèle: {model_name}")
    
    def load(self):
        """Charge le modèle"""
        if not self.model.is_loaded():
            self.model.load()
    
    def generate(self, prompt: str, use_cache: bool = True, **kwargs) -> str:
        """
        Génère une réponse en temps réel
        """
        self.load()
        
        # Vérifier le cache
        cache_key = hash(prompt + str(kwargs))
        if use_cache and cache_key in self._cache:
            logger.debug(f"✅ Cache hit: {cache_key}")
            return self._cache[cache_key]
        
        # Générer la réponse
        response = self.model.generate(prompt, **kwargs)
        
        # Mettre en cache
        if use_cache:
            self._cache[cache_key] = response
            if len(self._cache) > self._max_cache_size:
                # Supprimer les plus anciennes
                keys = list(self._cache.keys())[:100]
                for key in keys:
                    del self._cache[key]
        
        return response
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming
        """
        self.load()
        
        for chunk in self.model.generate_stream(prompt, **kwargs):
            yield chunk
    
    def chat_completion(self, messages: list, **kwargs) -> str:
        """
        Complétion de chat pour l'API
        """
        self.load()
        
        # Convertir les messages en format Llama
        prompt = self._format_messages(messages)
        return self.generate(prompt, **kwargs)
    
    def chat_completion_stream(self, messages: list, **kwargs) -> Generator[str, None, None]:
        """
        Complétion de chat en streaming
        """
        self.load()
        
        prompt = self._format_messages(messages)
        for chunk in self.model.generate_stream(prompt, **kwargs):
            yield chunk
    
    def _format_messages(self, messages: list) -> str:
        """
        Formate les messages pour le modèle
        """
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"<|{role}|>\n{content}")
        
        formatted.append("<|assistant|>\n")
        return "\n".join(formatted)
    
    def clear_cache(self):
        """Vide le cache"""
        self._cache.clear()
        logger.info("🧹 Cache vidé")
    
    def get_cache_stats(self) -> Dict:
        """Statistiques du cache"""
        return {
            'size': len(self._cache),
            'max_size': self._max_cache_size,
            'hit_rate': len([k for k in self._cache if self._cache[k]]) / max(len(self._cache), 1)
        }

if __name__ == "__main__":
    # Test de l'inférence en temps réel
    inference = RealtimeInference()
    
    # Test de génération
    response = inference.generate("Bonjour, comment allez-vous ?")
    print(response)
    
    # Test de streaming
    for chunk in inference.generate_stream("Racontez-moi une histoire sur le GNL en 3 phrases."):
        print(chunk, end='', flush=True)