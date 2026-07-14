"""
Indexeur Neo4j pour le chargement des données
Phase 1/3 - Indexation et gestion des données dans Neo4j
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional
import csv
import json

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jIndexer:
    """
    Indexeur pour charger et gérer les données dans Neo4j
    """
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        logger.info(f"🔗 URI Neo4j : {self.uri}")

    def connect(self):
        """Établit la connexion à Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("✅ Connecté à Neo4j")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion : {e}")
            return False

    def close(self):
        """Ferme la connexion à Neo4j"""
        if self.driver:
            self.driver.close()
            logger.info("🔒 Connexion fermée")

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Exécute une requête Cypher"""
        if not self.driver:
            if not self.connect():
                return []
        
        with self.driver.session() as session:
            try:
                result = session.run(query, params or {})
                records = [record.data() for record in result]
                logger.info(f"✅ Requête exécutée : {len(records)} enregistrements")
                return records
            except Exception as e:
                logger.error(f"❌ Erreur d'exécution : {e}")
                return []

    # ============================================================
    # INDEXATION
    # ============================================================

    def index_node(self, node_type: str, properties: Dict) -> Dict:
        """
        Indexe un nœud dans Neo4j
        """
        # S'assurer que l'ID est présent
        if 'id' not in properties:
            logger.error("❌ Propriété 'id' requise")
            return {"success": False, "error": "id requis"}
        
        query = f"""
        MERGE (n:{node_type} {{id: $id}})
        SET n += $properties,
            n.updated_at = datetime()
        RETURN n
        """
        
        result = self.execute_query(query, {
            "id": properties['id'],
            "properties": properties
        })
        
        if result:
            logger.info(f"✅ Nœud {node_type} ({properties['id']}) indexé")
            return {"success": True, "data": result[0]}
        else:
            return {"success": False, "error": "Erreur d'indexation"}

    def index_relationship(self, rel_type: str, source_id: str, target_id: str, properties: Optional[Dict] = None) -> Dict:
        """
        Indexe une relation dans Neo4j
        """
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        SET r += $properties,
            r.updated_at = datetime()
        RETURN r
        """
        
        result = self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties or {}
        })
        
        if result:
            logger.info(f"✅ Relation {rel_type} créée : {source_id} → {target_id}")
            return {"success": True, "data": result[0]}
        else:
            return {"success": False, "error": "Erreur de création"}

    def index_batch_nodes(self, node_type: str, nodes: List[Dict]) -> Dict:
        """
        Indexe un lot de nœuds en une seule transaction
        """
        if not nodes:
            return {"success": False, "error": "Aucun nœud à indexer"}
        
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{node_type} {{id: node.id}})
        SET n += node.properties,
            n.updated_at = datetime()
        RETURN count(n) as created
        """
        
        result = self.execute_query(query, {"nodes": nodes})
        
        if result:
            count = result[0].get('created', 0)
            logger.info(f"✅ {count} nœuds {node_type} indexés")
            return {"success": True, "count": count}
        else:
            return {"success": False, "error": "Erreur d'indexation"}

    # ============================================================
    # IMPORTATION CSV
    # ============================================================

    def import_csv(self, filepath: str, node_type: str, id_column: str, mapping: Optional[Dict] = None) -> Dict:
        """
        Importe un fichier CSV vers Neo4j
        """
        if not os.path.exists(filepath):
            return {"success": False, "error": f"Fichier non trouvé : {filepath}"}
        
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            nodes = []
            
            for row in reader:
                # Appliquer le mapping si fourni
                if mapping:
                    mapped = {}
                    for target, source in mapping.items():
                        mapped[target] = row.get(source, '')
                else:
                    mapped = row
                
                # S'assurer que l'ID est présent
                if id_column not in mapped or not mapped[id_column]:
                    logger.warning(f"⚠️ Ligne ignorée : ID manquant")
                    continue
                
                nodes.append({
                    "id": mapped[id_column],
                    "properties": mapped
                })
            
            return self.index_batch_nodes(node_type, nodes)

    # ============================================================
    # IMPORTATION JSON
    # ============================================================

    def import_json(self, filepath: str, node_type: str, id_key: str = 'id') -> Dict:
        """
        Importe un fichier JSON vers Neo4j
        """
        if not os.path.exists(filepath):
            return {"success": False, "error": f"Fichier non trouvé : {filepath}"}
        
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            data = json.load(file)
            items = data if isinstance(data, list) else data.get('items', [])
            
            nodes = []
            for item in items:
                if id_key not in item or not item[id_key]:
                    logger.warning(f"⚠️ Élément ignoré : ID manquant")
                    continue
                
                nodes.append({
                    "id": item[id_key],
                    "properties": item
                })
            
            return self.index_batch_nodes(node_type, nodes)

    # ============================================================
    # CRÉATION DES INDEX
    # ============================================================

    def create_indexes(self):
        """
        Crée les indexes pour optimiser les performances
        """
        indexes = [
            "CREATE INDEX idx_fournisseur_id IF NOT EXISTS FOR (n:Fournisseur) ON (n.id)",
            "CREATE INDEX idx_terminal_id IF NOT EXISTS FOR (n:Terminal) ON (n.id)",
            "CREATE INDEX idx_pipeline_id IF NOT EXISTS FOR (n:Pipeline) ON (n.id)",
            "CREATE INDEX idx_client_id IF NOT EXISTS FOR (n:Client) ON (n.id)",
            "CREATE INDEX idx_incident_id IF NOT EXISTS FOR (n:Incident) ON (n.id)",
            "CREATE INDEX idx_equipment_id IF NOT EXISTS FOR (n:Equipement) ON (n.id)",
        ]
        
        if not self.connect():
            return {"success": False, "error": "Connexion impossible"}
        
        try:
            with self.driver.session() as session:
                for query in indexes:
                    session.run(query)
                    logger.info(f"✅ Index créé : {query.split('ON')[1].strip()}")
            return {"success": True}
        except Exception as e:
            logger.error(f"❌ Erreur création indexes : {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.close()

    # ============================================================
    # CLEANUP
    # ============================================================

    def clear_database(self):
        """
        Supprime tous les nœuds et relations (⚠️ DANGER)
        """
        if not self.connect():
            return {"success": False, "error": "Connexion impossible"}
        
        try:
            with self.driver.session() as session:
                session.run("MATCH ()-[r]-() DELETE r")
                session.run("MATCH (n) DELETE n")
                logger.info("🗑️ Base de données nettoyée")
            return {"success": True}
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage : {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.close()


if __name__ == "__main__":
    # Test de l'indexeur
    indexer = Neo4jIndexer()
    indexer.create_indexes()