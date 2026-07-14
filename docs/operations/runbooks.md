📋 Runbooks

Introduction

Runbooks pour la résolution des incidents courants.

Catégories

1. [Base de données](base-de-données)
2. [API            ](api)
3. [Agents         ](agents)
4. [Infrastructure ](infrastructure)

BASE DE DONNÉES

Neo4j - Connexion Perdue

Symptômes
- API retourne "Neo4j connection failed"
- Neo4j Browser inaccessible
- Requêtes Cypher timeout

Cause Possible
- Service arrêté
- Ressources insuffisantes
- Réseau

Résolution

1. Vérifier le statut
kubectl get pods -n gnl-knowledge-graph | grep neo4j

2. Voir les logs
kubectl logs -f -n gnl-knowledge-graph deployment/neo4j

3. Redémarrer
kubectl rollout restart deployment/neo4j -n gnl-knowledge-graph

4. Vérifier
kubectl port-forward service/neo4j-service -n gnl-knowledge-graph 7687:7687
Vérification

Tester la connexion
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687')"
Neo4j - Stockage Plein
Symptômes

No space left on device"

Neo4j refuse de démarrer

Performances dégradées

Cause Possible

Données trop volumineuses

Logs accumulés

Backups non nettoyés

Résolution

1. Vérifier l'espace
df -h /data

2. Nettoyer les logs
kubectl exec -it -n gnl-knowledge-graph deployment/neo4j -- \
  rm -rf /logs/*

3. Nettoyer les données
kubectl exec -it -n gnl-knowledge-graph deployment/neo4j -- \
  cypher-shell -u neo4j -p $PASSWORD "MATCH (n) WHERE n.created_at < date('2025-01-01') DETACH DELETE n"

4. Agrandir le PVC
kubectl patch pvc neo4j-data-pvc -n gnl-knowledge-graph \
  -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
API
API - Temps de Réponse Élevé
Symptômes

Latence > 5s

Timeout fréquents

CPU élevé

Cause Possible

Requêtes non indexées

Volume de données important

Cache inefficace

Résolution

1. Identifier les requêtes lentes
Dans Neo4j:
CALL dbms.listQueries();

2. Optimiser le cache Redis
redis-cli INFO stats

3. Augmenter les ressources
kubectl patch deployment/gnl-api -n gnl-knowledge-graph \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"gnl-api","resources":{"limits":{"cpu":"2","memory":"4Gi"}}}]}}}}'

4. Ajouter des réplicas
kubectl scale deployment/gnl-api -n gnl-knowledge-graph --replicas=3
Vérification

Tester la performance
ab -n 1000 -c 10 http://api.gnl-knowledge-graph.com/api/health
API - Erreurs 500
Symptômes

Réponses 500

Internal Server Error"

Logs d'erreur

Cause Possible

Bug dans le code

Données invalides

Connexions DB

Résolution

1. Voir les logs
kubectl logs -f -n gnl-knowledge-graph deployment/gnl-api --tail=100

2. Identifier l'erreur
Dans les logs, chercher "ERROR", "Exception", "Traceback"

3. Corriger le code
Si bug, créer une PR avec correction

4. Redéployer
kubectl rollout restart deployment/gnl-api -n gnl-knowledge-graph

5. Rollback si nécessaire
kubectl rollout undo deployment/gnl-api -n gnl-knowledge-graph
AGENTS
Agent - Réponse Lente
Symptômes

Réponses > 30s

Timeout

CPU élevé

Cause Possible

LLM lent

Requêtes complexes

Cache inefficace

Résolution

1. Vérifier la disponibilité du LLM
curl http://ollama:11434/api/tags

2. Optimiser les requêtes
Réduire les sauts dans les requêtes Cypher

3. Activer le cache
export CACHE_ENABLED=true

4. Augmenter les ressources
kubectl patch deployment/gnl-agents -n gnl-knowledge-graph \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"gnl-agents","resources":{"limits":{"cpu":"4","memory":"8Gi"}}}]}}}}'
Agent - Mauvaise Réponse
Symptômes

Réponses incohérentes

Hallucinations

Informations erronées

Cause Possible

Contexte insuffisant

Prompt mal formulé

Modèle non adapté

Résolution

1. Vérifier le contexte
Dans les logs, voir les données envoyées au LLM

2. Ajuster les prompts
Modifier les templates dans src/agents/tools/llm_tools.py

3. Changer de modèle
export LLM_MODEL=llama3:70b

4. Ajouter des exemples (few-shot)
Dans les prompts, ajouter des exemples

5. Vérifier les données
S'assurer que les données Neo4j sont correctes
INFRASTRUCTURE
Kubernetes - Pods CrashLoopBackOff
Symptômes

Pods redémarrent en boucle

CrashLoopBackOff

Logs d'erreur

Cause Possible

Application se plante

Ressources insuffisantes

Configuration invalide

Résolution

bash
1. Voir les logs
kubectl logs -f -n gnl-knowledge-graph deployment/gnl-api

2. Voir l'état
kubectl describe pod -n gnl-knowledge-graph <pod-name>

3. Vérifier les ressources
kubectl top pod -n gnl-knowledge-graph

4. Augmenter les ressources
kubectl patch deployment/gnl-api -n gnl-knowledge-graph \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"gnl-api","resources":{"requests":{"memory":"512Mi"}}}]}}}}'

5. Vérifier la configuration
kubectl describe configmap gnl-config -n gnl-knowledge-graph
Docker - Service ne démarre pas
Symptômes

Container exit

Exited (1)"

Port déjà utilisé

Cause Possible

Port occupé

Configuration erronée

Dépendance non démarrée

Résolution

1. Voir les logs
docker logs gnl-api

2. Vérifier les ports
netstat -tlnp | grep 8000

3. Libérer le port
sudo kill -9 <PID>

4. Redémarrer le service
docker-compose restart gnl-api

5. Voir les dépendances
docker-compose ps
PROCÉDURE D'ESCALADE
Niveau 1 - Support
Contact: helpdesk@gnl-company.com
Temps: 24/7
Délai: < 15 min

Niveau 2 - DevOps
Contact: devops@gnl-company.com
Temps: 24/7
Délai: < 30 min

Niveau 3 - SRE
Contact: sre@gnl-company.com
Temps: 24/7
Délai: < 1h

Niveau 4 - Direction
Contact: cto@gnl-company.com
Temps: Jours ouvrés
Délai: < 24h

POST-MORTEM
Template

Title: "[Incident] Titre de l'incident"
Date: 2026-07-10
Duration: 2h
Impact: API indisponible 30 min

Résumé:
  - Ce qui s'est passé
  - Impact
  - Cause racine

Timeline:
  - 12:00: Début de l'incident
  - 12:15: Alerte déclenchée
  - 12:30: Intervention
  - 13:00: Résolution

Actions:
  - Immédiates:
    - Redémarrage du service
  - Correctives:
    - Mise à jour du monitoring
  - Préventives:
    - Ajout de test

Lessons Learned:
  - Leçon 1
  - Leçon 2

Follow-up:
  - Action 1: Responsable, Date
  - Action 2: Responsable, Date
CONTACTS D'URGENCE

DevOps:
  - Thomas Bernard: +33 1 23 45 67 89
  - Sophie Lefevre: +33 1 23 45 67 90

SRE:
  - Pierre Durand: +33 1 23 45 67 91
  - Marie Martin: +33 1 23 45 67 92

Support:
  - Hotline: +33 1 23 45 67 88
  - Email: helpdesk@gnl-company.com