"""
Client Neo4j - Gestion de la connexion et des opérations
"""

from neo4j import GraphDatabase, Result, Transaction
from typing import Dict, List, Any, Optional, Callable
import os
import logging
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jClient:
    """
    Client Neo4j pour les opérations sur le graphe
    """
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialise le client Neo4j
        
        Args:
            uri: URI de connexion (ex: bolt://localhost:7687)
            user: Nom d'utilisateur
            password: Mot de passe
        """
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD')
        self.driver = None
        
        if not self.password:
            logger.warning("⚠️ Mot de passe Neo4j non défini dans .env")
        
        logger.info(f"🔗 URI Neo4j : {self.uri}")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Neo4j
        """
        try:
            if not self.password:
                raise ValueError("Mot de passe Neo4j non défini")
            
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Vérifier la connexion
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connecté à Neo4j")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Neo4j : {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("🔒 Connexion Neo4j fermée")
    
    @contextmanager
    def session(self):
        """
        Context manager pour les sessions Neo4j
        """
        if not self.driver:
            if not self.connect():
                raise RuntimeError("Impossible de se connecter à Neo4j")
        
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()
    
    @contextmanager
    def transaction(self):
        """
        Context manager pour les transactions Neo4j
        """
        with self.session() as session:
            tx = session.begin_transaction()
            try:
                yield tx
                tx.commit()
            except Exception as e:
                tx.rollback()
                logger.error(f"❌ Transaction annulée : {e}")
                raise
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Exécute une requête Cypher
        
        Args:
            query: Requête Cypher
            parameters: Paramètres de la requête
            
        Returns:
            Liste des résultats
        """
        with self.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Exécute une requête d'écriture Cypher
        """
        with self.transaction() as tx:
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_batch(self, queries: List[tuple]) -> List[List[Dict]]:
        """
        Exécute un lot de requêtes en une seule transaction
        
        Args:
            queries: Liste de tuples (query, parameters)
            
        Returns:
            Liste des résultats pour chaque requête
        """
        results = []
        with self.transaction() as tx:
            for query, params in queries:
                result = tx.run(query, params or {})
                results.append([record.data() for record in result])
        return results
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état de la connexion
        """
        try:
            result = self.execute_query("RETURN 1 as test")
            return {
                "status": "healthy",
                "uri": self.uri,
                "connected": True,
                "test": result[0].get('test') if result else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "uri": self.uri,
                "connected": False,
                "error": str(e)
            }
    
    def get_version(self) -> str:
        """
        Récupère la version de Neo4j
        """
        result = self.execute_query("CALL dbms.components() YIELD name, versions RETURN name, versions")
        if result:
            return f"{result[0]['name']} {result[0]['versions'][0]}"
        return "Inconnue"
    
    def create_index(self, label: str, property_name: str) -> bool:
        """
        Crée un index sur une propriété
        """
        query = f"""
        CREATE INDEX idx_{label}_{property_name} IF NOT EXISTS
        FOR (n:{label}) ON (n.{property_name})
        """
        try:
            self.execute_query(query)
            logger.info(f"✅ Index créé : {label}.{property_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur création index : {e}")
            return False

if __name__ == "__main__":
    # Test du client
    client = Neo4jClient()
    if client.connect():
        print("Version :", client.get_version())
        print("Health :", client.health_check())
        client.close()