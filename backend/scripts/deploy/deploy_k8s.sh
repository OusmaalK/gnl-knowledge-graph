#!/bin/bash
# ============================================================================
# Script de déploiement Kubernetes
# ============================================================================
# Description: Déploie l'application sur Kubernetes
# Utilisation: ./deploy_k8s.sh [namespace]
# ============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${1:-gnl-knowledge-graph}"
ENVIRONMENT="${2:-dev}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups/k8s_${TIMESTAMP}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   GNL Knowledge Graph - Déploiement K8s${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Namespace: ${NAMESPACE}${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e ""

# Vérifier les prérequis
echo -e "${YELLOW}🔍 Vérification des prérequis...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl n'est pas installé${NC}"
    exit 1
fi

if ! command -v kustomize &> /dev/null; then
    echo -e "${RED}❌ kustomize n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prérequis vérifiés${NC}"
echo -e ""

# Vérifier la connexion au cluster
echo -e "${YELLOW}🔗 Vérification de la connexion au cluster...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Connexion au cluster impossible${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Connexion au cluster établie${NC}"
echo -e ""

# Créer le namespace
echo -e "${YELLOW}📁 Création du namespace...${NC}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace créé${NC}"
echo -e ""

# Créer les secrets
echo -e "${YELLOW}🔐 Création des secrets...${NC}"
if [ -f "../.env" ]; then
    # Générer les secrets à partir du .env
    kubectl create secret generic gnl-secrets \
        --namespace=${NAMESPACE} \
        --from-env-file=../.env \
        --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}✅ Secrets créés à partir de .env${NC}"
else
    echo -e "${RED}❌ Fichier .env non trouvé${NC}"
    exit 1
fi
echo -e ""

# Sauvegarder la configuration actuelle
echo -e "${YELLOW}💾 Sauvegarde de la configuration actuelle...${NC}"
mkdir -p ${BACKUP_DIR}
kubectl get all -n ${NAMESPACE} -o yaml > ${BACKUP_DIR}/current_state.yaml
echo -e "${GREEN}✅ Sauvegarde effectuée dans ${BACKUP_DIR}${NC}"
echo -e ""

# Déployer avec kustomize
echo -e "${YELLOW}🚀 Déploiement de l'application...${NC}"
kubectl apply -k ../deploy/kubernetes/overlays/${ENVIRONMENT}/
echo -e "${GREEN}✅ Application déployée${NC}"
echo -e ""

# Attendre que les pods soient prêts
echo -e "${YELLOW}⏳ Attente du démarrage des pods...${NC}"
kubectl wait --for=condition=ready pod -l app=gnl-api -n ${NAMESPACE} --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=gnl-agents -n ${NAMESPACE} --timeout=120s || true
echo -e "${GREEN}✅ Pods prêts${NC}"
echo -e ""

# Afficher les services
echo -e "${YELLOW}📋 Services déployés :${NC}"
kubectl get services -n ${NAMESPACE}
echo -e ""

# Afficher les pods
echo -e "${YELLOW}📋 Pods en cours d'exécution :${NC}"
kubectl get pods -n ${NAMESPACE}
echo -e ""

# Vérifier le health check
echo -e "${YELLOW}🔍 Vérification du health check...${NC}"
sleep 10
kubectl port-forward service/api-service -n ${NAMESPACE} 8000:8000 &
PF_PID=$!
sleep 5

if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check OK${NC}"
else
    echo -e "${RED}❌ Health check échoué${NC}"
fi

kill $PF_PID 2>/dev/null
echo -e ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Déploiement terminé avec succès !${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}📌 Pour accéder à l'API :${NC}"
echo -e "   kubectl port-forward service/api-service -n ${NAMESPACE} 8000:8000"
echo -e "   curl http://localhost:8000/api/health"
echo -e ""
echo -e "${YELLOW}📌 Pour voir les logs :${NC}"
echo -e "   kubectl logs -f -n ${NAMESPACE} -l app=gnl-api"
echo -e ""
echo -e "${YELLOW}📌 Pour supprimer le déploiement :${NC}"
echo -e "   kubectl delete -k ../deploy/kubernetes/overlays/${ENVIRONMENT}/"