#!/usr/bin/env python
"""
Script d'initialisation de l'ontologie
Version corrigée - Stockage simplifié
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent (backend) au PYTHONPATH
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import logging
import yaml
import json
from src.graph.operations.crud import GraphCRUD

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_ontology(ontology_path: str):
    """
    Charge l'ontologie dans Neo4j
    """
    logger.info("🚀 Initialisation de l'ontologie...")
    logger.info(f"📁 Fichier : {ontology_path}")
    
    # Chercher le fichier dans différents emplacements
    possible_paths = [
        ontology_path,
        Path(__file__).parent.parent.parent.parent / ontology_path,
        Path(__file__).parent.parent.parent.parent / "ontology" / "gnl" / "ontology.yaml",
        Path(__file__).parent.parent.parent / "ontology" / "gnl" / "ontology.yaml",
    ]
    
    found_path = None
    for path in possible_paths:
        if Path(path).exists():
            found_path = path
            break
    
    if not found_path:
        logger.error(f"❌ Fichier non trouvé : {ontology_path}")
        logger.info(f"🔍 Recherché dans : {possible_paths}")
        sys.exit(1)
    
    # Charger le fichier YAML
    try:
        with open(found_path, 'r', encoding='utf-8') as f:
            ontology = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"❌ Erreur chargement YAML : {e}")
        sys.exit(1)
    
    crud = GraphCRUD()
    if not crud.connect():
        logger.error("❌ Connexion à Neo4j impossible")
        sys.exit(1)
    
    # Supprimer l'ancienne ontologie si elle existe
    try:
        crud.execute_query("MATCH (n:Ontologie) DETACH DELETE n")
        crud.execute_query("MATCH (n:EntiteOntologie) DETACH DELETE n")
        crud.execute_query("MATCH (n:RelationOntologie) DETACH DELETE n")
        logger.info("🗑️ Ancienne ontologie supprimée")
    except:
        pass
    
    # Créer le nœud d'ontologie
    logger.info("📝 Création du nœud d'ontologie...")
    crud.create_node('Ontologie', {
        'id': 'ontologie_gnl',
        'nom': 'Ontologie GNL',
        'version': ontology.get('version', '1.0.0'),
        'created_at': '2026-07-11',
        'nb_entites': len(ontology.get('entities', {})),
        'nb_relations': len(ontology.get('relationships', {}))
    })
    
    # Créer les entités - Stockage simplifié
    logger.info("📝 Création des entités...")
    entities = ontology.get('entities', {})
    for entity_name, entity_data in entities.items():
        # Extraire les propriétés simples
        props = []
        for p in entity_data.get('properties', []):
            props.append({
                'name': p.get('name', ''),
                'type': p.get('type', 'string'),
                'required': p.get('required', False),
                'description': p.get('description', '')
            })
        
        crud.create_node('EntiteOntologie', {
            'id': entity_name,
            'nom': entity_name,
            'description': entity_data.get('description', ''),
            'nb_proprietes': len(props),
            'proprietes': json.dumps(props, ensure_ascii=False)  # Stocker en JSON
        })
        logger.info(f"   ✅ {entity_name}")
    
    # Créer les relations - Stockage simplifié
    logger.info("📝 Création des relations...")
    relationships = ontology.get('relationships', {})
    for rel_name, rel_data in relationships.items():
        crud.create_node('RelationOntologie', {
            'id': rel_name,
            'nom': rel_name,
            'description': rel_data.get('description', ''),
            'source': rel_data.get('source', ''),
            'target': rel_data.get('target', ''),
            'cardinality': rel_data.get('cardinality', '')
        })
        logger.info(f"   ✅ {rel_name}")
    
    crud.close()
    logger.info("✅ Ontologie initialisée avec succès !")
    logger.info(f"📊 {len(entities)} entités et {len(relationships)} relations créées")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="ontology/gnl/ontology.yaml", help="Fichier d'ontologie")
    args = parser.parse_args()
    load_ontology(args.file)