📐 Schéma de l'Ontologie

## Vue d'Ensemble
┌─────────────────────────────────────────────────────────────────────────────┐
│ ONTOLOGIE GNL │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ FOURNISSEUR │────▶│ TERMINAL │────▶│ PIPELINE │ │
│ │ │ │ │ │ │ │
│ │ - id │ │ - id │ │ - id │ │
│ │ - nom │ │ - nom │ │ - nom │ │
│ │ - pays │ │ - localisation│ │ - longueur │ │
│ │ - ville │ │ - capacite │ │ - pression │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │ │ │ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ METHANIER │ │ STOCKAGE │ │ CLIENT │ │
│ │ │ │ │ │ │ │
│ │ - id │ │ - id │ │ - id │ │
│ │ - nom │ │ - nom │ │ - nom │ │
│ │ - capacite │ │ - capacite │ │ - contrat │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ COMPRESSEUR │ │ INCIDENT │ │
│ │ │ │ │ │
│ │ - id │ │ - id │ │
│ │ - nom │ │ - description│ │
│ │ - puissance │ │ - gravite │ │
│ └──────────────┘ │ - date │ │
│ │ - cause │ │
│ └──────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘

text

## Relations Détaillées

### FOURNIT

```yaml
Type: Relation
Source: Fournisseur
Target: Terminal
Cardinalité: N:M
Propriétés:
  - quantite: integer (quantité fournie)
  - date: datetime (date de fourniture)
  - statut: enum (actif, suspendu)
Exemple:
  - Source: FOUR-001 (TotalEnergies)
  - Target: TERM-001 (Fos-sur-Mer)
  - Propriétés: {quantite: 100000, date: "2026-01-01", statut: "actif"}
ALIMENTE
yaml
Type: Relation
Source: Terminal
Target: Pipeline
Cardinalité: 1:N
Propriétés:
  - debit: float (débit en m³/s)
  - date: datetime (date d'alimentation)
  - statut: enum (actif, suspendu)
Exemple:
  - Source: TERM-001 (Fos-sur-Mer)
  - Target: PIPE-001 (Nord-Sud)
  - Propriétés: {debit: 50, date: "2026-07-10", statut: "actif"}
DESSERT
yaml
Type: Relation
Source: Pipeline
Target: Client
Cardinalité: 1:N
Propriétés:
  - volume: integer (volume distribué)
  - contrat: string (référence contrat)
  - date_debut: datetime
  - statut: enum (actif, suspendu, termine)
Exemple:
  - Source: PIPE-001 (Nord-Sud)
  - Target: CLIENT-001 (EDF)
  - Propriétés: {volume: 200, contrat: "GNL-2026-001", statut: "actif"}
AFFECTE
yaml
Type: Relation
Source: Incident
Target: Equipement
Cardinalité: N:M
Propriétés:
  - date: datetime (date d'affectation)
  - impact: enum (direct, indirect, potentiel)
  - severite: enum (faible, moyen, eleve, critique)
Exemple:
  - Source: INC-001 (Fuite sur pipeline)
  - Target: PIPE-001 (Nord-Sud)
  - Propriétés: {date: "2026-07-08", impact: "direct", severite: "critique"}
DEPEND_DE
yaml
Type: Relation
Source: Pipeline
Target: Compresseur
Cardinalité: N:M
Propriétés:
  - type: enum (pression, debit, controle)
  - niveau: enum (critique, important, secondaire)
  - date_debut: datetime
Exemple:
  - Source: PIPE-001 (Nord-Sud)
  - Target: COMP-001 (Compresseur Nord)
  - Propriétés: {type: "pression", niveau: "critique"}
STOCKE
yaml
Type: Relation
Source: Terminal
Target: Stockage
Cardinalité: 1:N
Propriétés:
  - capacite_utilisee: integer
  - date: datetime
Exemple:
  - Source: TERM-001 (Fos-sur-Mer)
  - Target: STOCK-001 (Stockage Souterrain)
  - Propriétés: {capacite_utilisee: 200000, date: "2026-07-10"}
LIVRE_A
yaml
Type: Relation
Source: Méthanier
Target: Terminal
Cardinalité: N:1
Propriétés:
  - date: datetime
  - quantite: integer
  - statut: enum (planifie, en_cours, termine, annule)
Exemple:
  - Source: METH-001 (GNL Explorer)
  - Target: TERM-001 (Fos-sur-Mer)
  - Propriétés: {date: "2026-07-10", quantite: 150000, statut: "termine"}
Schéma Complet
Fichier YAML
Le schéma complet est disponible dans :
ontology/gnl/ontology.yaml

Validation
bash
# Valider le schéma
python scripts/validate_schema.py --file ontology/gnl/ontology.yaml

# Valider une instance
python scripts/validate_instance.py --schema ontology/gnl/ontology.yaml --instance data/instance.json