#!/bin/bash
# ============================================================================
# Script pour exécuter les tests
# ============================================================================
# Description: Exécute les tests unitaires et d'intégration
# Utilisation: ./run_tests.sh [test_path]
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   GNL Knowledge Graph - Tests${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""

# Se placer à la racine du projet
cd ../..

# Activer l'environnement virtuel
echo -e "${YELLOW}🔧 Activation de l'environnement virtuel...${NC}"
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
echo -e ""

# Installation des dépendances de test
echo -e "${YELLOW}📦 Installation des dépendances de test...${NC}"
pip install -r requirements-dev.txt -q
echo -e "${GREEN}✅ Dépendances installées${NC}"
echo -e ""

# Déterminer le chemin de test
TEST_PATH="${1:-tests/}"
echo -e "${YELLOW}📋 Test path: ${TEST_PATH}${NC}"
echo -e ""

# Exécuter les tests
echo -e "${YELLOW}🧪 Exécution des tests...${NC}"
echo -e ""

pytest ${TEST_PATH} \
    -v \
    --cov=src \
    --cov-report=term \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    --maxfail=1 \
    --tb=short

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   ✅ Tous les tests sont passés !${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}   ❌ Certains tests ont échoué${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi

# Ouvrir le rapport de couverture
if [ -f "htmlcov/index.html" ]; then
    echo -e ""
    echo -e "${YELLOW}📊 Rapport de couverture généré dans htmlcov/index.html${NC}"
    echo -e "${YELLOW}🔍 Ouvrir avec : open htmlcov/index.html${NC}"
fi