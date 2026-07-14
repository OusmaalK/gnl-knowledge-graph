"""
Requêtes de base du graphe GNL
Phase 2 - Fondations des requêtes
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseQueries:
    """
    Classe de base contenant les requêtes fondamentales
    pour l'analyse du réseau GNL.
    """
    
    def __init__(self):
        """Initialise la connexion à Neo4j"""
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
        """
        Exécute une requête Cypher et retourne les résultats
        
        Args:
            query: Requête Cypher à exécuter
            params: Paramètres de la requête (optionnel)
            
        Returns:
            Liste des résultats sous forme de dictionnaires
        """
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
    # REQUÊTES DE BASE
    # ============================================================

    def get_all_nodes(self, limit: int = 50) -> List[Dict]:
        """Retourne tous les nœuds du graphe"""
        query = """
        MATCH (n)
        RETURN n, labels(n) as labels
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_all_relationships(self, limit: int = 50) -> List[Dict]:
        """Retourne toutes les relations du graphe"""
        query = """
        MATCH (n)-[r]->(m)
        RETURN n.id as source, 
               type(r) as relation, 
               m.id as target,
               properties(r) as properties
        LIMIT $limit
        """
        return self.execute_query(query, {"limit": limit})

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Retourne tous les nœuds d'un type donné"""
        query = f"""
        MATCH (n:{node_type})
        RETURN n, labels(n) as labels
        """
        return self.execute_query(query)

    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """Retourne un nœud par son ID"""
        query = """
        MATCH (n {id: $node_id})
        RETURN n, labels(n) as labels
        """
        results = self.execute_query(query, {"node_id": node_id})
        return results[0] if results else None

    def get_relationships_by_type(self, rel_type: str) -> List[Dict]:
        """Retourne toutes les relations d'un type donné"""
        query = f"""
        MATCH (n)-[r:{rel_type}]->(m)
        RETURN n.id as source, 
               labels(n) as source_type,
               type(r) as relation, 
               m.id as target,
               labels(m) as target_type,
               properties(r) as properties
        """
        return self.execute_query(query)

    def get_neighbors(self, node_id: str) -> List[Dict]:
        """Retourne tous les voisins d'un nœud"""
        query = """
        MATCH (n {id: $node_id})-[r]-(neighbor)
        RETURN neighbor.id as neighbor_id,
               labels(neighbor) as neighbor_type,
               type(r) as relation,
               n.id as source_id
        """
        return self.execute_query(query, {"node_id": node_id})

    def get_node_degree(self, node_id: str) -> Dict:
        """Retourne le degré d'un nœud (nombre de relations)"""
        query = """
        MATCH (n {id: $node_id})
        OPTIONAL MATCH (n)-[r]-()
        RETURN n.id as id,
               count(r) as degree,
               labels(n) as type
        """
        results = self.execute_query(query, {"node_id": node_id})
        return results[0] if results else {"id": node_id, "degree": 0}

    def get_node_count(self) -> int:
        """Retourne le nombre total de nœuds"""
        query = """
        MATCH (n)
        RETURN count(n) as total
        """
        results = self.execute_query(query)
        return results[0]['total'] if results else 0

    def get_relationship_count(self) -> int:
        """Retourne le nombre total de relations"""
        query = """
        MATCH ()-[r]->()
        RETURN count(r) as total
        """
        results = self.execute_query(query)
        return results[0]['total'] if results else 0

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques complètes du graphe
        """
        stats = {
            'total_nodes': self.get_node_count(),
            'total_relationships': self.get_relationship_count(),
            'node_types': {},
            'relationship_types': {}
        }
        
        # Compter les nœuds par type
        query = """
        MATCH (n)
        RETURN labels(n)[0] as type, count(n) as count
        ORDER BY count DESC
        """
        results = self.execute_query(query)
        for record in results:
            stats['node_types'][record['type']] = record['count']
        
        # Compter les relations par type
        query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(r) as count
        ORDER BY count DESC
        """
        results = self.execute_query(query)
        for record in results:
            stats['relationship_types'][record['type']] = record['count']
        
        return stats

    def get_supply_chain(self) -> List[Dict]:
        """
        Retourne la chaîne d'approvisionnement complète
        """
        query = """
        MATCH path = (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)
        OPTIONAL MATCH (p)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (p)-[:DEPEND_DE]->(comp:Compresseur)
        RETURN 
            f.id as fournisseur_id,
            f.nom as fournisseur,
            t.id as terminal_id,
            t.nom as terminal,
            p.id as pipeline_id,
            p.nom as pipeline,
            p.statut as pipeline_statut,
            collect(DISTINCT c.nom) as clients,
            comp.nom as compresseur
        ORDER BY f.nom
        """
        return self.execute_query(query)

    def print_statistics(self):
        """Affiche les statistiques du graphe de manière lisible"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 STATISTIQUES DU GRAPHE GNL")
        print("="*60)
        print(f"\n📌 Total nœuds : {stats['total_nodes']}")
        print(f"📌 Total relations : {stats['total_relationships']}")
        
        print("\n🏷️  NŒUDS PAR TYPE :")
        for type_name, count in stats['node_types'].items():
            print(f"   {type_name:15} : {count}")
        
        print("\n🔗 RELATIONS PAR TYPE :")
        for type_name, count in stats['relationship_types'].items():
            print(f"   {type_name:15} : {count}")
        print("\n" + "="*60)

    def run_all_basic_queries(self):
        """Exécute toutes les requêtes de base pour validation"""
        if not self.connect():
            logger.error("❌ Impossible de se connecter à Neo4j")
            return
        
        try:
            logger.info("\n" + "="*60)
            logger.info("🔍 EXÉCUTION DES REQUÊTES DE BASE")
            logger.info("="*60)
            
            # Statistiques
            self.print_statistics()
            
            # Chaîne d'approvisionnement
            logger.info("\n📦 CHAÎNE D'APPROVISIONNEMENT :")
            chain = self.get_supply_chain()
            for item in chain:
                logger.info(f"   {item['fournisseur']} → {item['terminal']} → {item['pipeline']}")
                if item['clients']:
                    logger.info(f"      Clients : {', '.join(item['clients'])}")
            
            # Nœuds par type (exemple : Fournisseurs)
            logger.info("\n🏷️  FOURNISSEURS :")
            fournisseurs = self.get_nodes_by_type('Fournisseur')
            for item in fournisseurs:
                node = item.get('n', {})
                logger.info(f"   - {node.get('nom', 'N/A')} ({node.get('id', 'N/A')})")
            
            logger.info("\n✅ Toutes les requêtes de base exécutées avec succès !")
            
        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
        finally:
            self.close()


if __name__ == "__main__":
    # Test des requêtes de base
    base = BaseQueries()
    base.run_all_basic_queries()