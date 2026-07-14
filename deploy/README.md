markdown
# 🚀 DÉPLOIEMENT - GNL Knowledge Graph

Ce dossier contient tous les fichiers de déploiement pour le projet GNL Knowledge Graph.

## 📁 Structure
deploy/
├── docker/ # Dockerfiles pour les différents services
├── kubernetes/ # Déploiement Kubernetes
├── terraform/ # Infrastructure as Code (Terraform)
└── helm/ # Charts Helm pour Kubernetes

text

## 🐳 Docker

### Construction des images

```bash
# Construire toutes les images
docker build -f deploy/docker/Dockerfile.api -t gnl-api:latest .
docker build -f deploy/docker/Dockerfile.agent -t gnl-agent:latest .
docker build -f deploy/docker/Dockerfile.ingestion -t gnl-ingestion:latest .
docker build -f deploy/docker/Dockerfile.transform -t gnl-transform:latest .
Services Docker Compose
bash
# Démarrer tous les services
docker-compose up -d

# Démarrer un service spécifique
docker-compose up -d neo4j
☸️ Kubernetes
Déploiement
bash
# Développement
kubectl apply -k deploy/kubernetes/overlays/dev/

# Production
kubectl apply -k deploy/kubernetes/overlays/prod/
Services
Service	Port	Description
Neo4j	7474, 7687	Base de données graphe
Qdrant	6333	Base vectorielle
Kafka	9092	Messagerie
Redis	6379	Cache
API	8000	API REST
Agents	8001	Services Agents
🏗️ Terraform
Initialisation
bash
cd deploy/terraform/environments/dev
terraform init
terraform plan
terraform apply
Variables
Copier terraform.tfvars.example vers terraform.tfvars et configurer :

hcl
project_name = "gnl-knowledge-graph"
environment = "dev"
region = "eu-west-1"
🎛️ Helm
Installation
bash
# Développement
helm install gnl-graph ./helm/gnl-graph -f ./helm/gnl-graph/values-dev.yaml

# Production
helm install gnl-graph ./helm/gnl-graph -f ./helm/gnl-graph/values-prod.yaml
🔐 Sécurité
Les secrets sont gérés via Kubernetes Secrets ou HashiCorp Vault

Les mots de passe sont stockés dans des variables d'environnement

TLS/SSL configuré pour les endpoints externes

📊 Monitoring
Prometheus pour les métriques

Grafana pour les dashboards

ELK Stack pour les logs

🔄 CI/CD
Pipeline intégré avec :

GitHub Actions / GitLab CI

Tests automatiques

Déploiement continu (Blue/Green ou Canary)

text

---

## 📄 FICHIER : `deploy/docker/Dockerfile.api`

```dockerfile
# Dockerfile pour l'API FastAPI
# Utilisation: docker build -f deploy/docker/Dockerfile.api -t gnl-api .

FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
COPY requirements-prod.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copier le code source
COPY src/ ./src/
COPY config/ ./config/
COPY .env .env

# Créer un utilisateur non-root
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Changer les permissions
RUN chown -R appuser:appgroup /app

USER appuser

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
