# 📚 ONTOLOGIE DU PROJET GNL KNOWLEDGE GRAPH

## 📖 Introduction

Ce dossier contient l'ontologie complète du réseau de transport de Gaz Naturel Liquéfié (GNL). L'ontologie définit les concepts, entités et relations qui structurent notre graphe de connaissances.

## 🏗️ Structure

## 🎯 Objectifs

1. **Définir un langage commun** pour toutes les équipes
2. **Structurer les données** selon un modèle cohérent
3. **Faciliter l'interopérabilité** entre les systèmes
4. **Permettre l'évolution** du modèle

## 🔷 Principales Entités

### Types de Nœuds

| Entité | Description | Exemple |
|--------|-------------|---------|
| **Fournisseur** | Producteur/fournisseur de GNL | TotalEnergies |
| **Terminal** | Point de réception et distribution | Fos-sur-Mer |
| **Méthanier** | Navire de transport de GNL | GNL Explorer |
| **Pipeline** | Canalisation de transport | Nord-Sud |
| **Client** | Destinataire final | EDF |
| **Stockage** | Installation de stockage | Stockage Souterrain |
| **Compresseur** | Équipement de régulation | Compresseur Nord |
| **Incident** | Événement anormal | Fuite sur pipeline |

### Types de Relations

| Relation | Source → Cible | Description |
|----------|---------------|-------------|
| **FOURNIT** | Fournisseur → Terminal | Approvisionnement |
| **LIVRE_A** | Méthanier → Terminal | Livraison |
| **ALIMENTE** | Terminal → Pipeline | Alimentation |
| **DESSERT** | Pipeline → Client | Distribution |
| **STOCKE** | Terminal → Stockage | Stockage |
| **DEPEND_DE** | Pipeline → Compresseur | Dépendance |
| **AFFECTE** | Incident → Équipement | Impact |

## 📝 Format des Fichiers

Les fichiers sont au format YAML :

```yaml
entity_type:
  name: "Nom de l'entité"
  description: "Description détaillée"
  properties:
    - name: "propriété1"
      type: "string"
      required: true
    - name: "propriété2"
      type: "integer"
      required: false
  relationships:
    - type: "RELATION"
      target: "Cible"
      cardinality: "1:N"
    

Pour valider l'ontologie :

python -c "
import yaml
with open('ontology/gnl/ontology.yaml', 'r') as f:
    data = yaml.safe_load(f)
    print('✅ Ontologie valide')
"

📊 Visualisation
L'ontologie peut être visualisée avec :

bash
# Générer un diagramme
python scripts/visualize_ontology.py