#!/usr/bin/env python3
"""
IoT Data Importer - Injection des données capteurs dans Neo4j
Path: backend/scripts/maintenance/import_iot_neo4j.py
Description: Lit les fichiers JSON IoT et crée les nœuds dans Neo4j.
"""

import os
import json
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# === CONFIGURATION ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement du .env
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "GnL_Neo4j_2026_Secure!")

def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        logger.info(f"✅ Connexion Neo4j établie sur {NEO4J_URI}")
        return driver
    except Exception as e:
        logger.error(f"❌ Erreur de connexion Neo4j: {e}")
        return None

def import_iot_json_to_neo4j(driver, json_path):
    """Lit un fichier JSON et crée des nœuds SensorData dans Neo4j."""
    if not os.path.exists(json_path):
        logger.warning(f"⚠️ Fichier introuvable : {json_path}")
        return 0

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            sensor_data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Erreur de lecture JSON: {e}")
        return 0

    if not sensor_data:
        logger.info(f"ℹ️ Fichier vide : {json_path}")
        return 0

    query = """
    UNWIND $rows AS row
    // Créer le nœud de données capteur
    CREATE (s:SensorData {
        id: row.timestamp + '-' + row.equipment_id,
        timestamp: row.timestamp,
        temperature: row.temperature,
        pression: row.pression,
        equipment_id: row.equipment_id
    })
    // Si le nœud capteur est lié à un pipeline, on crée une relation
    WITH s, row
    MATCH (p:Pipeline {id: row.equipment_id})
    MERGE (p)-[:HAS_SENSOR]->(s)
    """
    
    try:
        with driver.session() as session:
            session.run(query, rows=sensor_data)
        logger.info(f"✅ {len(sensor_data)} enregistrements importés depuis {os.path.basename(json_path)}")
        return len(sensor_data)
    except Exception as e:
        logger.error(f"❌ Erreur Cypher: {e}")
        return 0

def main():
    driver = get_neo4j_driver()
    if not driver:
        return

    # Dossier contenant les fichiers JSON des capteurs
    iot_dir = os.path.join(os.path.dirname(__file__), '../../data/raw/iot')
    
    if not os.path.exists(iot_dir):
        logger.warning(f"⚠️ Le dossier {iot_dir} n'existe pas encore.")
        return

    # Parcourir tous les fichiers JSON du dossier
    imported_count = 0
    for filename in os.listdir(iot_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(iot_dir, filename)
            count = import_iot_json_to_neo4j(driver, filepath)
            imported_count += count

    driver.close()
    logger.info(f"🎉 Importation terminée. Total : {imported_count} données capteurs.")

if __name__ == "__main__":
    main()