"""
Opérations CRUD sur le graphe Neo4j
Phase 3 - Création, lecture, mise à jour, suppression
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraphCRUD:
    """
    Opérations CRUD sur le graphe Neo4j
    """
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None

    def connect(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self.driver

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Exécute une requête"""
        driver = self.connect()
        with driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    # ============================================================
    # CREATE
    # ============================================================

    def create_node(self, label: str, properties: Dict) -> Dict:
        """
        Crée un nœud
        """
        if 'id' not in properties:
            logger.error("❌ Propriété 'id' requise")
            return {"success": False, "error": "id requis"}
        
        query = f"""
        CREATE (n:{label} $properties)
        SET n.updated_at = datetime()
        RETURN n
        """
        results = self.execute_query(query, {"properties": properties})
        
        if results:
            logger.info(f"✅ Nœud créé : {label} ({properties['id']})")
            return {"success": True, "data": results[0]}
        return {"success": False, "error": "Création échouée"}

    def create_relationship(self, rel_type: str, source_id: str, target_id: str, 
                           properties: Optional[Dict] = None) -> Dict:
        """
        Crée une relation
        """
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} $properties]->(target)
        SET r.updated_at = datetime()
        RETURN r
        """
        results = self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties or {}
        })
        
        if results:
            logger.info(f"✅ Relation créée : {source_id} -[{rel_type}]-> {target_id}")
            return {"success": True, "data": results[0]}
        return {"success": False, "error": "Création échouée"}

    # ============================================================
    # READ
    # ============================================================

    def get_node(self, node_id: str) -> Optional[Dict]:
        """
        Récupère un nœud par son ID
        """
        query = """
        MATCH (n {id: $id})
        RETURN n, labels(n) as labels
        """
        results = self.execute_query(query, {"id": node_id})
        return results[0] if results else None

    def get_nodes_by_label(self, label: str, limit: int = 100) -> List[Dict]:
        """
        Récupère tous les nœuds d'un label
        """
        query = f"""
        MATCH (n:{label})
        RETURN n, labels(n) as labels
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_relationships(self, node_id: str, direction: str = 'BOTH') -> List[Dict]:
        """
        Récupère les relations d'un nœud
        """
        if direction == 'OUTGOING':
            rel_pattern = '-[r]->'
        elif direction == 'INCOMING':
            rel_pattern = '<-[r]-'
        else:
            rel_pattern = '-[r]-'
        
        query = f"""
        MATCH (n {{id: $id}}){rel_pattern}(m)
        RETURN n.id as source, type(r) as type, m.id as target, properties(r) as properties
        """
        return self.execute_query(query, {"id": node_id})

    # ============================================================
    # UPDATE
    # ============================================================

    def update_node(self, node_id: str, properties: Dict) -> Dict:
        """
        Met à jour un nœud
        """
        query = """
        MATCH (n {id: $id})
        SET n += $properties,
            n.updated_at = datetime()
        RETURN n
        """
        results = self.execute_query(query, {"id": node_id, "properties": properties})
        
        if results:
            logger.info(f"✅ Nœud mis à jour : {node_id}")
            return {"success": True, "data": results[0]}
        return {"success": False, "error": "Mise à jour échouée"}

    # ============================================================
    # DELETE
    # ============================================================

    def delete_node(self, node_id: str) -> Dict:
        """
        Supprime un nœud
        """
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        results = self.execute_query(query, {"id": node_id})
        
        if results and results[0].get('deleted', 0) > 0:
            logger.info(f"🗑️ Nœud supprimé : {node_id}")
            return {"success": True}
        return {"success": False, "error": "Suppression échouée"}

    def delete_relationship(self, source_id: str, target_id: str, rel_type: str) -> Dict:
        """
        Supprime une relation
        """
        query = f"""
        MATCH (source {{id: $source_id}})-[r:{rel_type}]->(target {{id: $target_id}})
        DELETE r
        RETURN count(r) as deleted
        """
        results = self.execute_query(query, {"source_id": source_id, "target_id": target_id})
        
        if results and results[0].get('deleted', 0) > 0:
            logger.info(f"🗑️ Relation supprimée : {source_id} -[{rel_type}]-> {target_id}")
            return {"success": True}
        return {"success": False, "error": "Suppression échouée"}