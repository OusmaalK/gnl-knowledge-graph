#!/usr/bin/env python
"""
Script d'initialisation de Kafka
Version corrigée avec PYTHONPATH
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent (backend) au PYTHONPATH
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import logging
from src.infrastructure.kafka.admin import KafkaAdmin
from src.infrastructure.kafka.topics import TOPICS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_kafka():
    """
    Initialise Kafka (création des topics)
    """
    logger.info("🚀 Initialisation de Kafka...")
    
    admin = KafkaAdmin()
    if not admin.connect():
        logger.error("❌ Connexion à Kafka impossible")
        sys.exit(1)
    
    # Créer les topics
    logger.info("📇 Création des topics...")
    for topic_name, config in TOPICS.items():
        logger.info(f"   Création de {topic_name}...")
        admin.create_topic(
            topic_name=topic_name,
            num_partitions=config.get('num_partitions', 6),
            replication_factor=config.get('replication_factor', 1),
            config=config.get('config', {})
        )
    
    # Lister les topics
    logger.info("📋 Topics créés :")
    topics = admin.list_topics()
    for topic in topics:
        logger.info(f"   - {topic}")
    
    admin.close()
    logger.info("✅ Kafka initialisé")

if __name__ == "__main__":
    init_kafka()