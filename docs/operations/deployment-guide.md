🚀 Guide de Déploiement

## Introduction

Ce guide décrit les procédures de déploiement du GNL Knowledge Graph.

## Prérequis

### Outils

```yaml
Requis:
  - Docker 20.10+
  - Docker Compose 2.0+
  - Kubernetes 1.25+
  - Helm 3.0+
  - kubectl 1.25+
  - Terraform 1.0+
Infrastructure
yaml
Minimum:
  - CPU: 4 cores
  - RAM: 16 GB
  - Storage: 50 GB

Recommandé:
  - CPU: 8 cores
  - RAM: 32 GB
  - Storage: 100 GB
Déploiement Local (Docker Compose)
Étape 1: Configuration
bash
# Cloner le dépôt
git clone https://gitlab.com/gnl-knowledge-graph.git
cd gnl-knowledge-graph

# Copier la configuration
cp .env.example .env

# Éditer .env
nano .env
Étape 2: Démarrer les Services
bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f
Étape 3: Initialiser la Base de Données
bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Initialiser Neo4j
python scripts/setup/init_db.py

# Initialiser les topics Kafka
python scripts/setup/init_kafka.py

# Initialiser l'ontologie
python scripts/setup/init_ontology.py
Étape 4: Importer les Données
bash
# Importer les CSV
python src/ingestion/import_csv.py

# Importer les JSON
python src/ingestion/import_json.py
Étape 5: Lancer l'Application
bash
# Démarrer l'API
python -m src.api.app

# OU avec uvicorn
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
Déploiement Kubernetes
Étape 1: Préparer le Cluster
bash
# Créer le namespace
kubectl create namespace gnl-knowledge-graph

# Créer les secrets
kubectl create secret generic gnl-secrets \
  --namespace gnl-knowledge-graph \
  --from-env-file=.env
Étape 2: Déployer avec Kustomize
bash
# Développement
kubectl apply -k deploy/kubernetes/overlays/dev/

# Staging
kubectl apply -k deploy/kubernetes/overlays/staging/

# Production
kubectl apply -k deploy/kubernetes/overlays/prod/
Étape 3: Vérifier le Déploiement
bash
# Voir les pods
kubectl get pods -n gnl-knowledge-graph

# Voir les services
kubectl get services -n gnl-knowledge-graph

# Voir les ingresses
kubectl get ingress -n gnl-knowledge-graph
Étape 4: Tester l'API
bash
# Port-forward
kubectl port-forward service/api-service -n gnl-knowledge-graph 8000:8000

# Tester le health check
curl http://localhost:8000/api/health
Déploiement avec Helm
Étape 1: Installer les Dépendances
bash
# Mettre à jour les dépendances
helm dependency update deploy/helm/gnl-graph/
Étape 2: Installer le Chart
bash
# Développement
helm install gnl-graph deploy/helm/gnl-graph/ \
  -f deploy/helm/gnl-graph/values-dev.yaml \
  --namespace gnl-knowledge-graph \
  --create-namespace

# Production
helm install gnl-graph deploy/helm/gnl-graph/ \
  -f deploy/helm/gnl-graph/values-prod.yaml \
  --namespace gnl-knowledge-graph \
  --create-namespace
Étape 3: Mettre à Jour
bash
# Mettre à jour le chart
helm upgrade gnl-graph deploy/helm/gnl-graph/ \
  -f deploy/helm/gnl-graph/values-prod.yaml
Étape 4: Désinstaller
bash
# Désinstaller
helm uninstall gnl-graph --namespace gnl-knowledge-graph
Déploiement Infrastructure (Terraform)
Étape 1: Initialiser Terraform
bash
cd deploy/terraform/environments/dev

# Initialiser
terraform init

# Planifier
terraform plan
Étape 2: Appliquer
bash
# Appliquer
terraform apply

# Confirmer
yes
Étape 3: Détruire
bash
# Détruire
terraform destroy
Rollback
Kubernetes
bash
# Rollback d'un déploiement
kubectl rollout undo deployment/gnl-api -n gnl-knowledge-graph

# Voir l'historique
kubectl rollout history deployment/gnl-api -n gnl-knowledge-graph
Helm
bash
# Voir l'historique
helm history gnl-graph --namespace gnl-knowledge-graph

# Rollback
helm rollback gnl-graph 1 --namespace gnl-knowledge-graph
Vérification Post-Déploiement
Health Checks
bash
# API
curl http://localhost:8000/api/health

# Neo4j
curl http://localhost:7474

# Qdrant
curl http://localhost:6333
Tests de Base
bash
# Exécuter les tests
pytest tests/

# Tester l'API
python scripts/test_api.py
Problèmes Courants
Neo4j ne démarre pas
bash
# Voir les logs
docker logs gnl-neo4j

# Augmenter la mémoire
export NEO4J_dbms_memory_heap_max__size=4g
Kafka ne démarre pas
bash
# Voir les logs
docker logs gnl-kafka

# Augmenter la mémoire
export KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"
API ne répond pas
bash
# Voir les logs
docker logs gnl-api

# Vérifier les connexions
docker exec gnl-api curl neo4j:7687