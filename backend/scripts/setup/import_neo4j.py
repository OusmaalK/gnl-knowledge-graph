#!/usr/bin/env python3
"""
Script d'importation de données CSV vers Neo4j
Path: backend/scripts/setup/import_neo4j.py
Description: Lit les fichiers CSV dans data/raw/ et peuple la base Neo4j.
"""

import csv
import os
import sys
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# === CONFIGURATION DU LOGGING ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === CHARGEMENT DU FICHIER .ENV ===
# Le script suppose que le fichier .env est situé à la racine du dossier 'backend'
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"✅ Fichier .env chargé depuis {env_path}")
else:
    logger.warning("⚠️ Fichier .env non trouvé. Assurez-vous que les variables Neo4j sont définies dans l'environnement.")

# === CONFIGURATION NEO4J ===
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "GnL_Neo4j_2026_Secure!")

def get_neo4j_driver():
    """Établit la connexion à Neo4j."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        logger.info(f"✅ Connexion à Neo4j établie sur {NEO4J_URI}")
        return driver
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à Neo4j: {e}")
        sys.exit(1)

# === FONCTIONS D'IMPORTATION ===

def import_csv_to_neo4j(driver, file_path, label, id_field="id"):
    """
    Importe un fichier CSV dans Neo4j sous forme de nœuds.
    Args:
        driver: Connexion Neo4j.
        file_path: Chemin absolu vers le fichier CSV.
        label: Le label Neo4j à attribuer (ex: 'Pipeline').
        id_field: Le nom de la colonne qui sert d'identifiant unique.
    """
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ Fichier ignoré (introuvable) : {file_path}")
        return

    logger.info(f"📂 Importation de {file_path} en tant que nœuds :{label}...")
    
    # Lecture du fichier CSV avec détection du délimiteur (; ou ,)
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    
    if not rows:
        logger.warning(f"⚠️ Le fichier {file_path} est vide.")
        return

    # Préparer la requête Cypher
    # Nous construisons dynamiquement la requête en fonction des colonnes du CSV
    properties = rows[0].keys()
    props_str = ", ".join([f"{k}: row.{k}" for k in properties])
    
    query = f"""
    UNWIND $rows AS row
    MERGE (n:{label} {{id: row.{id_field}}})
    SET n += {{{props_str}}}
    """
    
    try:
        with driver.session() as session:
            session.run(query, rows=rows)
        logger.info(f"✅ {len(rows)} nœuds '{label}' importés avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'importation de {label}: {e}")

def create_relationships(driver, file_path, rel_type, source_label, source_field, target_label, target_field):
    """
    Crée des relations entre des nœuds existants basés sur un fichier CSV.
    """
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ Fichier de relations ignoré (introuvable) : {file_path}")
        return

    logger.info(f"🔗 Importation des relations {rel_type} depuis {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    
    if not rows:
        logger.warning(f"⚠️ Le fichier {file_path} est vide.")
        return

    query = f"""
    UNWIND $rows AS row
    MATCH (a:{source_label} {{id: row.{source_field}}})
    MATCH (b:{target_label} {{id: row.{target_field}}})
    MERGE (a)-[:{rel_type}]->(b)
    """
    
    try:
        with driver.session() as session:
            session.run(query, rows=rows)
        logger.info(f"✅ {len(rows)} relations '{rel_type}' créées.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des relations {rel_type}: {e}")

# === POINT D'ENTRÉE PRINCIPAL ===

def main():
    driver = get_neo4j_driver()
    
    # Définir le chemin du dossier raw
    RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data/raw')
    
    # --- 1. Importation des NŒUDS (CSV) ---
    # Le script est intelligent : il adapte les propriétés selon ce qui est dans le CSV
    import_csv_to_neo4j(driver, os.path.join(RAW_DATA_DIR, 'pipelines.csv'), 'Pipeline')
    import_csv_to_neo4j(driver, os.path.join(RAW_DATA_DIR, 'terminals.csv'), 'Terminal')
    import_csv_to_neo4j(driver, os.path.join(RAW_DATA_DIR, 'clients.csv'), 'Client')
    import_csv_to_neo4j(driver, os.path.join(RAW_DATA_DIR, 'compressors.csv'), 'Compresseur')
    import_csv_to_neo4j(driver, os.path.join(RAW_DATA_DIR, 'incidents.csv'), 'Incident', id_field='id')
    
    # --- 2. Importation des RELATIONS (JSON pour les relations complexes) ---
    # À noter : Pour les relations simples, vous pouvez aussi utiliser le fichier CSV.
    # Le script s'attend à un fichier JSON contenant un tableau d'objets {source, target}.
    # Exemple de structure JSON pour relations :
    # [ {"source": "TERM-001", "target": "PIPE-001"}, {"source": "TERM-001", "target": "PIPE-002"} ]
    
    relationships_file = os.path.join(RAW_DATA_DIR, 'relations.json')
    if os.path.exists(relationships_file):
        import json
        with open(relationships_file, 'r', encoding='utf-8') as f:
            rels = json.load(f)
        logger.info(f"🔗 Importation des relations depuis relations.json...")
        
        # Exemple: Créer des relations ALIMENTE entre Terminaux et Pipelines
        try:
            with driver.session() as session:
                for rel in rels:
                    if rel.get('type') == 'ALIMENTE':
                        session.run("""
                        MATCH (t:Terminal {id: $source})
                        MATCH (p:Pipeline {id: $target})
                        MERGE (t)-[:ALIMENTE]->(p)
                        """, source=rel['source'], target=rel['target'])
                    elif rel.get('type') == 'DESSERT':
                        session.run("""
                        MATCH (p:Pipeline {id: $source})
                        MATCH (c:Client {id: $target})
                        MERGE (p)-[:DESSERT]->(c)
                        """, source=rel['source'], target=rel['target'])
            logger.info(f"✅ Relations JSON importées avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'import JSON: {e}")

    driver.close()
    logger.info("🎉 Importation terminée avec succès !")

if __name__ == "__main__":
    main()