"""
Recherche de routes alternatives
Phase 2 - Optimisation des routes
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouteFinder:
    """Trouve des routes alternatives dans le réseau GNL"""
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        
    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
    def close(self):
        if self.driver:
            self.driver.close()
    
    def find_shortest_path(self, start_id, end_id):
        """
        Trouve le chemin le plus court entre deux nœuds
        """
        query = """
        MATCH path = shortestPath(
            (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
        )
        RETURN [n in nodes(path) | n.id] as Path,
               length(path) as Distance,
               [r in relationships(path) | type(r)] as Relations
        """
        
        with self.driver.session() as session:
            result = session.run(query, start_id=start_id, end_id=end_id)
            return result.single()
    
    def find_alternative_route(self, start_id, end_id, exclude_id):
        """
        Trouve une route alternative en excluant un équipement défaillant
        """
        query = """
        MATCH path = shortestPath(
            (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
        )
        WHERE NONE(n IN nodes(path) WHERE n.id = $exclude_id)
        RETURN [n in nodes(path) | n.id] as Path,
               length(path) as Distance
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                start_id=start_id, 
                end_id=end_id, 
                exclude_id=exclude_id
            )
            return result.single()
    
    def find_all_paths(self, start_id, end_id):
        """
        Trouve tous les chemins possibles entre deux nœuds
        """
        query = """
        MATCH path = (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
        RETURN [n in nodes(path) | n.id] as Path,
               length(path) as Distance
        ORDER BY Distance ASC
        LIMIT 5
        """
        
        with self.driver.session() as session:
            result = session.run(query, start_id=start_id, end_id=end_id)
            return [record.data() for record in result]
    
    def get_network_status(self):
        """
        État du réseau (santé des pipelines)
        """
        query = """
        MATCH (p:Pipeline)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(p)
        RETURN p.id as Pipeline,
               p.statut as Statut,
               count(i) as Incidents
        ORDER BY Incidents DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def run_analysis(self):
        """Exécute l'analyse des routes"""
        self.connect()
        
        logger.info("\n" + "="*60)
        logger.info("🗺️ ANALYSE DES ROUTES - RÉSEAU GNL")
        logger.info("="*60)
        
        # 1. Chemin le plus court
        logger.info("\n1️⃣ Chemin le plus court Terminal → Client :")
        path = self.find_shortest_path("TERM-001", "CLIENT-001")
        if path:
            logger.info(f"   Chemin : {' → '.join(path['Path'])}")
            logger.info(f"   Distance : {path['Distance']}")
            logger.info(f"   Relations : {path['Relations']}")
        
        # 2. Route alternative (sans PIPE-001)
        logger.info("\n2️⃣ Route alternative (sans PIPE-001) :")
        alt = self.find_alternative_route("TERM-001", "CLIENT-001", "PIPE-001")
        if alt:
            logger.info(f"   Chemin alternatif : {' → '.join(alt['Path'])}")
            logger.info(f"   Distance : {alt['Distance']}")
        else:
            logger.info("   ⚠️ Aucune route alternative trouvée")
        
        # 3. État du réseau
        logger.info("\n3️⃣ État du réseau :")
        status = self.get_network_status()
        for item in status:
            logger.info(f"   {item['Pipeline']} : statut={item['Statut']}, incidents={item['Incidents']}")
        
        self.close()

if __name__ == "__main__":
    router = RouteFinder()
    router.run_analysis()