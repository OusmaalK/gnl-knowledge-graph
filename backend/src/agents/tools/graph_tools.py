"""
Outils d'interrogation du graphe Neo4j
Phase 3 - Outils pour les agents avec support LLM
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphTools:
    """
    Outils pour interroger le graphe Neo4j
    Utilisés par les agents IA
    """
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        
    def connect(self):
        """Établit la connexion à Neo4j"""
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self.driver
    
    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Exécute une requête Cypher"""
        driver = self.connect()
        with driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    
    # ============================================================
    # OUTILS POUR LES AGENTS
    # ============================================================
    
    def get_equipment_info(self, equipment_id: str) -> Dict:
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (e)-[:DEPEND_DE]->(comp:Compresseur)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN 
            e.id as id,
            labels(e)[0] as type,
            e.nom as nom,
            e.statut as statut,
            collect(DISTINCT c.nom) as clients,
            collect(DISTINCT comp.nom) as dependances,
            collect(DISTINCT i.id) as incidents_ids,
            collect(DISTINCT i.description) as incidents_descriptions,
            count(DISTINCT i) as nombre_incidents
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        return results[0] if results else {}
    
    def get_impact_analysis(self, equipment_id: str) -> Dict:
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (e)-[:DEPEND_DE]->(comp:Compresseur)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN 
            e.id as equipment_id,
            e.nom as equipment_name,
            labels(e)[0] as equipment_type,
            e.statut as statut,
            collect(DISTINCT c.nom) as clients_impactes,
            collect(DISTINCT comp.nom) as dependances_critiques,
            count(DISTINCT i) as incidents_count,
            collect(DISTINCT i.gravite) as gravites
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        return results[0] if results else {}
    
    def get_alternative_route(self, start_id: str, end_id: str, exclude_id: Optional[str] = None) -> Dict:
        if exclude_id:
            query = """
            MATCH path = shortestPath(
                (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
            )
            WHERE NONE(n IN nodes(path) WHERE n.id = $exclude_id)
            RETURN [n in nodes(path) | n.id] as path,
                   [n in nodes(path) | labels(n)[0]] as types,
                   length(path) as distance
            """
            params = {"start_id": start_id, "end_id": end_id, "exclude_id": exclude_id}
        else:
            query = """
            MATCH path = shortestPath(
                (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
            )
            RETURN [n in nodes(path) | n.id] as path,
                   [n in nodes(path) | labels(n)[0]] as types,
                   length(path) as distance
            """
            params = {"start_id": start_id, "end_id": end_id}
        
        results = self.execute_query(query, params)
        return results[0] if results else {"path": [], "distance": -1}
    
    def get_risk_score(self, equipment_id: str) -> Dict:
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN 
            e.id as equipment_id,
            e.nom as equipment_name,
            count(DISTINCT i) as incidents_count,
            count(DISTINCT c) as clients_count,
            CASE 
                WHEN count(DISTINCT i) >= 3 THEN 90
                WHEN count(DISTINCT i) >= 1 THEN 60
                ELSE 20
            END as score,
            CASE 
                WHEN count(DISTINCT i) >= 3 THEN 'CRITIQUE'
                WHEN count(DISTINCT i) >= 1 THEN 'ELEVE'
                ELSE 'FAIBLE'
            END as niveau
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        return results[0] if results else {}
    
    def get_incident_history(self, equipment_id: Optional[str] = None) -> List[Dict]:
        if equipment_id:
            query = """
            MATCH (i:Incident)-[:AFFECTE]->(e {id: $equipment_id})
            RETURN i.id as id,
                   i.description as description,
                   i.gravite as gravite,
                   i.date as date,
                   i.cause as cause,
                   i.duree_min as duree,
                   e.id as equipment_id,
                   e.nom as equipment_name
            ORDER BY i.date DESC
            """
            params = {"equipment_id": equipment_id}
        else:
            query = """
            MATCH (i:Incident)-[:AFFECTE]->(e)
            RETURN i.id as id,
                   i.description as description,
                   i.gravite as gravite,
                   i.date as date,
                   i.cause as cause,
                   i.duree_min as duree,
                   e.id as equipment_id,
                   e.nom as equipment_name
            ORDER BY i.date DESC
            """
            params = {}
        
        return self.execute_query(query, params)
    
    def get_supply_chain(self) -> List[Dict]:
        query = """
        MATCH path = (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)
        OPTIONAL MATCH (p)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(p)
        RETURN 
            f.nom as fournisseur,
            t.nom as terminal,
            p.nom as pipeline,
            p.statut as statut,
            collect(DISTINCT c.nom) as clients,
            collect(DISTINCT i.description) as incidents
        ORDER BY f.nom
        """
        return self.execute_query(query)
    
    def get_statistics(self) -> Dict:
        query = """
        MATCH (n)
        WITH count(n) as total_nodes
        MATCH ()-[r]->()
        WITH total_nodes, count(r) as total_relations
        MATCH (i:Incident)
        WITH total_nodes, total_relations, count(i) as total_incidents
        MATCH (p:Pipeline)
        WITH total_nodes, total_relations, total_incidents, count(p) as total_pipelines
        MATCH (c:Client)
        RETURN total_nodes, total_relations, total_incidents, total_pipelines, count(c) as total_clients
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    
    # ============================================================
    # CONTEXTE POUR LLM
    # ============================================================
    
    def get_context_for_llm(self) -> str:
        """
        Récupère un résumé du réseau GNL pour le contexte LLM
        """
        stats = self.get_statistics()
        incidents = self.get_incident_history()
        supply_chain = self.get_supply_chain()
        
        context = []
        context.append("📊 RÉSEAU GNL - CONTEXTE")
        context.append("=" * 40)
        
        # Statistiques
        context.append(f"\n📈 Statistiques :")
        context.append(f"   - Nœuds : {stats.get('total_nodes', 0)}")
        context.append(f"   - Relations : {stats.get('total_relations', 0)}")
        context.append(f"   - Incidents : {stats.get('total_incidents', 0)}")
        context.append(f"   - Pipelines : {stats.get('total_pipelines', 0)}")
        context.append(f"   - Clients : {stats.get('total_clients', 0)}")
        
        # Incidents récents
        if incidents:
            context.append(f"\n🚨 Incidents récents :")
            for inc in incidents[:3]:
                context.append(f"   - {inc['id']} : {inc['description']} (Gravité: {inc['gravite']})")
        
        # Chaîne d'approvisionnement
        if supply_chain:
            context.append(f"\n📦 Chaîne d'approvisionnement :")
            for item in supply_chain[:2]:
                context.append(f"   - {item['fournisseur']} → {item['terminal']} → {item['pipeline']}")
        
        return "\n".join(context)
    
    def get_incident_statistics(self) -> Dict:
        query = """
        MATCH (i:Incident)
        RETURN 
            count(i) as total,
            count(DISTINCT i.cause) as causes_distinctes,
            collect(DISTINCT i.gravite) as gravites,
            collect(DISTINCT i.cause) as causes
        """
        results = self.execute_query(query)
        stats = results[0] if results else {}
        
        query_gravite = """
        MATCH (i:Incident)
        RETURN i.gravite as gravite, count(i) as nombre
        ORDER BY nombre DESC
        """
        stats['repartition_gravite'] = self.execute_query(query_gravite)
        
        query_cause = """
        MATCH (i:Incident)
        RETURN i.cause as cause, count(i) as nombre
        ORDER BY nombre DESC
        """
        stats['repartition_cause'] = self.execute_query(query_cause)
        
        return stats