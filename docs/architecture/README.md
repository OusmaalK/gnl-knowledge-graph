🌐 Ontologie GNL

Introduction

L'ontologie GNL est le modèle de données qui structure notre graphe de connaissances. Elle définit les concepts, les relations et les règles du domaine du transport de Gaz Naturel Liquéfié.

Concepts Fondamentaux

Entités (Nœuds)

| Entité      | Description                     | Exemples             |
|-------------|---------------------------------|----------------------|
| Fournisseur | Producteur/fournisseur de GNL   | TotalEnergies, Shell |
| Terminal    | Point de réception/distribution | Fos-sur-Mer, Montoir |
| Méthanier   | Navire de transport             | GNL Explorer         |
| Pipeline    | Canalisation de transport       | Nord-Sud             |
| Client      | Destinataire final              | EDF, Engie           |
| Stockage    | Installation de stockage        | Stockage Souterrain  |
| Compresseur | Équipement de régulation        | Compresseur Nord     |
| Incident    | Événement anormal               | Fuite sur pipeline   |
| Commande    | Transaction commerciale         | Commande GNL-2026    |

Relations

| Relation | Source → Cible         | Description       |
|----------|------------------------|-------------------|
| FOURNIT  | Fournisseur → Terminal | Approvisionnement |
| LIVRE_A  | Méthanier → Terminal   | Livraison         |
| ALIMENTE | Terminal → Pipeline    | Alimentation      |
| DESSERT  | Pipeline → Client      | Distribution      |
| STOCKE   | Terminal → Stockage    | Stockage          |
| DEPEND_DE| Pipeline → Compresseur | Dépendance        |
| AFFECTE  | Incident → Équipement  | Impact            |

Modèle de Données

Structure des Nœuds

Fournisseur:
  - id: string (FOUR-XXX)
  - nom: string
  - pays: string
  - ville: string
  - statut: enum (actif, inactif, suspendu)
  - created_at: datetime
  - updated_at: datetime

Terminal:
  - id: string (TERM-XXX)
  - nom: string
  - localisation: string
  - capacite_m3: integer
  - type: enum (LNG, CNG, LPG)
  - statut: enum (actif, en_construction, maintenance, hors_service)
  - created_at: datetime
  - updated_at: datetime

Pipeline:
  - id: string (PIPE-XXX)
  - nom: string
  - longueur_km: integer
  - pression_max_bar: integer
  - statut: enum (actif, en_test, maintenance, hors_service)
  - created_at: datetime
  - updated_at: datetime

Structure des Relations

FOURNIT:
  - quantite: integer
  - date: datetime
  - statut: enum (actif, suspendu)

AFFECTE:
  - date: datetime
  - impact: enum (direct, indirect, potentiel)
  - severite: enum (faible, moyen, eleve, critique)

Règles Métier
Validation des IDs
regex
Fournisseur: ^FOUR-\d{3,4}$
Terminal: ^TERM-\d{3,4}$
Pipeline: ^PIPE-\d{3,4}$
Incident: ^INC-\d{3,4}$
Client: ^CLIENT-\d{3,4}$
Compresseur: ^COMP-\d{3,4}$
Stockage: ^STOCK-\d{3,4}$
Commande: ^CMD-\d{3,4}$
Méthanier: ^METH-\d{3,4}$

Cardinalités

FOURNIT: Fournisseur (N) → Terminal (M)
ALIMENTE: Terminal (1) → Pipeline (N)
DESSERT: Pipeline (1) → Client (N)
AFFECTE: Incident (N) → Equipement (M)
DEPEND_DE: Pipeline (N) → Compresseur (M)
Évolution de l'Ontologie
Processus de Changement
Proposition : Description du changement

Revue : Évaluation par l'équipe

Validation : Approbation

Implémentation : Mise à jour

Migration : Données existantes

Documentation : Mise à jour de la doc

Versionnement

Version: 1.0.0
Format: MAJEUR.MINEUR.PATCH
  - MAJEUR: Changements incompatibles
  - MINEUR: Ajouts compatibles
  - PATCH: Corrections
Outils

Visualisation

Générer le diagramme de l'ontologie
python scripts/visualize_ontology.py

Générer la documentation
python scripts/generate_ontology_docs.py

Validation

Valider l'ontologie
python scripts/validate_ontology.py

Valider une instance
python scripts/validate_instance.py --file data/instance.json