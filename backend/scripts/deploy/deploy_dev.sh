#!/bin/bash
# ============================================================================
# Script de déploiement en développement
# ============================================================================
# Description: Déploie l'application en environnement de développement
# Utilisation: ./deploy_dev.sh
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   GNL Knowledge Graph - Déploiement Dev${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""

# Se placer à la racine du projet
cd ../..

# Vérifier Docker
echo -e "${YELLOW}🔍 Vérification de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas en cours d'exécution${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker OK${NC}"
echo -e ""

# Construire les images Docker
echo -e "${YELLOW}🐳 Construction des images Docker...${NC}"
docker build -f deploy/docker/Dockerfile.api -t gnl-api:dev .
docker build -f deploy/docker/Dockerfile.agent -t gnl-agent:dev .
docker build -f deploy/docker/Dockerfile.ingestion -t gnl-ingestion:dev .
docker build -f deploy/docker/Dockerfile.transform -t gnl-transform:dev .
echo -e "${GREEN}✅ Images Docker construites${NC}"
echo -e ""

# Démarrer les services avec Docker Compose (dev)
echo -e "${YELLOW}🚀 Démarrage des services...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
echo -e "${GREEN}✅ Services démarrés${NC}"
echo -e ""

# Attendre que les services soient prêts
echo -e "${YELLOW}⏳ Attente des services...${NC}"
sleep 10
echo -e "${GREEN}✅ Services prêts${NC}"
echo -e ""

# Vérifier les services
echo -e "${YELLOW}🔍 Vérification des services...${NC}"
echo -e "   Neo4j : http://localhost:7474"
echo -e "   Qdrant : http://localhost:6333"
echo -e "   API    : http://localhost:8000/docs"

# Tester l'API
if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API OK${NC}"
else
    echo -e "${YELLOW}⚠️ API non disponible${NC}"
fi
echo -e ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Déploiement Dev terminé !${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}📌 Accès aux services :${NC}"
echo -e "   Neo4j Browser : http://localhost:7474"
echo -e "   Qdrant        : http://localhost:6333"
echo -e "   API Docs      : http://localhost:8000/docs"
echo -e ""
echo -e "${YELLOW}📌 Pour voir les logs :${NC}"
echo -e "   docker-compose logs -f"
echo -e ""
echo -e "${YELLOW}📌 Pour arrêter :${NC}"
echo -e "   docker-compose down"