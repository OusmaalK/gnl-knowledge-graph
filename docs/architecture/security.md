 🔐 Sécurité

Introduction

Ce document décrit les mesures de sécurité mises en place dans le projet GNL Knowledge Graph.

Principes de Sécurité

1. Défense en profondeur** : Plusieurs couches de sécurité
2. Moindre privilège** : Accès minimal nécessaire
3. Sécurité par défaut** : Sécurisé par défaut
4. Traçabilité** : Logs et audits
5. Confidentialité** : Données protégées

Authentification

API


Méthodes:
  - API Key: X-API-Key header
  - JWT Token: Bearer token
  - OAuth2: (future)

Gestion:
  - Clés: Générées aléatoirement
  - Rotation: Mensuelle
  - Révocation: Immédiate
Neo4j

Méthodes:
  - Username / Password
  - TLS/SSL

Gestion:
  - Mot de passe: Complexe (12+ caractères)
  - Rotation: Trimestrielle
  - Accès: Restreint par IP
Kafka

Méthodes:
  - SASL/SCRAM
  - TLS/SSL

Gestion:
  - Utilisateurs: Admin, Producer, Consumer
  - Permissions: ACL sur les topics
Autorisation (RBAC)
Rôles
Rôle	Description	Permissions
Admin	Administration complète	Toutes les opérations
Analyst	Analyse des données	Lecture + requêtes
Viewer	Consultation	Lecture uniquement
Agent	Agents IA	Requêtes spécifiques
Permissions

READ:
  - Graph nodes
  - Graph relationships
  - Incidents
  - Statistics

WRITE:
  - Create nodes
  - Update nodes
  - Delete nodes
  - Create relationships

ADMIN:
  - User management
  - Configuration
  - Backup/Restore
  - Monitoring
Chiffrement
En Transit

Protocoles:
  - HTTPS: API (port 8000)
  - TLS: Neo4j (port 7687)
  - TLS: Kafka (port 9093)
  - TLS: Redis (port 6380)

Certificats:
  - Type: Let's Encrypt / Auto-signés
  - Renouvellement: Automatique
  - Validation: Strict
Au Repos

Données:
  - Neo4j: Enterprise encryption
  - Redis: Persistence encryption
  - Backup: GPG encryption

Clés:
  - Génération: Sécurisée
  - Stockage: Vault / Kubernetes Secrets
  - Rotation: Régulière
Sécurité des Conteneurs
Images Docker

Bonnes pratiques:
  - Images minimales (slim)
  - Non-root user
  - Pas de secrets
  - Scan de vulnérabilités

Outils:
  - Trivy: Scan des images
  - Snyk: Scan des dépendances
  - Docker Bench: Configuration
Kubernetes

Sécurité:
  - Network Policies
  - Pod Security Policies
  - Secrets (encrypted)
  - RBAC

Monitoring:
  - Falco: Détection d'anomalies
  - Audit logs
  - Kubernetes events
Sécurité des Données
Classification

Niveaux:
  - PUBLIC: Données publiques
  - INTERNAL: Usage interne
  - CONFIDENTIAL: Données sensibles
  - RESTRICTED: Données critiques

Mesures:
  - CONFIDENTIAL: Chiffrement + Accès limité
  - RESTRICTED: Chiffrement + Audit + Approbation
PII (Personally Identifiable Information)

Données:
  - Noms des contacts
  - Emails
  - Téléphones

Mesures:
  - Pseudonymisation
  - Accès limité
  - Logs d'accès
  - Suppression après 30 jours
Audit et Logs
Logs

Types:
  - Access logs: Toutes les requêtes
  - Audit logs: Actions sensibles
  - Security logs: Tentatives échouées
  - System logs: Erreurs système

Conservation:
  - Access logs: 30 jours
  - Audit logs: 1 an
  - Security logs: 1 an
Monitoring

Alertes:
  - Échecs d'authentification multiples
  - Accès non autorisés
  - Changements de configuration
  - Backup échoué
Gestion des Incidents
Plan de Réponse
Détection : Monitoring + Alertes

Analyse : Évaluation de l'impact

Containment : Isolation des systèmes

Eradication : Suppression de la menace

Restauration : Retour à l'état normal

Post-incident : Analyse et améliorations

Contacts

Équipe Sécurité:
  - Responsable: ousmaalk@gmail.com
  - Tél: +213658270729
  - Disponibilité: 24/7

Escalade:
  - Niveau 1: Équipe Sécurité
  - Niveau 2: Direction
  - Niveau 3: RSSI
Conformité
Réglementations

RGPD:
  - Protection des données personnelles
  - Droit à l'oubli
  - Portabilité des données

ISO 27001:
  - Management de la sécurité
  - Contrôles d'accès
  - Audits réguliers

NIS2:
  - Sécurité des réseaux
  - Notification des incidents
  - Cyber-résilience
Bonnes Pratiques
Développement
Code Review : Toute modification

Static Analysis : SonarQube / Bandit

Dynamic Analysis : Tests de sécurité

Dépendances : Mises à jour régulières

Secrets : Jamais en dur

Opérations
Principle of Least Privilege : Accès minimal

Regular Audits : Revue des permissions

Backup : Test des restaurations

Patches : Mises à jour de sécurité

Incident Response : Exercices réguliers

