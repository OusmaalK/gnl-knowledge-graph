#!/usr/bin/env python
"""
Script de migration de base de données
"""

import sys
import argparse
import logging
from pathlib import Path
import json
import yaml
from datetime import datetime

from src.graph.operations.crud import GraphCRUD
from src.graph.operations.batch import BatchOperations

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """
    Gestionnaire de migrations
    """
    
    def __init__(self):
        self.crud = GraphCRUD()
        self.batch = BatchOperations()
    
    def close(self):
        self.crud.close()
        self.batch.close()
    
    def export_to_json(self, output_file: str) -> bool:
        """
        Exporte le graphe en JSON
        """
        logger.info(f"📤 Export vers {output_file}")
        
        try:
            # Récupérer tous les nœuds
            query_nodes = "MATCH (n) RETURN n, labels(n) as labels"
            nodes = self.crud.execute_query(query_nodes)
            
            # Récupérer toutes les relations
            query_rels = "MATCH (n)-[r]->(m) RETURN n.id as source, type(r) as type, m.id as target, properties(r) as properties"
            relationships = self.crud.execute_query(query_rels)
            
            data = {
                "exported_at": datetime.now().isoformat(),
                "nodes": nodes,
                "relationships": relationships
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"✅ Export terminé : {len(nodes)} nœuds, {len(relationships)} relations")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur export : {e}")
            return False
    
    def import_from_json(self, input_file: str) -> bool:
        """
        Importe un fichier JSON
        """
        logger.info(f"📥 Import depuis {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nodes = data.get('nodes', [])
            relationships = data.get('relationships', [])
            
            # Importer les nœuds
            for node in nodes:
                n = node.get('n', {})
                labels = node.get('labels', [])
                if labels:
                    self.crud.create_node(labels[0], n)
            
            # Importer les relations
            for rel in relationships:
                source = rel.get('source')
                target = rel.get('target')
                rel_type = rel.get('type')
                properties = rel.get('properties', {})
                if source and target and rel_type:
                    self.crud.create_relationship(rel_type, source, target, properties)
            
            logger.info(f"✅ Import terminé : {len(nodes)} nœuds, {len(relationships)} relations")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur import : {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Migration de base de données")
    parser.add_argument("--action", choices=["export", "import"], required=True)
    parser.add_argument("--file", required=True, help="Fichier de migration")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.action == "export":
        success = migrator.export_to_json(args.file)
    elif args.action == "import":
        success = migrator.import_from_json(args.file)
    
    migrator.close()
    
    if success:
        logger.info("✅ Migration terminée avec succès")
        sys.exit(0)
    else:
        logger.error("❌ Migration échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()