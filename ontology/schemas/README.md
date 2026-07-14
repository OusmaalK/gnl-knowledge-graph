markdown
# 📐 SCHEMAS DE VALIDATION

## 📖 Introduction

Ce dossier contient les schémas de validation pour les données du projet GNL Knowledge Graph.

## 📁 Structure
schemas/
├── entities/ # Schémas pour les entités
├── relationships/ # Schémas pour les relations
└── queries/ # Schémas pour les requêtes

text

## 🔧 Utilisation

### Valider une entité

```python
from jsonschema import validate
import json

with open('schemas/entities/pipeline.json', 'r') as f:
    schema = json.load(f)

data = {
    "id": "PIPE-001",
    "nom": "Nord-Sud",
    "longueur_km": 200
}

validate(instance=data, schema=schema)
Valider une relation
python
with open('schemas/relationships/fournit.json', 'r') as f:
    schema = json.load(f)

data = {
    "source": "FOUR-001",
    "target": "TERM-001",
    "quantite": 100000
}

validate(instance=data, schema=schema)
📋 Schémas Disponibles
Fichier	Description
entities/fournisseur.json	Schéma Fournisseur
entities/pipeline.json	Schéma Pipeline
entities/incident.json	Schéma Incident
relationships/fournit.json	Schéma FOURNIT
relationships/affecte.json	Schéma AFFECTE
🔄 Génération des Schémas
Les schémas sont générés automatiquement à partir de l'ontologie :

bash
python scripts/generate_schemas.py
