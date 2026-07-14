"""
Client Redis - Gestion du cache et de la mémoire
"""

import os
import logging
import json
from typing import Any, Optional, Dict, List, Union
import redis
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    """
    Client Redis pour la gestion du cache
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, password: Optional[str] = None):
        """
        Initialise le client Redis
        
        Args:
            host: Hôte Redis
            port: Port Redis
            password: Mot de passe Redis
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.client: Optional[Redis] = None
        self._default_ttl = 3600  # 1 heure par défaut
        logger.info(f"🔗 Redis : {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Redis
        """
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Vérifier la connexion
            self.client.ping()
            logger.info("✅ Connecté à Redis")
            return True
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"❌ Erreur de connexion Redis : {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue Redis : {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("🔒 Connexion Redis fermée")
    
    def ping(self) -> bool:
        """
        Vérifie si Redis est accessible
        """
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stocke une valeur en cache
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl: Durée de vie en secondes
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # Sérialiser les objets Python
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
            
            ttl = ttl or self._default_ttl
            self.client.setex(key, ttl, value)
            logger.debug(f"✅ Cache SET : {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur SET {key} : {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Tenter de désérialiser JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"❌ Erreur GET {key} : {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Supprime une clé du cache
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            self.client.delete(key)
            logger.debug(f"🗑️ Cache DELETE : {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur DELETE {key} : {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Erreur EXISTS {key} : {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Modifie la durée de vie d'une clé
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            return self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"❌ Erreur EXPIRE {key} : {e}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Incrémente une valeur
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"❌ Erreur INCR {key} : {e}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Décrémente une valeur
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"❌ Erreur DECR {key} : {e}")
            return None
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Liste les clés correspondant à un pattern
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"❌ Erreur KEYS {pattern} : {e}")
            return []
    
    def clear_all(self) -> bool:
        """
        Vide tout le cache (⚠️ DANGER)
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            self.client.flushdb()
            logger.info("🗑️ Cache Redis vidé")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur FLUSHDB : {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Récupère les statistiques Redis
        """
        if not self.client:
            if not self.connect():
                return {}
        
        try:
            info = self.client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_days': info.get('uptime_in_days', 0)
            }
        except Exception as e:
            logger.error(f"❌ Erreur stats : {e}")
            return {}
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état de Redis
        """
        try:
            if not self.client:
                if not self.connect():
                    return {"status": "unhealthy", "error": "Connection failed"}
            
            return {
                "status": "healthy",
                "host": self.host,
                "port": self.port,
                "ping": self.ping(),
                "stats": self.get_stats()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test du client
    client = RedisClient()
    print("Health :", client.health_check())
    
    # Test cache
    client.set("test", {"message": "Hello GNL!"}, 60)
    value = client.get("test")
    print("Cache test :", value)
    
    client.close()