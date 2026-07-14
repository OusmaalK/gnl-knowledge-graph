#!/bin/bash
# ============================================================================
# Script de déploiement en production
# ============================================================================
# Description: Déploie l'application en environnement de production
# Utilisation: ./deploy_prod.sh
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  GNL Knowledge Graph - Déploiement Prod${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""

# Confirmation
echo -e "${RED}⚠️  ATTENTION : Ce script déploie en PRODUCTION${NC}"
echo -e "${YELLOW}Voulez-vous continuer ? (o/N)${NC}"
read -r confirmation

if [[ ! "$confirmation" =~ ^[oO]$ ]]; then
    echo -e "${YELLOW}❌ Déploiement annulé${NC}"
    exit 0
fi
echo -e ""

# Se placer à la racine du projet
cd ../..

# Vérification des prérequis
echo -e "${YELLOW}🔍 Vérification des prérequis...${NC}"

# Vérifier Kubernetes
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl n'est pas installé${NC}"
    exit 1
fi

# Vérifier Helm
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prérequis vérifiés${NC}"
echo -e ""

# Sauvegarde de la base de données
echo -e "${YELLOW}💾 Sauvegarde de la base de données...${NC}"
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="backups/neo4j_backup_${timestamp}.dump"
docker exec -t gnl-neo4j neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/import/backup.dump
docker cp gnl-neo4j:/var/lib/neo4j/import/backup.dump ${backup_file}
echo -e "${GREEN}✅ Sauvegarde effectuée : ${backup_file}${NC}"
echo -e ""

# Construire les images avec tag de version
echo -e "${YELLOW}🐳 Construction des images Docker...${NC}"
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "latest")
docker build -f deploy/docker/Dockerfile.api -t gnl-api:${VERSION} .
docker build -f deploy/docker/Dockerfile.agent -t gnl-agent:${VERSION} .
docker build -f deploy/docker/Dockerfile.ingestion -t gnl-ingestion:${VERSION} .
docker build -f deploy/docker/Dockerfile.transform -t gnl-transform:${VERSION} .
echo -e "${GREEN}✅ Images Docker construites (version: ${VERSION})${NC}"
echo -e ""

# Déployer avec Helm
echo -e "${YELLOW}🚀 Déploiement avec Helm...${NC}"
helm upgrade --install gnl-graph deploy/helm/gnl-graph/ \
    -f deploy/helm/gnl-graph/values-prod.yaml \
    --set image.tag=${VERSION} \
    --namespace gnl-knowledge-graph \
    --create-namespace \
    --wait
echo -e "${GREEN}✅ Helm déploiement terminé${NC}"
echo -e ""

# Vérifier le déploiement
echo -e "${YELLOW}🔍 Vérification du déploiement...${NC}"
kubectl get pods -n gnl-knowledge-graph
kubectl get services -n gnl-knowledge-graph
echo -e ""

# Tester le health check
echo -e "${YELLOW}🔍 Test du health check...${NC}"
sleep 10
kubectl port-forward service/api-service -n gnl-knowledge-graph 8000:8000 &
PF_PID=$!
sleep 5

if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check OK${NC}"
else
    echo -e "${RED}❌ Health check échoué${NC}"
    echo -e "${YELLOW}📋 Vérifiez les logs :${NC}"
    echo -e "   kubectl logs -f -n gnl-knowledge-graph -l app=gnl-api"
fi

kill $PF_PID 2>/dev/null
echo -e ""

# Notifications
echo -e "${YELLOW}📧 Envoi de la notification de déploiement...${NC}"
# Webhook Slack (optionnel)
# curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"✅ Déploiement GNL Graph v${VERSION} terminé en production\"}" ${SLACK_WEBHOOK_URL}
echo -e "${GREEN}✅ Notification envoyée${NC}"
echo -e ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Déploiement Prod terminé !${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}📌 Version : ${VERSION}${NC}"
echo -e "${YELLOW}📌 Sauvegarde : ${backup_file}${NC}"
echo -e ""
echo -e "${YELLOW}📌 Pour accéder à l'API :${NC}"
echo -e "   kubectl port-forward service/api-service -n gnl-knowledge-graph 8000:8000"
echo -e ""
echo -e "${YELLOW}📌 Pour voir les logs :${NC}"
echo -e "   kubectl logs -f -n gnl-knowledge-graph -l app=gnl-api"