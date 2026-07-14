#!/bin/bash
# ============================================================================
# Script pour formater le code
# ============================================================================
# Description: Formate le code Python avec black et isort
# Utilisation: ./format_code.sh [check]
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   GNL Knowledge Graph - Format Code${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""

# Se placer à la racine du projet
cd ../..

# Activer l'environnement virtuel
echo -e "${YELLOW}🔧 Activation de l'environnement virtuel...${NC}"
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
echo -e ""

# Déterminer le mode
MODE="${1:-format}"
CHECK=""
if [ "${MODE}" == "check" ]; then
    CHECK="--check"
    echo -e "${YELLOW}🔍 Mode: Vérification uniquement${NC}"
else
    echo -e "${YELLOW}🔧 Mode: Formatage${NC}"
fi
echo -e ""

# Fichiers à formater
FILES="src/ tests/ scripts/"

# isort
echo -e "${YELLOW}📦 isort : tri des imports...${NC}"
if [ "${MODE}" == "check" ]; then
    isort ${FILES} ${CHECK}
else
    isort ${FILES}
fi
echo -e "${GREEN}✅ isort terminé${NC}"

echo -e ""

# black
echo -e "${YELLOW}🎨 black : formatage du code...${NC}"
if [ "${MODE}" == "check" ]; then
    black ${FILES} ${CHECK}
else
    black ${FILES}
fi
echo -e "${GREEN}✅ black terminé${NC}"

echo -e ""

# flake8 (vérification uniquement)
if [ "${MODE}" == "check" ]; then
    echo -e "${YELLOW}🔍 flake8 : vérification du code...${NC}"
    flake8 ${FILES}
    echo -e "${GREEN}✅ flake8 terminé${NC}"
fi

echo -e ""

# mypy (vérification uniquement)
if [ "${MODE}" == "check" ]; then
    echo -e "${YELLOW}🔍 mypy : vérification des types...${NC}"
    mypy src/
    echo -e "${GREEN}✅ mypy terminé${NC}"
fi

echo -e ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Formatage terminé !${NC}"
echo -e "${GREEN}========================================${NC}"