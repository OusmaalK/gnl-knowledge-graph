Introduction

Ce document décrit les flux de données à travers le système GNL Knowledge Graph.

Flux Globaux

1. Flux d'Ingestion
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────┐
│ Données │───▶ │Kafka        │───▶│ Normalize   │───▶ │ Neo4j  │
│ Sources │     │ (Stream)    │     │ (Process)   │     │ (Store)│
└─────────┘     └─────────────┘     └─────────────┘     └────────┘

text

2. Flux d'Analyse
┌─────────────┐     ┌─────────────┐    ┌─────────────┐     ┌─────────┐
│ Requête     │───▶│ Agent IA    │───▶│ Neo4j       │───▶│ Réponse │
│ Utilisateur │     │ (Process)   │    │ (Query)     │     │(Result) │
└─────────────┘     └─────────────┘    └─────────────┘     └─────────┘

Flux Détaillés

Ingestion des Données SAP


Source: Fichiers CSV (fournisseurs, terminaux, pipelines)
Étapes:
  1. Lecture du CSV
  2. Normalisation des données
  3. Création des nœuds Neo4j
  4. Création des relations
  5. Indexation

Fréquence: Quotidienne
Responsable: Ingestion Service
Ingestion des Incidents

Source: Fichiers JSON / Rapports
Étapes:
  1. Lecture du JSON
  2. Validation des données
  3. Extraction des entités
  4. Création des nœuds Incident
  5. Liaison aux équipements

Fréquence: Continue
Responsable: Reports Connector
Ingestion des Données IoT

Source: Capteurs (MQTT)
Étapes:
  1. Réception MQTT
  2. Envoi vers Kafka
  3. Normalisation
  4. Stockage dans Neo4j

Fréquence: Temps réel (5s)
Responsable: IoT Connector
Requête d'Analyse

Source: Utilisateur (API / Interface)
Étapes:
  1. Authentification
  2. Validation de la requête
  3. Sélection de l'agent
  4. Exécution de la logique
  5. Requête Neo4j
  6. Génération de la réponse
  7. Retour à l'utilisateur

Temps: < 3 secondes
Responsable: API + Agents
Modèles de Données
Nœuds

Fournisseur:
  - id: string (FOUR-XXX)
  - nom: string
  - pays: string
  - ville: string
  - statut: enum

Terminal:
  - id: string (TERM-XXX)
  - nom: string
  - localisation: string
  - capacite_m3: integer
  - statut: enum

Pipeline:
  - id: string (PIPE-XXX)
  - nom: string
  - longueur_km: integer
  - pression_max_bar: integer
  - statut: enum

Incident:
  - id: string (INC-XXX)
  - description: string
  - gravite: enum
  - date: datetime
  - cause: string
  - duree_min: integer

Relations

FOURNIT:
  - source: Fournisseur
  - target: Terminal
  - propriétés: quantite, date

ALIMENTE:
  - source: Terminal
  - target: Pipeline
  - propriétés: debit

DESSERT:
  - source: Pipeline
  - target: Client
  - propriétés: volume

AFFECTE:
  - source: Incident
  - target: Equipement
  - propriétés: date, impact
Optimisation des Flux
Cache
Redis : Cache des requêtes fréquentes

TTL : 1 heure pour les analyses courantes

Invalidation : Automatique lors des mises à jour

Indexation
Neo4j : Index sur id pour tous les nœuds

Composite : Index sur (type, statut)

Full-text : Sur les descriptions

Batch Processing
Taille : 1000 enregistrements par lot

Fréquence : 15 minutes

Transaction : Une transaction par lot

Supervision
Métriques de Flux

Ingestion:
  - records_processed: count
  - records_failed: count
  - duration_seconds: histogram

Requêtes:
  - requests_total: counter
  - request_duration: histogram
  - query_error_rate: gauge

Cache:
  - hit_rate: gauge
  - miss_rate: gauge
  - size: gauge
Alertes

Critiques:
  - Taux d'erreur > 5%
  - Temps de réponse > 10s
  - Cache hit < 50%

Warnings:
  - Ingestion échouée
  - Neo4j disconnect
  - Kafka lag > 1000
Évolutions Futures
Streaming temps réel : Réduction de la latence

Data Lake : Stockage des données brutes

ML Pipelines : Intégration de modèles ML

Federated Queries : Requêtes multi-sources