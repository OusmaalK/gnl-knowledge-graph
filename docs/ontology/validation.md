✅ Validation de l'Ontologie

## Introduction

Ce document décrit le processus de validation de l'ontologie GNL.

## Types de Validation

### 1. Validation Syntaxique

Vérifie que l'ontologie est syntaxiquement correcte.

```yaml
Contrôles:
  - Fichier YAML valide
  - Structure conforme
  - Types corrects
  - Références valides

Outil: yamllint
Commande: yamllint ontology/gnl/ontology.yaml
2. Validation Sémantique
Vérifie que l'ontologie est cohérente avec le domaine.

yaml
Contrôles:
  - Concepts corrects
  - Relations cohérentes
  - Cardinalités valides
  - Propriétés adéquates

Outil: Script de validation
Commande: python scripts/validate_ontology.py
3. Validation des Données
Vérifie que les données respectent l'ontologie.

yaml
Contrôles:
  - IDs valides
  - Types de données
  - Enums corrects
  - Relations valides
  - Contraintes métier

Outil: Validators
Commande: python scripts/validate_data.py
Tests de Validation
Test des IDs
python
def test_ids():
    valid_ids = [
        "FOUR-001", "TERM-001", "PIPE-001",
        "INC-001", "CLIENT-001", "COMP-001"
    ]
    invalid_ids = [
        "FOUR-01", "TERM-01", "PIPE-01",
        "INC-01", "CLIENT-01", "COMP-01"
    ]
    
    for id in valid_ids:
        assert validate_id(id) == True
    for id in invalid_ids:
        assert validate_id(id) == False
Test des Types
python
def test_types():
    data = {
        "id": "PIPE-001",
        "nom": "Nord-Sud",
        "longueur_km": 200,
        "statut": "actif"
    }
    
    assert validate_pipeline(data) == True
    
    data_bad = {
        "id": "PIPE-001",
        "nom": "Nord-Sud",
        "longueur_km": "200",  # Mauvais type
        "statut": "actif"
    }
    assert validate_pipeline(data_bad) == False
Test des Relations
python
def test_relationships():
    # Test FOURNIT
    source = "FOUR-001"
    target = "TERM-001"
    assert validate_relationship("FOURNIT", source, target) == True
    
    # Test ALIMENTE
    source = "TERM-001"
    target = "PIPE-001"
    assert validate_relationship("ALIMENTE", source, target) == True
    
    # Test invalid
    source = "FOUR-001"
    target = "CLIENT-001"
    assert validate_relationship("ALIMENTE", source, target) == False
Validation Continue
CI/CD Pipeline
yaml
validate-ontology:
  stage: validate
  script:
    - yamllint ontology/gnl/ontology.yaml
    - python scripts/validate_ontology.py
    - python scripts/validate_data.py --all
  only:
    - merge_requests
    - main
Métriques de Validation
yaml
Métriques:
  - Couverture: 100%
  - Taux de validation: 99.5%
  - Taux d'erreur: < 1%
  - Temps de validation: < 5s
Rapports de Validation
Exemple de Rapport
yaml
Date: 2026-07-10
Version: 1.0.0
Résultats:
  - Tests syntaxiques: 5/5 ✅
  - Tests sémantiques: 8/8 ✅
  - Tests de données: 12/12 ✅
  - Tests de relations: 6/6 ✅
Conclusion: ✅ Ontologie validée
Outils de Validation
1. Yamllint
bash
# Installer
pip install yamllint

# Utiliser
yamllint ontology/gnl/ontology.yaml
2. Script Python
python
# scripts/validate_ontology.py
import yaml
import json
from pathlib import Path

def validate_ontology(filepath):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    # Validation des entités
    entities = data.get('entities', {})
    for name, entity in entities.items():
        assert 'properties' in entity
        assert 'description' in entity
        
    # Validation des relations
    relationships = data.get('relationships', {})
    for name, rel in relationships.items():
        assert 'source' in rel
        assert 'target' in rel
        
    print(f"✅ Ontologie validée: {filepath}")

if __name__ == "__main__":
    validate_ontology("ontology/gnl/ontology.yaml")
3. Validation JSON Schema
json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "entities": {
      "type": "object",
      "patternProperties": {
        "^[A-Za-z]+$": {
          "type": "object",
          "properties": {
            "description": {"type": "string"},
            "properties": {"type": "array"}
          },
          "required": ["description", "properties"]
        }
      }
    }
  },
  "required": ["entities", "relationships"]
}
Conclusion
La validation de l'ontologie est un processus continu qui garantit la qualité et la cohérence des données du projet GNL Knowledge Graph. Toutes les validations sont automatisées et intégrées dans le pipeline CI/CD.