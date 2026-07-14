#!/usr/bin/env python
"""
Script de sauvegarde de Neo4j
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

def backup_neo4j() -> bool:
    """
    Sauvegarde la base de données Neo4j
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"neo4j_backup_{timestamp}.dump"
    
    logger.info(f"🚀 Début de la sauvegarde Neo4j")
    logger.info(f"📁 Fichier de sauvegarde : {backup_file}")
    
    try:
        # Vérifier que Neo4j est en cours d'exécution
        logger.info("🔍 Vérification de Neo4j...")
        
        # Exécuter la sauvegarde
        cmd = [
            "docker", "exec", "-t", "gnl-neo4j",
            "neo4j-admin", "dump",
            "--database=neo4j",
            "--to=/var/lib/neo4j/import/backup.dump"
        ]
        
        logger.info(f"🔄 Exécution : {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Erreur de sauvegarde : {result.stderr}")
            return False
        
        # Copier le fichier de sauvegarde
        cmd_copy = [
            "docker", "cp",
            "gnl-neo4j:/var/lib/neo4j/import/backup.dump",
            str(backup_file)
        ]
        
        logger.info(f"🔄 Copie : {' '.join(cmd_copy)}")
        result = subprocess.run(cmd_copy, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Erreur de copie : {result.stderr}")
            return False
        
        # Supprimer le fichier temporaire
        cmd_cleanup = [
            "docker", "exec", "-t", "gnl-neo4j",
            "rm", "-f", "/var/lib/neo4j/import/backup.dump"
        ]
        subprocess.run(cmd_cleanup, capture_output=True, text=True)
        
        # Vérifier la taille du fichier
        file_size = backup_file.stat().st_size
        logger.info(f"✅ Sauvegarde terminée : {file_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        return False

def restore_neo4j(backup_file: Path) -> bool:
    """
    Restaure une sauvegarde Neo4j
    """
    if not backup_file.exists():
        logger.error(f"❌ Fichier non trouvé : {backup_file}")
        return False
    
    logger.info(f"🚀 Restauration de : {backup_file}")
    
    try:
        # Copier le fichier dans le conteneur
        cmd_copy = [
            "docker", "cp",
            str(backup_file),
            "gnl-neo4j:/var/lib/neo4j/import/backup.dump"
        ]
        
        logger.info(f"🔄 Copie du fichier de sauvegarde...")
        result = subprocess.run(cmd_copy, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Erreur de copie : {result.stderr}")
            return False
        
        # Restaurer la base de données
        cmd_restore = [
            "docker", "exec", "-t", "gnl-neo4j",
            "neo4j-admin", "load",
            "--database=neo4j",
            "--from=/var/lib/neo4j/import/backup.dump",
            "--force"
        ]
        
        logger.info(f"🔄 Restauration...")
        result = subprocess.run(cmd_restore, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Erreur de restauration : {result.stderr}")
            return False
        
        # Supprimer le fichier temporaire
        cmd_cleanup = [
            "docker", "exec", "-t", "gnl-neo4j",
            "rm", "-f", "/var/lib/neo4j/import/backup.dump"
        ]
        subprocess.run(cmd_cleanup, capture_output=True, text=True)
        
        logger.info("✅ Restauration terminée")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        return False

def list_backups() -> None:
    """
    Liste les sauvegardes disponibles
    """
    backups = sorted(BACKUP_DIR.glob("neo4j_backup_*.dump"), reverse=True)
    
    if not backups:
        logger.info("📋 Aucune sauvegarde trouvée")
        return
    
    logger.info(f"📋 {len(backups)} sauvegardes trouvées :")
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / 1024 / 1024
        logger.info(f"   {i}. {backup.name} ({size:.2f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Sauvegarde Neo4j")
    parser.add_argument("--action", choices=["backup", "restore", "list"], default="backup")
    parser.add_argument("--file", help="Fichier de sauvegarde à restaurer")
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_backups()
    elif args.action == "backup":
        if backup_neo4j():
            logger.info("✅ Sauvegarde terminée avec succès")
        else:
            logger.error("❌ Sauvegarde échouée")
            sys.exit(1)
    elif args.action == "restore":
        if args.file:
            backup_file = Path(args.file)
            if restore_neo4j(backup_file):
                logger.info("✅ Restauration terminée avec succès")
            else:
                logger.error("❌ Restauration échouée")
                sys.exit(1)
        else:
            logger.error("❌ Veuillez spécifier un fichier avec --file")
            sys.exit(1)

if __name__ == "__main__":
    main()