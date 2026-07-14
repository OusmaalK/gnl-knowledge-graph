#!/usr/bin/env python
"""
Script de nettoyage des données
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.graph.operations.maintenance import GraphMaintenance
from src.infrastructure.neo4j.client import Neo4jClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_orphans():
    """Nettoie les nœuds orphelins"""
    logger.info("🧹 Nettoyage des nœuds orphelins...")
    maintenance = GraphMaintenance()
    result = maintenance.cleanup_orphan_nodes()
    logger.info(f"✅ {result.get('deleted', 0)} nœuds orphelins supprimés")
    maintenance.close()

def cleanup_duplicates():
    """Nettoie les doublons"""
    logger.info("🧹 Nettoyage des doublons...")
    maintenance = GraphMaintenance()
    result = maintenance.cleanup_duplicates()
    logger.info(f"✅ {result.get('deleted', 0)} doublons supprimés")
    maintenance.close()

def cleanup_old_incidents(days: int = 365):
    """Supprime les incidents anciens"""
    logger.info(f"🧹 Suppression des incidents > {days} jours...")
    maintenance = GraphMaintenance()
    result = maintenance.cleanup_old_incidents(days)
    logger.info(f"✅ {result.get('deleted', 0)} incidents supprimés")
    maintenance.close()

def validate_graph():
    """Valide l'intégrité du graphe"""
    logger.info("🔍 Validation du graphe...")
    maintenance = GraphMaintenance()
    result = maintenance.validate_graph()
    
    if result.get('has_issues'):
        logger.warning(f"⚠️ Problèmes détectés : {result.get('issues')}")
        if result.get('issues'):
            for issue in result['issues']:
                logger.warning(f"   - {issue}")
    else:
        logger.info("✅ Grape valide")
    
    maintenance.close()

def repair_graph():
    """Répare les problèmes d'intégrité"""
    logger.info("🔧 Réparation du graphe...")
    maintenance = GraphMaintenance()
    result = maintenance.repair_graph()
    logger.info(f"✅ {result.get('repaired', 0)} réparations effectuées")
    maintenance.close()

def get_stats():
    """Affiche les statistiques"""
    logger.info("📊 Statistiques du graphe...")
    maintenance = GraphMaintenance()
    stats = maintenance.get_database_stats()
    
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    maintenance.close()

def main():
    parser = argparse.ArgumentParser(description="Nettoyage des données")
    parser.add_argument("--action", choices=["orphans", "duplicates", "old_incidents", "validate", "repair", "stats", "all"], default="all")
    parser.add_argument("--days", type=int, default=365, help="Nombre de jours pour old_incidents")
    
    args = parser.parse_args()
    
    if args.action == "orphans":
        cleanup_orphans()
    elif args.action == "duplicates":
        cleanup_duplicates()
    elif args.action == "old_incidents":
        cleanup_old_incidents(args.days)
    elif args.action == "validate":
        validate_graph()
    elif args.action == "repair":
        repair_graph()
    elif args.action == "stats":
        get_stats()
    elif args.action == "all":
        cleanup_orphans()
        cleanup_duplicates()
        cleanup_old_incidents(args.days)
        validate_graph()
        repair_graph()
        get_stats()
        logger.info("✅ Nettoyage complet terminé")

if __name__ == "__main__":
    main()