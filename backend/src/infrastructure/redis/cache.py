"""
Gestionnaire de cache pour le projet GNL
"""

import logging
from typing import Any, Optional, Callable, Dict
from functools import wraps
import hashlib
import json
from .client import RedisClient

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestionnaire de cache avec décorateurs et helpers
    """
    
    def __init__(self, redis_client: Optional[RedisClient] = None, default_ttl: int = 3600):
        """
        Initialise le gestionnaire de cache
        
        Args:
            redis_client: Instance de RedisClient
            default_ttl: Durée de vie par défaut (secondes)
        """
        self.client = redis_client or RedisClient()
        self.default_ttl = default_ttl
        self._connect()
    
    def _connect(self) -> bool:
        """Établit la connexion à Redis"""
        return self.client.connect()
    
    def close(self):
        """Ferme la connexion"""
        self.client.close()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Génère une clé de cache unique
        
        Args:
            prefix: Préfixe de la clé
            *args, **kwargs: Arguments pour générer la clé
        """
        key_parts = [prefix]
        
        if args:
            key_parts.extend([str(arg) for arg in args])
        
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])
        
        raw_key = ":".join(key_parts)
        
        # Créer un hash pour éviter les clés trop longues
        if len(raw_key) > 200:
            raw_key = f"{prefix}:{hashlib.md5(raw_key.encode()).hexdigest()[:16]}"
        
        return raw_key
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Récupère la valeur du cache ou l'exécute et la stocke
        
        Args:
            key: Clé de cache
            func: Fonction à exécuter si la clé n'existe pas
            ttl: Durée de vie
        """
        # Vérifier le cache
        cached = self.client.get(key)
        if cached is not None:
            logger.debug(f"✅ Cache HIT : {key}")
            return cached
        
        # Exécuter la fonction
        logger.debug(f"💾 Cache MISS : {key}")
        result = func()
        
        # Stocker dans le cache
        if result is not None:
            self.client.set(key, result, ttl or self.default_ttl)
        
        return result
    
    def cache_result(self, ttl: Optional[int] = None, prefix: str = "cache"):
        """
        Décorateur pour mettre en cache le résultat d'une fonction
        
        Args:
            ttl: Durée de vie (secondes)
            prefix: Préfixe de la clé
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Générer la clé
                key = self._generate_key(prefix, func.__name__, *args, **kwargs)
                return self.get_or_set(key, lambda: func(*args, **kwargs), ttl)
            return wrapper
        return decorator
    
    def invalidate(self, pattern: str) -> int:
        """
        Invalide les clés correspondant à un pattern
        
        Args:
            pattern: Pattern de clés à supprimer
        """
        keys = self.client.keys(pattern)
        if keys:
            count = self.client.delete(*keys)
            logger.info(f"🗑️ {count} clés invalidées (pattern: {pattern})")
            return count
        return 0
    
    def invalidate_prefix(self, prefix: str) -> int:
        """
        Invalide toutes les clés avec un préfixe donné
        """
        return self.invalidate(f"{prefix}:*")
    
    def clear_all(self) -> bool:
        """
        Vide tout le cache
        """
        return self.client.clear_all()
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état du cache
        """
        return self.client.health_check()
    
    # Helpers pour différents types de données
    
    def cache_query_result(self, query_key: str, query_func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Cache spécifique pour les requêtes
        """
        return self.get_or_set(f"query:{query_key}", query_func, ttl)
    
    def cache_graph_query(self, cypher: str, params: Dict, query_func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Cache pour les requêtes Neo4j
        """
        key = self._generate_key("graph", cypher, json.dumps(params, sort_keys=True))
        return self.get_or_set(key, query_func, ttl)
    
    def cache_agent_response(self, agent_name: str, question: str, response_func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Cache pour les réponses des agents
        """
        key = self._generate_key("agent", agent_name, question)
        return self.get_or_set(key, response_func, ttl)

if __name__ == "__main__":
    # Test du cache
    cache = CacheManager()
    
    # Test avec décorateur
    @cache.cache_result(ttl=60, prefix="test")
    def expensive_function(name: str):
        print(f"💪 Exécution coûteuse pour {name}")
        return f"Résultat pour {name}"
    
    # Première exécution (cache miss)
    print(expensive_function("GNL"))
    print(expensive_function("GNL"))  # Cache hit
    
    # Test d'invalidation
    cache.invalidate_prefix("test")
    print(expensive_function("GNL"))  # Cache miss
    
    cache.close()