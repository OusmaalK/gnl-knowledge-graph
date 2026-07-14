markdown
# 🌐 ONTOLOGIE GNL

## 📖 Introduction

Cette ontologie définit les concepts spécifiques au domaine du transport de Gaz Naturel Liquéfié (GNL).

## 🏗️ Structure
gnl/
├── entities/ # Types de nœuds GNL
├── relationships/ # Types de relations GNL
├── agents/ # Outils pour agents IA
└── validation/ # Tests de validation

text

## 🔷 Entités GNL

### Fournisseur
Producteur ou fournisseur de GNL.

**Propriétés :**
- `id`: Identifiant unique
- `nom`: Nom du fournisseur
- `pays`: Pays d'origine
- `ville`: Ville du siège
- `statut`: Actif, inactif, suspendu

### Terminal
Point de réception et distribution de GNL.

**Propriétés :**
- `id`: Identifiant unique
- `nom`: Nom du terminal
- `localisation`: Lieu
- `capacite_m3`: Capacité en m³
- `type`: LNG, CNG, LPG
- `statut`: Actif, en construction, maintenance

### Méthanier
Navire de transport de GNL.

**Propriétés :**
- `id`: Identifiant unique
- `nom`: Nom du navire
- `capacite_m3`: Capacité en m³
- `statut`: En croisière, à quai, en chargement

### Pipeline
Canalisation de transport de GNL.

**Propriétés :**
- `id`: Identifiant unique
- `nom`: Nom du pipeline
- `longueur_km`: Longueur en km
- `pression_max_bar`: Pression maximale
- `statut`: Actif, en test, maintenance

## 🔗 Relations GNL

### FOURNIT
Relation entre un fournisseur et un terminal.

### ALIMENTE
Relation entre un terminal et un pipeline.

### DESSERT
Relation entre un pipeline et un client.

### AFFECTE
Relation entre un incident et un équipement.

## 🎯 Utilisation

### Charger l'ontologie

```python
import yaml

with open('ontology/gnl/ontology.yaml', 'r') as f:
    ontology = yaml.safe_load(f)
Valider une entité
python
from src.utils.validators import Validators

validator = Validators()
result = validator.validate_pipeline_data({
    'id': 'PIPE-001',
    'nom': 'Nord-Sud',
    'longueur_km': 200
})