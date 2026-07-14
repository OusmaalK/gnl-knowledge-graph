"""
Prédiction des risques et détection de patterns
Phase 2 - Analyse prédictive
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskPredictor:
    """Prédit les risques basés sur l'historique des incidents"""
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        
    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info("✅ Connecté à Neo4j")
        
    def close(self):
        if self.driver:
            self.driver.close()
    
    def get_incident_patterns(self):
        """
        Détecte les patterns récurrents d'incidents
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN e.id as Equipement,
               collect(i.cause) as Causes,
               collect(i.gravite) as Gravites,
               count(i) as NombreIncidents
        ORDER BY NombreIncidents DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def get_high_risk_equipment(self, threshold=2):
        """
        Identifie les équipements à haut risque
        (plus de 'threshold' incidents)
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        WITH e, count(i) as nb_incidents
        WHERE nb_incidents > $threshold
        RETURN e.id as Equipement,
               labels(e)[0] as Type,
               nb_incidents,
               CASE 
                   WHEN nb_incidents >= 3 THEN 'CRITIQUE'
                   WHEN nb_incidents >= 2 THEN 'ELEVE'
                   ELSE 'MODERE'
               END as Risque
        ORDER BY nb_incidents DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, threshold=threshold)
            return [record.data() for record in result]
    
    def get_cause_analysis(self):
        """
        Analyse des causes principales d'incidents
        """
        query = """
        MATCH (i:Incident)
        RETURN i.cause as Cause,
               count(i) as Nombre,
               collect(i.id) as Incidents
        ORDER BY Nombre DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def get_chain_reaction_risk(self):
        """
        Risque d'effet domino
        Un pipeline défaillant peut affecter d'autres équipements
        """
        query = """
        MATCH (p:Pipeline)-[:DEPEND_DE]->(comp:Compresseur)
        MATCH (i:Incident)-[:AFFECTE]->(p)
        RETURN p.id as Pipeline,
               comp.id as Compresseur,
               count(i) as IncidentsPipeline,
               CASE 
                   WHEN count(i) > 1 THEN 'RISQUE EFFET DOMINO'
                   ELSE 'RISQUE MODERE'
               END as Alerte
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def predict_risk_score(self, equipment_id):
        """
        Calcule un score de risque pour un équipement
        Basé sur l'historique et la criticité
        """
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN e.id as Equipement,
               count(i) as NombreIncidents,
               count(c) as NombreClients,
               CASE 
                   WHEN count(i) >= 3 THEN 'CRITIQUE'
                   WHEN count(i) >= 1 THEN 'ELEVE'
                   ELSE 'FAIBLE'
               END as NiveauRisque,
               CASE 
                   WHEN count(i) >= 3 THEN 90
                   WHEN count(i) >= 1 THEN 60
                   ELSE 20
               END as ScoreRisque
        """
        
        with self.driver.session() as session:
            result = session.run(query, equipment_id=equipment_id)
            return result.single()
    
    def get_predictive_alerts(self):
        """
        Génère des alertes prédictives basées sur les patterns
        """
        logger.info("\n🔔 ALERTES PRÉDICTIVES")
        logger.info("-"*50)
        
        # 1. Équipements à haut risque
        high_risk = self.get_high_risk_equipment(1)
        if high_risk:
            for item in high_risk:
                logger.info(f"⚠️  {item['Equipement']} ({item['Type']}) - Risque {item['Risque']} ({item['nb_incidents']} incidents)")
        else:
            logger.info("✅ Aucun équipement à haut risque détecté")
        
        # 2. Effet domino
        domino = self.get_chain_reaction_risk()
        for item in domino:
            if item['Alerte'] == 'RISQUE EFFET DOMINO':
                logger.info(f"🔄 {item['Pipeline']} → {item['Compresseur']} : {item['Alerte']}")
        
        # 3. Causes principales
        logger.info("\n📊 ANALYSE DES CAUSES :")
        causes = self.get_cause_analysis()
        for item in causes:
            logger.info(f"   {item['Cause']} : {item['Nombre']} incidents")

    def run_analysis(self):
        """Exécute l'analyse complète des risques"""
        self.connect()
        
        logger.info("\n" + "="*60)
        logger.info("⚠️ ANALYSE PRÉDICTIVE - RISQUES GNL")
        logger.info("="*60)
        
        # Analyse des patterns
        patterns = self.get_incident_patterns()
        for item in patterns:
            logger.info(f"\n📋 {item['Equipement']} : {item['NombreIncidents']} incidents")
            if item['Causes']:
                logger.info(f"   Causes : {', '.join(set(item['Causes']))}")
            if item['Gravites']:
                logger.info(f"   Gravités : {', '.join(set(item['Gravites']))}")
        
        # Alertes prédictives
        self.get_predictive_alerts()
        
        # Score de risque pour PIPE-001
        score = self.predict_risk_score("PIPE-001")
        if score:
            logger.info(f"\n📊 SCORE DE RISQUE PIPE-001 :")
            logger.info(f"   Niveau : {score['NiveauRisque']}")
            logger.info(f"   Score : {score['ScoreRisque']}/100")
            logger.info(f"   Incidents : {score['NombreIncidents']}")
            logger.info(f"   Clients impactés : {score['NombreClients']}")
        
        self.close()


if __name__ == "__main__":
    predictor = RiskPredictor()
    predictor.run_analysis()