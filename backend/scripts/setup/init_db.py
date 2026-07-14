#!/usr/bin/env python
"""
Script d'initialisation de la base de données Neo4j
Version corrigée
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent (backend) au PYTHONPATH
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import logging
from src.infrastructure.neo4j.client import Neo4jClient
from src.graph.indexers.neo4j_indexer import Neo4jIndexer
from src.graph.operations.crud import GraphCRUD
from src.graph.operations.maintenance import GraphMaintenance  # <-- AJOUT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialise la base de données Neo4j
    """
    logger.info("🚀 Initialisation de la base de données...")
    
    # Créer les indexes
    logger.info("📇 Création des indexes...")
    indexer = Neo4jIndexer()
    if not indexer.connect():
        logger.error("❌ Connexion à Neo4j impossible")
        sys.exit(1)
    
    indexer.create_indexes()
    indexer.close()
    
    # Vérifier la connexion
    logger.info("🔍 Vérification de la connexion...")
    crud = GraphCRUD()
    if not crud.connect():
        logger.error("❌ Connexion à Neo4j impossible")
        sys.exit(1)
    
    # Afficher les statistiques - Utiliser GraphMaintenance
    logger.info("📊 Statistiques initiales...")
    maintenance = GraphMaintenance()
    stats = maintenance.get_database_stats()  # <-- CORRECTION
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    crud.close()
    maintenance.close()
    logger.info("✅ Base de données initialisée")

if __name__ == "__main__":
    init_database()