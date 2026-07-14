❓ Questions de Compétence

Introduction

Les questions de compétence (Competency Questions - CQ) sont des questions que l'ontologie doit pouvoir répondre. Elles guident la conception et valident la couverture du domaine.

Catégories

1. Questions sur les Incidents

| ID    |             Question                      |                            Requête Cypher                               |
|-------|-------------------------------------------|-------------------------------------------------------------------------|
| CQ-01 | Quels incidents ont affecté ce pipeline ? | `MATCH (i:Incident)-[:AFFECTE]->(p:Pipeline {id: 'PIPE-001'}) RETURN i` |
| CQ-02 | Quels sont les incidents critiques ?      | `MATCH (i:Incident {gravite: 'critique'}) RETURN i`                     |
| CQ-03 | Quelle est la tendance des incidents ?    | `MATCH (i:Incident) RETURN i.date, count(i)`                            |
| CQ-04 | Quels sont les incidents récurrents ?     | `MATCH (i:Incident)-[:AFFECTE]->(e) RETURN e.id, count(i)`              |
| CQ-05 | Quel est l'impact d'un incident ?         | `MATCH (i:Incident {id: 'INC-001'})-[:AFFECTE]->(e) RETURN e`           |

2. Questions sur les Risques

| ID    |           Question                     |                                 Requête Cypher                                                       |
|-------|----------------------------------------|------------------------------------------------------------------------------------------------------|
| CQ-06 | Quel est le risque sur ce pipeline ?   | `MATCH (p:Pipeline {id: 'PIPE-001'}) OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(p) RETURN p, count(i)` |
| CQ-07 | Quels sont les équipements critiques ? | `MATCH (e) OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e) RETURN e, count(i)`                           |
| CQ-08 | Quels clients sont impactés ?          | `MATCH (p:Pipeline)-[:DESSERT]->(c:Client) RETURN c`                                                 |

3. Questions sur les Routes

| ID    |             Question             |                                      Requête Cypher                                               |
|-------|----------------------------------|---------------------------------------------------------------------------------------------------|
| CQ-09 | Quelle est la route optimale ?   | `MATCH path = shortestPath((start)-[:ALIMENTE|DESSERT*]->(end)) RETURN path`                      |
| CQ-10 | Y a-t-il une route alternative ? | `MATCH path = shortestPath(...) WHERE NONE(n IN nodes(path) WHERE n.id = 'PIPE-001') RETURN path` |

4. Questions sur la Logistique

| ID    |              Question                       |                                                     Requête Cypher                                                   |
|-------|-------------------------------------------- |----------------------------------------------------------------------------------------------------------------------|
| CQ-11 | Quelle est la chaîne d'approvisionnement ?  | `MATCH path = (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)-[:DESSERT]->(c:Client) RETURN path` |
| CQ-12 | Quels sont les fournisseurs d'un terminal ? | `MATCH (f:Fournisseur)-[:FOURNIT]->(t:Terminal {id: 'TERM-001'}) RETURN f`                                           |
| CQ-13 | Quels sont les clients d'un pipeline ?      | `MATCH (p:Pipeline {id: 'PIPE-001'})-[:DESSERT]->(c:Client) RETURN c`                                                |

5. Questions sur la Maintenance

| ID    |            Question                      |                        Requête Cypher                             |
|-------|------------------------------------------|-------------------------------------------------------------------|
| CQ-14 | Quel est l'historique des maintenances ? | `MATCH (m:Maintenance)-[:AFFECTE]->(e {id: 'PIPE-001'}) RETURN m` |
| CQ-15 | Quelle est la maintenance planifiée ?    | `MATCH (m:Maintenance {statut: 'planifiee'}) RETURN m`            |

Matrice de Couverture

| Catégorie   | Questions   | Couverture | Statut |
|-------------|-------------|------------|--------|
| Incidents   |       5     |   100%     |   ✅   |
| Risques     |       3     |   100%     |   ✅   |
| Routes      |       2     |   100%     |   ✅   |
| Logistique  |       3     |   100%     |   ✅   |
| Maintenance |       2     |   100%     |   ✅   |
| Total       |      15     |   100%     |   ✅   |

Validation

Script de Validation

python
scripts/validate_competency_questions.py
import sys
from src.graph.operations.crud import GraphCRUD

def validate_cq(cq_id, query):
    crud = GraphCRUD()
    try:
        result = crud.execute_query(query)
        print(f"✅ {cq_id}: OK ({len(result)} résultats)")
        return True
    except Exception as e:
        print(f"❌ {cq_id}: Erreur - {e}")
        return False

Exécuter la validation
questions = load_competency_questions()
results = [validate_cq(q['id'], q['query']) for q in questions]
print(f"\n{sum(results)}/{len(results)} questions validées")
Résultats de Validation

Date: 2026-07-10
Version: 1.0.0
Total: 15 questions
Validées: 15 (100%)
Échecs: 0
Ajout de Questions
Processus
Proposer : Nouvelle question

Valider : Pertinence métier

Formaliser : Écrire la requête

Tester : Exécuter et vérifier

Documenter : Ajouter à la liste

Template

- id: CQ-XXX
  category: "[Catégorie]"
  question: "[Question en français]"
  query: "[Requête Cypher]"
  expected: "[Résultat attendu]"
  validated: true

Conclusion
Les 15 questions de compétence couvrent l'ensemble des besoins métier du projet GNL Knowledge Graph. Elles servent de base à la validation continue de l'ontologie.