📊 Monitoring et Observabilité

## Introduction

Ce document décrit le système de monitoring et d'observabilité du GNL Knowledge Graph.

## Architecture
┌─────────────────────────────────────────────────────────────────────────┐
│ Métriques et Logs │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Application │────▶│ Prometheus │────▶│ Grafana │ │
│ │ (Metrics) │ │ (Collect) │ │ (Dashboards) │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Application │────▶│ Loki │────▶│ Grafana │ │
│ │ (Logs) │ │ (Collect) │ │ (Logs) │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Application │────▶│ Tempo │────▶│ Grafana │ │
│ │ (Traces) │ │ (Collect) │ │ (Traces) │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────┘

text

## Métriques Collectées

### Métriques Système

```yaml
CPU:
  - usage_percent: Utilisation CPU (%)
  - load_avg: Charge moyenne

Mémoire:
  - used_bytes: Mémoire utilisée
  - available_bytes: Mémoire disponible
  - usage_percent: Utilisation mémoire (%)

Disque:
  - used_bytes: Espace utilisé
  - available_bytes: Espace disponible
  - usage_percent: Utilisation disque (%)

Réseau:
  - rx_bytes: Octets reçus
  - tx_bytes: Octets envoyés
  - errors: Erreurs réseau
Métriques Application
yaml
API:
  - requests_total: Nombre de requêtes
  - request_duration: Durée des requêtes
  - error_rate: Taux d'erreur
  - active_connections: Connexions actives

Neo4j:
  - query_count: Nombre de requêtes
  - query_duration: Durée des requêtes
  - cache_hit_rate: Taux de cache
  - connections: Connexions actives
  - node_count: Nombre de nœuds
  - relationship_count: Nombre de relations

Agents:
  - calls_total: Nombre d'appels
  - duration: Durée des appels
  - error_rate: Taux d'erreur

Cache (Redis):
  - hit_rate: Taux de succès
  - miss_rate: Taux d'échec
  - memory_usage: Utilisation mémoire
  - keys: Nombre de clés
Métriques Business
yaml
Incidents:
  - total: Nombre total d'incidents
  - by_severity: Incidents par gravité
  - by_cause: Incidents par cause
  - resolution_time: Temps de résolution

Logistique:
  - total_routes: Nombre de routes
  - total_volume: Volume total transporté
  - active_pipelines: Pipelines actifs
  - active_terminals: Terminaux actifs

Risques:
  - critical_equipment: Équipements critiques
  - high_risk_equipment: Équipements à haut risque
Dashboards Grafana
Dashboard Principaux
yaml
1. System Overview:
   - État des services
   - Utilisation des ressources
   - Alertes en cours

2. API Performance:
   - Requêtes par seconde
   - Latence
   - Erreurs

3. Neo4j:
   - Requêtes par seconde
   - Cache hit rate
   - Taille de la base

4. Agents:
   - Appels par agent
   - Temps de réponse
   - Taux d'erreur

5. Business:
   - Incidents
   - Risques
   - Logistique
Exemple de Dashboard
json
{
  "title": "GNL Graph - Overview",
  "panels": [
    {
      "title": "API Health",
      "type": "stat",
      "targets": [
        {"expr": "up{job='gnl-api'}"}
      ]
    },
    {
      "title": "Neo4j Queries",
      "type": "graph",
      "targets": [
        {"expr": "rate(neo4j_query_count[5m])"}
      ]
    },
    {
      "title": "Incidents",
      "type": "table",
      "targets": [
        {"expr": "gnl_incidents_total"}
      ]
    }
  ]
}
Alertes
Règles d'Alerte
yaml
Critiques:
  - API down: alert if up < 1 for 2m
  - Neo4j down: alert if up < 1 for 2m
  - High error rate: alert if error_rate > 5% for 5m
  - Low cache hit: alert if cache_hit_rate < 50%

Warnings:
  - High CPU: alert if cpu > 80% for 10m
  - High memory: alert if memory > 85% for 10m
  - High response time: alert if duration > 5s for 5m
  - High incident rate: alert if incidents > 10 in 1h

Info:
  - Backup completed
  - Deployment successful
  - New incident detected
Configuration AlertManager
yaml
route:
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'

receivers:
- name: 'slack-notifications'
  slack_configs:
  - channel: '#alerts'
    title: '{{ .GroupLabels.alertname }}'
    text: '{{ .CommonAnnotations.description }}'

- name: 'email-notifications'
  email_configs:
  - to: 'team@gnl-company.com'
    from: 'alerts@gnl-company.com'
Logging
Structure des Logs
json
{
  "timestamp": "2026-07-10T12:00:00Z",
  "level": "INFO",
  "service": "gnl-api",
  "request_id": "abc-123",
  "message": "User request processed",
  "user": "admin",
  "endpoint": "/api/graph/query",
  "duration_ms": 150
}
Logs par Service
yaml
API:
  - access.log: Requêtes HTTP
  - error.log: Erreurs
  - app.log: Logs applicatifs

Neo4j:
  - query.log: Requêtes
  - debug.log: Débogage

Agents:
  - agent.log: Logs des agents  - llm.log: Appels LLM
Rotation des Logs
yaml
Strategy:
  - Rotation: Quotidienne
  - Compression: gzip
  - Retention: 30 jours

Directives logrotate:
  /var/log/gnl/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
      systemctl reload gnl-api
    endscript
  }
Traces (Distributed Tracing)
Configuration
yaml
Exporter: OTLP (OpenTelemetry)
Endpoint: otel-collector:4317
Sampling: 10% en prod, 100% en dev

Services:
  - API: all requests
  - Neo4j: all queries
  - Agents: all calls
Outils
Prometheus
bash
# Voir les targets
curl http://prometheus:9090/api/v1/targets

# Exécuter une requête
curl 'http://prometheus:9090/api/v1/query?query=up'

# Voir les alertes
curl http://alertmanager:9093/api/v1/alerts
Grafana
bash
# Accès
http://grafana:3000

# Login
User: admin
Password: admin
Loki
bash
# Rechercher des logs
curl -G -s "http://loki:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="gnl-api"}'
Bonnes Pratiques
Métriques
Naming : service_metric_unit

Labels : Limiter à 10 labels

Types : Counter pour événements, Gauge pour états

Cardinalité : Éviter les labels à haute cardinalité

Alertes
Clarté : Descriptions compréhensibles

Actionnables : Instructions de résolution

Seuils : Basés sur des SLOs

Escalade : Définir les niveaux

Logs
Structured Logging : Format JSON

Niveaux : ERROR, WARN, INFO, DEBUG

Corrélation : request_id pour tracer

Rotation : 30 jours de rétention