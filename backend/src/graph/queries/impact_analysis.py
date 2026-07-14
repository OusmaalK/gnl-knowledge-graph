"""
Analyse d'impact des pannes d'équipements
Phase 2 - Requêtes avancées
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImpactAnalysis:
    """Analyse l'impact des pannes d'équipements sur le réseau GNL"""
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        
    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info(f"✅ Connecté à Neo4j : {self.uri}")
        
    def close(self):
        if self.driver:
            self.driver.close()
            
    def get_impacted_clients(self, pipeline_id):
        """
        Trouve tous les clients impactés par une panne de pipeline
        Requête : PIPE-001 tombe en panne → quels clients sont impactés ?
        """
        query = """
        MATCH (p:Pipeline {id: $pipeline_id})-[:DESSERT]->(c:Client)
        RETURN p.id as Pipeline,
               p.nom as NomPipeline,
               collect(c.nom) as ClientsImpactes,
               count(c) as NombreClients
        """
        
        with self.driver.session() as session:
            result = session.run(query, pipeline_id=pipeline_id)
            return result.single()
    
    def get_full_chain(self):
        """
        Retourne toute la chaîne d'approvisionnement
        """
        query = """
        MATCH path = (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)
        OPTIONAL MATCH (p)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (p)-[:DEPEND_DE]->(comp:Compresseur)
        RETURN 
            f.nom as Fournisseur,
            t.nom as Terminal,
            p.nom as Pipeline,
            collect(c.nom) as Clients,
            comp.nom as Compresseur
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def get_equipment_incident_history(self, equipment_id):
        """
        Historique des incidents pour un équipement donné
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e {id: $equipment_id})
        RETURN e.id as Equipement,
               collect(i.id) as Incidents,
               collect(i.description) as Descriptions,
               collect(i.date) as Dates
        """
        
        with self.driver.session() as session:
            result = session.run(query, equipment_id=equipment_id)
            return result.single()
    
    def get_bottlenecks(self):
        """
        Détection des goulots d'étranglement
        Équipements qui desservent le plus de clients
        """
        query = """
        MATCH (p:Pipeline)-[:DESSERT]->(c:Client)
        WITH p, count(c) as nb_clients
        ORDER BY nb_clients DESC
        LIMIT 3
        RETURN p.id as Pipeline, p.nom as Nom, nb_clients
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def get_critical_equipment(self):
        """
        Équipements critiques basés sur le nombre d'incidents
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        WITH e, count(i) as nb_incidents
        ORDER BY nb_incidents DESC
        LIMIT 5
        RETURN e.id as Equipement, 
               labels(e)[0] as Type,
               nb_incidents
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def run_all_analyses(self):
        """Exécute toutes les analyses"""
        self.connect()
        
        logger.info("\n" + "="*60)
        logger.info("📊 ANALYSE D'IMPACT - RÉSEAU GNL")
        logger.info("="*60)
        
        # 1. Impact sur les clients
        logger.info("\n1️⃣ Impact d'une panne du pipeline PIPE-001 :")
        result = self.get_impacted_clients("PIPE-001")
        if result:
            logger.info(f"   Pipeline : {result['NomPipeline']}")
            logger.info(f"   Clients impactés : {', '.join(result['ClientsImpactes'])}")
            logger.info(f"   Nombre de clients : {result['NombreClients']}")
        
        # 2. Chaîne d'approvisionnement
        logger.info("\n2️⃣ Chaîne d'approvisionnement :")
        chain = self.get_full_chain()
        for item in chain[:3]:
            logger.info(f"   {item['Fournisseur']} → {item['Terminal']} → {item['Pipeline']}")
        
        # 3. Équipements critiques
        logger.info("\n3️⃣ Équipements critiques (plus d'incidents) :")
        critical = self.get_critical_equipment()
        for item in critical:
            logger.info(f"   {item['Equipement']} ({item['Type']}) : {item['nb_incidents']} incidents")
        
        self.close()
        
        return {
            'impact': result,
            'chain': chain,
            'critical': critical
        }

if __name__ == "__main__":
    analysis = ImpactAnalysis()
    results = analysis.run_all_analyses()