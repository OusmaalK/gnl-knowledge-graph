⚙️ Configuration de la Plateforme GNL Knowledge Graph

📖 Introduction

Ce dossier contient tous les fichiers de configuration pour la plateforme GNL Knowledge Graph. La configuration est organisée par environnement (dev, prod) et par composant partagé.

📂 Structure
config/
├── dev/ # Configuration de développement
├── prod/ # Configuration de production
└── shared/ # Configuration partagée

🔧 Environnements

Dev (Développement)
- Ressources minimales
- Logs détaillés
- Debug activé
- Rechargement automatique

Prod (Production)
- Ressources optimisées
- Logs réduits
- Debug désactivé
- Haute disponibilité

📋 Composants

Application (`app_config.yaml`)
- Configuration générale de l'application
- Variables d'environnement
- Fonctionnalités activées/désactivées

Neo4j (`neo4j_config.yaml`)
- Connexion à la base de données graphe
- Paramètres de performance
- Configuration des indexes

Kafka (`kafka_config.yaml`)
- Configuration des topics
- Paramètres de streaming
- Gestion des partitions

Qdrant (`qdrant_config.yaml`)
- Configuration de la base vectorielle
- Collections d'embeddings
- Paramètres de recherche

Logging (`logging.yaml`)
- Configuration des logs
- Niveaux de log
- Format des logs

Monitoring (`monitoring.yaml`)
- Métriques Prometheus
- Dashboards Grafana
- Alertes

Alerts (`alerts.yaml`)
- Règles d'alertes
- Seuils de notification
- Canaux de notification

🚀 Utilisation

Charger la configuration

import yaml

def load_config(env="dev"):
    with open(f"config/{env}/app_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    return config
Modifier la configuration
Modifier le fichier YAML correspondant

Redémarrer l'application

Vérifier les changements

🔒 Sécurité
Les secrets sont stockés dans .env et Kubernetes Secrets

Les mots de passe ne sont pas versionnés

Les configurations sensibles sont exclues du Git

📝 Notes
Les fichiers YAML sont commentés pour faciliter la compréhension

Les valeurs par défaut sont définies dans chaque fichier

Les configurations d'environnement peuvent être surchargées