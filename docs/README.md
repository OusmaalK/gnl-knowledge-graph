
📚 GNL Knowledge Graph - Documentation

Bienvenue dans la documentation du projet GNL Knowledge Graph.

📖 Introduction

Ce projet vise à construire un graphe de connaissances pour le réseau de transport de Gaz Naturel Liquéfié (GNL). Il permet de modéliser les relations complexes entre les fournisseurs, terminaux, pipelines, clients et incidents.

🏗️ Structure de la Documentation
docs/
├── README.md  Ce fichier
├── architecture/  Documentation d'architecture
│ ├── architecture-overview.md  Vue d'ensemble
│ ├── data-flow.md  Flux de données
│ └── security.md Sécurité
├── ontology/  Documentation de l'ontologie
│ ├── ontology-schema.md  Schéma de l'ontologie
│ ├── competency-questions.md  Questions de compétence
│ └── validation.md  Validation
└── operations/  Documentation opérationnelle
├── deployment-guide.md  Guide de déploiement
├── monitoring.md  Monitoring
└── runbooks.md  Runbooks

🚀 Quick Start

Prérequis
- Python 3.11+
- Docker et Docker Compose
- Neo4j 5.14+
- Git

Installation
Cloner le dépôt
git clone https://gitlab.com/gnl-knowledge-graph.git
cd gnl-knowledge-graph

Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows

Installer les dépendances
pip install -r requirements.txt

Configurer l'environnement
cp .env.example .env
Éditer .env avec vos paramètres

Démarrer les services
docker-compose up -d

Initialiser la base de données
python scripts/setup/init_db.py

Lancer l'API
python -m src.api.app

📊 Architecture

Le projet est basé sur une architecture microservices avec :

Neo4j               : Base de données graphe
Qdrant              : Base de données vectorielle
Kafka               : Messagerie et streaming
Redis               : Cache et mémoire
FastAPI             : API REST
LangChain/LangGraph : Agents IA
React/Next.js       : Interface utilisateur

🎯 Fonctionnalités Principales

Ontologie GNL        : Modélisation du réseau de transport
Ingestion de données : Import depuis CSV, JSON, APIs
Analyse avancée      : Impact, routes, risques
Agents IA            : Diagnostic, logistique, maintenance
Interface utilisateur: Dashboard, chat, visualisation

📋 Phases du Projet
Phase	Description	Statut
Phase 0	Ontologie et cadrage	    ✅ Terminée
Phase 1	Ingestion et intégration	✅ Terminée
Phase 2	Construction du réseau	    ✅ Terminée
Phase 3	Agents IA et GraphRAG	    ✅ Terminée
Phase 4	Mise en production	        🔄 En cours

🔗 Liens Utiles
Documentation API
Neo4j Browser
Qdrant Dashboard

👥 Équipe
Chef de projet : Ousmaal Khaled
Ontologue      : Ousmaal Khaled
Développeurs   : Ousmaal Khaled
DevOps         : Ousmaal Khaled

📝 Licence
Propriétaire - GNL Company
Pour toute question, contactez : ousmaalk@gmail.com

🔷 ARCHITECTURE
📄 FICHIER : `docs/architecture/README.md`

🏗️ Architecture du Projet

Vue d'Ensemble
L'architecture du GNL Knowledge Graph est conçue pour être scalable, résiliente et maintenable. Elle repose sur des composants éprouvés et suit les bonnes pratiques de l'industrie.

Principes d'Architecture
1. Séparation des préoccupations : Chaque composant a une responsabilité unique
2. Scalabilité horizontale       : Les services peuvent être répliqués
3. Découplage                    : Les services communiquent via des interfaces bien définies
4. Observabilité                 : Tous les composants sont monitorés
5. Sécurité                      : Authentification et autorisation à tous les niveaux

Architecture Générale
┌─────────────────────────────────────────────────────────────────────┐
│ Interface Utilisateur                                               │
│ (React / Next.js / Cytoscape)                                       │
└─────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ API Gateway (FastAPI)                                               │
│ Authentification / Routage                                          │
└─────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ Agents IA (LangGraph)                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│ │ Diagnostic   │ │ Logistics    │ │ Maintenance  │                  │
│ └──────────────┘ └──────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ Couche de Données                                                   │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│ │Neo4j (Graphe)│ │ Qdrant (Vect)│ │ Redis (Cache)│                  │
│ └──────────────┘ └──────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ Ingestion de Données                                                │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│ │ Kafka        │ │ MQTT         │ │ CSV/JSON     │                  │
│ └──────────────┘ └──────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘


Composants Principaux
1. Interface Utilisateur (Frontend)
- Framework : Next.js 14
- Visualisation : Cytoscape.js
- UI : Tailwind CSS

2. API (Backend)
- Framework : FastAPI
- Authentification : JWT + API Key
- Documentation : OpenAPI (Swagger)

3. Agents IA
- Framework : LangChain / LangGraph
- Modèles : Llama 3 via Ollama
- Outils : GraphTools, LLMTools

4. Base de Données
- Graphe : Neo4j 5.14
- Vectorielle : Qdrant 1.7
- Cache : Redis 7.2

5. Messagerie
- Streaming : Kafka 3.4
- IoT : MQTT

Flux de Données

1. Ingestion     : Données → Kafka → Normalisation → Neo4j
2. Requête       : API → Agents → Neo4j → Réponse
3. Visualisation : Frontend → API → Neo4j → Cytoscape

Sécurité
- Authentification : JWT + API Key
- Autorisation     : RBAC (Role-Based Access Control)
- Chiffrement      : TLS pour toutes les communications
- Secrets          : HashiCorp Vault / Kubernetes Secrets

Performance

- Cache      : Redis pour les requêtes fréquentes
- Indexation : Index Neo4j optimisés
- Limitation : Rate limiting sur l'API

Résilience

- Réplication : Services répliqués (Kubernetes)
- Backup      : Sauvegardes automatiques Neo4j
- Monitoring  : Prometheus + Grafana
- Alertes     : AlertManager

Évolutions Futures

- Intégration de données IoT en temps réel
- Ajout de nouveaux types d'agents
- Interface utilisateur enrichie
- API publique


📋 RÉSUMÉ DES FICHIERS DOCS

| Dossier       | Fichier                    | Description                 |
|---------------|----------------------------|-----------------------------|
| root          | `README.md`                | Documentation principale    |
| architecture/ | `README.md`                | Vue d'ensemble architecture |
|               | `architecture-overview.md` | Architecture détaillée      |
|               | `data-flow.md`             | Flux de données             |
|               | `security.md`              | Sécurité                    |
| ontology/     | `README.md`                | Ontologie                   |
|               | `ontology-schema.md`       | Schéma de l'ontologie       |
|               | `competency-questions.md`  | Questions de compétence     |
|               | `validation.md`            | Validation                  |
| operations/   | `README.md`                | Opérations                  |
|               | `deployment-guide.md`      | Guide de déploiement        |
|               | `monitoring.md`            | Monitoring                  |
|               | `runbooks.md`              | Runbooks                    |

Total : 13 fichiers** ✅