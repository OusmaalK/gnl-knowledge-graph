"""
Driver Neo4j - Configuration avancée et optimisation
"""

from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import time

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jDriver:
    """
    Driver Neo4j avec configuration avancée
    """
    
    _instance = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jDriver, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            self.user = os.getenv('NEO4J_USER', 'neo4j')
            self.password = os.getenv('NEO4J_PASSWORD')
            self._max_retries = 3
            self._retry_delay = 1
            logger.info(f"🔗 URI Neo4j : {self.uri}")
    
    def get_driver(self) -> Driver:
        """
        Retourne le driver Neo4j (Singleton)
        """
        if self._driver is None:
            self._connect()
        return self._driver
    
    def _connect(self) -> bool:
        """
        Établit la connexion avec retry
        """
        for attempt in range(self._max_retries):
            try:
                if not self.password:
                    raise ValueError("Mot de passe Neo4j non défini")
                
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60
                )
                
                # Vérifier la connexion
                with self._driver.session() as session:
                    session.run("RETURN 1")
                
                logger.info(f"✅ Driver Neo4j initialisé (tentative {attempt + 1})")
                return True
                
            except (ServiceUnavailable, AuthError) as e:
                logger.warning(f"⚠️ Tentative {attempt + 1}/{self._max_retries} échouée : {e}")
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    logger.error(f"❌ Échec connexion Neo4j après {self._max_retries} tentatives")
                    raise
            except Exception as e:
                logger.error(f"❌ Erreur inattendue : {e}")
                raise
        
        return False
    
    def close(self):
        """Ferme le driver"""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("🔒 Driver Neo4j fermé")
    
    def session(self) -> Session:
        """
        Retourne une session Neo4j
        """
        driver = self.get_driver()
        return driver.session()
    
    def transaction(self) -> Transaction:
        """
        Retourne une transaction Neo4j
        """
        session = self.session()
        return session.begin_transaction()
    
    @staticmethod
    def reset():
        """
        Réinitialise le driver (utile pour les tests)
        """
        if Neo4jDriver._driver:
            Neo4jDriver._driver.close()
            Neo4jDriver._driver = None
        Neo4jDriver._instance = None
        logger.info("🔄 Driver Neo4j réinitialisé")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état du driver
        """
        try:
            driver = self.get_driver()
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
            return {
                "status": "healthy",
                "uri": self.uri,
                "connected": True,
                "test": record.get('test') if record else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "uri": self.uri,
                "connected": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test du driver
    driver = Neo4jDriver()
    print("Health :", driver.health_check())
    driver.close()