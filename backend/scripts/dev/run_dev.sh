#!/bin/bash
# ============================================================================
# Script pour lancer l'environnement de développement
# ============================================================================
# Description: Lance l'environnement de développement complet
# Utilisation: ./run_dev.sh
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   GNL Knowledge Graph - Dev Environment${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""

# Se placer à la racine du projet
cd ../..

# Activer l'environnement virtuel
echo -e "${YELLOW}🔧 Activation de l'environnement virtuel...${NC}"
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
echo -e ""

# Vérifier les dépendances
echo -e "${YELLOW}📦 Vérification des dépendances...${NC}"
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
echo -e "${GREEN}✅ Dépendances vérifiées${NC}"
echo -e ""

# Vérifier Neo4j
echo -e "${YELLOW}🔍 Vérification de Neo4j...${NC}"
if curl -s http://localhost:7474 &> /dev/null; then
    echo -e "${GREEN}✅ Neo4j en cours d'exécution${NC}"
else
    echo -e "${YELLOW}⚠️ Neo4j non disponible, démarrage...${NC}"
    docker-compose up -d neo4j
    sleep 10
fi
echo -e ""

# Vérifier Qdrant
echo -e "${YELLOW}🔍 Vérification de Qdrant...${NC}"
if curl -s http://localhost:6333 &> /dev/null; then
    echo -e "${GREEN}✅ Qdrant en cours d'exécution${NC}"
else
    echo -e "${YELLOW}⚠️ Qdrant non disponible, démarrage...${NC}"
    docker-compose up -d qdrant
    sleep 5
fi
echo -e ""

# Démarrer l'API
echo -e "${YELLOW}🚀 Démarrage de l'API FastAPI...${NC}"
echo -e "${GREEN}✅ API disponible sur http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}📌 Appuyez sur Ctrl+C pour arrêter${NC}"
echo -e ""

# Lancer l'API avec uvicorn
python -m src.api.app