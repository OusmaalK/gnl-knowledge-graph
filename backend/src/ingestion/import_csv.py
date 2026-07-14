"""
Script d'importation des données GNL vers Neo4j
Phase 1 - Ingestion des données
"""

import os
import csv
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jIngestion:
    """Classe d'ingestion des données dans Neo4j"""
    
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
            logger.info(f"✅ Connecté à Neo4j : {self.uri}")
        except Exception as e:
            logger.error(f"❌ Erreur de connexion : {e}")
            raise

    def close(self):
        """Ferme la connexion"""
        if self.driver:
            self.driver.close()
            logger.info("🔒 Connexion fermée")

    def import_fournisseurs(self, csv_path):
        """Importe les fournisseurs depuis un fichier CSV"""
        if not os.path.exists(csv_path):
            logger.error(f"❌ Fichier non trouvé : {csv_path}")
            return 0
            
        query = """
        MERGE (f:Fournisseur {id: $fournisseur_id})
        SET f.nom = $nom,
            f.pays = $pays,
            f.ville = $ville,
            f.adresse = $adresse,
            f.contact = $contact,
            f.email = $email,
            f.statut = $statut,
            f.updated_at = datetime()
        RETURN f
        """
        
        with self.driver.session() as session:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    try:
                        session.run(query, row)
                        count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur sur {row.get('fournisseur_id')}: {e}")
                logger.info(f"✅ {count} fournisseurs importés")
                return count

    def import_terminaux(self, csv_path):
        """Importe les terminaux depuis un fichier CSV"""
        if not os.path.exists(csv_path):
            logger.error(f"❌ Fichier non trouvé : {csv_path}")
            return 0
            
        query = """
        MERGE (t:Terminal {id: $terminal_id})
        SET t.nom = $nom,
            t.localisation = $localisation,
            t.capacite_m3 = toInteger($capacite_m3),
            t.type = $type,
            t.statut = $statut,
            t.updated_at = datetime()
        RETURN t
        """
        
        with self.driver.session() as session:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    try:
                        session.run(query, row)
                        count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur sur {row.get('terminal_id')}: {e}")
                logger.info(f"✅ {count} terminaux importés")
                return count

    def import_pipelines(self, csv_path):
        """Importe les pipelines depuis un fichier CSV"""
        if not os.path.exists(csv_path):
            logger.error(f"❌ Fichier non trouvé : {csv_path}")
            return 0
            
        query = """
        MERGE (p:Pipeline {id: $pipeline_id})
        SET p.nom = $nom,
            p.longueur_km = toInteger($longueur_km),
            p.depart = $depart,
            p.arrivee = $arrivee,
            p.pression_max_bar = toInteger($pression_max_bar),
            p.statut = $statut,
            p.updated_at = datetime()
        RETURN p
        """
        
        with self.driver.session() as session:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    try:
                        session.run(query, row)
                        count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur sur {row.get('pipeline_id')}: {e}")
                logger.info(f"✅ {count} pipelines importés")
                return count

    def create_relations(self):
        """Crée les relations entre les entités"""
        logger.info("🔗 Création des relations...")
        
        # Relations FOURNIT (Fournisseur -> Terminal)
        query_fournit = """
        MATCH (f:Fournisseur {id: $fournisseur_id})
        MATCH (t:Terminal {id: $terminal_id})
        MERGE (f)-[:FOURNIT {date: datetime(), statut: 'actif'}]->(t)
        """
        
        relations_fournit = [
            {'fournisseur_id': 'FOUR-001', 'terminal_id': 'TERM-001'},
            {'fournisseur_id': 'FOUR-002', 'terminal_id': 'TERM-002'},
            {'fournisseur_id': 'FOUR-001', 'terminal_id': 'TERM-003'},
            {'fournisseur_id': 'FOUR-003', 'terminal_id': 'TERM-004'},
            {'fournisseur_id': 'FOUR-004', 'terminal_id': 'TERM-005'},
        ]
        
        with self.driver.session() as session:
            count = 0
            for rel in relations_fournit:
                try:
                    session.run(query_fournit, rel)
                    count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Erreur relation {rel}: {e}")
            logger.info(f"✅ {count} relations FOURNIT créées")
        
        # Relations ALIMENTE (Terminal -> Pipeline)
        query_alimente = """
        MATCH (t:Terminal {id: $terminal_id})
        MATCH (p:Pipeline {id: $pipeline_id})
        MERGE (t)-[:ALIMENTE {debit: $debit, date: datetime()}]->(p)
        """
        
        relations_alimente = [
            {'terminal_id': 'TERM-001', 'pipeline_id': 'PIPE-001', 'debit': 50},
            {'terminal_id': 'TERM-002', 'pipeline_id': 'PIPE-002', 'debit': 45},
            {'terminal_id': 'TERM-003', 'pipeline_id': 'PIPE-003', 'debit': 55},
            {'terminal_id': 'TERM-001', 'pipeline_id': 'PIPE-004', 'debit': 30},
        ]
        
        with self.driver.session() as session:
            count = 0
            for rel in relations_alimente:
                try:
                    session.run(query_alimente, rel)
                    count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Erreur relation {rel}: {e}")
            logger.info(f"✅ {count} relations ALIMENTE créées")

    def verify_data(self):
        """Vérifie les données importées"""
        logger.info("🔍 Vérification des données importées...")
        
        queries = [
            ("Nœuds Fournisseur", "MATCH (f:Fournisseur) RETURN count(f) as total"),
            ("Nœuds Terminal", "MATCH (t:Terminal) RETURN count(t) as total"),
            ("Nœuds Pipeline", "MATCH (p:Pipeline) RETURN count(p) as total"),
            ("Relations FOURNIT", "MATCH ()-[:FOURNIT]->() RETURN count(*) as total"),
            ("Relations ALIMENTE", "MATCH ()-[:ALIMENTE]->() RETURN count(*) as total"),
            ("Total Nœuds", "MATCH (n) RETURN count(n) as total"),
            ("Total Relations", "MATCH ()-[r]->() RETURN count(r) as total"),
        ]
        
        with self.driver.session() as session:
            for label, query in queries:
                result = session.run(query)
                record = result.single()
                if record:
                    logger.info(f"  📊 {label}: {record['total']}")

    def run_full_import(self):
        """Exécute l'importation complète"""
        logger.info("="*60)
        logger.info("🚀 PHASE 1 - INGESTION DES DONNÉES GNL")
        logger.info("="*60)
        
        self.connect()
        try:
            # Importer les données
            logger.info("\n📥 Importation des données...")
            self.import_fournisseurs('data/raw/sap/fournisseurs.csv')
            self.import_terminaux('data/raw/sap/terminaux.csv')
            self.import_pipelines('data/raw/sap/pipelines.csv')
            
            # Créer les relations
            logger.info("\n🔗 Création des relations...")
            self.create_relations()
            
            # Vérifier les données
            logger.info("\n🔍 Vérification...")
            self.verify_data()
            
            logger.info("\n" + "="*60)
            logger.info("✅ IMPORTATION TERMINÉE AVEC SUCCÈS !")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'importation : {e}")
            raise
        finally:
            self.close()

if __name__ == "__main__":
    ingestion = Neo4jIngestion()
    ingestion.run_full_import()