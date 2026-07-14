import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSONIngestion:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info(f"✅ Connecté à Neo4j : {self.uri}")

    def close(self):
        if self.driver:
            self.driver.close()

    def import_incidents(self, json_path):
        """Importe les incidents depuis un fichier JSON"""
        query = """
        MERGE (i:Incident {id: $incident_id})
        SET i.date = datetime($date),
            i.gravite = $gravite,
            i.description = $description,
            i.cause = $cause,
            i.action = $action,
            i.duree_min = $duree_min,
            i.updated_at = datetime()
        RETURN i
        """
        
        with self.driver.session() as session:
            with open(json_path, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)
                incidents = data if isinstance(data, list) else data.get('incidents', [])
                
                count = 0
                for incident in incidents:
                    session.run(query, incident)
                    count += 1
                logger.info(f"✅ {count} incidents importés")

    def link_incidents_to_equipment(self):
        """Relie les incidents aux équipements concernés"""
        query = """
        MATCH (i:Incident {id: $incident_id})
        MATCH (e {id: $equipement_id})
        MERGE (i)-[:AFFECTE]->(e)
        """
        
        with self.driver.session() as session:
            # Exemple : relier les incidents à des équipements
            links = [
                {'incident_id': 'INC-001', 'equipement_id': 'PIPE-001'},
                {'incident_id': 'INC-002', 'equipement_id': 'COMP-001'},
            ]
            for link in links:
                session.run(query, link)
            logger.info(f"✅ {len(links)} relations AFFECTE créées")

    def import_all(self):
        self.connect()
        try:
            self.import_incidents('data/raw/reports/incidents.json')
            self.link_incidents_to_equipment()
            logger.info("✅ Import des incidents terminé")
        finally:
            self.close()

if __name__ == "__main__":
    ingestion = JSONIngestion()
    ingestion.import_all()