🔧 Opérations

## Introduction

Ce dossier contient la documentation opérationnelle pour le déploiement, le monitoring et la gestion du projet GNL Knowledge Graph.

## Documents

| Document | Description |
|----------|-------------|
| [deployment-guide.md](deployment-guide.md) | Guide de déploiement |
| [monitoring.md](monitoring.md) | Monitoring et observabilité |
| [runbooks.md](runbooks.md) | Runbooks pour les incidents |

## Équipe

### Rôles

| Rôle | Responsabilité |
|------|----------------|
| **DevOps** | Infrastructure, déploiement |
| **SRE** | Monitoring, performance |
| **Support** | Incidents, assistance |

### Contacts

```yaml
DevOps:
  - Nom: Thomas Bernard
  - Email: thomas.bernard@gnl-company.com
  - Tél: +33 1 23 45 67 89

SRE:
  - Nom: Sophie Lefevre
  - Email: sophie.lefevre@gnl-company.com
  - Tél: +33 1 23 45 67 90
Environnements
Environnement	URL	Description
Dev	dev.gnl-knowledge-graph.com	Développement
Staging	staging.gnl-knowledge-graph.com	Pré-production
Prod	gnl-knowledge-graph.com	Production
Calendrier des Opérations
yaml
Quotidien:
  - Backup Neo4j (02:00)
  - Rotation des logs (03:00)
  - Vérification des alertes (08:00)

Hebdomadaire:
  - Revue des métriques (Lundi 10:00)
  - Mise à jour de sécurité (Mercredi)

Mensuel:
  - Audit de sécurité (1er jeudi)
  - Test de restauration (2e mardi)
Contacts d'Urgence
yaml
Niveau 1 (DevOps):
  - Disponible: 24/7
  - Temps de réponse: < 15 min

Niveau 2 (SRE):
  - Disponible: 24/7
  - Temps de réponse: < 30 min

Niveau 3 (Architecte):
  - Disponible: Jours ouvrés
  - Temps de réponse: < 2h