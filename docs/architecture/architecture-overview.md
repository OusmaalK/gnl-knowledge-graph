 🏛️ Architecture - Vue d'Ensemble

Vision du Projet

Le GNL Knowledge Graph est un système intelligent qui modélise l'ensemble du réseau de transport de Gaz Naturel Liquéfié. Il permet de :

1. Visualiser les relations complexes entre les acteurs du réseau
2. Analyser l'impact des incidents et des pannes
3. Prédire les risques et les tendances
4. Optimiser les routes et la logistique
5. Automatiser les décisions via des agents IA

Architecture Technique

Stack Technologique

| Couche          | Technologies                            |
|-----------------|-----------------------------------------|
| Frontend        | Next.js, React, Cytoscape, Tailwind CSS |
| API             | FastAPI, Pydantic, Uvicorn              |
| Agents          | LangChain, LangGraph, Ollama            |
| Base de données | Neo4j, Qdrant, Redis                    |
| Messagerie      | Kafka, MQTT                             |
| Orchestration   | Kubernetes, Helm, Terraform             |
| Monitoring      | Prometheus, Grafana, OpenTelemetry      |
| CI/CD           | GitLab CI / GitHub Actions              |

Architecture des Microservices
┌─────────────────────────────────────┐
│ API Gateway (FastAPI)               │
│ Port: 8000 / Routes: /api/* / /docs │
└─────────────────────────────────────┘
                   │
┌──────────────────┼─────────────────┐
│                  │                 │
▼                  ▼                 ▼
┌────────────┐ ┌──────────────┐ ┌─────────────┐
│ Diagnostic │ │ Logistics    │ │ Maintenance │
│ Agent      │ │ Agent        │ │ Agent       │
│ Port: 8001 │ │ Port: 8002   │ │ Port: 8003  │
└────────────┘ └──────────────┘ └─────────────┘
│                     │                 │
└─────────────────────┼─────────────────┘
                      │
                      ▼
┌────────────────────────────────┐
│ Neo4j (Base de données graphe) │
│ Port: 7474 / 7687              │
└────────────────────────────────┘
                │
┌───────────────┼────────────────┐
│               │                │
▼               ▼                ▼
┌────────────┐ ┌────────────┐ ┌─────────────┐
│ Qdrant     │ │ Redis      │ │ Kafka       │
│ (Vecteurs) │ │ (Cache)    │ │ (Streaming) │
│ Port: 6333 │ │ Port: 6379 │ │ Port: 9092  │
└────────────┘ └────────────┘ └─────────────┘


Composants Détaillés

1. API Gateway (FastAPI)

- Rôle : Point d'entrée unique pour les clients
- Fonctionnalités :
  - Routage des requêtes
  - Authentification (JWT + API Key)
  - Validation des données (Pydantic)
  - Documentation OpenAPI
  - Rate limiting
  - Logging structuré

2. Agents IA (LangGraph)

Diagnostic Agent
- Rôle : Analyser et diagnostiquer les incidents
- Capacités :
  - `diagnose_incident()` : Analyser un incident
  - `analyze_pattern()` : Détecter des patterns
  - `suggest_solution()` : Proposer des solutions

Logistics Agent
- Rôle : Optimiser les routes et la logistique
- Capacités :
  - `find_best_route()` : Trouver la route optimale
  - `find_alternative_route()` : Routes alternatives
  - `analyze_impact()` : Analyser l'impact

Maintenance Agent
- Rôle : Maintenance prédictive
- Capacités :
  - `analyze_risk()` : Évaluer les risques
  - `plan_maintenance()` : Planifier la maintenance
  - `get_critical_equipment()` : Équipements critiques

3. Base de Données

Neo4j (Graphe)
- Nœuds : 9 types (Fournisseur, Terminal, Pipeline, etc.)
- Relations : 8 types (FOURNIT, ALIMENTE, etc.)
- Index : Optimisés pour la performance

Qdrant (Vecteurs)
- Collections : Incidents, Maintenance, Logistique
- Embeddings : BGE-M3 (1024 dimensions)
- Recherche : Similarité cosinus

Redis (Cache)
- TTL : Configurable par type de donnée
- Stratégie : LRU (Least Recently Used)

4. Ingestion de Données

Kafka
- Topics : iot, tracking, incidents, pipelines
- Partitions : Configurées par topic
- Retention : 7 jours (configurable)

Connecteurs
- IoT : MQTT → Kafka
- SAP : CSV → Neo4j
- Tracking : AIS → Kafka
- Rapports : JSON → Neo4j

Scalabilité

Stratégies de Scalabilité

1. Horizontal : Réplication des pods Kubernetes
2. Vertical : Augmentation des ressources
3. Database : Réplication Neo4j, sharding Qdrant
4. Cache : Redis Cluster

Limites Actuelles

| Service | Limite      | Plan d'évolution |
|---------|-------------|------------------|
| Neo4j   | 100k nœuds  | Cluster Neo4j    |
| Qdrant  | 1M vecteurs | Sharding         |
| API     | 1000 req/s  | Load Balancer    |
| Agents  | 100 req/s   | Autoscaling      |

Sécurité

Authentification
- API : JWT + API Key
- Neo4j : Username / Password
- Kafka : SASL/SCRAM

Autorisation
- RBAC : Rôles (admin, analyst, viewer)
- Neo4j : Permissions par nœud/relation
- API : Scopes par endpoint

Chiffrement
- TLS : Toutes les communications externes
- Données : Chiffrement au repos (Neo4j Enterprise)

Monitoring

Métriques
- Performance : Temps de réponse, latence
- Erreurs : Taux d'erreur, exceptions
- Système : CPU, mémoire, disque
- Business : Incidents, clients, risques

Alertes
- Critiques : API down, Neo4j down
- Warning : Temps de réponse élevé, cache faible
- Info : Déploiement, backup

Dashboards
- Grafana : Dashboards personnalisés
- Prometheus : Métriques en temps réel
- Kibana : Logs centralisés